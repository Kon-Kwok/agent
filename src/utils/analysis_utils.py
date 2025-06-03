import pandas as pd
from src.utils.llm_utils import call_gemini_llm

def perform_volatility_analysis(exchange_rates):
    """
    进行波动分析。
    """
    print("进行波动分析...")
    if not exchange_rates:
        print("没有汇率数据可供分析。")
        return {"average_volatility": 0.0, "max_fluctuation": 0.0}

    df = pd.DataFrame(exchange_rates)
    df['rate'] = pd.to_numeric(df['rate'], errors='coerce')
    df.dropna(subset=['rate'], inplace=True)

    if df.empty:
        print("数据清洗后没有有效汇率数据可供分析。")
        return {"average_volatility": 0.0, "max_fluctuation": 0.0}

    try:
        df['daily_change'] = df['rate'].diff().abs()
        average_volatility = df['daily_change'].mean()
        max_fluctuation = df['daily_change'].max()

        return {"average_volatility": average_volatility, "max_fluctuation": max_fluctuation}
    except Exception as e:
        print(f"波动分析失败: {e}")
        return {"average_volatility": 0.0, "max_fluctuation": 0.0}

def extract_news_keywords(news_summaries):
    """
    使用LLM提取新闻关键词。
    """
    print("使用LLM提取新闻关键词...")
    if not news_summaries:
        return []

    # 将新闻摘要合并成一个大文本
    combined_text = "\n".join([f"标题: {news['title']}\n摘要: {news['snippet']}" for news in news_summaries])
    
    prompt = f"""请从以下新闻内容中提取5-10个最重要的关键词或短语，用逗号分隔。
新闻内容：
{combined_text}
"""
    keywords_str = call_gemini_llm(prompt, model_name="gemini-1.5-flash", temperature=0.3)
    if keywords_str:
        return [kw.strip() for kw in keywords_str.split(',') if kw.strip()]
    return []

def correlate_events(exchange_rates, news_summaries):
    """
    关联汇率数据和新闻事件。
    简化为识别新闻中提到的日期，并与汇率数据进行粗略匹配。
    """
    print("关联汇率数据和新闻事件...")
    key_events = []
    if not news_summaries or not exchange_rates:
        return []

    # 将汇率数据转换为DataFrame，方便日期查找
    df_rates = pd.DataFrame(exchange_rates)
    df_rates['date'] = pd.to_datetime(df_rates['date'])
    
    for news in news_summaries:
        # 尝试从新闻摘要中提取日期信息
        # 这是一个简化的示例，实际应用中可能需要更复杂的日期提取逻辑
        prompt = f"""请从以下新闻摘要中提取一个最相关的日期（格式为YYYY-MM-DD），如果没有明确日期则返回'无'。
新闻摘要：
{news['snippet']}
"""
        event_date_str = call_gemini_llm(prompt, model_name="gemini-1.5-flash", temperature=0.1)
        
        if event_date_str and event_date_str != '无':
            try:
                event_date = pd.to_datetime(event_date_str)
                # 检查该日期附近是否有汇率数据
                # 简化为直接检查该日期是否存在汇率数据
                if event_date in df_rates['date'].values:
                    key_events.append({"date": event_date_str, "event": news['title']})
            except ValueError:
                pass # 日期格式不正确，跳过

    return key_events
