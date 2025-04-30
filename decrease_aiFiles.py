import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
from decrease_aiRate import process_article

def process_folder(
    folder_path: str,
    config_path: str = "./config.toml",
    prompt_path: str = "./prompts/professional_Editor.toml",
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    处理指定文件夹中的所有markdown和txt文件，并将处理后的文件保存到指定目录
    
    Args:
        folder_path: 需要处理的文件夹路径
        config_path: 配置文件路径
        prompt_path: 提示词文件路径
        output_dir: 输出目录，默认为当前目录下的processed_articles文件夹
        
    Returns:
        包含处理结果的字典，包含以下键:
        - success: 处理成功的文件数量
        - failed: 处理失败的文件数量
        - skipped: 跳过的文件数量
        - total: 总文件数量
        - output_dir: 输出目录
        - processed_files: 处理成功的文件列表
        - failed_files: 处理失败的文件列表
    """
    # 检查文件夹是否存在
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        raise ValueError(f"文件夹 {folder_path} 不存在或不是一个目录")
    
    # 创建输出目录
    timestamp = datetime.now().strftime("%Y%m%d_%H")
    if output_dir is None:
        output_dir = os.path.join("./processed_articles", f"ai_{timestamp}")
    else:
        output_dir = os.path.join(output_dir, f"ai_{timestamp}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有需要处理的文件
    files_to_process = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith((".md", ".txt")):
                file_path = os.path.join(root, file)
                files_to_process.append(file_path)
    
    total_files = len(files_to_process)
    if total_files == 0:
        return {
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0,
            "output_dir": output_dir,
            "processed_files": [],
            "failed_files": []
        }
    
    # 处理统计
    processed_count = 0
    failed_count = 0
    skipped_count = 0
    processed_files = []
    failed_files = []
    
    # 处理每个文件
    for file_idx, file_path in enumerate(files_to_process):
        try:
            print(f"处理文件 [{file_idx + 1}/{total_files}]: {file_path}")
            
            # 读取文件内容
            with open(file_path, "r", encoding="utf-8") as f:
                article_content = f.read()
            
            if not article_content.strip():
                print(f"文件 {file_path} 内容为空，已跳过")
                skipped_count += 1
                continue
            
            # 生成输出文件名
            file_name = os.path.basename(file_path)
            base_name, ext = os.path.splitext(file_name)
            output_file_name = f"decreaseAI_{base_name}.md"
            output_file_path = os.path.join(output_dir, output_file_name)
            
            # 处理文章 - 使用导入的process_article函数
            processed_content = []
            for processed_chunk in process_article(
                article=article_content,
                config_path=config_path,
                prompt_path=prompt_path
            ):
                processed_content.append(processed_chunk)
            
            # 将处理后的内容写入文件
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write("".join(processed_content))
            
            processed_count += 1
            processed_files.append({
                "original": file_path,
                "processed": output_file_path
            })
            
            print(f"文件处理完成: {output_file_path}")
            
            # 在处理下一个文件前等待一小段时间，避免对API的高频请求
            if file_idx < total_files - 1:
                print("等待3秒后处理下一个文件...")
                time.sleep(3)
        
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")
            failed_count += 1
            failed_files.append({
                "file": file_path,
                "error": str(e)
            })
    
    result = {
        "success": processed_count,
        "failed": failed_count,
        "skipped": skipped_count,
        "total": total_files,
        "output_dir": output_dir,
        "processed_files": processed_files,
        "failed_files": failed_files
    }
    
    print(f"\n处理完成! 成功: {processed_count}, 失败: {failed_count}, 跳过: {skipped_count}, 总计: {total_files}")
    print(f"处理后的文件保存在: {output_dir}")
    
    return result


# 使用示例
if __name__ == "__main__":
    result = process_folder(
        folder_path="./articles",
        config_path="./config.toml",
        prompt_path="./prompts/professional_Editor.toml"
    )
    print(result)
