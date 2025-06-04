import requests
import json
from datetime import datetime
import os
def send_research_request(query="defualt"):
    """向本地深度研究服务发送请求"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_dir = "./temp_search_result"
    os.makedirs(output_dir, exist_ok=True)  # exist_ok=True 表示目录存在时不报错
    filename = f"{output_dir}/weather_report_{timestamp}.txt"
    url = "http://47.237.119.79:8861/api/sse"
    ## http://47.237.119.79:8861/
    
    config = {
        "query": query,
        "provider": "anthropic",
        "thinkingModel": "claude-3-7-sonnet-20250219",
        "taskModel": "claude-3-7-sonnet-20250219",
        "searchProvider": "model",
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
        print("❌ 连接失败: 请确保本地服务已启动 (pnpm dev)")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP错误: {e}")
        if 'response' in locals():
            print("响应内容:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求错误: {e}")
    except Exception as e:
        print(f"❌ 其他错误: {e}")

if __name__ == "__main__":
    for x in send_research_request("上海天气,摘要"):
        continue
