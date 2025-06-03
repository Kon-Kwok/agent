import matplotlib.pyplot as plt
import pandas as pd
import os
from src.utils.llm_utils import call_gemini_llm
from matplotlib.font_manager import FontProperties

# 配置Matplotlib使用英文字体
plt.rcParams['font.family'] = 'DejaVu Sans' # 使用默认的英文字体
plt.rcParams['axes.unicode_minus'] = False # 解决负号显示问题

def generate_report_outline(exchange_rates, volatility_metrics, key_events, high_frequency_keywords, news_summary, key_insights, sentiment_analysis):
    """
    使用LLM生成报告大纲。
    """
    print("使用LLM生成报告大纲...")
    prompt = f"""请根据以下分析数据，生成一份详细的汇率分析报告大纲。大纲应包含以下部分：
1.  引言 (Introduction)
2.  数据概览 (Data Overview)
3.  波动性分析 (Volatility Analysis) - 包含波动指标：{volatility_metrics}
4.  新闻分析 (News Analysis)
    a.  新闻整体总结: {news_summary if news_summary else '无'}
    b.  关键信息: {key_insights if key_insights else '无'}
    c.  情绪分析: {sentiment_analysis if sentiment_analysis else '无'}
    d.  高频关键词: {high_frequency_keywords if high_frequency_keywords else '无'}
5.  关键事件回顾与影响 (Key Events Review and Impact) - 包含事件：{key_events}
6.  结论与展望 (Conclusion and Outlook)

请以Markdown格式输出大纲。
"""
    outline = call_gemini_llm(prompt, model_name="gemini-1.5-flash", temperature=0.5)
    return outline if outline else "## 报告大纲生成失败。\n"

def generate_exchange_rate_chart(exchange_rates, key_events):
    """
    生成带事件标记的汇率走势图。
    """
    print("生成汇率走势图...")
    if not exchange_rates:
        print("没有汇率数据可供生成图表。")
        return ""

    df = pd.DataFrame(exchange_rates)
    df['date'] = pd.to_datetime(df['date'])
    df['rate'] = pd.to_numeric(df['rate'], errors='coerce')
    df.dropna(subset=['rate'], inplace=True)
    df = df.sort_values(by='date')

    if df.empty:
        print("数据清洗后没有有效汇率数据可供生成图表。")
        return ""

    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['rate'], label='Exchange Rate', color='blue')

    # 标记关键事件
    for event in key_events:
        event_date = pd.to_datetime(event['date'])
        if event_date in df['date'].values:
            # 找到对应日期的汇率值
            rate_at_event = df[df['date'] == event_date]['rate'].iloc[0]
            plt.scatter(event_date, rate_at_event, color='red', s=100, zorder=5, label=f"事件: {event['event']}")
            plt.annotate(event['event'], (event_date, rate_at_event),
                         textcoords="offset points", xytext=(0,10), ha='center', fontsize=9, color='red')

    plt.title('Exchange Rate Trend and Key Events')
    plt.xlabel('Date')
    plt.ylabel('Exchange Rate')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # 确保data目录存在
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    chart_path = os.path.join(output_dir, "exchange_rate_chart.png")
    plt.savefig(chart_path)
    plt.close() # 关闭图表，释放内存
    print(f"汇率走势图已保存到: {chart_path}")
    return chart_path

def generate_conclusion_summary(volatility_metrics, key_events, high_frequency_keywords, news_summary, sentiment_analysis):
    """
    使用LLM生成核心结论摘要。
    """
    print("使用LLM生成核心结论摘要...")
    prompt = f"""根据以下分析结果，撰写一份关于汇率走势的核心结论摘要。
波动指标：{volatility_metrics}
关键事件：{key_events}
高频关键词：{high_frequency_keywords}
新闻整体总结：{news_summary if news_summary else '无'}
新闻情绪分析：{sentiment_analysis if sentiment_analysis else '无'}

请总结汇率的主要趋势、波动性特征，以及关键事件和相关主题对汇率的影响。同时结合新闻的整体总结和情绪分析，提供更全面的结论。
"""
    summary = call_gemini_llm(prompt, model_name="gemini-1.5-flash", temperature=0.7)
    return summary if summary else "核心结论摘要生成失败。\n"
