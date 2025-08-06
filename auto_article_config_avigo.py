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

 
keyword_list =[
    {
        "category": "temp",
        "keyword_en": "business aviation, private aviation, bizav, general aviation (GA), private jet, charter flights, ",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "on-demand charter, air taxi, Part 135, AOC, corporate flight, high-net-worth travel",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "airport closure, airport closed, airport reopens, runway closure, taxiway closure, NOTAM, TFR (temporary flight restriction), airspace restriction",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "slot control, airport slots, PPR (prior permission required), curfew, capacity constraints, ground delay program (GDP)",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "ground stop, flow control, ATC delay, diversion, alternates, de-icing, ARFF level, RFFS downgrade, apron congestion, ramp closure",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "VIP movement, state visit, special security measures, CIQ (customs immigration quarantine), CBP, APIS, eAPIS, preclearance, GAF (General Aviation Facility)",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "FBO opening, new FBO, FBO expansion, FBO acquisition, FBO network, ground handling, ramp services, hangar space",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "crew lounge, concierge, fueling, Jet A, SAF availability, fuel shortage, fuel price, contract fuel, handling fees, parking/stand availability, GA terminal, VIP terminal",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "Major FBO / handlers: Signature Aviation, Atlantic Aviation, Jet Aviation, ExecuJet, Universal Weather and Aviation",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "Major FBO / handlers: Jetex, Skyservice, Sheltair, Million Air, TAC Air, Aero Centers, Meridian, Ross Aviation, Luxaviation Group, Menzies Aviation (GA ops), Jet In, Avflight",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "business aviation operational update, private jet advisory, bizav service disruption, charter flight impact, corporate aviation closure",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp", 
        "keyword_en": "airport closure NOTAM private aviation, runway works business jets, TFR temporary flight restriction bizav, airspace closure corporate flights",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "FBO opening North America, Signature Aviation expansion Europe, Atlantic Aviation Middle East, Jet Aviation acquisition Asia",
        "keyword_zh": "temp",
        "priority": "temp", 
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "hurricane private aviation closure, typhoon business jet diversion, wildfire charter flight disruption, volcanic ash bizav impact",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "NBAA-BACE aircraft announcement, EBACE order signing, LABACE demo tour, Dubai Airshow private jet launch",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "Gulfstream G700 delivery, Bombardier Global 8000 certification, Dassault Falcon 10X entry into service, Citation Longitude backlog",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "NetJets fleet expansion, Flexjet membership program, VistaJet route expansion, XO dynamic pricing platform",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "FAA regulation private aviation, EASA bizav directive, pilot shortage charter industry, crew training business jets",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "SAF availability Signature Aviation, sustainable fuel Jet Aviation, carbon neutral private jets, net-zero business aviation",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "luxury private jet journey Aman, Four Seasons Private Jet expedition, bespoke aviation itinerary UHNWI, yacht charter private aviation",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "Dubai private aviation hub, Abu Dhabi business jets, Doha charter flights, Riyadh corporate aviation, Gulf bizav operations",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "Teterboro KTEB private jets, Van Nuys KVNY business aviation, Nice LFMN charter flights, Aspen KASE seasonal operations",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "Ibiza private jet traffic, Mallorca PMI business aviation, Mykonos charter flights, Santorini private aircraft operations",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "Maldives VRMM private aviation, Seychelles FSIA business jets, Phuket VTSP charter operations, Bali WADD corporate flights",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "Jackson Hole KJAC private jets, Napa KSTS business aviation, Bahamas MYNN charter flights, Caribbean private aircraft",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "Victor charter broker platform, LunaJets instant booking, Air Charter Service ACS, Chapman Freeborn wholesale marketplace",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "Jet Edge Vista acquisition, Qatar Executive fleet renewal, TAG Aviation new base, Global Jet partnership",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "bizav traffic trends North America, European private aviation demand, Middle East charter growth, Asia business jet movements",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "Rolls-Royce Pearl engine delivery, Pratt Whitney PW300 maintenance, Williams FJ44 AOG support, Honeywell HTF7000 upgrade",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "MRO expansion business aviation, maintenance slot availability, parts shortage private jets, supply chain bizav impact",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "VIP movement state visit, security alert private aviation, diplomatic flights closure, special measures bizav",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "eVTOL urban air mobility, electric aircraft development, vertiport infrastructure, charging network private aviation",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "Monaco Yacht Show private jets, Cannes Film Festival aviation, Art Basel charter flights, F1 Grand Prix bizav",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "ski season private aviation Aspen, golf masters charter flights, safari lodges Africa bizav, wellness retreat private jets",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "Rosewood private jet services, Mandarin Oriental aviation, Six Senses charter partnerships, Belmond luxury travel",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "ground delay program GDP bizav, flow control private aviation, ATC delay business jets, diversion charter flights",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "fuel shortage private aviation, Jet A price increase, contract fuel bizav, handling fees FBO",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "hangar space availability, crew lounge opening, concierge services FBO, VIP terminal private aviation",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "GCAA UAE private aviation, GACA Saudi bizav regulation, DGCA India charter rules, CAAC China business jets",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
    },
    {
        "category": "temp",
        "keyword_en": "Neste SAF private aviation, Avfuel sustainable fuel, World Fuel Services SAF certificate, TotalEnergies Aviation carbon neutral",
        "keyword_zh": "temp",
        "priority": "temp",
        "description": "temp"
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
Your service company: Avi-Go,The Largest Data & Charter Marketplace Platform for Business Aviation.From advanced AI models to multi-agent systems, Transform your aviation business with Avi-Go's AI-powered features today.The all-in-one air charter platform connects you to a global network of brokers and operators, streamlining the charter flight booking workflow.
As a professional SEO expert, you should have the following professional qualities and steps:
1: You need to have sharp insight and apply internet marketing or advertising operations mindset to identify the most compelling breaking news, industry dynamics, and trending topics that can attract user engagement. Consider how to naturally connect these elements with your brand, then distill them into relevant keywords.
2. You should not limit yourself to one country, pay attention to news trends, and consider keyword difficulty, content length, relevance, and search intent.
3. The article intention can be classified - Transactional (e.g. "private jet booking platform"), - Informational (e.g. "charter operator/ops software"), - Localised (e.g. "private jet Bangkok to Singapore"), - Navigational (e.g. brand or platform name searches)
4. The keywords

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
- Try to use numbers (2025, 7 methods, 8 steps, etc.)

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

News provided by AVI-GO company {0}
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
- Use active voice to introduce company content (e.g., Avi-Go ...)

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
