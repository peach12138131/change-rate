import requests
import json
from datetime import datetime
import os
import random
from typing import List, Dict, Any, Optional,Generator
import time
from auto_article_config import keyword_list,claude_key,tavily_key,openai_key,generate_svg_prompt,rewrite_prompt,extract_svg_from_text, extract_final_report,news_schema,seo_metadata,seo_keywords,seo_link,seo_rewrite_prompt

def query_gpt_model(prompt: str, article: str, api_key: str, base_url: str = "https://api.anthropic.com/v1", 
                   model: str = "claude-sonnet-4-20250514", max_tokens: int = 10240, 
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
            {"role": "user", "content": f"{prompt}\n \n{article}"}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response_json = response.json()
        time.sleep(10)
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



def query_openai_model(prompt: str, article: str, api_key: str, base_url: str = "https://api.openai.com/v1", 
                       model: str = "gpt-4.1-2025-04-14", max_tokens: int = 10240, 
                       temperature: float = 0.8,json_schema: dict = None) -> Optional[str]:
    
    url = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": f"{prompt}\n \n{article}"}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    if json_schema:
        payload["response_format"] = {
            "type": "json_schema",
            "json_schema": json_schema
        }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response_json = response.json()
        time.sleep(10)
        if "choices" in response_json and len(response_json["choices"]) > 0:
            text_content = response_json["choices"][0]["message"]["content"]
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
                    # print(f"\n[事件]: {current_event}")

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
                                # print(f"\n[文本内容]: {text_content}")

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






def search_news(tavily_api_key: str=tavily_key, query: str="", max_results: int = 80, days: int = 3, 
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
        
        print(f"✅ 找到 {len(results)} 条新闻结果\n")
        print(results)
        
        # 如果包含AI答案摘要，打印出来
        if include_answer and answer:
            print(f"📝 AI摘要: {answer[:]}...")
        
        return answer,results
        
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







def auto_write_article(news_list):
    """自动写文章的主函数"""
    
    
    try:
        news_list=news_list 
       
        # 对每条进行深度搜素,对每条进行深度搜索并生成单独文章
        for i, news in enumerate(news_list, 1): 
            category = news.get("category", "")
            keyword = news.get("keyword_en", "")
            description= news.get("description", "")
            print(f"\n[表情] 正在研究第 {i} 条新闻:")
            print(f"标题: {category}")
            print(f"内容: {description}")

            #获取实时新闻主题
            topic,news_results=search_news(query=f"Search for diversity news releated to private jet (or business charter) about:{category},keyword:{keyword}Please find relevant news articles, expert opinions, and background information.")

            print(f"主题: {news_results}")

            extract_query =f"Please extract the news that most relevant to private charter topic about:{category},{description} from the following news results.Note:1.the content should be related 2.Try choose diverse sources"

            extract_news = query_openai_model(extract_query,news_results,openai_key,json_schema=news_schema)
            print(f"提取的新闻: {extract_news}")

            # # 构建研究查询
            # query = f"Please research the related information and related news releated to private jet (or business charter) about this news topic: {news_results}"
            
            # # 进行深度研究
            # print("[表情] 开始深度研究...")
            # research_content = ""
            # for content_chunk in send_research_request(query=query):
            #     research_content += content_chunk
            
            # 


            if extract_news:
                # 提取最终报告
                # final_report = extract_final_report(research_content)
                final_report = extract_news
                
                # 构建原始log回溯
                article_content = f"# {category}\n\n## description\n{description}\n\n## the research material and collected news \n{final_report}"
                
                
                # 调用API改写文章
                print(f" 正在生成第 {i} 条新闻的文章...")
                if random.choice([True, False]):
                    rewritten_article = query_gpt_model(rewrite_prompt, article_content, claude_key, temperature=1.0)
                    model_used = "claude"
                else:
                    rewritten_article = query_openai_model(rewrite_prompt, article_content, openai_key, temperature=1.0)
                    model_used = "OpenAI"

                print(f"[表情] 使用了 {model_used} 模型")
                
                
                #seo改写流程1，提取关键字
                keywords_prompt=seo_keywords.format(rewritten_article)
                keywords=query_gpt_model(keywords_prompt, "", claude_key, temperature=1.0)


                #2生成metadata
                metadata_prompt=seo_metadata.format(rewritten_article,keywords)
                metadata=query_gpt_model(metadata_prompt, "", claude_key, temperature=1.0)

                #3重写
                seo_rewrite=seo_rewrite_prompt.format(final_report,metadata)
                seo_article=query_gpt_model(seo_rewrite, "", claude_key, temperature=1.0)
                
                #植入链接
                seo_link_prompt=seo_link.format(seo_article)
                final_seo_article=query_gpt_model(seo_link_prompt, "", claude_key, temperature=1.0)
                final_seo_article=f"keywords\n{keywords}\n\n{final_seo_article}"

                log_content=f"collected news \n{final_report} \n \nkeywords\n{keywords}\n\n"





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

                    #保存seo文章
                    seo_filename = f"{output_dir}/seo_article_{i}_{safe_title}_{timestamp}.txt"
                    with open(seo_filename, 'w', encoding='utf-8') as f:
                        f.write(final_seo_article)


                    # 保存SVG文件 - 关键代码就这几行
                    svg_text = query_gpt_model(generate_svg_prompt, rewritten_article, claude_key)
                    svg_codes=extract_svg_from_text(svg_text)
                    for idx, svg_code in enumerate(svg_codes):
                        svg_filename = f"{output_dir}/chart_{i}_{safe_title}_{timestamp}_{idx+1}.svg"
                        with open(svg_filename, 'w', encoding='utf-8') as f:
                            f.write(svg_code)
                        print(f"[成功] SVG已保存: {svg_filename}")
                    

                    # 同时保存原始研究内容
                    raw_filename = f"{output_dir}/raw_research_{i}_{safe_title}_{timestamp}.txt"
                    with open(raw_filename, 'w', encoding='utf-8') as f:
                        f.write(log_content)
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
    auto_write_article(news_list=keyword_list)

    # 设置每天10点执行
    schedule.every().day.at("10:00").do(auto_write_article, news_list=keyword_list)

    # 保持运行
    while True:
        schedule.run_pending()
        time.sleep(60)
    
 
    
