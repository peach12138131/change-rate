import os
import re 
import html
tavily_key=""
claude_key=""


generate_svg_prompt=""""
    Please analyze the main content of this article, focusing on its narrative logic, data usage, and event trend changes. Create SVG illustrations that match this article, with requirements for a concise illustration style, refined text, no unnecessary text symbols, and colors that align with the simple and elegant style of the private jet industry. Output 1 SVG image based on the content. This is the article:
   
    """
rewrite_prompt="""
# Role: Human Private Charter Website Article Editor Simulator
Output Language: English
## Main Task
Completely rewrite AI-collected information and reports into professional website articles with the characteristics of professional human editors, while maintaining original information and viewpoints.

## Workflow
1. Carefully read and understand the core information and viewpoints in AI-generated input text, organizing scattered knowledge points into complete and coherent articles.
2. Retain core information and strictly maintain the format of original images and tables. However, tables can be rearranged.
3. Rewrite content from scratch as an authentic human author:
   - Add some subtle logical leaps but professional viewpoints
   - Appropriately describe articles from a Marketplace perspective
   - Avoid excessive subheadings and numbering systems; articles should be complete, coherent, and in-depth
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
    # 原有18个关键词
    {
        "category": "Business Aviation & Charter Services",
        "keyword_en": "Private jet charter, executive jet rental, business aviation services, luxury aircraft charter, corporate jet booking",
        "keyword_zh": "私人包机",
        "priority": "High",
        "description": "High-intent search, direct alignment with core services"
    },
    {
        "category": "Business Aviation & Charter Services",
        "keyword_en": "Empty leg flights, deadhead flights, repositioning flights, one-way charter deals, discounted private jet",
        "keyword_zh": "空段航班",
        "priority": "High",
        "description": "Popular and high-converting charter search term"
    },
    {
        "category": "Business Aviation & Charter Services",
        "keyword_en": "On-demand charter, instant jet booking, last-minute private flights, immediate aircraft availability, urgent charter service",
        "keyword_zh": "按需包机",
        "priority": "High",
        "description": "Transactional keyword targeting spontaneous bookers"
    },
    {
        "category": "Business Aviation & Charter Services",
        "keyword_en": "Corporate aviation, business jet services, executive aircraft, company plane rental, corporate flight department",
        "keyword_zh": "公务机",
        "priority": "High",
        "description": "Appeals to corporate clients and business travelers"
    },
    {
        "category": "Business Aviation & Charter Services",
        "keyword_en": "Jet card programs, prepaid flight hours, membership aviation, flight card benefits, charter membership plans",
        "keyword_zh": "飞行卡",
        "priority": "High",
        "description": "Strong branded keyword, long-term client interest"
    },
    {
        "category": "Business Aviation & Charter Services",
        "keyword_en": "Air taxi, urban air mobility, short-haul flights, regional aviation, city-to-city private transport",
        "keyword_zh": "空中出租车",
        "priority": "High",
        "description": "Rising trend in short-distance luxury mobility"
    },
    {
        "category": "Business Aviation & Charter Services",
        "keyword_en": "ACMI leasing, wet lease aviation, aircraft crew maintenance insurance, charter operator services, aviation wet rental",
        "keyword_zh": "湿租",
        "priority": "Medium",
        "description": "Relevant for operators and specialized customers"
    },
    {
        "category": "Business Aviation & Charter Services",
        "keyword_en": "Fractional ownership vs charter, aircraft ownership models, shared jet ownership, private aviation comparison, jet ownership alternatives",
        "keyword_zh": "分时所有权vs包机",
        "priority": "Medium",
        "description": "Educational content for consideration-stage audience"
    },
    {
        "category": "Luxury Travel & Concierge Experience",
        "keyword_en": "Private island resort, exclusive island getaway, luxury island destination, secluded tropical resort, UHNW island travel",
        "keyword_zh": "私人岛屿度假村",
        "priority": "Medium-High",
        "description": "Appeals to UHNWIs seeking luxury experiences"
    },
    {
        "category": "Luxury Travel & Concierge Experience",
        "keyword_en": "Superyacht charter, mega yacht rental, luxury yacht booking, yacht and jet packages, maritime aviation combo",
        "keyword_zh": "超级游艇",
        "priority": "Medium-High",
        "description": "Luxury lifestyle tie-in, high net worth appeal"
    },
    {
        "category": "Luxury Travel & Concierge Experience",
        "keyword_en": "Destination wedding travel, luxury wedding flights, bridal party charter, wedding guest transport, celebration jet rental",
        "keyword_zh": "目的地婚礼",
        "priority": "Medium-High",
        "description": "Niche but emotionally resonant travel segment"
    },
    {
        "category": "Luxury Travel & Concierge Experience",
        "keyword_en": "Helicopter transfer, chopper service, rotorcraft transport, helicopter taxi, vertical takeoff aircraft",
        "keyword_zh": "直升机接驳",
        "priority": "Medium-High",
        "description": "Common add-on for private jet travelers"
    },
    {
        "category": "Luxury Travel & Concierge Experience",
        "keyword_en": "Ultra-luxury resort, five-star resort destination, premium hospitality, exclusive resort access, luxury accommodation packages",
        "keyword_zh": "超奢华度假村",
        "priority": "Medium-High",
        "description": "Luxury-focused travelers often search by destination type"
    },
    {
        "category": "Luxury Travel & Concierge Experience",
        "keyword_en": "Wellness retreats, luxury spa destinations, health resort travel, rejuvenation getaways, medical tourism private jets",
        "keyword_zh": "康养度假",
        "priority": "Medium-High",
        "description": "Growing trend in affluent wellness travel"
    },
    {
        "category": "Luxury Travel & Concierge Experience",
        "keyword_en": "Michelin star dining experiences, gourmet travel, culinary tourism, fine dining destinations, gastronomic adventures",
        "keyword_zh": "米其林餐饮",
        "priority": "Medium-High",
        "description": "Food-focused high-end travel is highly searched"
    },
    {
        "category": "FBO & Airport Infrastructure",
        "keyword_en": "FBO expansion Asia, fixed base operator growth, private aviation infrastructure, Asia Pacific FBO development, regional aviation hubs",
        "keyword_zh": "亚洲FBO扩张",
        "priority": "Medium",
        "description": "Authoritative regional SEO targeting for FBOs"
    },
    {
        "category": "FBO & Airport Infrastructure",
        "keyword_en": "Luxury FBO lounges, premium terminal services, executive airport facilities, VIP aviation lounges, private jet terminals",
        "keyword_zh": "奢华FBO休息室",
        "priority": "Medium",
        "description": "Builds brand trust and regional positioning"
    },
    {
        "category": "FBO & Airport Infrastructure",
        "keyword_en": "SAF availability airports, sustainable aviation fuel, biofuel private jets, green aviation fuel, carbon neutral flights",
        "keyword_zh": "可持续航空燃料",
        "priority": "Medium",
        "description": "Sustainability content that supports brand values"
    },
    
    # 新增12个实时性动态关键词
    {
        "category": "Political & Regulatory Impact",
        "keyword_en": "Private jet sanctions impact, aviation sanctions Russia, oligarch aircraft seizure, political flight restrictions, diplomatic aviation bans",
        "keyword_zh": "私人飞机制裁影响",
        "priority": "High",
        "description": "Real-time political developments affecting private aviation access"
    },
    {
        "category": "Political & Regulatory Impact",
        "keyword_en": "Cross-border aviation restrictions, international flight permissions, visa requirements private jets, customs private aviation, border control aircraft",
        "keyword_zh": "跨境航空限制",
        "priority": "High",
        "description": "Border policy changes impacting international private flights"
    },
    {
        "category": "Climate & Weather Impact",
        "keyword_en": "Hurricane private jet evacuation, storm aircraft relocation, weather emergency flights, natural disaster aviation, extreme weather charter",
        "keyword_zh": "飓风私人飞机疏散",
        "priority": "High",
        "description": "Extreme weather events driving emergency charter demand"
    },
    {
        "category": "Climate & Weather Impact",
        "keyword_en": "Airport closure flight diversions, weather delays private aviation, runway closures, alternate airport routing, meteorological flight restrictions",
        "keyword_zh": "机场关闭航班改航",
        "priority": "Medium-High",
        "description": "Weather-related disruptions affecting private aviation operations"
    },
    {
        "category": "Economic & Market Dynamics",
        "keyword_en": "Private jet market recession impact, luxury aviation economic downturn, charter demand crisis, aviation market volatility, economic uncertainty flights",
        "keyword_zh": "私人飞机市场经济衰退影响",
        "priority": "High",
        "description": "Economic downturns affecting luxury aviation demand"
    },
    {
        "category": "Economic & Market Dynamics",
        "keyword_en": "New wealth millionaires private jet demand, crypto wealth aviation, tech IPO private flights, startup founders aircraft, emerging rich charter market",
        "keyword_zh": "新富阶层百万富翁私人飞机需求",
        "priority": "Medium-High",
        "description": "Emerging wealth sources including crypto, tech IPOs, and new millionaires driving charter market expansion"
    },
    {
        "category": "Regional Conflicts & Security",
        "keyword_en": "War zone private jet restrictions, military conflict flight bans, combat area aviation, wartime flight restrictions, conflict zone aircraft",
        "keyword_zh": "战区私人飞机限制",
        "priority": "High",
        "description": "Military conflicts affecting private aviation routing"
    },
    {
        "category": "Regional Conflicts & Security",
        "keyword_en": "Private aviation security threats, aircraft hijacking prevention, aviation terrorism risk, flight security measures, private jet safety protocols",
        "keyword_zh": "私人航空安全威胁",
        "priority": "Medium-High",
        "description": "Security incidents impacting private flight operations"
    },
    {
        "category": "Health & Emergency Response",
        "keyword_en": "Medical evacuation private jet, air ambulance services, emergency medical transport, critical patient flights, hospital aircraft transfer",
        "keyword_zh": "医疗疏散私人飞机",
        "priority": "High",
        "description": "Health emergencies driving specialized charter demand"
    },
    {
        "category": "Health & Emergency Response",
        "keyword_en": "VIP patient transport services, luxury medical flights, private healthcare aviation, executive medical transport, premium patient transfer",
        "keyword_zh": "VIP病患运输服务",
        "priority": "Medium-High",
        "description": "High-end medical transport for wealthy patients requiring privacy and comfort"
    },
    {
        "category": "Technology & Innovation Impact",
        "keyword_en": "AI flight optimization private jets, artificial intelligence aviation, machine learning flight planning, automated charter booking, smart aircraft systems",
        "keyword_zh": "AI航班优化私人飞机",
        "priority": "Medium",
        "description": "Technology disruptions transforming charter operations"
    },
    {
        "category": "Environmental & Sustainability",
        "keyword_en": "Carbon offset private aviation, net zero private jets, environmental impact luxury travel, green aviation initiatives, climate conscious flying",
        "keyword_zh": "私人航空碳抵消",
        "priority": "Medium-High",
        "description": "Environmental regulations affecting luxury travel choices"
    }
]


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


if __name__ == "__main__":
    test_text = """

Both illustrations use a clean,
"""
    # 提取SVG代码
    svg_codes = extract_svg_from_text(test_text)
    print(f"提取到的SVG代码:{len(svg_codes)},{svg_codes}")
