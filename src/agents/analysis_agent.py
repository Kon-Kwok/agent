from src.utils.analysis_utils import perform_volatility_analysis, extract_news_keywords, correlate_events

def analysis_agent(data):
    """
    阶段2：分析Agent。
    对收集到的汇率数据和新闻摘要进行波动分析、关键词提取和事件关联。
    """
    print("分析Agent接收到数据...")
    exchange_rates = data["exchange_rates"]
    processed_news = data["processed_news"]

    volatility_metrics = perform_volatility_analysis(exchange_rates)
    print(f"完成波动分析: {volatility_metrics}")

    high_frequency_keywords = None
    key_events = None

    if processed_news and 'detailed_news_analysis' in processed_news:
        # 提取LLM处理后的新闻详细分析部分，用于关键词提取和事件关联
        news_for_analysis = processed_news['detailed_news_analysis']
        high_frequency_keywords = extract_news_keywords(news_for_analysis)
        print(f"提取新闻关键词: {high_frequency_keywords}")

        key_events = correlate_events(exchange_rates, news_for_analysis)
        print(f"关联关键事件: {key_events}")
    else:
        print("没有LLM处理后的新闻数据或格式不正确，跳过关键词提取和事件关联。")

    # 生成分析.md文件 (可选，如果最终报告足够详细，可以省略此中间文件)
    # analysis_content = f"# 汇率分析报告\n\n## 波动指标\n{volatility_metrics}\n\n## 高频关键词\n{high_frequency_keywords}\n\n## 关键事件\n{key_events}\n"
    # with open("分析.md", "w", encoding="utf-8") as f:
    #     f.write(analysis_content)
    # print("生成分析.md文件")

    return {
        "exchange_rates": exchange_rates,
        "processed_news": processed_news, # 传递LLM处理后的新闻数据
        "volatility_metrics": volatility_metrics,
        "high_frequency_keywords": high_frequency_keywords,
        "key_events": key_events,
    }
