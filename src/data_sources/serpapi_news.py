import http.client
import json
from src.config.settings import SERPER_API_KEY

def get_news_summaries(currency_pair, start_date, end_date):
    """
    从数据源获取新闻摘要。
    """
    print(f"从数据源获取 {currency_pair} 从 {start_date} 到 {end_date} 的新闻摘要...")
    try:
        conn = http.client.HTTPSConnection("google.serper.dev")
        
        # 优化查询，使其更通用，并尝试获取更多新闻
        query = f"{currency_pair} exchange rate news" # 简化查询，不包含日期，以获取更广泛的结果
        payload = json.dumps({
          "q": query,
          "tbm": "nws", # 搜索新闻
          "num": 50, # 增加获取新闻的数量，以便后续筛选
          "tbs": "qdr:y" # 限制在过去一年内的新闻，避免过旧或不相关
        })
        headers = {
          'X-API-KEY': SERPER_API_KEY,
          'Content-Type': 'application/json'
        }
        
        conn.request("POST", "/search", payload, headers)
        res = conn.getresponse()
        data = res.read()
        news_results = json.loads(data.decode("utf-8"))

        if 'news_results' in news_results and news_results['news_results']:
            # 返回完整的新闻结果列表，以便后续LLM处理
            return news_results['news_results']
        else:
            print(f"Serper API 返回无新闻结果。完整响应: {json.dumps(news_results, indent=2, ensure_ascii=False)}")
            return []
    except Exception as e:
        print(f"Serper API 新闻抓取失败: {e}. 完整响应数据: {data.decode('utf-8') if 'data' in locals() else 'N/A'}")
        return []
