import json
import requests
import yaml
import os
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup

def load_config():
    """
    Loads configuration from config.yaml file.
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Warning: config.yaml not found at {config_path}. Using default values.")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing config.yaml: {e}. Using default values.")
        return {}

def fetch_html_content(url):
    """
    Fetches HTML content from a given URL.
    """
    config = load_config()
    
    # 从配置文件获取headers，如果没有配置则使用默认值
    tradingview_config = config.get('tradingview', {})
    headers_config = tradingview_config.get('headers', {})
    
    headers = {
        'User-Agent': headers_config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'),
        'cookie': headers_config.get('cookie', '')
    }
    
    # 获取超时设置
    timeout = config.get('news', {}).get('timeout_seconds', 10)
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def parse_news_html(html_content):
    """
    Parses the HTML content to extract news title and body.
    It prioritizes extracting data from an embedded JSON script,
    falling back to standard HTML tag parsing if the JSON is not found.
    """
    if not html_content:
        return {"title": "Error", "content": "Empty HTML content provided."}

    soup = BeautifulSoup(html_content, 'html.parser')
    
    title = ""
    content_paragraphs = []

    # --- 优先策略：从嵌入的 JSON 数据中提取 ---
    # 现代网页经常将数据嵌入在 <script> 标签中
    scripts = soup.find_all('script', type='application/prs.init-data+json')
    for script in scripts:
        try:
            # 尝试解析 script 标签内的 JSON 内容
            data = json.loads(script.string)
            
            # 遍历 JSON 数据，寻找包含 'story' 的键
            for key in data:
                if isinstance(data[key], dict) and 'story' in data[key]:
                    story_data = data[key]['story']
                    
                    # 提取标题
                    if 'title' in story_data:
                        title = story_data['title']
                    
                    # 提取内容 (以 AST 结构存储)
                    if 'astDescription' in story_data and 'children' in story_data['astDescription']:
                        for paragraph_node in story_data['astDescription']['children']:
                            # 确保节点是段落类型并且有内容
                            if paragraph_node.get('type') == 'p' and 'children' in paragraph_node:
                                paragraph_text = "".join(p_child for p_child in paragraph_node['children'] if isinstance(p_child, str))
                                if paragraph_text:
                                    content_paragraphs.append(paragraph_text)
                        
                        # 如果通过 JSON 成功提取到内容，直接返回结果
                        if title and content_paragraphs:
                            return {
                                "title": title.strip(),
                                "content": "\n".join(content_paragraphs)
                            }
        except (json.JSONDecodeError, TypeError, KeyError):
            # 如果解析失败或结构不匹配，就跳过这个 script 标签
            continue

    # --- 降级策略：如果 JSON 提取失败，则解析 HTML 标签 ---
    # (此逻辑与你原始代码相似，但做了优化和简化)
    print("Warning: Could not parse embedded JSON. Falling back to HTML tag parsing.")
    
    # 查找标题
    title_tag = soup.find('h1', class_='title-KX2tCBZq') # 使用更精确的 class
    if not title_tag:
        title_tag = soup.find('h1', class_='tv-news-article__title')
    if not title_tag:
        title_tag = soup.find('h1') # Fallback
    if title_tag:
        title = title_tag.get_text(strip=True)

    # 查找内容主体
    # class 'body-KX2tCBZq' 是付费文章的主要容器
    main_content_div = soup.find('div', class_='body-KX2tCBZq')
    if main_content_div:
        # 直接查找容器内所有的 <p> 标签
        paragraphs = main_content_div.find_all('p')
        for p in paragraphs:
            paragraph_text = p.get_text(strip=True)
            if paragraph_text:
                content_paragraphs.append(paragraph_text)
    
    # 如果两种方法都找不到内容，给出最终提示
    if not content_paragraphs:
        return {
            "title": title if title else "No Title Found",
            "content": "No readable content found on this page after trying all methods."
        }

    return {
        "title": title,
        "content": "\n".join(content_paragraphs)
    }


def save_to_json(data, filename="news_output.json"):
    """
    Saves the extracted data to a JSON file.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"News content saved to {filename}")

def fetch_news_content(news_url):
    """
    Fetches and parses news content from a given TradingView news URL.
    """
    html_content = fetch_html_content(news_url)
    if html_content:
        news_data = parse_news_html(html_content)
    else:
        news_data = {"title": "Error", "content": "Failed to retrieve HTML content."}
    return news_data

def fetch_tradingview_news(symbol, target_date = '2025-07-31', window = 1):
    url = "https://news-mediator.tradingview.com/news-flow/v1/news"
    params = {
        "filter": [
            "lang:en",
            f"symbol:NASDAQ:{symbol}"
        ],
        "streaming": "false"  # Set to "true" for streaming, "false" for a single snapshot
    }
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()

    start_time = datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=9, minute=30)
    end_time = start_time + timedelta(days=window)

    print(start_time, end_time)
    response = requests.get(url, params=params)
    response.raise_for_status()
    news_items = response.json().get("items", [])

    all_news = {
        "symbol": symbol,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "news": []
    }
    for item in news_items:
        # item['published']: 2025-07-30 16:20:12 UTC
        published_dt = datetime.utcfromtimestamp(item["published"])
        if published_dt < start_time or published_dt > end_time:
            continue
        link = item.get("link") or f"https://www.tradingview.com{item.get('storyPath','')}"
        if not link.startswith('https://www.tradingview.com'):
            continue
        related = ", ".join([s["symbol"] for s in item.get("relatedSymbols", [])])
        print(f"Fetching {item.get('title')}\n")
        content = fetch_news_content(link)['content']
        all_news["news"].append({
            "title": item.get("title", "No Title"),
            "source": item.get("source", "Unknown Source"),
            "published": published_dt.strftime('%Y-%m-%d %H:%M:%S UTC'),
            "related_symbols": related,
            "link": link,
            "content": content
        })

    return all_news

if __name__ == "__main__":
    # This part will be executed when the script is run directly.
    
    news_data = fetch_tradingview_news('TSLA',target_date='2025-07-31')
    save_to_json(news_data)
    
    # news_data = fetch_tradingview_news('TSLA',target_date='2025-07-30')
    # save_to_json(news_data)
