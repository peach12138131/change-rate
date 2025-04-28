import gradio as gr
import time
import os
import toml
from typing import Generator, List, Dict, Any, Optional


from decrease_aiRate import load_config, load_prompt, split_text, query_gpt_model, process_article

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

def create_gradio_interface():
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
        
    # 启动Gradio应用
    demo.queue()  # 支持流式输出
    demo.launch(server_name="0.0.0.0", server_port=int(port))

if __name__ == "__main__":
    create_gradio_interface()
