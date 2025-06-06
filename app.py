import gradio as gr
import time
import os
import toml
import zipfile
import tempfile
import shutil
import random
import asyncio
import threading
import queue
from datetime import datetime
from typing import Generator, List, Dict, Any, Optional, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from decrease_aiRate import load_config, load_prompt, split_text, query_gpt_model, process_article
from decrease_aiFiles import process_folder  # 处理文件夹
from multi_Articles import process_articles_multi  # 导入修改后的多文章处理函数
from deep_research import send_research_request , extract_final_report  # 深度研究请求

# 全局线程池，支持多个并发任务
executor = ThreadPoolExecutor(max_workers=8)  # 增加并发数

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

def get_prompt_name_from_path(prompt_path, prompt_files, prompt_names):
    """从prompt路径获取显示名称"""
    if prompt_path in prompt_files:
        index = prompt_files.index(prompt_path)
        return prompt_names[index]
    return os.path.basename(prompt_path).replace(".toml", "")

def extract_zip_to_temp(zip_file):
    """将上传的ZIP文件解压到临时目录"""
    temp_dir = tempfile.mkdtemp(prefix="ai_decrease_")
    
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
        
        return output_zip
        
    except Exception as e:
        return f"处理出错: {str(e)}"

def research_and_process_single_async(query, prompt_name, password):
    """异步执行深度研究并使用单一风格处理 - 保持并发能力"""
    if password != CORRECT_PASSWORD:
        yield "密码错误，无法处理文章。", ""
        return
    
    if not query.strip():
        yield "请输入研究查询内容", ""
        return
    
    # 获取选择的prompt路径
    selected_index = prompt_names.index(prompt_name) if prompt_name in prompt_names else 0
    prompt_path = prompt_files[selected_index]
    
    try:
        # 显示开始状态
        yield "正在启动深度研究任务...", ""
        
        # 使用队列进行线程间通信
        result_queue = queue.Queue()
        research_content = ""
        
        def research_worker():
            """在单独线程中执行研究，通过队列传递结果"""
            try:
                content = ""
                for chunk in send_research_request(query):
                    content += chunk
                    result_queue.put(("chunk", content))
                result_queue.put(("done", content))
            except Exception as e:
                result_queue.put(("error", str(e)))
        
        # 提交研究任务到线程池
        future = executor.submit(research_worker)
        
        # 实时获取研究进展
        while True:
            try:
                # 非阻塞获取队列内容，超时0.1秒
                msg_type, content = result_queue.get(timeout=0.1)
                
                if msg_type == "chunk":
                    research_content = content
                    yield f"【研究进行中】\n\n{research_content}", ""
                elif msg_type == "done":
                    research_content = content
                    yield f"【研究完成】\n\n{research_content}", ""
                    break
                elif msg_type == "error":
                    yield f"研究出错: {content}", ""
                    return
                    
            except queue.Empty:
                # 队列为空，继续等待
                continue
            except Exception as e:
                yield f"处理出错: {str(e)}", ""
                return
        
        # 第二步：处理研究结果
        if research_content.strip():
            final_report_content = extract_final_report(research_content)
    
            if final_report_content != research_content:
                yield f"【研究完成】\n\n{research_content}", f"正在处理最终报告内容... (已提取 {len(final_report_content)} 字符)"
            else:
                yield f"【研究完成】\n\n{research_content}", "正在处理研究结果..."
            
            # 异步处理文章
            def do_process():
                all_results = []
                for chunk in process_article(final_report_content, prompt_path=prompt_path):
                    all_results.append(chunk)
                return "\n\n".join(all_results)
            
            future = executor.submit(do_process)
            processed_result = future.result()
            
            yield f"【研究完成】\n\n{research_content}", f"【处理结果】\n\n{processed_result}"
        else:
            yield f"【研究完成】\n\n{research_content}", "研究内容为空，无法进行处理"
            
    except Exception as e:
        yield f"处理出错: {str(e)}", ""

def research_and_process_multi_async(query, num_articles, prompt_selections, random_prompt, password):
    """异步执行深度研究并使用多风格分块处理 - 保持并发能力"""
    # 初始化结果列表
    results = [""] * 11  # 0-研究结果，1-10处理结果
    
    if password != CORRECT_PASSWORD:
        results[0] = "密码错误，无法处理文章。"
        yield results
        return
    
    if not query.strip():
        results[0] = "请输入研究查询内容"
        yield results
        return
    
    if not prompt_selections:
        results[0] = "请至少选择一种文本风格"
        yield results
        return
    
    # 获取选择的prompt路径
    selected_prompt_paths = []
    for prompt_name in prompt_selections:
        if prompt_name in prompt_names:
            selected_index = prompt_names.index(prompt_name)
            selected_prompt_paths.append(prompt_files[selected_index])
    
    if not selected_prompt_paths:
        selected_prompt_paths = [prompt_files[0]]
    
    try:
        # 第一步：使用队列进行线程间通信的深度研究
        results[0] = "正在启动深度研究任务..."
        yield results
        
        # 使用队列进行线程间通信
        result_queue = queue.Queue()
        research_content = ""
        
        def research_worker():
            """在单独线程中执行研究，通过队列传递结果"""
            try:
                content = ""
                for chunk in send_research_request(query):
                    content += chunk
                    result_queue.put(("chunk", content))
                result_queue.put(("done", content))
            except Exception as e:
                result_queue.put(("error", str(e)))
        
        # 提交研究任务到线程池
        future = executor.submit(research_worker)
        
        # 实时获取研究进展
        while True:
            try:
                # 非阻塞获取队列内容，超时0.1秒
                msg_type, content = result_queue.get(timeout=0.1)
                
                if msg_type == "chunk":
                    research_content = content
                    results[0] = f"【研究进行中】\n\n{research_content}"
                    yield results
                elif msg_type == "done":
                    research_content = content
                    results[0] = f"【研究完成】\n\n{research_content}"
                    yield results
                    break
                elif msg_type == "error":
                    results[0] = f"研究出错: {content}"
                    yield results
                    return
                    
            except queue.Empty:
                # 队列为空，继续等待
                continue
            except Exception as e:
                results[0] = f"处理出错: {str(e)}"
                yield results
                return
        
        # 第二步：多风格分块处理
        if research_content.strip():
            # 初始化处理状态
            for i in range(1, num_articles + 1):
                results[i] = "等待处理..."
            yield results
            
            final_report_content = extract_final_report(research_content)

            if final_report_content != research_content:
                results[0] = f"【研究完成】\n\n{research_content}\n\n【提取最终报告】已提取 {len(final_report_content)} 字符用于处理"
                yield results
            
            # 异步处理多个文章块
            def do_multi_process():
                processed_results = []
                for i, (chunk, prompt_path) in enumerate(process_articles_multi(
                    article=final_report_content,
                    num_articles=num_articles,
                    prompt_paths=selected_prompt_paths,
                    random_prompt=random_prompt
                )):
                    if i < 10:  # 最多处理10个块
                        style_name = get_prompt_name_from_path(prompt_path, prompt_files, prompt_names)
                        processed_results.append(f"【风格: {style_name}】\n\n{chunk}")
                return processed_results
            
            # 提交处理任务到线程池
            future = executor.submit(do_multi_process)
            processed_results = future.result()
            
            # 更新结果
            for i, result_text in enumerate(processed_results):
                if i + 1 < len(results):
                    results[i + 1] = result_text
            
            # 处理完成后，将未使用的文本框清空
            for i in range(len(processed_results) + 1, 11):
                results[i] = ""
                
        else:
            results[1] = "研究内容为空，无法进行处理"
            
        yield results
        
    except Exception as e:
        results[0] = f"处理出错: {str(e)}"
        yield results

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
    
    def process_multi_with_updates(article, num_articles, prompt_selections, random_prompt, password):
        """处理文章分块，每个文章块在单独的文本框中显示，并指明使用的prompt风格"""
        # 初始化结果列表（最多10个块）
        results = [""] * 10
        
        if password != CORRECT_PASSWORD:
            results[0] = "密码错误，无法处理文章。"
            return results
            
        if not article:
            results[0] = "请输入文章内容"
            return results
        
        if not prompt_selections:
            results[0] = "请至少选择一种文本风格"
            return results
        
        # 获取选择的prompt路径和名称
        selected_prompt_paths = []
        for prompt_name in prompt_selections:
            if prompt_name in prompt_names:
                selected_index = prompt_names.index(prompt_name)
                selected_prompt_paths.append(prompt_files[selected_index])
        
        if not selected_prompt_paths:
            selected_prompt_paths = [prompt_files[0]]  # 默认使用第一个prompt
        
        # 初始化为等待处理状态
        for i in range(num_articles):
            results[i] = "等待处理..."
        
        # 使用多文章处理函数
        for i, (chunk, prompt_path) in enumerate(process_articles_multi(
            article=article,
            num_articles=num_articles,
            prompt_paths=selected_prompt_paths,
            random_prompt=random_prompt
        )):
            if i < 10:  # 最多处理10个块
                # 获取prompt的显示名称
                style_name = get_prompt_name_from_path(prompt_path, prompt_files, prompt_names)
                
                # 更新对应位置的结果，包含风格信息
                results[i] = f"【风格: {style_name}】\n\n{chunk}"
                
                # 实时更新UI
                yield results
        
        # 处理完成后，将未使用的文本框清空
        for i in range(num_articles, 10):
            results[i] = ""
            
        yield results
    
    # Gradio界面
    with gr.Blocks(title="Aeromind") as demo:
        gr.Markdown("# Aeromind")
        gr.Markdown("一站式文本AI生成系统")
        
        with gr.Row():
            # 密码输入框
            password_input = gr.Textbox(
                type="password",  # 使用密码类型，显示为****
                label="Password",
                placeholder="请输入密码",
                value=""  
            )
        
        # 创建选项卡
        with gr.Tabs():
            with gr.TabItem("单一风格处理"):
                with gr.Row():
                    # 选择Prompt
                    prompt_dropdown = gr.Dropdown(
                        choices=prompt_names,
                        value=prompt_names[0] if prompt_names else None,
                        label="选择文本风格"
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
            
            with gr.TabItem("多风格分块处理"):
                with gr.Row():
                    # 输入文章
                    multi_input_text = gr.Textbox(
                        lines=10, 
                        placeholder="请输入你的文章...",
                        label="输入文章"
                    )
                
                with gr.Row():
                    # 文章块数量选择
                    num_articles_slider = gr.Slider(
                        minimum=2, 
                        maximum=10, 
                        value=3, 
                        step=1, 
                        label="文章分块数量", 
                        info="选择将文章分为几个块处理 (2-10)"
                    )
                    
                    # 随机选择prompt选项
                    random_prompt_checkbox = gr.Checkbox(
                        label="随机分配文本风格", 
                        value=False, 
                        info="随机分配选定的文本风格到各个文章块"
                    )
                
                with gr.Row():
                    # 多选Prompt
                    multi_prompt_dropdown = gr.Dropdown(
                        choices=prompt_names,
                        value=[prompt_names[0]] if prompt_names else None,
                        label="选择一个或多个文本风格",
                        multiselect=True,
                        info="可以选择多种风格，系统会自动分配到各个文章块"
                    )
                
                # 处理按钮
                multi_process_button = gr.Button("开始多风格处理")
                
                # 创建文章块输出区域
                article_chunks_output = []
                
                # 每行显示2个文本框，最多10个文本框
                for row in range(5):  # 5行，每行2个
                    with gr.Row():
                        for col in range(2):  # 每行2列
                            chunk_index = row * 2 + col
                            chunk_output = gr.Textbox(
                                lines=10, 
                                label=f"文章块 {chunk_index + 1}",
                                interactive=False
                            )
                            article_chunks_output.append(chunk_output)
                
                # 绑定事件 - 这里不使用列表嵌套，直接传递所有文本框
                multi_process_button.click(
                    fn=process_multi_with_updates,
                    inputs=[
                        multi_input_text, 
                        num_articles_slider, 
                        multi_prompt_dropdown, 
                        random_prompt_checkbox, 
                        password_input
                    ],
                    outputs=article_chunks_output
                )
            
            with gr.TabItem("深度研究 + 单一风格 "):
                with gr.Row():
                    # 研究查询输入
                    research_query_input = gr.Textbox(
                        lines=3,
                        placeholder="请输入研究主题或查询内容",
                        label="研究查询",
                        info="输入你想要深度研究的主题 - 支持多用户并发"
                    )
                
                with gr.Row():
                    # 选择处理风格
                    research_prompt_dropdown = gr.Dropdown(
                        choices=prompt_names,
                        value=prompt_names[0] if prompt_names else None,
                        label="选择处理风格",
                        info="选择用于处理研究结果的文本风格"
                    )
                
                # 处理按钮
                research_process_button = gr.Button("开始深度研究 + 处理", variant="primary")
                
                with gr.Row():
                    # 研究结果显示
                    research_output = gr.Textbox(
                        lines=12,
                        label="研究结果 (支持并发)",
                        interactive=False
                    )
                    
                    # 处理结果显示
                    research_processed_output = gr.Textbox(
                        lines=12,
                        label="处理结果",
                        interactive=False
                    )
                
                # 绑定事件
                research_process_button.click(
                    fn=research_and_process_single_async,
                    inputs=[research_query_input, research_prompt_dropdown, password_input],
                    outputs=[research_output, research_processed_output]
                )
            
            with gr.TabItem("深度研究 + 多风格分块 "):
                with gr.Row():
                    # 研究查询输入
                    research_multi_query_input = gr.Textbox(
                        lines=3,
                        placeholder="请输入研究主题或查询内容",
                        label="研究查询",
                        info="输入你想要深度研究的主题 - 支持多用户并发"
                    )
                
                with gr.Row():
                    # 文章块数量选择
                    research_num_articles_slider = gr.Slider(
                        minimum=2, 
                        maximum=10, 
                        value=3, 
                        step=1, 
                        label="文章分块数量", 
                        info="选择将研究结果分为几个块处理 (2-10)"
                    )
                    
                    # 随机选择prompt选项
                    research_random_prompt_checkbox = gr.Checkbox(
                        label="随机分配文本风格", 
                        value=False, 
                        info="随机分配选定的文本风格到各个文章块"
                    )
                
                with gr.Row():
                    # 多选Prompt
                    research_multi_prompt_dropdown = gr.Dropdown(
                        choices=prompt_names,
                        value=[prompt_names[0]] if prompt_names else None,
                        label="选择一个或多个文本风格",
                        multiselect=True,
                        info="可以选择多种风格，系统会自动分配到各个文章块"
                    )
                
                # 处理按钮
                research_multi_process_button = gr.Button("开始深度研究 + 多风格处理", variant="primary")
                
                # 研究结果显示区域
                with gr.Row():
                    research_multi_output = gr.Textbox(
                        lines=10,
                        label="研究结果 (支持并发)",
                        interactive=False
                    )
                
                # 创建文章块输出区域
                research_article_chunks_output = []
                
                # 每行显示2个文本框，最多10个文本框
                for row in range(5):  # 5行，每行2个
                    with gr.Row():
                        for col in range(2):  # 每行2列
                            chunk_index = row * 2 + col
                            chunk_output = gr.Textbox(
                                lines=8, 
                                label=f"处理结果 {chunk_index + 1}",
                                interactive=False
                            )
                            research_article_chunks_output.append(chunk_output)
                
                # 将研究结果和处理结果合并为一个输出列表
                research_multi_outputs = [research_multi_output] + research_article_chunks_output
                
                # 绑定事件
                research_multi_process_button.click(
                    fn=research_and_process_multi_async,
                    inputs=[
                        research_multi_query_input,
                        research_num_articles_slider,
                        research_multi_prompt_dropdown,
                        research_random_prompt_checkbox,
                        password_input
                    ],
                    outputs=research_multi_outputs
                )
            
            with gr.TabItem("批量处理 (ZIP文件)"):
                with gr.Row():
                    # ZIP文件上传
                    zip_file_input = gr.File(
                        label="上传ZIP文件 (包含 .md 或 .txt 文件)",
                        file_types=[".zip"]
                    )
                
                with gr.Row():
                    # 选择单一Prompt用于ZIP处理
                    zip_prompt_dropdown = gr.Dropdown(
                        choices=prompt_names,
                        value=prompt_names[0] if prompt_names else None,
                        label="选择文本风格"
                    )
                
                # 处理ZIP按钮
                process_zip_button = gr.Button("处理ZIP文件")
                
                # 处理结果和下载链接
                zip_result = gr.File(label="处理结果 (ZIP文件下载)")
                
                # 绑定事件
                process_zip_button.click(
                    fn=process_zip_file,
                    inputs=[zip_file_input, zip_prompt_dropdown, password_input],
                    outputs=zip_result
                )
        
    # 启动Gradio应用 - 关键配置
    demo.queue(
        max_size=20,          # 最大队列大小
        default_concurrency_limit=8   # 同时处理的任务数
    )
    demo.launch(
        server_name="0.0.0.0", 
        server_port=int(port),
        max_threads=16        # 增加线程数
    )

if __name__ == "__main__":
    create_gradio_interface()
