def parse_user_query(user_query):
    """
    解析用户请求，提取货币对。
    实际实现中需要更复杂的自然语言处理来解析用户请求。
    """
    if "中美汇率" in user_query:
        return "USD/CNY"
    return "USD/CNY" # 默认值
