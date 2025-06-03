from src.utils.report_utils import generate_report_outline, generate_exchange_rate_chart, generate_conclusion_summary

def report_generation_agent(analysis_data):
    """
    阶段3：报告生成Agent。
    根据分析数据生成报告大纲、汇率走势图和核心结论摘要，并最终生成报告文件。
    """
    print("报告生成Agent接收到分析数据...")
    
    exchange_rates = analysis_data.get("exchange_rates", [])
    processed_news = analysis_data.get("processed_news", {})
    volatility_metrics = analysis_data.get("volatility_metrics", {})
    key_events = analysis_data.get("key_events", [])
    high_frequency_keywords = analysis_data.get("high_frequency_keywords", [])

    # 生成报告大纲
    report_outline = generate_report_outline(
        exchange_rates,
        volatility_metrics,
        key_events,
        high_frequency_keywords,
        processed_news.get("summary"), # LLM生成的整体新闻总结
        processed_news.get("key_insights"), # LLM提取的关键信息
        processed_news.get("sentiment_analysis") # LLM分析的情绪
    )
    print(f"生成报告大纲: {report_outline[:100]}...") # 打印部分内容，避免过长

    # 生成汇率走势图
    chart_path = generate_exchange_rate_chart(exchange_rates, key_events)
    print(f"生成汇率走势图: {chart_path}")

    # 生成核心结论摘要
    conclusion_summary = generate_conclusion_summary(
        volatility_metrics, 
        key_events,
        high_frequency_keywords,
        processed_news.get("summary"), # LLM生成的整体新闻总结
        processed_news.get("sentiment_analysis") # LLM分析的情绪
    )
    print(f"生成核心结论摘要: {conclusion_summary[:100]}...") # 打印部分内容，避免过长

    final_report_content = f"# 汇率分析最终报告\n\n{report_outline}\n\n## 汇率走势图\n![汇率走势图]({chart_path})\n\n## 核心结论\n{conclusion_summary}\n"
    with open("报告.md", "w", encoding="utf-8") as f:
        f.write(final_report_content)
    print("生成报告.md文件")

    return {"final_report_path": "报告.md"}
