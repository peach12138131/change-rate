import requests
import json
from datetime import datetime
import os
from typing import List, Dict, Any, Optional,Generator
import time
from auto_article_config import keyword_list,claude_key,tavily_key,generate_svg_prompt,rewrite_prompt,extract_svg_from_text

def query_gpt_model(prompt: str, article: str, api_key: str, base_url: str = "https://api.anthropic.com/v1", 
                   model: str = "claude-3-7-sonnet-20250219", max_tokens: int = 10240, 
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


def send_research_request(query="defualt"):
    """向本地深度研究服务发送请求"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_dir = "./temp_search_result"
    os.makedirs(output_dir, exist_ok=True)  # exist_ok=True 表示目录存在时不报错
    filename = f"{output_dir}/deesearch_report_{timestamp}.txt"
    url = "http://47.237.119.79:8861/api/sse"
    ## http://47.237.119.79:8861/

    # config = {
    #     "query": query,
    #     "provider": "anthropic",
    #     "thinkingModel": "claude-sonnet-4-20250514",
    #     "taskModel": "claude-sonnet-4-20250514",
    #     "searchProvider":"tavily",
    #     "language": "en-US",
    #     "maxResult": 5,
    #     "enableCitationImage": True,
    #     "enableReferences": True
    # }
    
    config = {
        "query": query,
        "provider": "openai",
        "thinkingModel": "gpt-4.1-2025-04-14",
        "taskModel": "gpt-4.1-2025-04-14",
        "searchProvider": "tavily",
        "language": "en-US",
        "maxResult": 5,
        "enableCitationImage": False,
        "enableReferences": True
    }
    
    try:
        # 发送请求，启用流式处理
        response = requests.post(url, json=config, stream=True,timeout=(60,6000)) #容忍度高,超时时间要很长保证搜索,
        response.raise_for_status()
        
        print("连接成功，开始接收数据...")
        print("状态码:", response.status_code)
        print("=" * 50)
        final_report = ""
        current_event = None
        last_content = ""
        # 处理流式响应
        for line in response.iter_lines(decode_unicode=True):
            if line.strip():
               
                # print(line)
                if line.startswith('event: '):
                    # 解析事件类型
                    current_event = line[7:].strip()
                    print(f"\n[事件]: {current_event}")

                elif line.startswith('data: '):
                    # 提取data部分
                    data = line[6:].strip()
                    
                    # 清理末尾的多余字符 )}
                    if data.endswith(')}'):
                        data = data[:-2]

                    if data:
                        try:
                            # 解析JSON数据
                            json_data = json.loads(data)
                            # print(f"\n[数据]: {json_data}")
                            if current_event == "message" and json_data.get("type") == "text":
                                text_content = json_data.get("text", "")
                                if text_content== last_content:
                                    continue
                                else:
                                    final_report += text_content
                                last_content = text_content
                                print(f"\n[文本内容]: {text_content}")

                                yield text_content


                                


                        except json.JSONDecodeError as e:
                            print(f"\n[JSON解析错误]: {e}")
                            print(f"[原始数据]: {repr(data)}")



        print("\n" + "=" * 50)
        print("数据接收完成")
        print(f"累积文本长度: {len(final_report)} 字符")

        if final_report:
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(final_report)
            print("报告已保存到 weather_report.txt")

        
    except requests.exceptions.ConnectionError:
        print("[表情] 连接失败: 请确保本地服务已启动 (pnpm dev)")
    except requests.exceptions.HTTPError as e:
        print(f"[表情] HTTP错误: {e}")
        if 'response' in locals():
            print("响应内容:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"[表情] 请求错误: {e}")
    except Exception as e:
        print(f"[表情] 其他错误: {e}")


def extract_final_report(content):
    """提取 <final-report> 和 </final-report> 之间的内容"""
    start_tag = "<final-report>"
    end_tag = "</final-report>"
    
    start_index = content.find(start_tag)
    if start_index == -1:
        print("没有找到 <final-report> 标签")
        return content  # 如果没有找到标签，返回原内容
    
    end_index = content.find(end_tag, start_index)
    if end_index == -1:
        print("没有找到 </final-report> 标签")
        return content  # 如果没有找到结束标签，返回原内容
    
    # 提取标签之间的内容
    start_index += len(start_tag)
    final_report = content[start_index:end_index].strip()
    
    return final_report



def search_news(tavily_api_key: str=tavily_key, query: str="", max_results: int = 20, days: int = 3, 
                search_depth: str = "basic", include_answer: bool = True) -> List[Dict[str, Any]]:
    """
    使用Tavily API搜索新闻
    
    Args:
        tavily_api_key: Tavily API密钥
        query: 搜索查询词
        max_results: 最大返回结果数 (默认10)
        days: 搜索时间范围(天) (默认7天)
        search_depth: 搜索深度 "basic" 或 "advanced" (默认basic)
        include_answer: 是否包含AI生成的答案摘要 (默认True)
    
    Returns:
        包含搜索结果的字典列表
    """
    url = "https://api.tavily.com/search"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {tavily_api_key}'
    }
    
    data = {
        "query": query,
        "topic": "news",  # 专门搜索新闻
        "search_depth": search_depth,  # 搜索深度
        "chunks_per_source": 3,  # 每个来源的内容块数
        "max_results": max_results,  # 最大结果数
        "time_range": None,  # 时间范围(null表示使用days参数)
        "days": days,  # 搜索最近N天的新闻
        "include_answer": include_answer,  # 包含AI生成的答案摘要
        "include_raw_content": False,  # 不包含原始HTML内容
        "include_images": False,  # 包含图片
        "include_image_descriptions": False,  # 不包含图片描述
        "include_domains": [],  # 包含的域名列表(空表示不限制)
        "exclude_domains": [],  # 排除的域名列表
        "country": None  # 国家限制(null表示全球)
    }
    
    try:
        print(f"🔍 正在搜索新闻: {query}")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()  # 检查HTTP错误
        
        result = response.json()
        
        # 检查API响应状态
        if 'results' not in result:
            print(f"⚠️ API响应异常: {result}")
            return []
        
        results = result.get("results", [])
        answer = result.get("answer", "")  # AI生成的答案摘要
        
        print(f"✅ 找到 {len(results)} 条新闻结果")
        
        # 如果包含AI答案摘要，打印出来
        if include_answer and answer:
            print(f"📝 AI摘要: {answer[:]}...")
        
        return answer
        
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请检查网络连接")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP错误: {e}")
        if hasattr(e.response, 'text'):
            print(f"错误详情: {e.response.text}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求错误: {e}")
        return []
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return []







def auto_write_article(news_list, api_key="", base_url="https://api.anthropic.com/v1"):
    """自动写文章的主函数"""
    
    
    try:
        news_list=news_list 
        all_research_content = ""
        # 对每条进行深度搜素
        # 对每条进行深度搜索并生成单独文章
        for i, news in enumerate(news_list, 1): 
            category = news.get("category", "")
            keyword = news.get("keyword_en", "")
            description= news.get("description", "")
            print(f"\n[表情] 正在研究第 {i} 条新闻:")
            print(f"标题: {category}")
            print(f"内容: {description}")

            #获取实时新闻主题
            topic=search_news(query=f"Search for recent news and analysis about::{category},keyword:{keyword},description:{description}Please find relevant news articles, expert opinions, and background information.")

            # 构建研究查询
            query = f"Please research the related information and related news about this news topic: {topic}"
            
            # 进行深度研究
            print("[表情] 开始深度研究...")
            research_content = ""
            for content_chunk in send_research_request(query=query):
                research_content += content_chunk
            
            if research_content:
                # 提取最终报告
                final_report = extract_final_report(research_content)
                
                # 构建单篇文章内容
                article_content = f"# {category}\n\n## 原始新闻内容\n{description}\n\n## 深度研究报告\n{final_report}"
                time.sleep(10)
                
                # 调用API改写文章
                print(f"[表情] 正在生成第 {i} 条新闻的文章...")
                rewritten_article = query_gpt_model(rewrite_prompt, article_content, api_key, base_url)
                time.sleep(10)
                
                if rewritten_article:
                    date_str = datetime.now().strftime("%Y%m%d")
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # 清理文件名，移除特殊字符
                    safe_title = "".join(c for c in category if c.isalnum() or c in (' ', '-', '_')).rstrip()[:50]
                    
                    # 创建带日期的输出目录
                    output_dir = f"./output/{date_str}"
                    os.makedirs(output_dir, exist_ok=True)
                    
                    # 保存改写后的文章
                    filename = f"{output_dir}/article_{i}_{safe_title}_{timestamp}.txt"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(rewritten_article)

                    svg_text = query_gpt_model(generate_svg_prompt, rewritten_article, api_key, base_url)
                    time.sleep(10)
                    svg_codes=extract_svg_from_text(svg_text)
                    # 保存SVG文件 - 关键代码就这几行
                    for idx, svg_code in enumerate(svg_codes):
                        svg_filename = f"{output_dir}/chart_{i}_{safe_title}_{timestamp}_{idx+1}.svg"
                        with open(svg_filename, 'w', encoding='utf-8') as f:
                            f.write(svg_code)
                        print(f"[成功] SVG已保存: {svg_filename}")
                    
                    # 同时保存原始研究内容
                    raw_filename = f"{output_dir}/raw_research_{i}_{safe_title}_{timestamp}.txt"
                    with open(raw_filename, 'w', encoding='utf-8') as f:
                        f.write(article_content)
                else:
                    print(f"[表情] 第 {i} 条新闻文章生成失败")
                    
                print(f"[表情] 第 {i} 条新闻处理完成")
            else:
                print(f"[表情] 第 {i} 条新闻研究失败")

        print("\n[表情] 所有新闻处理完成！")
            
    except Exception as e:
        print(f"[表情] 处理失败: {e}")
        return None




if __name__ == "__main__":
    import schedule
    import time
    # 立即执行一次
    auto_write_article(news_list=keyword_list, api_key=claude_key)
    
    # 设置每天10点执行
    schedule.every().day.at("10:00").do(auto_write_article, news_list=keyword_list, api_key=claude_key)
    
    # 保持运行
    while True:
        schedule.run_pending()
        time.sleep(60)
    
 
    
