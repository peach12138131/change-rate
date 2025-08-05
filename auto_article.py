import requests
import json
from datetime import datetime
import os
import random
from typing import List, Dict, Any, Optional,Generator
from collections import defaultdict
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
        time.sleep(30)
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
        
        
        # 如果包含AI答案摘要，打印出来
        if include_answer and answer:
            print(f"📝 AI摘要: {answer[:]}...")
        
        return answer, results
        
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
        news_pool=[]
        news_list=news_list 
        date_str = datetime.now().strftime("%Y%m%d")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 创建带日期的输出目录
        output_dir = f"./output/{date_str}"
        os.makedirs(output_dir, exist_ok=True)
       
        # 对关键词进行搜索，生成新闻池
        for i, news in enumerate(news_list): 
            category = news.get("category", "")
            keyword = news.get("keyword_en", "")
            description= news.get("description", "")
            print(f"\n[表情] 正在研究第 {i} 新闻:")
            print(f"标题: {category}")
            print(f"内容: {description}")

            #获取实时新闻主题
            topic,news_results=search_news(query=f"Search for diversity news releated to private jet (or business charter) about:{category},keyword:{keyword}Please find relevant news articles, expert opinions, and background information.")

           
            print("筛选新闻中")
            extract_query =f"""Current time {date_str}. 
                                Please extract the news that most relevant to private charter topic about from the following news results.
                                Important Note:
                                1.the news content should be related 
                                2.Try choose diverse sources
                                3.Filter out the news too old 
                                4.Filter out news from which it's difficult to obtain useful information,such as those that are too short, too old, or irrelevant.
                                """
            extract_news = query_openai_model(extract_query,news_results,openai_key,json_schema=news_schema)

            print(extract_news)
            extract_news=json.loads(extract_news)
            print(extract_news["news_list"])
            

            news_pool.append(extract_news["news_list"])

           

            

         #去对news_pool进行去重
        all_news = []
        for news_list in news_pool:
            all_news.extend(news_list)

        # 用字典去重，URL作为key
        unique_news_dict = {}
        for news in all_news:
            url = news.get('url')
            if url:
                unique_news_dict[url] = news  # 如果URL重复，会被覆盖

        news_pool = list(unique_news_dict.values())

        #保存news_pool为json
        news_file_name=os.path.join(output_dir, "jetbay_news_pool.json")
        with open(news_file_name, "w", encoding="utf-8") as f:
            json.dump(news_pool, f, ensure_ascii=False, indent=4)


       


        
            
           
        if news_pool:
            # 按类别分组新闻
            news_by_category = defaultdict(list)
            for news in news_pool:
                category = news.get('category', 'Unknown')
                news_by_category[category].append(news)
            
            print(f"发现 {len(news_by_category)} 个类别的新闻")
            for category, news_list in news_by_category.items():
                print(f"类别 '{category}': {len(news_list)} 条新闻")
                start_idx = 0
                batch_count = 0

                while start_idx < len(news_list):
                    batch_size = min(random.randint(5, 12), len(news_list) - start_idx)
                    end_idx = start_idx + batch_size
                    print(f"\n处理第 {batch_count + 1} 批次：索引 {start_idx}-{end_idx-1} ({batch_size} 条新闻)")
                    batch_news = news_list[start_idx:end_idx]
                    final_report = ""
                    for new in enumerate(batch_news):
                        final_report += f"{new}\n\n"
                    
                    # 构建原始log回溯
                    article_content = f"## the research material and collected news \n{final_report}"
                    
                    
                    # 调用API改写文章
                    print(f" 正在生成第 {batch_count + 1} 条新闻的文章...")
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
                        
                        
                        
                        # 保存改写后的文章
                        filename = f"{output_dir}/article_{batch_count + 1}_{timestamp}.txt"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(rewritten_article)

                        #保存seo文章
                        jetbay_seo_dir=os.path.join(output_dir,"JETBAY")
                        os.makedirs(jetbay_seo_dir, exist_ok=True)

                        seo_filename = os.path.join(output_dir, 'JETBAY', f'seo_article_{batch_count + 1}_{timestamp}.txt')
                        with open(seo_filename, 'w', encoding='utf-8') as f:
                            f.write(final_seo_article)



                        # 同时保存原始研究内容
                        raw_filename = f"{output_dir}/raw_research_{batch_count + 1}_{timestamp}.txt"
                        with open(raw_filename, 'w', encoding='utf-8') as f:
                            f.write(log_content)
                    else:
                        print(f" 第 {batch_count + 1} 条新闻文章生成失败")
                        
                    print(f" 第 {batch_count + 1} 条新闻处理完成")

                    start_idx = end_idx
                    batch_count += 1
            

        print("\n 所有新闻处理完成！")
        return 0  
            
    except Exception as e:
        print(f" 处理失败: {e}")
        return 1


if __name__ == "__main__":
    import schedule
    import time 
    from datetime import datetime, timedelta

    max_retries = 3
    retry_interval_hours = 1
    retry_count = 0
    next_retry_time = None
    
    def execute_with_retry():
        """执行任务并处理重试逻辑"""
        global retry_count, next_retry_time
        
        print(f"执行任务... 尝试次数: {retry_count + 1}")
        res = auto_write_article(news_list=keyword_list)
        
        if res == 0:  # 成功
            print("任务执行成功！")
            retry_count = 0
            next_retry_time = None
        else:  # 失败
            retry_count += 1
            if retry_count < max_retries:
                next_retry_time = datetime.now() + timedelta(hours=retry_interval_hours)
                print(f"任务失败，将在 {next_retry_time.strftime('%H:%M')} 进行第 {retry_count + 1} 次重试...")
            else:
                print(f"任务失败，已达到最大重试次数 {max_retries}")
                retry_count = 0
                next_retry_time = None
    # 立即执行一次
    print("立即执行一次任务...")
    execute_with_retry()


    schedule.every().day.at("10:00").do(execute_with_retry)
    # 保持运行
    while True:
        if next_retry_time and datetime.now() >= next_retry_time:
                execute_with_retry()
        schedule.run_pending()
        time.sleep(60)
    
 
    
