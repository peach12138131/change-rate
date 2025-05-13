import random
from typing import List, Dict, Any, Optional, Generator, Tuple
from decrease_aiRate import load_config, load_prompt, query_gpt_model

def split_text_with_overlap(text: str, num_chunks: int, max_chunk_size: int, min_chunk_size: int, overlap_ratio: float = 0.3) -> List[str]:
    """
    Split text into chunks with overlap between consecutive chunks.
    
    Args:
        text: The text to split
        num_chunks: Number of chunks to split into
        max_chunk_size: Maximum size of each chunk
        min_chunk_size: Minimum size for meaningful text chunks
        overlap_ratio: Percentage of overlap between consecutive chunks
        
    Returns:
        List of text chunks
    """
    text_length = len(text)
    
    # If text is too short, duplicate it to meet num_chunks
    if text_length / num_chunks < min_chunk_size:
        return [text] * num_chunks
    
    # Calculate raw chunk size (without overlap)
    chunk_size_raw = text_length / (num_chunks - (num_chunks - 1) * overlap_ratio)
    
    # Cap at max_chunk_size if needed
    chunk_size = min(int(chunk_size_raw), max_chunk_size)
    
    # Calculate overlap size in characters
    overlap_size = int(chunk_size * overlap_ratio)
    
    chunks = []
    start_pos = 0
    
    for i in range(num_chunks):
        # For the last chunk, just take everything remaining
        if i == num_chunks - 1:
            chunks.append(text[start_pos:])
            break
            
        end_pos = min(start_pos + chunk_size, text_length)
        chunks.append(text[start_pos:end_pos])
        
        # Move start position for next chunk, accounting for overlap
        start_pos = end_pos - overlap_size
    
    return chunks

def select_prompts(prompt_paths: List[str], num_chunks: int, random_selection: bool = False) -> List[Tuple[str, str]]:
    """
    Select and distribute prompts for text chunks.
    
    Args:
        prompt_paths: List of paths to prompt files
        num_chunks: Number of chunks to process
        random_selection: Whether to randomly select prompts
        
    Returns:
        List of tuples containing (prompt_path, prompt_content) for each chunk
    """
    if not prompt_paths:
        raise ValueError("At least one prompt path must be provided")
    
    # Load all prompts
    all_prompts = []
    for path in prompt_paths:
        prompt = load_prompt(path)
        if prompt:
            all_prompts.append((path, prompt))
    
    if not all_prompts:
        raise ValueError("Failed to load any valid prompts")
    
    # Create the base prompt distribution (before randomization)
    base_distribution = []
    for i in range(num_chunks):
        prompt_idx = i % len(all_prompts)
        base_distribution.append(all_prompts[prompt_idx])
    
    # If random selection is enabled, shuffle the distribution
    if random_selection:
        random.shuffle(base_distribution)
    
    return base_distribution

def process_articles_multi(article: str, 
                          num_articles: int,
                          prompt_paths: List[str],
                          random_prompt: bool = False,
                          config_path: str = "./config.toml") -> Generator[Tuple[str, str], None, None]:
    """
    Process an article by splitting it into multiple chunks and applying different prompts.
    
    Args:
        article: The article text to process
        num_articles: Number of article chunks to split into
        prompt_paths: List of paths to prompt files
        random_prompt: Whether to randomly select prompts
        config_path: Path to config file
        
    Returns:
        Generator yielding tuples of (processed_chunk, prompt_path) for each chunk
    """
    # Load configuration
    config = load_config(config_path)
    llm_config = config.get("llm", {})
    chunk_size_config = config.get("chunk_size", {})
    max_chunk_size = chunk_size_config.get("chunk_size", 8096)
    min_chunk_size = chunk_size_config.get("min_size", 1024)
    
    # Split the article with overlap
    print(f"Splitting article into {num_articles} chunks with 30% overlap...")
    chunks = split_text_with_overlap(
        article, 
        num_articles, 
        max_chunk_size, 
        min_chunk_size, 
        overlap_ratio=0.3
    )
    
    # Select prompts for each chunk
    prompt_distribution = select_prompts(prompt_paths, len(chunks), random_prompt)
    
    # Process each chunk with its corresponding prompt
    print(f"Processing {len(chunks)} chunks with {len(prompt_paths)} available prompts...")
    
    for i, (chunk, (prompt_path, prompt)) in enumerate(zip(chunks, prompt_distribution)):
        print(f"Processing chunk {i+1}/{len(chunks)} with prompt from {prompt_path}...")
        
        # Retry logic similar to the original function
        retry_count = 0
        max_retries = 3
        processed_chunk = None
        
        while retry_count < max_retries and processed_chunk is None:
            if retry_count > 0:
                print(f"Retry attempt {retry_count}...")
            
            processed_chunk = query_gpt_model(
                prompt=prompt,
                article=chunk,
                api_key=llm_config.get("api_key", ""),
                base_url=llm_config.get("base_url", "https://api.anthropic.com/v1"),
                model=llm_config.get("model", "claude-3-7-sonnet-20250219"),
                max_tokens=llm_config.get("max_tokens", 8192),
                temperature=llm_config.get("temperature", 0.0)
            )
            
            retry_count += 1
            
            if processed_chunk is None and retry_count < max_retries:
                print(f"Processing failed, retrying in 10 seconds...")
                import time
                time.sleep(10)
        
        if processed_chunk:
            # 返回处理后的块内容和对应的prompt路径
            yield (processed_chunk, prompt_path)
        else:
            print(f"Processing failed for chunk {i+1} after maximum retries, returning original text")
            yield (chunk, prompt_path)
        
        # Wait before processing the next chunk to avoid rate limiting
        if i < len(chunks) - 1:
            print("Waiting 10 seconds before processing next chunk...")
            import time
            time.sleep(10)

# Example usage
def test_multi_process():
    # Create a test article
    test_article = "这是一篇测试文章。" * 1000
    
    # List of prompt paths
    prompt_paths = [
        "./prompts/professional_Editor.toml",
        "./prompts/creative_Editor.toml",
        "./prompts/technical_Editor.toml"
    ]
    
    # Process the article
    results = []
    prompt_info = []
    
    for processed_chunk, prompt_path in process_articles_multi(
        article=test_article,
        num_articles=5,
        prompt_paths=prompt_paths,
        random_prompt=True
    ):
        results.append(processed_chunk)
        prompt_info.append(prompt_path)
    
    # Output results
    print("\nProcessing results summary:")
    for i, (result, prompt) in enumerate(zip(results, prompt_info)):
        print(f"Chunk {i+1} using prompt {prompt}")
        print(f"Preview: {result[:100]}...")

if __name__ == "__main__":
    test_multi_process()
