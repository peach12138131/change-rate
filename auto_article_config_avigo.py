import os
import re 
import html



generate_svg_prompt=""""
    Please analyze the main content of this article, focusing on its narrative logic, data usage, and event trend changes. Create SVG illustrations that match this article, with requirements for a concise illustration style, refined text, no unnecessary text symbols, and colors that align with the simple and elegant style of the private jet industry. Output 1 SVG image based on the content. This is the article:
   
    """
rewrite_prompt="""
# Role: Human Private Charter Website Article Editor 
Output Language: English
## Main Task
Completely rewrite and reorganize AI-collected information into professional website articles with the characteristics of professional human editors, while maintaining original information and viewpoints.

## Workflow
1. Carefully read and understand the core information and viewpoints in AI-collected input news, organizing scattered knowledge points into complete and coherent articles.
2. Retain core information and strictly maintain the format of original images and tables, and must cite source URLs in IEEE style. 
3. Rewrite and expand more content from scratch as an authentic human author:
   - Connect scattered news and viewpoints with reasonable logic, and edit them into a complete and coherent article
   - Add some subtle logical leaps but professional viewpoints
   - Appropriately describe articles from a Marketplace perspective
   - Avoid excessive subheadings and numbering systems; articles should be complete, coherent, and in-depth just with necessary subheadings
   - Avoid using words like "Evolution".
4. Ensure rewritten content maintains the original text's core information and viewpoints, but with completely different expression style.
5. Use third-person perspective or third-person narrative in writing to demonstrate professionalism
6. Review the rewritten content to ensure it reads like the natural expression of a real professional expert.

## Important Notes
- Don't try to "rewrite" the original text, but completely recreate it.
- Add some minor imperfections, such as colloquial expressions or slight grammatical irregularities.
- Avoid overly perfect or structured expressions.
- Use third-person perspective or third-person narrative in writing to demonstrate professionalism

## Output Format
Directly output the rewritten content without any explanations or annotations.

## Initialization
Please recreate this content as an authentic human website article editor.
"""

    
keyword_list = [
    {
        "category": "Charter Platform & Booking Technology",
        "keyword_en": "private jet booking, charter management, aviation SaaS, digital marketplace, trip planning automation, aircraft sourcing, broker software",
        "keyword_zh": "私人飞机预订平台, 包机管理软件, 航空SaaS平台",
        "priority": "High",
        "description": "Core platform technology for charter booking and management"
    },
    {
        "category": "Aviation Data Intelligence & Analytics",
        "keyword_en": "aviation data platform, demand forecast, utilization analytics, pricing trends, business intelligence, market insights, flight data API",
        "keyword_zh": "航空数据平台, 私人飞机需求预测, 航空商业智能",
        "priority": "High",
        "description": "Data-driven insights and market intelligence for aviation industry"
    },
    {
        "category": "Fleet Management & Operations",
        "keyword_en": "fleet management SaaS, availability API, empty leg optimization, operator tools, positioning tracker, scheduling platform",
        "keyword_zh": "机队管理航空SaaS, 飞机可用性API, 空腿优化",
        "priority": "Medium",
        "description": "Operational efficiency tools for aviation fleet managers"
    },
    {
        "category": "Geographic Market Focus - Asia Pacific",
        "keyword_en": "Asia charter software, Singapore private jet, APAC platform, Malaysia aviation, India business aviation, Hong Kong booking, Thailand marketplace",
        "keyword_zh": "亚洲包机软件, 新加坡私人飞机预订, 亚太包机平台",
        "priority": "High",
        "description": "Regional market penetration in Asia-Pacific aviation sector"
    },
    {
        "category": "European Aviation Technology",
        "keyword_en": "Europe private jet, EU aviation data, Malta charter, UK business aviation, France aircraft, Germany SaaS, Switzerland platform",
        "keyword_zh": "欧洲私人飞机预订平台, 欧盟航空数据, 马耳他包机软件",
        "priority": "High",
        "description": "European market focus for aviation technology solutions"
    },
    {
        "category": "Competitive Intelligence & Positioning",
        "keyword_en": "Avi-Go vs Avinode, modern alternative, platform 2025, competitive analysis, technology disruption, next-gen solutions",
        "keyword_zh": "Avi-Go对比Avinode, 现代包机经纪替代方案, 数字航空平台",
        "priority": "Medium",
        "description": "Competitive positioning and market differentiation"
    },
    {
        "category": "API Integration & Partnerships",
        "keyword_en": "aviation API, FBO marketplace, fuel partner API, ecosystem sharing, platform integration, software connectivity, API suite",
        "keyword_zh": "航空API集成, FBO数字市场, 航空生态数据共享",
        "priority": "Medium",
        "description": "Technical integration and partnership opportunities"
    },
    {
        "category": "Middle East & Gulf Markets",
        "keyword_en": "Gulf charter software, UAE platform, MENA aviation, Qatar booking, Saudi business aviation, Bahrain management, Dubai SaaS",
        "keyword_zh": "海湾包机软件, 阿联酋私人飞机平台, 中东北非航空软件",
        "priority": "Medium",
        "description": "Strategic focus on Middle Eastern aviation markets"
    },
    {
        "category": "Long-tail & Voice Search Optimization",
        "keyword_en": "best sourcing tool 2025, save time quotes, real-time availability, operator development, digital transformation aviation",
        "keyword_zh": "2025年最佳私人飞机采购工具, 包机经纪人如何节省报价时间",
        "priority": "Low",
        "description": "Specific query optimization for voice and long-tail searches"
    },
    {
        "category": "Workflow Automation & ROI",
        "keyword_en": "charter automation, digital quoting ROI, lifecycle automation, productivity tools, process optimization, efficiency software",
        "keyword_zh": "包机工作流程自动化, 手动与数字报价投资回报率, 行程生命周期自动化",
        "priority": "Medium",
        "description": "Operational efficiency and return on investment focus"
    },
    {
        "category": "Core Technology Solutions",
        "keyword_en": "charter automation, aviation CRM, booking API, matching algorithm, pricing engine, broker dashboard, operator portal",
        "keyword_zh": "包机自动化, 航空CRM, 飞行预订API",
        "priority": "High",
        "description": "Essential technology components for aviation platforms"
    },
    {
        "category": "Business Models & Services",
        "keyword_en": "charter brokerage, leasing platform, sharing economy, aviation marketplace, flight aggregator, charter consolidation, aviation fintech",
        "keyword_zh": "包机经纪, 飞机租赁平台, 喷气机共享经济",
        "priority": "High",
        "description": "Different business approaches in charter aviation"
    },
    {
        "category": "User Experience & Interface",
        "keyword_en": "intuitive booking, mobile app, one-click search, streamlined quotes, user-friendly software, seamless planning",
        "keyword_zh": "直观包机预订, 移动航空应用, 一键飞机搜索",
        "priority": "Medium",
        "description": "User-centric design and experience optimization"
    },
    {
        "category": "Industry Pain Points",
        "keyword_en": "booking inefficiency, quote delays, availability gaps, pricing transparency, communication bottlenecks, operational blind spots",
        "keyword_zh": "包机预订效率低下, 手动报价延迟, 飞机可用性缺口",
        "priority": "Medium",
        "description": "Common challenges in traditional charter operations"
    },
    {
        "category": "Emerging Technologies",
        "keyword_en": "AI matching, blockchain records, IoT tracking, predictive maintenance, machine learning pricing, smart contracts",
        "keyword_zh": "AI飞机匹配, 区块链航空记录, 物联网飞行追踪",
        "priority": "Medium",
        "description": "Next-generation technologies transforming aviation"
    },
    {
        "category": "Market Segments",
        "keyword_en": "corporate aviation, luxury charter, medical flights, cargo solutions, government services, sports charters",
        "keyword_zh": "企业航空, 豪华旅行包机, 紧急医疗航班",
        "priority": "Medium",
        "description": "Specialized aviation market niches"
    },
    {
        "category": "Performance Metrics",
        "keyword_en": "conversion rates, booking velocity, utilization metrics, productivity KPIs, customer satisfaction, revenue optimization",
        "keyword_zh": "包机转化率, 预订速度, 飞机利用率指标",
        "priority": "Low",
        "description": "Key performance indicators for aviation businesses"
    },
    {
        "category": "Compliance & Safety",
        "keyword_en": "regulatory compliance, safety management, charter certification, flight protocols, insurance integration, regulatory reporting",
        "keyword_zh": "航空监管合规, 安全管理系统, 包机认证",
        "priority": "Medium",
        "description": "Regulatory and safety considerations in charter operations"
    },
    {
        "category": "Customer Journey",
        "keyword_en": "inquiry to booking, client onboarding, customer retention, VIP delivery, lifecycle management, loyalty programs",
        "keyword_zh": "包机咨询到预订, 客户入职航空, 重复客户保留",
        "priority": "Low",
        "description": "Complete customer experience in charter services"
    },
    {
        "category": "Innovation & Disruption",
        "keyword_en": "digital transformation, industry evolution, next-gen platforms, disruptive technology, future flying, startup ecosystem",
        "keyword_zh": "航空数字化转型, 包机行业演变, 下一代航空平台",
        "priority": "Medium",
        "description": "Industry transformation and future trends"
    },
    {
        "category": "Integration Ecosystems",
        "keyword_en": "software stack, platform ecosystem, third-party integrations, API marketplace, partner networks, connected services",
        "keyword_zh": "航空软件堆栈, 包机平台生态系统, 第三方集成",
        "priority": "Medium",
        "description": "Comprehensive integration and partnership strategies"
    },
    {
        "category": "Operational Excellence",
        "keyword_en": "operational efficiency, dispatch optimization, crew scheduling, maintenance coordination, fuel management, ground services",
        "keyword_zh": "包机运营效率, 飞行调度优化, 机组排班自动化",
        "priority": "Medium",
        "description": "Operational optimization across all charter touchpoints"
    }
]
    



news_schema = {
   "name": "news_extraction",
   "description": "Extract news information",
   "schema": {
       "type": "object",
       "properties": {
           "news_list": {
               "type": "array",
               "items": {
                   "type": "object",
                   "properties": {
                       "url": {
                           "type": "string",
                           "description": "Original news link"
                       },
                       "content": {
                           "type": "string",
                           "description": "News full content"
                       },
                       "category":{
                           "type": "string",
                           "enum": ["Transactional", "Informational", "Localised", "Navigational"],
                           "description": " The article intention can be classified - Transactional (e.g. book private jet Singapore), - Informational (e.g. how does private jet charter work), - Localised (e.g. private jet Bangkok to Singapore), - Navigational (e.g. brand or platform name searches)"
                       }
                   },
                   "required": ["url", "content","category"],
                   "additionalProperties": False  # 必须添加这个
               },
               "minItems": 30,
               "maxItems": 30
           }
       },
       "required": ["news_list"],
       "additionalProperties": False
       
   },
   "strict": True
}




seo_keywords="""

You are an excellent SEO optimizer for search engines, skilled in ranking optimization. Now you need to conduct important keyword research for SEO optimization. Please extract up to 10 keywords from the news materials provided by your client company, of which 3 should be long-tail keywords and 2 keywords summarize from hotest news.
Background: Keyword research refers to the process of finding keywords to compete for ranking in search engines. The purpose is to understand the potential intent of customer searches and how they search. It also involves analyzing and comparing keywords to find the best keyword opportunities.
Your service company: Avi-Go,The Largest Data & Charter Marketplace Platform for Business Aviation.From advanced AI models to multi-agent systems, Transform your aviation business with Avi-Go's AI-powered features today.The all-in-one air charter platform connects you to a global network of brokers and operators, streamlining the charter flight booking workflow.
As a professional SEO expert, you should have the following professional qualities and steps:
1: You need to have sharp insight and apply internet marketing or advertising operations mindset to identify the most compelling breaking news, industry dynamics, and trending topics that can attract user engagement. Consider how to naturally connect these elements with your brand, then distill them into relevant keywords.
2. You should not limit yourself to one country, pay attention to keyword trends, and consider keyword difficulty, content length, relevance, and search intent.
3. The article intention can be classified - Transactional (e.g. "book private jet Singapore"), - Informational (e.g. "how does private jet charter work"), - Localised (e.g. "private jet Bangkok to Singapore"), - Navigational (e.g. brand or platform name searches)

Workflow;
Step1: Comprehend all news content, identify current news hotspots, and determine a singular article intention classification based on comprehensive global analysis.
Step2: Leverage your professional expertise to extract keywords, ensuring all keywords align with the singular intention.

Recent news provided by Avi-Go company
{}

Only output the classified keywords.
"""

seo_metadata="""
Role:As an SEO expert working for a digital marketing agency. Your client has provided you with company name, service description, and keywords. Your task is to create title and meta description tags for their service pages. Your goal is to optimize pages for search engines and drive organic traffic to the website. When writing tags, keep in mind the company's target audience and brand guidelines.
Background: Meta Title & Meta Description are some HTML Meta Tags in web pages that mainly help search engines understand the content on the page, and are the most important first step in SEO optimization. Search engines will analyze these Meta Titles to navigate search topic keywords and rank them accordingly for keywords, so the quality of Meta Title will greatly affect SEO ranking.
Company Description: Avi-Go,The Largest Data & Charter Marketplace Platform for Business Aviation.From advanced AI models to multi-agent systems, Transform your aviation business with Avi-Go's AI-powered features today.The all-in-one air charter platform connects you to a global network of brokers and operators, streamlining the charter flight booking workflow.
As an SEO optimization expert, the Metadata you write should meet the following advantages:
Meta Title Reference Points(max 60 characters):
- Meta Title must be highly relevant to the content on the webpage
- Write naturally for search engine users, avoid excessive keyword stuffing
- Meta Title content should be specific, concise, and keep length within 30 characters
- Mention your most competitive keyword at least once, place it at the front of the title
- Avoid using the same Meta Title repeatedly
- Can include your brand name at the end
- Try to use numbers (2023, 7 methods, 8 steps, etc.)

Meta Description Reference Points (max 160 characters):
- Meta Description should not excessively stuff keywords
- Meta Description length should be kept within 120-180 characters
- Mention your most competitive keyword 1-2 times
- Use more verbs and clear call-to-actions (Call to Action)
- Try to make Meta Description look unique in search results
- Write content by analyzing search engine user goals

HTML Meta Tags
- Canonical Tag, URL Slug (clean, keyword-based)
- Robot Meta Tag

Header Tags
-Header Tags have a very significant impact on SEO optimization, usually used to embed keywords and long-tail keywords, so search engines can know what keywords your webpage content is related to. The weight decreases sequentially with their numbers, H1 has the highest weight, H6 has the lowest, and so on. More importantly, it helps search engines understand the structure of your webpage content and understand what keywords your content is related to.
-Your client wants to create official website articles that leverage trending news as hook points. In your header tags, you should select the most compelling news stories, then naturally weave in the brand messaging and key selling points, developing an expansive article structure.


FAQ Post, based on article content to propose questions and answers
- Focus on content layout: titles should be concise and clear, while containing keywords. Based on FAQ content, categorize them, questions and answers should be well-organized
- Question and answer design: questions should be targeted, answers should be detailed and specific, maintaining objectivity
- Keyword optimization strategy: using long-tail keywords can improve article precision and attract more precise traffic, keyword density should not be too high, maintain 2%-3% as appropriate

Workflow
1.Read through the entire news content, identify the hottest news that you believe can most attract readers, and design titles that can satisfy readers' curiosity, such as industry dynamics, or reflect current hot topics, celebrity news, or social trends, new tech, sports events .
2.Center around this news, explore related peripheral news, generate reports in a radiating manner, and design corresponding header structure.
3.FAQ design also needs to revolve around hot topics or trending subjects.

Important Notes
-Please refer to advantages throughout the entire process
-Article header design needs to be coherent with natural progression
-Note that the focus is not on news reporting, but on naturally integrating keywords into your article structure to attract readers

News provided by JETBAY company {0}
Keywords: {1}

Output:
Integrate keywords into HTML Meta Tags according to the ideas mentioned in the News, please output Meta Title (less than 60 characters), Meta Description (less than 160 characters), URL Slug, Headers (H1-H3 containing the article content, and a H2 FAQ section include 2-3 questions and answers as H3 sections, removing Q,A identifiers)
"""


seo_rewrite_prompt = """
# Role: Human Private Jet Website Article Editor
Output Language: English

## Main Task
Reorganize AI-collected information and write articles according to the provided SEO format, forming website articles with  human editorial characteristics, while maintaining original information and viewpoints.

## Workflow
1. Carefully read and understand the core information and viewpoints in the AI-collected input news, organize scattered knowledge points into complete coherent articles.
2. Retain core information, strictly maintain the format of original images and tables, and must cite source URLs in IEEE format.
3. Follow the provided SEO format and start rewriting and expanding more content as a real human author:
   - Use reasonable logic to connect scattered news and viewpoints, editing them into complete coherent articles
   - Add some subtle logical jumps but professional viewpoints
   - Avoid using too many long complex sentences. Use simple sentences, data, and examples for better readability and credibility.
   - Follow the header regulations in the format and naturally integrate keywords into the article
4. Ensure the rewritten content maintains the core information and viewpoints of the original text, but has completely different expression styles.
5. Use third-person perspective or third-person narration in writing to show professionalism
6. Review the rewritten content to ensure it reads like the natural expression of a real professional expert.
7. Control the main text output to 800-1500 words, FAQ Post is not counted in the main text

## Important Notes
- Add some slight imperfections, such as colloquial expressions or slight grammatical irregularities
- Avoid overly perfect or structured expressions
- Use third-person perspective or third-person narration in writing to show professionalism
- Your readers are ordinary people, so steer clear of complicated technical terms.

## Output Format
Directly output the written article, retain without any explanation or annotation. The final output should include: HTML Meta Tags (include Meta Title, Meta Description, URL Slug, Header), written article

## Initialization
Please write this content as a real human website article editor.
Collected article materials: {0}
SEO strategy format: {1}
"""

seo_link="""
# Role: Human AVI-GO Website Article Editor
Output Language: English
## Main Task
As a AVI-GO website editor, you need to read the currently written article, analyze the article's logical flow and structure, make only minor modifications, naturally integrate AVI-GO company descriptions and article links into the original article, and appropriately reduce the appearance frequency of other competing business jet charter companies.

## Workflow
1. Carefully read and understand the core information and viewpoints of the article, identify which segments can naturally integrate AVI-GO company information
2. As a AVI-GO article editor, if the article involves relevant content, naturally insert AVI-GO's business scope, brand positioning, market demands, etc., but must not conflict with the original article. Also reduce mentions of other competing business jet charter companies
  - Entry points must be natural, not contradicting the original article, do not force insertions of descriptions. If there are no suitable integration points in the entire article, you may choose not to insert descriptions
  - Modifications should be minimal, do not damage the original article structure
3. Review the modified article to ensure the integrity of the original article structure and that no content is lost

## Important Notes
- Entry points must be natural, control integration frequency not too high, 1-3 times.
- Reduce the frequency of competitor company appearances,but can not change the original viewpoints
- Cannot modify any original article structure, cannot significantly add or delete original article content

## Output Format
Directly output the written article, retain without any explanation or annotation. The final output should include all original parts: HTML Meta Tags (include Meta Title, Meta Description, URL Slug, Header), written article

## Initialization
Please refer to relevant materials and complete your advertising integration task
Company Description: Avi-Go,The Largest Data & Charter Marketplace Platform for Business Aviation.From advanced AI models to multi-agent systems, Transform your aviation business with Avi-Go's AI-powered features today.The all-in-one air charter platform connects you to a global network of brokers and operators, streamlining the charter flight booking workflow.
AVI-GO links:
| Category        | Link                                             | Keywords / Grouping               | Path                          |
|-----------------|--------------------------------------------------|-----------------------------------|-------------------------------|
| Home Page       | https://avi-go.com/                             | Avi-Go Platform, Charter Marketplace | -                             |
| Live Tracking   | https://marketplace.avi-go.com/live-flight-tracking | Real-time Flight Tracking, Aircraft Monitoring | /services/flight-tracking     |
| Empty Leg       | https://marketplace.avi-go.com/empty-legs       | Empty Leg Flights, Discounted Charter | /services/empty-legs          |
| Trip Board      | https://marketplace.avi-go.com/trip-board       | Trip Planning, Charter Management | /services/trip-planning       |
| AI Search       | https://marketplace.avi-go.com/aircraft-search  | AI Aircraft Search, Smart Matching | /services/ai-search           |
| AI BOT          | https://marketplace.avi-go.com/avibot           | Aviation Chatbot, AI Assistant   | /services/avibot              |
| Demo Center     | https://avi-go.com/view-demos                   | Platform Demo, Product Showcase  | /demo                         |
| Pricing         | https://avi-go.com/pricing                      | Pricing Plans, Subscription Models | /pricing                      |
| Getting Started | https://avi-go.com/help-center/getting-started/ | User Onboarding, Help Center     | /help/getting-started         |
| Registration    | https://marketplace.avi-go.com/user/register    | User Registration, Account Setup | /register                     |
| Feedback        | https://marketplace.avi-go.com/feedback         | User Feedback, Platform Reviews  | /feedback                     |
| Blog/News       | https://avi-go.com/blog                         | Aviation News, Industry Insights | /blog                         |
| Broker Solutions| https://avi-go.com/solutions/broker             | Charter Broker Tools, B2B Solutions | /solutions/broker             |
| Operator Solutions| https://avi-go.com/solutions/operator          | Operator Management, Fleet Tools | /solutions/operator           |
| About Us        | https://avi-go.com/about-us                     | Company Info, Team & Mission    | /about-us                     |
original article:{0}
"""

import re

def extract_svg_from_text(text):
    """
    从文本中提取SVG代码
    
    Args:
        text (str): 包含SVG代码的文本
    
    Returns:
        list: 提取到的SVG代码列表
    """
    svg_codes = []
    
    # 匹配 ```svg 代码块
    pattern1 = r'```svg\s*(.*?)\s*```'
    matches1 = re.findall(pattern1, text, re.DOTALL | re.IGNORECASE)
    
    # 匹配 <svg...> 标签（包括HTML实体编码的）
    pattern2 = r'<svg.*?</svg>'
    matches2 = re.findall(pattern2, text, re.DOTALL | re.IGNORECASE)
    
    # 匹配HTML实体编码的SVG
    pattern3 = r'&lt;svg.*?&lt;/svg&gt;'
    matches3 = re.findall(pattern3, text, re.DOTALL | re.IGNORECASE)
    
    # 处理所有匹配结果
    all_matches = matches1 + matches2 + matches3
    
    for match in all_matches:
        if match.strip():
            # HTML实体解码
            decoded_svg = html.unescape(match.strip())
            svg_codes.append(decoded_svg)
    
    # 简单去重
    return list(dict.fromkeys(svg_codes))


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

if __name__ == "__main__":
    test_text = """

Both illustrations use a clean,
"""
    # 提取SVG代码
    svg_codes = extract_svg_from_text(test_text)
    print(f"提取到的SVG代码:{len(svg_codes)},{svg_codes}")
