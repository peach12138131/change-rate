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
    # 会员制与所有权模式
    {
        "category": "Technology Innovation & Digital",
        "keyword_en": "AI flight optimization private jets, artificial intelligence aviation, machine learning flight planning, automated charter booking, smart aircraft systems",
        "keyword_zh": "AI航班优化私人飞机",
        "priority": "Medium",
        "description": "Technology disruptions transforming charter operations"
    },
    {
        "category": "Membership & Ownership Models",
        "keyword_en": "Jet card programs, prepaid flight hours, membership aviation, flight card benefits, charter membership plans",
        "keyword_zh": "飞行卡",
        "priority": "High",
        "description": "Strong branded keyword, long-term client interest"
    },
    {
        "category": "Luxury Travel Destinations",
        "keyword_en": "Private island resort, exclusive island getaway, luxury island destination, secluded tropical resort, UHNW island travel",
        "keyword_zh": "私人岛屿度假村",
        "priority": "Medium-High",
        "description": "Appeals to UHNWIs seeking luxury experiences"
    },
    {
        "category": "Specialized Travel Markets",
        "keyword_en": "Destination wedding travel, luxury wedding flights, bridal party charter, wedding guest transport, celebration jet rental",
        "keyword_zh": "目的地婚礼",
        "priority": "Medium-High",
        "description": "Niche but emotionally resonant travel segment"
    },
    {
        "category": "Membership & Ownership Models",
        "keyword_en": "Fractional ownership vs charter, aircraft ownership models, shared jet ownership, private aviation comparison, jet ownership alternatives",
        "keyword_zh": "分时所有权vs包机",
        "priority": "Medium",
        "description": "Educational content for consideration-stage audience"
    },
    {
        "category": "Membership & Ownership Models",
        "keyword_en": "ACMI leasing, wet lease aviation, aircraft crew maintenance insurance, charter operator services, aviation wet rental",
        "keyword_zh": "湿租",
        "priority": "Medium",
        "description": "Relevant for operators and specialized customers"
    },
    # 核心业务服务类关键词
    {
        "category": "Charter Services Core",
        "keyword_en": "Private jet charter, executive jet rental, business aviation services, luxury aircraft charter, corporate jet booking",
        "keyword_zh": "私人包机",
        "priority": "High",
        "description": "High-intent search, direct alignment with core services"
    },
    {
        "category": "Charter Services Core",
        "keyword_en": "Empty leg flights, deadhead flights, repositioning flights, one-way charter deals, discounted private jet",
        "keyword_zh": "空段航班",
        "priority": "High",
        "description": "Popular and high-converting charter search term"
    },
    {
        "category": "Charter Services Core",
        "keyword_en": "On-demand charter, instant jet booking, last-minute private flights, immediate aircraft availability, urgent charter service",
        "keyword_zh": "按需包机",
        "priority": "High",
        "description": "Transactional keyword targeting spontaneous bookers"
    },
    {
        "category": "Charter Services Core",
        "keyword_en": "Corporate aviation, business jet services, executive aircraft, company plane rental, corporate flight department",
        "keyword_zh": "公务机",
        "priority": "High",
        "description": "Appeals to corporate clients and business travelers"
    },
    
    
    
    # 新兴交通模式
    {
        "category": "Emerging Transportation",
        "keyword_en": "Air taxi, urban air mobility, short-haul flights, regional aviation, city-to-city private transport",
        "keyword_zh": "空中出租车",
        "priority": "High",
        "description": "Rising trend in short-distance luxury mobility"
    },
    {
        "category": "Emerging Transportation",
        "keyword_en": "Helicopter transfer, chopper service, rotorcraft transport, helicopter taxi, vertical takeoff aircraft",
        "keyword_zh": "直升机接驳",
        "priority": "Medium-High",
        "description": "Common add-on for private jet travelers"
    },
    
    # 高端旅游目的地
    
    {
        "category": "Luxury Travel Destinations",
        "keyword_en": "Ultra-luxury resort, five-star resort destination, premium hospitality, exclusive resort access, luxury accommodation packages",
        "keyword_zh": "超奢华度假村",
        "priority": "Medium-High",
        "description": "Luxury-focused travelers often search by destination type"
    },
    
    # 专业旅游细分市场
    
    {
        "category": "Specialized Travel Markets",
        "keyword_en": "Wellness retreats, luxury spa destinations, health resort travel, rejuvenation getaways, medical tourism private jets",
        "keyword_zh": "康养度假",
        "priority": "Medium-High",
        "description": "Growing trend in affluent wellness travel"
    },
    {
        "category": "Specialized Travel Markets",
        "keyword_en": "Michelin star dining experiences, gourmet travel, culinary tourism, fine dining destinations, gastronomic adventures",
        "keyword_zh": "米其林餐饮",
        "priority": "Medium-High",
        "description": "Food-focused high-end travel is highly searched"
    },
    
    # 奢华生活方式整合
    {
        "category": "Luxury Lifestyle Integration",
        "keyword_en": "Superyacht charter, mega yacht rental, luxury yacht booking, yacht and jet packages, maritime aviation combo",
        "keyword_zh": "超级游艇",
        "priority": "Medium-High",
        "description": "Luxury lifestyle tie-in, high net worth appeal"
    },
    
    # 基础设施与地面服务
    {
        "category": "Infrastructure & Ground Services",
        "keyword_en": "FBO expansion Asia, fixed base operator growth, private aviation infrastructure, Asia Pacific FBO development, regional aviation hubs",
        "keyword_zh": "亚洲FBO扩张",
        "priority": "Medium",
        "description": "Authoritative regional SEO targeting for FBOs"
    },
    {
        "category": "Infrastructure & Ground Services",
        "keyword_en": "Luxury FBO lounges, premium terminal services, executive airport facilities, VIP aviation lounges, private jet terminals",
        "keyword_zh": "奢华FBO休息室",
        "priority": "Medium",
        "description": "Builds brand trust and regional positioning"
    },
    
    # 可持续发展与环保
    {
        "category": "Sustainability & Environmental",
        "keyword_en": "SAF availability airports, sustainable aviation fuel, biofuel private jets, green aviation fuel, carbon neutral flights",
        "keyword_zh": "可持续航空燃料",
        "priority": "Medium",
        "description": "Sustainability content that supports brand values"
    },
    {
        "category": "Sustainability & Environmental",
        "keyword_en": "Carbon offset private aviation, net zero private jets, environmental impact luxury travel, green aviation initiatives, climate conscious flying",
        "keyword_zh": "私人航空碳抵消",
        "priority": "Medium-High",
        "description": "Environmental regulations affecting luxury travel choices"
    },
    
    # 地缘政治与监管影响
    {
        "category": "Geopolitical & Regulatory Impact",
        "keyword_en": "Private jet sanctions impact, aviation sanctions Russia, oligarch aircraft seizure, political flight restrictions, diplomatic aviation bans",
        "keyword_zh": "私人飞机制裁影响",
        "priority": "High",
        "description": "Real-time political developments affecting private aviation access"
    },
    {
        "category": "Geopolitical & Regulatory Impact",
        "keyword_en": "Cross-border aviation restrictions, international flight permissions, visa requirements private jets, customs private aviation, border control aircraft",
        "keyword_zh": "跨境航空限制",
        "priority": "High",
        "description": "Border policy changes impacting international private flights"
    },
    {
        "category": "Geopolitical & Regulatory Impact",
        "keyword_en": "War zone private jet restrictions, military conflict flight bans, combat area aviation, wartime flight restrictions, conflict zone aircraft",
        "keyword_zh": "战区私人飞机限制",
        "priority": "High",
        "description": "Military conflicts affecting private aviation routing"
    },
    
    # 危机应对与紧急服务
    {
        "category": "Crisis Response & Emergency Services",
        "keyword_en": "Hurricane private jet evacuation, storm aircraft relocation, weather emergency flights, natural disaster aviation, extreme weather charter",
        "keyword_zh": "飓风私人飞机疏散",
        "priority": "High",
        "description": "Extreme weather events driving emergency charter demand"
    },
    {
        "category": "Crisis Response & Emergency Services",
        "keyword_en": "Airport closure flight diversions, weather delays private aviation, runway closures, alternate airport routing, meteorological flight restrictions",
        "keyword_zh": "机场关闭航班改航",
        "priority": "Medium-High",
        "description": "Weather-related disruptions affecting private aviation operations"
    },
    {
        "category": "Crisis Response & Emergency Services",
        "keyword_en": "Private aviation security threats, aircraft hijacking prevention, aviation terrorism risk, flight security measures, private jet safety protocols",
        "keyword_zh": "私人航空安全威胁",
        "priority": "Medium-High",
        "description": "Security incidents impacting private flight operations"
    },
    
    # 医疗与健康服务
    {
        "category": "Medical & Health Services",
        "keyword_en": "Medical evacuation private jet, air ambulance services, emergency medical transport, critical patient flights, hospital aircraft transfer",
        "keyword_zh": "医疗疏散私人飞机",
        "priority": "High",
        "description": "Health emergencies driving specialized charter demand"
    },
    {
        "category": "Medical & Health Services",
        "keyword_en": "VIP patient transport services, luxury medical flights, private healthcare aviation, executive medical transport, premium patient transfer",
        "keyword_zh": "VIP病患运输服务",
        "priority": "Medium-High",
        "description": "High-end medical transport for wealthy patients requiring privacy and comfort"
    },
    
    # 经济市场动态
    {
        "category": "Economic Market Dynamics",
        "keyword_en": "Private jet market recession impact, luxury aviation economic downturn, charter demand crisis, aviation market volatility, economic uncertainty flights",
        "keyword_zh": "私人飞机市场经济衰退影响",
        "priority": "High",
        "description": "Economic downturns affecting luxury aviation demand"
    },
    {
        "category": "Economic Market Dynamics",
        "keyword_en": "New wealth millionaires private jet demand, crypto wealth aviation, tech IPO private flights, startup founders aircraft, emerging rich charter market",
        "keyword_zh": "新富阶层百万富翁私人飞机需求",
        "priority": "Medium-High",
        "description": "Emerging wealth sources including crypto, tech IPOs, and new millionaires driving charter market expansion"
    },
    
    # 技术创新与数字化
    
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
               "minItems": 10,
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
Your service company: JETBAY is a global private jet booking platform headquartered in Singapore, with 6 branches worldwide, committed to providing excellent global services. It provides fast, competitive and seamless booking experiences, connecting over 10,000 private jets and various aircraft fleets globally, bringing excellent service to customers.
As a professional SEO expert, you should have the following professional qualities and steps:
1: You need to have sharp insight and apply internet marketing or advertising operations mindset to identify the most compelling breaking news, industry dynamics, and trending topics that can attract user engagement. Consider how to naturally connect these elements with your brand, then distill them into relevant keywords.
2. You should not limit yourself to one country, pay attention to keyword trends, and consider keyword difficulty, content length, relevance, and search intent.
3. The article intention can be classified - Transactional (e.g. "book private jet Singapore"), - Informational (e.g. "how does private jet charter work"), - Localised (e.g. "private jet Bangkok to Singapore"), - Navigational (e.g. brand or platform name searches)

Workflow;
Step1: Comprehend all news content, identify current news hotspots, and determine a singular article intention classification based on comprehensive global analysis.
Step2: Leverage your professional expertise to extract keywords, ensuring all keywords align with the singular intention.

Recent news provided by JETBAY company
{}

Only output the classified keywords.
"""

seo_metadata="""
Role:As an SEO expert working for a digital marketing agency. Your client has provided you with company name, service description, and keywords. Your task is to create title and meta description tags for their service pages. Your goal is to optimize pages for search engines and drive organic traffic to the website. When writing tags, keep in mind the company's target audience and brand guidelines.
Background: Meta Title & Meta Description are some HTML Meta Tags in web pages that mainly help search engines understand the content on the page, and are the most important first step in SEO optimization. Search engines will analyze these Meta Titles to navigate search topic keywords and rank them accordingly for keywords, so the quality of Meta Title will greatly affect SEO ranking.
Company Description: JETBAY is a global private jet booking platform headquartered in Singapore, with 6 branches worldwide, committed to providing excellent global services. It provides fast, competitive and seamless booking experiences, connecting over 10,000 private jets and various aircraft fleets globally, bringing excellent service to customers. 24/7 aircraft availability without the burden of purchasing, with highly competitive prices. The AI team has mastered the global private jet operation database, can intelligently match optimal flight resources, reduce empty flights, and provide optimal charter solutions. JETBAY's mobile charter team has developed an AI platform that deeply integrates with databases, uses big data to optimize charter resources, and achieves efficient, convenient, and sustainable flight experiences. Our charter service team has over 20 years of rich experience, providing top-tier, cost-effective flight solutions 24/7, ensuring customers enjoy seamless and personalized charter experiences. Our operational support team pays attention to every detail with the highest standards, and with rich industry experience and strong cooperation networks, ensures your private flight is smooth and worry-free.
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
Reorganize AI-collected information and write articles according to the provided SEO format, forming website articles with human editorial characteristics, while maintaining original information and viewpoints. And improve the article's readability since your article's target audience is ordinary non-professionals, and the sentence difficulty should be at a Grade 6–8 reading level that can be read fluently.

## Workflow
1. Carefully read and understand the core information and viewpoints in the AI-collected input news, organize scattered knowledge points into complete coherent articles.
2. Retain core information and must cite source URLs in fixed format:<title of news article>, <company name/publisher> Available at: <link>
3. Follow the provided SEO format and start rewriting and expanding more content as a real human author:
   - Use reasonable logic to connect scattered news and viewpoints, editing them into complete coherent articles
   - Add some subtle logical jumps but professional viewpoints
   - Avoid using too many long complex sentences. Use simple sentences, data, and examples for better readability and credibility.
   - Follow the header regulations in the format and naturally integrate keywords into the article,Ensure keywords appear within the first 100 words, with an overall density of 1-1.5%, and avoid keyword stuffing.
4. Ensure the rewritten content maintains the core information and viewpoints of the original text, but has completely different expression styles.
5. Review the article's paragraphs, sentences, and words to improve readability
    - Reading difficulty should meet a 11-14 year old reading level for fluent reading
    - Avoid using obscure words and reduce the frequency of multi-syllable words. Simplify or define industry terms, and add annotations or vivid explanations when terms are first encountered
    - Sentence length should not be too long; avoid complex sentences with more than 25 words
    - Paragraphs should not contain too many sentences; average 2-4 sentences per paragraph, with content divided into chunks for easy reading
6. Control the main text output to 800-1500 words, FAQ Post is not counted in the main text

## Important Notes
- Avoid overly perfect or structured expressions
- Use third-person perspective or third-person narration in writing 
- Avoid overly long sentences, use simple sentences, words, and examples to improve readability and lower the reading barrier of the article.


## Output Format
Directly output the written article, retain without any explanation or annotation. The final output should include: HTML Meta Tags (include Meta Title, Meta Description, URL Slug, Header), written article

## Initialization
Please write this content as a real human website article editor.
Collected article materials: {0}
SEO strategy format: {1}
"""

seo_link="""
# Role: Human Private Jet Website Article Editor
Output Language: English
## Main Task
As a JETBAY website editor, you need to read the currently written article, analyze the article's logical flow and structure, make only minor modifications, naturally integrate JETBAY company descriptions and article links into the original article, and appropriately reduce the appearance frequency of other competing business jet charter companies.

## Workflow
1. Carefully read and understand the core information and viewpoints of the article, identify which segments can naturally integrate JETBAY company information
2. As a jetbay article editor, if the article involves relevant content, naturally insert JETBAY's business scope, brand positioning, market demands, etc., but must not conflict with the original article. Also reduce mentions of other competing business jet charter companies
  - Entry points must be natural, not contradicting the original article, do not force insertions of descriptions. If there are no suitable integration points in the entire article, you may choose not to insert descriptions
  - Modifications should be minimal, do not damage the original article structure
3. Review the modified article to ensure the integrity of the original article structure and that no content is lost

## Important Notes
- Entry points must be natural, control integration frequency not too high, 1-3 times.
- Reduce the frequency of competitor company appearances,but can not change the original viewpoints
- Cannot modify any original article structure, cannot significantly add or delete original article content
- Use active voice to introduce company content (e.g., JETBAY ...)

## Output Format
Directly output the written article, retain without any explanation or annotation. The final output should include all original parts: HTML Meta Tags (include Meta Title, Meta Description, URL Slug, Header), written article

## Initialization
Please refer to relevant materials and complete your advertising integration task
Company Description: JETBAY is a global private jet booking platform headquartered in Singapore, with 6 branches worldwide, committed to providing excellent global services. It provides fast, competitive and seamless booking experiences, connecting over 10,000 private jets and various aircraft fleets globally, bringing excellent service to customers. 24/7 aircraft availability without the burden of purchasing, with highly competitive prices. The AI team has mastered the global private jet operation database, can intelligently match optimal flight resources, reduce empty flights, and provide optimal charter solutions. JETBAY's mobile charter team has developed an AI platform that deeply integrates with databases, uses big data to optimize charter resources, and achieves efficient, convenient, and sustainable flight experiences. Our charter service team has over 20 years of rich experience, providing top-tier, cost-effective flight solutions 24/7, ensuring customers enjoy seamless and personalized charter experiences. Our operational support team pays attention to every detail with the highest standards, and with rich industry experience and strong cooperation networks, ensures your private flight is smooth and worry-free.
JETBAY links:
| Category        | Link                                             | Keywords / Grouping               | Path                          |
|-----------------|--------------------------------------------------|-----------------------------------|-------------------------------|
| Home Page       | https://www.jet-bay.com                          | TBC                               | -                             |
| Jet Card        | https://www.jet-bay.com/jet-card                 | JetCard, Private Jet Ownership    | -                             |
| Empty Leg       | https://www.jet-bay.com/empty-leg                | Empty Leg, Empty Leg Flights      | -                             |
| Product Page    | https://www.jet-bay.com/services                 | Private Jet Rental                | /services                     |
| Product Page    | https://www.jet-bay.com/services/private-jet-charter | Private Jet                   | /services/private-jet-charter |
| Product Page    | https://www.jet-bay.com/services/group-air-charter   | Group                         | /services/group-air-charter   |
| Product Page    | https://www.jet-bay.com/services/corporate-air-charter | Business                   | /services/corporate-air-charter |
| Product Page    | https://www.jet-bay.com/services/air-ambulance   | Air Ambulance                     | /services/air-ambulance       |
| Product Page    | https://www.jet-bay.com/services/pet-travel/     | Pet Travel                        | /services/pet-travel          |
| Product Page    | https://www.jet-bay.com/services/event-charter/  | Event                             | /services/event-charter       |
| Destination     | https://www.jet-bay.com/destination/             | Destination                       | /destination                  |
| News            | https://www.jet-bay.com/news/                     | News                              | /news                         |
| Booking Process | https://www.jet-bay.com/charter-guide/booking-process | Booking                    | -                             |
| About Us        | https://www.jet-bay.com/about-us                  | About Us                          | /about-us                     |

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
