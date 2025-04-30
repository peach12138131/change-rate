import gradio as gr
import time
import os
import toml
import zipfile
import tempfile
import shutil
from datetime import datetime
from typing import Generator, List, Dict, Any, Optional
from pathlib import Path


from decrease_aiRate import load_config, load_prompt, split_text, query_gpt_model, process_article
from decrease_aiFiles import process_folder  #处理文件夹

def list_prompt_files(prompt_dir="./prompts/"):
    
    prompt_files = []
    try:
        for file in os.listdir(prompt_dir):
            if file.endswith(".toml"):
                prompt_files.append(os.path.join(prompt_dir, file))
        return prompt_files
    except Exception as e:
        print(f"读取prompt目录失败: {e}")
        return []

def get_prompt_display_names(prompt_files):
    
    return [os.path.basename(file).replace(".toml", "") for file in prompt_files]



def extract_zip_to_temp(zip_file):
    """将上传的ZIP文件解压到临时目录"""
    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="ai_decrease_")
    
    # 解压ZIP文件
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    return temp_dir

def create_zip_from_folder(folder_path):
    """将处理后的文件夹打包成ZIP文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"processed_articles_{timestamp}.zip"
    zip_path = os.path.join(tempfile.gettempdir(), zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
    
    return zip_path

def process_zip_file(zip_file, prompt_name, password):
    """处理上传的ZIP文件并返回处理后的ZIP文件路径"""
    if password != CORRECT_PASSWORD:
        return "密码错误，无法处理文件。"
    
    if zip_file is None:
        return "请上传ZIP文件"
    
    # 获取选择的prompt路径
    selected_index = prompt_names.index(prompt_name) if prompt_name in prompt_names else 0
    prompt_path = prompt_files[selected_index]
    
    try:
        # 解压ZIP文件到临时目录
        temp_dir = extract_zip_to_temp(zip_file)
        
        # 处理解压后的文件夹
        result = process_folder(
            folder_path=temp_dir,
            prompt_path=prompt_path
        )
        
        if result["success"] == 0:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return "没有找到可处理的文件 (.md 或 .txt)"
        
        # 打包处理后的文件夹
        output_zip = create_zip_from_folder(result["output_dir"])
        
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        # 返回处理结果信息和ZIP文件路径
        result_message = f"处理完成! 成功: {result['success']}, 失败: {result['failed']}, 跳过: {result['skipped']}, 总计: {result['total']}"
        return output_zip
        
    except Exception as e:
        return f"处理出错: {str(e)}"

def create_gradio_interface():
    global CORRECT_PASSWORD, prompt_files, prompt_names
    
    # 加载配置
    config = load_config("./config.toml")
    port_config = config.get("port", {})
    port = port_config.get("port", 8860)
    
    # 密码
    CORRECT_PASSWORD = "vivo50"
    
    # 获取所有prompt文件
    prompt_files = list_prompt_files()
    prompt_names = get_prompt_display_names(prompt_files)
    
    if not prompt_files:
        print("警告: 没有找到任何prompt文件")
        prompt_files = ["./prompts/professional_Editor.toml"]  # 默认值
        prompt_names = ["professional_Editor"]
    
    def process_with_updates(article, prompt_name, password):
        """处理文章并实时更新结果"""
        if password != CORRECT_PASSWORD:
            return "密码错误，无法处理文章。"
            
        if not article:
            return "请输入文章内容"
        
        # 根据选择的prompt名找到对应的文件路径
        selected_index = prompt_names.index(prompt_name) if prompt_name in prompt_names else 0
        prompt_path = prompt_files[selected_index]
        
        all_results = []
        
        # 使用生成器
        for chunk in process_article(article, prompt_path=prompt_path):
            all_results.append(chunk)
            yield "\n\n".join(all_results)
    
    # Gradio界面
    with gr.Blocks(title="Decrease AI Effect") as demo:
        gr.Markdown("# Decrease AI Effect")
        gr.Markdown("减少AI生成痕迹")
        
        with gr.Row():
            # 密码输入框
            password_input = gr.Textbox(
                type="password",  # 使用密码类型，显示为****
                label="Password",
                placeholder="请输入密码",
                value=""  
            )
        
        with gr.Row():
            # 选择Prompt
            prompt_dropdown = gr.Dropdown(
                choices=prompt_names,
                value=prompt_names[0] if prompt_names else None,
                label="choose your style"
            )
        
        # 创建选项卡
        with gr.Tabs():
            with gr.TabItem("文本处理"):
                with gr.Row():
                    # 输入文章
                    input_text = gr.Textbox(
                        lines=10, 
                        placeholder="请输入你的文章...",
                        label="输入文章"
                    )
                
                # 处理按钮
                process_button = gr.Button("开始处理")
                
                with gr.Row():
                    # 结果输出框
                    output_text = gr.Textbox(
                        lines=15,
                        label="处理结果 (实时更新)",
                        interactive=False
                    )
                
                # 绑定事件
                process_button.click(
                    fn=process_with_updates,
                    inputs=[input_text, prompt_dropdown, password_input],
                    outputs=output_text
                )

                with gr.Row():
                    markdown_view = gr.Markdown(
                        value="",
                        label="Markdown View"
                    )
                    
                view_button = gr.Button("以Markdown格式查看")

                view_button.click(
                    fn=lambda x: x,  # 简单地传递文本
                    inputs=output_text,
                    outputs=markdown_view
                )
            
            with gr.TabItem("批量处理 (ZIP文件)"):
                with gr.Row():
                    # ZIP文件上传
                    zip_file_input = gr.File(
                        label="上传ZIP文件 (包含 .md 或 .txt 文件)",
                        file_types=[".zip"]
                    )
                
                # 处理ZIP按钮
                process_zip_button = gr.Button("处理ZIP文件")
                
                # 处理结果和下载链接
                zip_result = gr.File(label="处理结果 (ZIP文件下载)")
                
                # 绑定事件
                process_zip_button.click(
                    fn=process_zip_file,
                    inputs=[zip_file_input, prompt_dropdown, password_input],
                    outputs=zip_result
                )
        
    # 启动Gradio应用
    demo.queue()  # 支持流式输出
    demo.launch(server_name="0.0.0.0", server_port=int(port))

if __name__ == "__main__":
    create_gradio_interface()
