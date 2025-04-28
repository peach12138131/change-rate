import toml
import requests
from typing import List, Dict, Any, Optional,Generator
import time


def load_config(config_path: str) -> Dict[str, Any]:
    
    try:
        return toml.load(config_path)
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return {}

def load_prompt(prompt_path: str) -> str:
  
    try:
        config = toml.load(prompt_path)
        return config.get("prompt", "")
    except Exception as e:
        print(f"加载提示词文件失败: {e}")
        return ""

def split_text(text: str, chunk_size: int = 8096) -> List[str]:
   
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks

def query_gpt_model(prompt: str, article: str, api_key: str, base_url: str = "https://api.anthropic.com/v1", 
                   model: str = "claude-3-7-sonnet-20250219", max_tokens: int = 8192, 
                   temperature: float = 0.0) -> Optional[str]:
  
    url = f"{base_url}/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": f"{prompt}\n here is article:\n{article}"}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response_json = response.json()
        if "content" in response_json and len(response_json["content"]) > 0:
           
            text_content = response_json["content"][0]["text"]
            return text_content
        else:
            print("API返回内容格式异常")
            return None
    except requests.exceptions.RequestException as e:
        print(f"API请求异常: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"API错误响应: {e.response.text}")
        return None



def process_article(article: str, config_path: str = "./config.toml", 
                   prompt_path: str = "./prompts/professional_Editor.toml") -> Generator[str, None, None]:
    
    # 加载配置
    config = load_config(config_path)
    llm_config = config.get("llm", {})
    chunk_size_config = config.get("chunk_size", {})
    chunk_size = chunk_size_config.get("chunk_size", 8096)
    
    # 加载提示词
    prompt = load_prompt(prompt_path)
    print(prompt)
    if not prompt:
        yield "提示词加载失败"
        return
    
    # 分割文章
    chunks = split_text(article, chunk_size=chunk_size)
    print(f"文章已分割为 {len(chunks)} 个部分")
    
    # 处理每个部分
    for i, chunk in enumerate(chunks):
        print(f"正在处理第 {i+1}/{len(chunks)} 部分...")
        
      
        retry_count = 0
        max_retries = 3
        processed_chunk = None
        
        while retry_count < max_retries and processed_chunk is None:
            if retry_count > 0:
                print(f"第 {retry_count} 次重试...")
            
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
                print(f"处理失败，将在10秒后重试...")
                time.sleep(10)  # 失败后等待10秒再重试
        
        if processed_chunk:
            yield processed_chunk
        else:
            print(f"第 {i+1} 部分处理失败，达到最大重试次数，返回原文")
            yield chunk
        
        # 等待10秒，
        if i < len(chunks) - 1:  
            print("等待10秒后处理下一块...")
            time.sleep(10)

# 测试函数
def test_process():
    # 创建一个测试文章
    test_article = "这是一篇测试文章。" * 1000 
    
    # 处理文章
    result = process_article(test_article)
    
    # 输出结果
    print("\n处理结果摘要:")
    print(result[:500] + "...")  
if __name__ == "__main__":
    test_process()
