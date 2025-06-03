# agent_rate.py
import yfinance as yf
import pandas as pd
import numpy as np
from serpapi.google_search import GoogleSearch # 导入 serpapi 库的 GoogleSearch
from langgraph.graph import Graph
from pandasai import Agent
from pandasai.llm.openai import OpenAI

# 阶段1：数据收集Agent
def data_collection_agent(user_query):
    print(f"数据收集Agent接收到查询: {user_query}")
    # 1、解析用户请求
    currency_pair = parse_user_query(user_query)
    print(f"解析用户请求，货币对: {currency_pair}")

    # 2、获取汇率数据
    exchange_rates = get_exchange_rates(currency_pair, "2019-01-01", "2024-12-31") # 示例时间范围
    print(f"获取汇率数据，数据量: {len(exchange_rates) if exchange_rates else 0}")

    # 3、获取新闻摘要
    news_summaries = get_news_summaries(currency_pair, "2019-01-01", "2024-12-31") # 示例时间范围
    print(f"获取新闻摘要，新闻量: {len(news_summaries) if news_summaries else 0}")

    return {"exchange_rates": exchange_rates, "news_summaries": news_summaries}

def parse_user_query(user_query):
    # 实际实现中需要更复杂的自然语言处理来解析用户请求
    # 这里简化为直接返回一个货币对
    if "中美汇率" in user_query:
        return "USD/CNY"
    return "USD/CNY" # 默认值

def get_exchange_rates(currency_pair, start_date, end_date):
    print(f"调用yfinance获取 {currency_pair} 从 {start_date} 到 {end_date} 的汇率数据...")
    try:
        # yfinance 获取汇率数据
        # 对于汇率，yfinance 通常使用 'CURRENCY_PAIR=X' 的形式，例如 'CNY=X' 表示美元兑人民币
        # 或者直接使用 'USDCNY=X'，但通常是 'CNY=X' 表示 USD/CNY
        # 这里假设 currency_pair 是 'USD/CNY'，对应 yfinance 的 'CNY=X'
        if currency_pair == "USD/CNY":
            ticker = "CNY=X" # 示例：美元兑人民币
        else:
            print(f"暂不支持 {currency_pair} 的yfinance数据获取。")
            return []

        data = yf.download(ticker, start=start_date, end=end_date)
        if not data.empty:
            # yfinance 返回的 'Close' 列是收盘价，日期是索引
            exchange_rates = data[['Close']].reset_index().rename(columns={'Date': 'date', 'Close': 'rate'}).to_dict(orient='records')
            return exchange_rates
        else:
            print(f"yfinance未能获取到 {currency_pair} 的数据。")
            return []
    except Exception as e:
        print(f"yfinance数据获取失败: {e}")
        return []

def get_news_summaries(currency_pair, start_date, end_date):
    print(f"从数据源获取 {currency_pair} 从 {start_date} 到 {end_date} 的新闻摘要...")
    try:
        # 使用 SerpApi 进行新闻抓取
        # 需要设置 SERPER_API_KEY 环境变量
        # serper_api_key = os.environ.get("SERPER_API_KEY=1f8bcb604ceea0d919e85f47cf09ec2a60065430")
        # if not serper_api_key:
        #     raise ValueError("SERPER_API_KEY 环境变量未设置")

        params = {
            "q": f"{currency_pair} 汇率新闻 {start_date} 到 {end_date}",
            "tbm": "nws", # 搜索新闻
            "api_key": "YOUR_SERPER_API_KEY_HERE" # 替换为实际的 API Key 或从环境变量获取
        }
        search = GoogleSearch(params)
        news_results = search.get_dict()

        if 'news_results' in news_results and news_results['news_results']:
            return [item['snippet'] for item in news_results['news_results']]
        else:
            return []
    except Exception as e:
        print(f"SerpApi 新闻抓取失败: {e}")
        return [] # 模拟数据作为回退

# 阶段2：分析Agent
def analysis_agent(data):
    print("分析Agent接收到数据...")
    exchange_rates = data["exchange_rates"]
    news_summaries = data["news_summaries"]

    # 1、基础波动分析
    volatility_metrics = perform_volatility_analysis(exchange_rates)
    print(f"完成波动分析: {volatility_metrics}")

    # 2、新闻关键词提取
    high_frequency_keywords = extract_news_keywords(news_summaries)
    print(f"提取新闻关键词: {high_frequency_keywords}")

    # 3、简单事件关联
    key_events = correlate_events(exchange_rates, news_summaries)
    print(f"关联关键事件: {key_events}")

    # 生成分析.md文件
    analysis_content = f"# 汇率分析报告\n\n## 波动指标\n{volatility_metrics}\n\n## 高频关键词\n{high_frequency_keywords}\n\n## 关键事件\n{key_events}\n"
    with open("分析.md", "w", encoding="utf-8") as f:
        f.write(analysis_content)
    print("生成分析.md文件")

    return {
        "exchange_rates": exchange_rates, # 添加 exchange_rates
        "news_summaries": news_summaries, # 添加 news_summaries
        "volatility_metrics": volatility_metrics,
        "high_frequency_keywords": high_frequency_keywords,
        "key_events": key_events,
        "analysis_file": "分析.md"
    }



def perform_volatility_analysis(exchange_rates):
    print("调用PandasAI进行波动分析...")
    if not exchange_rates:
        print("没有汇率数据可供分析。")
        return {"average_volatility": 0.0, "max_fluctuation": 0.0}

    df = pd.DataFrame(exchange_rates)
    df['rate'] = pd.to_numeric(df['rate'], errors='coerce')
    df.dropna(subset=['rate'], inplace=True)

    if df.empty:
        print("数据清洗后没有有效汇率数据可供分析。")
        return {"average_volatility": 0.0, "max_fluctuation": 0.0}

    # 初始化 PandasAI，可以使用 DeepSeek API 作为 LLM 后端
    llm = OpenAI(api_token="YOUR_OPENAI_API_KEY") # 替换为您的 OpenAI API Key
     # 请确保已设置 OPENAI_API_KEY 环境变量，或者直接在此处提供您的 API 密钥
    # pandas_ai = Agent(llm)

    # 暂时使用默认的 LLM 或不指定 LLM，如果用户没有提供 DeepSeek API Key
    pandas_ai = PandasAI(llm=None) # 或者使用默认的 LLM，如果已配置

    try:
        # 计算日波动率
        df['daily_change'] = df['rate'].diff().abs()
        average_volatility = pandas_ai.run(df, "计算 daily_change 的平均值")
        max_fluctuation = pandas_ai.run(df, "计算 daily_change 的最大值")

        return {"average_volatility": average_volatility, "max_fluctuation": max_fluctuation}
    except Exception as e:
        print(f"PandasAI 分析失败: {e}")
        return {"average_volatility": 0.0, "max_fluctuation": 0.0} # 失败时返回模拟数据

def extract_news_keywords(news_summaries):
    # 提取新闻关键词，这里是模拟数据
    print("提取新闻关键词...")
    # 实际应使用NLP库进行关键词提取
    return ["特朗普", "关税", "贸易战", "汇率政策"]

def correlate_events(exchange_rates, news_summaries):
    # 关联汇率数据和新闻事件，这里是模拟数据
    print("关联汇率数据和新闻事件...")
    # 实际应实现事件检测和关联逻辑
    return [{"date": "2019-01-01", "event": "中美贸易谈判开始"}]

# 阶段3：报告生成Agent
def report_generation_agent(analysis_data):
    print("报告生成Agent接收到分析数据...")
    # 1、报告结构Agent
    report_outline = generate_report_outline(analysis_data)
    print(f"生成报告大纲: {report_outline}")

    # 2、可视化Agent
    chart_path = generate_exchange_rate_chart(analysis_data["exchange_rates"], analysis_data["key_events"])
    print(f"生成汇率走势图: {chart_path}")

    # 3、自然语言生成Agent
    conclusion_summary = generate_conclusion_summary(analysis_data["volatility_metrics"], analysis_data["key_events"])
    print(f"生成核心结论摘要: {conclusion_summary}")

    # 最终报告内容
    final_report_content = f"# 汇率分析最终报告\n\n{report_outline}\n\n## 汇率走势图\n![汇率走势图]({chart_path})\n\n## 核心结论\n{conclusion_summary}\n"
    with open("报告.md", "w", encoding="utf-8") as f:
        f.write(final_report_content)
    print("生成报告.md文件")

    return {"final_report_path": "报告.md"}

def generate_report_outline(analysis_data):
    # 生成报告大纲，这里是模拟数据
    print("生成报告大纲...")
    return "## 1. 数据概览\n## 2. 波动分析\n## 3. 关键事件回顾\n## 4. 结论与展望\n"

def generate_exchange_rate_chart(exchange_rates, key_events):
    # 生成带事件标记的汇率走势图，这里是模拟文件路径
    print("生成汇率走势图...")
    # 实际应使用matplotlib, seaborn等库生成图表并保存
    return "exchange_rate_chart.png" # 假设生成了图片

def generate_conclusion_summary(volatility_metrics, key_events):
    # 生成3句话的核心结论摘要，这里是模拟文本
    print("生成核心结论摘要...")
    return "根据分析，汇率在特定时期波动较大。关键事件对汇率产生了显著影响。未来汇率走势需密切关注国际贸易政策变化。"

# 构建LangGraph工作流
workflow = Graph()

workflow.add_node("data_collection", data_collection_agent)
workflow.add_node("analysis", analysis_agent)
workflow.add_node("report_generation", report_generation_agent)

workflow.set_entry_point("data_collection")
workflow.add_edge("data_collection", "analysis")
workflow.add_edge("analysis", "report_generation")
workflow.set_finish_point("report_generation")

app = workflow.compile()

if __name__ == "__main__":
    # 示例运行
    user_query = "2019年1月1日至2024年12月31日特朗普上台加征关税后，对中美汇率的影响"
    result = app.invoke(user_query)
    print("\n--- 最终结果 --- ")
    print(result)