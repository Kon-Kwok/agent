from src.utils.query_parser import parse_user_query
from src.data_sources.yfinance_data import get_exchange_rates_yfinance
from src.data_sources.serpapi_news import get_news_summaries
from src.utils.llm_utils import call_gemini_llm_with_messages
import json

def data_collection_agent(user_query):
    """
    阶段1：数据收集Agent。
    根据用户查询解析货币对，并从yfinance获取汇率数据，同时获取新闻摘要。
    """
    print(f"数据收集Agent接收到查询: {user_query}")
    currency_pair = parse_user_query(user_query)
    print(f"解析用户请求，货币对: {currency_pair}")

    # 从yfinance获取数据
    exchange_rates = get_exchange_rates_yfinance(currency_pair, "2019-01-01", "2024-12-31")
    print(f"从yfinance获取汇率数据，数据量: {len(exchange_rates) if exchange_rates else 0}")

    if not exchange_rates:
        print("未能从yfinance获取到汇率数据。")

    news_results = get_news_summaries(currency_pair, "2019-01-01", "2024-12-31")
    print(f"获取新闻结果，新闻量: {len(news_results) if news_results else 0}")

    processed_news_output = None
    if news_results:
        # 使用LLM处理新闻结果
        news_prompt = f"""
        以下是关于 "{currency_pair}" 的新闻结果。请对这些新闻进行总结，提取关键信息，并分析其对汇率的潜在影响（利好、利空、中性）。
        请以结构化的JSON格式返回结果，包含以下字段：
        - "summary": 对所有新闻的整体总结。
        - "key_insights": 提取出的关键信息点列表。
        - "sentiment_analysis": 对整体新闻情绪的判断（"positive", "negative", "neutral"）。
        - "detailed_news_analysis": 一个列表，包含每条新闻的详细分析，每个元素包含：
            - "title": 新闻标题。
            - "snippet": 新闻摘要。
            - "analysis": 对该新闻的简要分析及其对汇率的潜在影响。

        新闻数据：
        {json.dumps(news_results, indent=2, ensure_ascii=False)}
        """
        print("调用LLM处理新闻...")
        processed_news_output = call_gemini_llm_with_messages([{"role": "user", "parts": [news_prompt]}])
        print("LLM新闻处理完成。")
        try:
            processed_news_output = json.loads(processed_news_output)
        except json.JSONDecodeError:
            print("LLM返回的不是有效的JSON格式。")
            processed_news_output = {"error": "LLM返回格式错误", "raw_output": processed_news_output}

    return {"exchange_rates": exchange_rates, "processed_news": processed_news_output}
