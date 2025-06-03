import yfinance as yf
import pandas as pd

def get_exchange_rates_yfinance(currency_pair, start_date, end_date):
    """
    调用yfinance获取汇率数据。
    """
    print(f"调用yfinance获取 {currency_pair} 从 {start_date} 到 {end_date} 的汇率数据...")
    try:
        if currency_pair == "USD/CNY":
            ticker = "CNY=X"
        else:
            print(f"暂不支持 {currency_pair} 的yfinance数据获取。")
            return []

        data = yf.download(ticker, start=start_date, end=end_date)
        print(f"YFinance 返回的原始数据列: {data.columns.tolist()}")
        print(f"YFinance 返回的原始数据前5行:\n{data.head()}")
        if not data.empty:
            close_column_name = ('Close', ticker) if isinstance(data.columns, pd.MultiIndex) else 'Close'
            
            close_prices = data[close_column_name]
            df_temp = close_prices.reset_index()
            df_temp.columns = ['date', 'rate']
            exchange_rates = df_temp.to_dict(orient='records')
            print(f"转换后的汇率数据前5项: {exchange_rates[:5]}")
            return exchange_rates
        else:
            print(f"yfinance未能获取到 {currency_pair} 的数据。")
            return []
    except Exception as e:
        print(f"yfinance数据获取失败: {e}")
        return []
