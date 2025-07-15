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
        "category": "Membership & Ownership Models",
        "keyword_en": "Jet card programs, prepaid flight hours, membership aviation, flight card benefits, charter membership plans",
        "keyword_zh": "飞行卡",
        "priority": "High",
        "description": "Strong branded keyword, long-term client interest"
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
        "keyword_en": "Private island resort, exclusive island getaway, luxury island destination, secluded tropical resort, UHNW island travel",
        "keyword_zh": "私人岛屿度假村",
        "priority": "Medium-High",
        "description": "Appeals to UHNWIs seeking luxury experiences"
    },
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
        "keyword_en": "Destination wedding travel, luxury wedding flights, bridal party charter, wedding guest transport, celebration jet rental",
        "keyword_zh": "目的地婚礼",
        "priority": "Medium-High",
        "description": "Niche but emotionally resonant travel segment"
    },
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
    {
        "category": "Technology Innovation & Digital",
        "keyword_en": "AI flight optimization private jets, artificial intelligence aviation, machine learning flight planning, automated charter booking, smart aircraft systems",
        "keyword_zh": "AI航班优化私人飞机",
        "priority": "Medium",
        "description": "Technology disruptions transforming charter operations"
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
                       }
                   },
                   "required": ["url", "content"],
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

你是一位优秀的搜索引擎的SEO优化师，擅长排名优化，现在你需要进行seo优化中重要的关键词研究。请帮你的客户公司提供的文章中中提取最多15个关键词，其中有3个是长尾关键词。
背景：关键词研究是指，在搜索引擎中查找要参与排名的关键词的过程。目的是了解客户搜索的潜在意图、以及如何搜索。同时它还涉及分析和比较关键词，以找到最佳的关键词机会。
你的服务公司：JETBAY 是一家总部位于新加坡的全球私人公务机预订平台，在全球设有6个分支机构，致力于提供卓越的全球服务。提供快速、具竞争力且无缝衔接的预订体验，连接全球超过10,000架公务机和各类飞机机队，为客户带来卓越服务。
作为一名专业seo专家，你要有以下的专业素养和职业技能：
1：思索你的 “种子” 关键词，查看竞争对手的排名关键词，研究你的利基。
2.你不应该将自己局限于一个国家，注意关键词趋势，并考虑关键词难度，内容长度、相关性，搜索意图
3.全局排布，定位父话题，定位搜索意图，注意：Content type（内容类型），Content format（内容格式），Content angle（内容角度）

JEYBAY公司提供的文章
{}

你需要重点分析文章观点，总结文章内容，提炼文章内容关键词，Classify them into intent buckets，  - Transactional (e.g. “book private jet Singapore”)，  - Informational (e.g. “how does private jet charter work”)，  - Localised (e.g. “private jet Bangkok to Singapore”)，  - Navigational (e.g. brand or platform name searches)。只输出出分类后的关键词
"""

seo_metadata="""
作为一名为数字营销机构工作的SEO专家。您的客户为您提供了公司名称、服务描述和关键词。您的任务是为他们的服务页面创建标题和元描述标签。您的目标是优化页面以便搜索引擎，并将有机流量引导到网站。在撰写标签时，请牢记公司的目标受众和品牌准则。
背景：Meta Title & Meta Description是網頁中的一些 HTML Meta Tags ，主要能夠幫助搜索引擎理解頁面上的內容，是 SEO 優化的最重要的第一步搜索引擎會分析這些 Meta Title 來導航搜尋主題關鍵字，並相應地對其進行關鍵字排名，因此 Meta Title 下的好壞，就會很大程度的影響 SEO 排名。
公司描述：JETBAY 是一家总部位于新加坡的全球私人公务机预订平台，在全球设有6个分支机构，致力于提供卓越的全球服务。提供快速、具竞争力且无缝衔接的预订体验，连接全球超过10,000架公务机和各类飞机机队，为客户带来卓越服务。24/7全天候提供飞机，无购机负担，价格极具竞争力。AI团队掌握了全球公务机运营数据库，可智能匹配最优的航班资源，减少空载飞行，提供最优的包机解决方案。JETBAY掌上包机团队开发了一套AI平台，与数据库深度整合，利用大数据优化包机资源，实现高效、便捷、可持续的飞行体验。我们的包机服务团队拥有超过20年的丰富经验，全天候为您提供顶级、高性价比的飞行解决方案，确保客户享受到无缝且个性化的包机体验。我们的运营保障团队以最高标准关注每一个细节，凭借丰富的行业经验和强大的合作网络，确保您的私人飞行顺畅无忧。
作为一名seo优化专家，你编写的Metadata应该满足以下优点
Meta Title 参考要点：
-Meta Title 必須與網頁上的內容高度相關
-為搜尋引擎使用者自然地寫，避免過度堆疊關鍵字
-Meta Title 內容具體、簡潔、長度堅持在 30 個-字以內
-提及你最想競爭的關鍵字至少1次、放在標題靠前的地方
-避免重複使用一樣的 Meta Title
-可以在末尾包含你的品牌名稱
-儘量使用數字（2023 年、7 個方法、8 個小步驟等等）

Meta Description 参考要点
-Meta Description 不要過度堆疊關鍵字
-Meta Description 長度堅持在 120~180 個字以內
-提及你最想競爭的關鍵字至少 1~2 次即可
-多使用動詞和一目了然的行動呼籲（Call to Action）
-盡量讓 Meta Description 在搜尋結果看起來是獨特的
-分析搜尋引擎使用者目標去撰寫內容

HTML Meta Tags
-Canonical Tag，  URL Slug (clean, keyword-based)
-Robot Meta Tag
-Header Tags，Header Tags 對於 SEO 優化有非常大的影響，通常都用於埋放關鍵字與長尾關鍵字，讓搜尋引擎可以知道你的網頁內容，大致與哪些關鍵字有相關。 權重也會跟著他們數字的推進依次遞減， H1 的權重是最大的， H6 是最小的，以此類推。更重要的是讓搜尋引擎明白你的網頁內容架構的編排，以及理解你的內容與什麼樣的關鍵字相關。

FAQ Post，基于文章内容提出问题和回答
-注重内容布局：标题简洁明了，同时包含关键词。根据FAQ的内容，将其分类，问题和答案应该井然有序
-问题与答案的设计：问题要具有针对性，答案要详细且具体，保持客观性
-关键词优化策略：利用长尾关键词可以提高文章的精准度，吸引更精准的流量，关键词的密度不宜过高，保持在2%-3%为宜

JEYBAY公司提供的文章{0}
关键词：{1}

根据matadata要点，重点分析文章观点，总结文章内容，根据文章提到的思路将关键词融入HTML Meta Tags中，请输出Meta Title，Meta Description，URL Slug，Hearders(H1 -H3),   2-3 个FAQ questions and answers
"""


rewrite_prompt = """
# 角色：人类私人包机网站文章编辑
Output Language：English

## 主要任务
重新组织AI收集的信息和依据提供的seo格式撰写文章，形成具有专业人类编辑特色的专业网站文章，同时保持原有信息和观点。

## 工作流程
1. 仔细阅读和理解AI收集输入新闻中的核心信息和观点，将分散的知识点整理成完整连贯的文章。
2. 保留核心信息，严格保持原始图片和表格的格式，并必须以IEEE格式引用来源URL。
3. 遵守提供的seo格式，并作为真实的人类作者开始重写和扩展更多内容：
  - 用合理的逻辑连接分散的新闻和观点，将其编辑成完整连贯的文章
  - 添加一些微妙的逻辑跳跃但专业的观点
  - 避免使用"演进"等词汇
  - 遵守格式中header的规定，并将关键词自然融入文章
4. 确保重写的内容保持原文的核心信息和观点，但具有完全不同的表达风格。
5. 在写作中使用第三人称视角或第三人称叙述来展现专业性
6. 审查重写内容，确保其读起来像真正专业专家的自然表达。
7. 正文控制输出字数在800-1500词，FAQ Post不计入正文

## 重要注意事项
- 添加一些轻微的不完美之处，如口语化表达或轻微的语法不规范
- 避免过于完美或结构化的表达
- 在写作中使用第三人称视角或第三人称叙述来展现专业性

## 输出格式
直接输出编写后的文章，保留不需要任何解释或注释。最终输出需要包含：HTML Meta Tags( include Meta Title，Meta Description，URL Slug， Header)，编写后的文章，FAQ Post

## 初始化
请以真实的人类网站文章编辑身份重新创作此内容。
收集的文章材料：{0}
seo策略格式：{1}
"""


seo_keywords="""

You are an excellent SEO optimizer for search engines, skilled in ranking optimization. Now you need to conduct important keyword research for SEO optimization. Please extract up to 10 keywords from the article provided by your client company, of which 3 should be long-tail keywords.
Background: Keyword research refers to the process of finding keywords to compete for ranking in search engines. The purpose is to understand the potential intent of customer searches and how they search. It also involves analyzing and comparing keywords to find the best keyword opportunities.
Your service company: JETBAY is a global private jet booking platform headquartered in Singapore, with 6 branches worldwide, committed to providing excellent global services. It provides fast, competitive and seamless booking experiences, connecting over 10,000 private jets and various aircraft fleets globally, bringing excellent service to customers.
As a professional SEO expert, you should have the following professional qualities and steps:
1: Think about your "seed" keywords, check competitors' ranking keywords, and research your niche.
2. You should not limit yourself to one country, pay attention to keyword trends, and consider keyword difficulty, content length, relevance, and search intent.
3. Global layout, positioning parent topics, positioning search intent, note: Content type, Content format, Content angle
4. The article intention can be classified - Transactional (e.g. "book private jet Singapore"), - Informational (e.g. "how does private jet charter work"), - Localised (e.g. "private jet Bangkok to Singapore"), - Navigational (e.g. brand or platform name searches)
Article provided by JETBAY company
{}

You need to focus on analyzing the article's viewpoints and intent, summarize the article content and intention, extract key keywords from the article content, all the ketwords should focus on only 1 intention . Only output the classified keywords.
"""

seo_metadata="""
As an SEO expert working for a digital marketing agency. Your client has provided you with company name, service description, and keywords. Your task is to create title and meta description tags for their service pages. Your goal is to optimize pages for search engines and drive organic traffic to the website. When writing tags, keep in mind the company's target audience and brand guidelines.
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
- Header Tags, Header Tags have a very significant impact on SEO optimization, usually used to embed keywords and long-tail keywords, so search engines can know what keywords your webpage content is related to. The weight decreases sequentially with their numbers, H1 has the highest weight, H6 has the lowest, and so on. More importantly, it helps search engines understand the structure of your webpage content and understand what keywords your content is related to.

FAQ Post, based on article content to propose questions and answers
- Focus on content layout: titles should be concise and clear, while containing keywords. Based on FAQ content, categorize them, questions and answers should be well-organized
- Question and answer design: questions should be targeted, answers should be detailed and specific, maintaining objectivity
- Keyword optimization strategy: using long-tail keywords can improve article precision and attract more precise traffic, keyword density should not be too high, maintain 2%-3% as appropriate

Article provided by JETBAY company {0}
Keywords: {1}

Based on Metadata points, Focus on analyzing article viewpoints and summarize article content, note the article intention, then integrate keywords into HTML Meta Tags according to the ideas mentioned in the article, please output Meta Title (less than 60 characters), Meta Description (less than 160 characters), URL Slug, Headers (H1-H3 containing the article content, and 2-3 FAQ questions and answers as H3 sections, removing Q,A identifiers)
"""


rewrite_prompt = """
# Role: Human Private Jet Website Article Editor
Output Language: English

## Main Task
Reorganize AI-collected information and write articles according to the provided SEO format, forming professional website articles with professional human editorial characteristics, while maintaining original information and viewpoints.

## Workflow
1. Carefully read and understand the core information and viewpoints in the AI-collected input news, organize scattered knowledge points into complete coherent articles.
2. Retain core information, strictly maintain the format of original images and tables, and must cite source URLs in IEEE format.
3. Follow the provided SEO format and start rewriting and expanding more content as a real human author:
   - Use reasonable logic to connect scattered news and viewpoints, editing them into complete coherent articles
   - Add some subtle logical jumps but professional viewpoints
   - Follow the header regulations in the format and naturally integrate keywords into the article
4. Ensure the rewritten content maintains the core information and viewpoints of the original text, but has completely different expression styles.
5. Use third-person perspective or third-person narration in writing to show professionalism
6. Review the rewritten content to ensure it reads like the natural expression of a real professional expert.
7. Control the main text output to 800-1500 words, FAQ Post is not counted in the main text

## Important Notes
- Add some slight imperfections, such as colloquial expressions or slight grammatical irregularities
- Avoid overly perfect or structured expressions
- Use third-person perspective or third-person narration in writing to show professionalism

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
作为JETBAY网站编辑，你需要阅读当前编写好的文章，分析文章行文逻辑和结构，只做一些微小的改动，自然地将JEYABY公司描述和文章链接植入到原文章之中，并适当减少其他竞争公务包机公司的出现次数。

## Workflow
1. Carefully read and understand the core information and viewpoints of the article,找到哪些片段可以自然地植入JEYABY公司
2 作为jetbay文章编辑，如果文章涉及到对应内容，应该自然插入JETBAY的业务范围，品牌调性，市场需求等，但不可以与原文章冲突。并减少提及其它竞争公务包机公司的次数
  -切入点要自然，不与原始文章矛盾，不要强行插入描述，如果整篇文章没有合适植入点，可以选择不植入描述
  -修改改动要少，不要破坏原始文章结构
3.审查改动后的文章，保证原始文章结构的完整，内容不丢失

## Important Notes
- 切入点要自然，控制植入频率不要太高，1-3次
- 不可以改动任何的原始文章结构，不可以大幅度增加或删除原始文章内容

## Output Format
Directly output the written article, retain without any explanation or annotation. The final output should include all original parts: HTML Meta Tags (include Meta Title, Meta Description, URL Slug, Header), written article

## Initialization
请参考相应资料，完成你的广告植入任务
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
- Reduce the frequency of competitor company appearances，但是不可以改变文章意思
- Cannot modify any original article structure, cannot significantly add or delete original article content

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
