from langchain.tools import BaseTool
from typing import Optional, Type, Literal
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import json
import os
import re
from langchain.agents import create_react_agent
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.tools import Tool
from langchain_community.utilities import SerpAPIWrapper

# 设置API密钥
os.environ['DeepSeek_API_Key'] = 'sk-59e9eee380844860bf1470b4085b2d2e'
os.environ['SERPAPI_API_KEY'] = '84f9a13c965073ff2f641239ef94ed58e2aef757014016c07b98cb5d51e9e3ef'

class ExchangeRateTool(BaseTool):
    name: str = "exchange_rate_data"
    description: str = """
    这是一个用于获取不同国家之间汇率历史数据的工具。
    
    输入格式要求:
    需要一个JSON字符串,包含以下字段:
    - start_date: 开始日期,格式为YYYY-MM-DD
    - end_date: 结束日期,格式为YYYY-MM-DD  
    - from_currency: 源货币代码(如USD)
    - to_currency: 目标货币代码(如CNY)
    
    示例:
    {
        "start_date": "2022-01-01",
        "end_date": "2024-01-01",
        "from_currency": "USD", 
        "to_currency": "CNY"
    }
    
    注意: 在使用此工具之前，请先使用 exchange_rate_search 工具获取准确的时间范围。
    """

    def _run(self, query: str) -> str:
        """执行汇率数据查询"""
        try:
            # 解析输入的JSON
            query = query.strip()
            if query.startswith('```json'):
                query = query[7:]
            if query.endswith('```'):
                query = query[:-3]
                
            params = json.loads(query)
            start_date = params["start_date"]
            end_date = params["end_date"] 
            from_currency = params["from_currency"]
            to_currency = params["to_currency"]

            # 构建货币对符号
            symbol = f"{from_currency}{to_currency}=X"
            print(f"构建查询符号: {symbol}\n")
            
            # 获取数据
            print("正在从Yahoo Finance获取数据...")
            exchange_rate = yf.Ticker(symbol)
            df = exchange_rate.history(start=start_date, end=end_date, interval='1d')

            if df.empty:
                return "未找到符合条件的汇率数据"

            # 处理数据
            print("正在处理数据...")
            df = df.reset_index()
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
            
            for col in ['Open', 'High', 'Low', 'Close']:
                df[col] = df[col].round(4)

            # 保存数据
            print("正在保存数据...")
            output_dir = 'data'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            filename = f'{from_currency}_{to_currency}_{start_date}_to_{end_date}.csv'
            filepath = os.path.join(output_dir, filename)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            print(f"数据已保存到: {filepath}")
            return f"已成功获取{from_currency}/{to_currency}从{start_date}到{end_date}的汇率数据,并保存到{filepath}"

        except json.JSONDecodeError as e:
            error_msg = f"JSON解析错误: {str(e)}"
            print(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"获取数据时发生错误: {str(e)}"
            print(error_msg)
            return error_msg

    async def _arun(self, query: str) -> str:
        """异步运行方法"""
        return self._run(query)

class ExchangeRateSearch(BaseTool):
    name: Literal["exchange_rate_search"] = "exchange_rate_search"
    description: str = """
    用于搜索特定历史时期的事件起止时间。
    当用户询问特定时期(如金融危机、奥运会等)的事件时，必须首先使用此工具。
    输入应该是对事件的描述,例如"2008年金融危机"。
    此工具会通过搜索引擎查询该历史事件的具体起止时间，并返回一段话，告诉大模型起止时间是多少。
    """
    llm: ChatOpenAI # 添加 LLM 属性

    def _run(self, query: str) -> str:
        search = SerpAPIWrapper()
        search_query = f"{query} 开始时间 结束时间 具体日期"
        print(f"正在搜索: {search_query}")
        results = search.run(search_query)
        print(f"搜索结果: {results}")
        
        try:
            if not results:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)
                dates = {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d")
                }
            else:
                # 使用 LLM 提取日期
                dates = self._extract_dates_from_search(query, results)
            
            # 验证日期的合理性
            if datetime.strptime(dates['end_date'], '%Y-%m-%d') < datetime.strptime(dates['start_date'], '%Y-%m-%d'):
                dates['start_date'], dates['end_date'] = dates['end_date'], dates['start_date']
            
            return f"事件 '{query}' 的起止时间是从 {dates['start_date']} 到 {dates['end_date']}。"
        except Exception as e:
            return f"搜索解析错误: {str(e)}"

    def _extract_dates_from_search(self, query: str, search_results: str) -> dict:
        """使用 LLM 从搜索结果中提取日期信息"""
        prompt = f"""
        请阅读以下搜索结果，并从中提取与事件 "{query}" 最相关的开始日期和结束日期。
        搜索结果:
        {search_results}

        请以 JSON 格式返回结果，包含 "start_date" 和 "end_date" 字段，日期格式为 YYYY-MM-DD。
        如果无法确定精确日期，请根据搜索结果推断一个合理的日期范围。
        示例输出:
        {{
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
        }}
        """
        print("正在使用 LLM 提取日期...")
        llm_response = self.llm.invoke(prompt)
        print(f"LLM 响应: {llm_response}")

        try:
            # 移除 markdown 代码块标记
            json_string = llm_response.content.strip()
            if json_string.startswith('```json'):
                json_string = json_string[7:]
            if json_string.endswith('```'):
                json_string = json_string[:-3]
            json_string = json_string.strip() # 再次去除可能的空白字符

            # 尝试解析 LLM 的 JSON 输出
            dates = json.loads(json_string)
            if "start_date" in dates and "end_date" in dates:
                 # 验证日期格式
                datetime.strptime(dates['start_date'], '%Y-%m-%d')
                datetime.strptime(dates['end_date'], '%Y-%m-%d')
                return dates
            else:
                raise ValueError("LLM 返回的 JSON 格式不正确")
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"从 LLM 响应中提取日期失败: {str(e)}")

    async def _arun(self, query: str) -> str:
        return self._run(query)

class DollarIndexTool(BaseTool):
    """获取美元指数数据的工具"""
    name: str = "dollar_index_data"
    description: str = """
    获取指定时间范围内的美元指数(DXY)数据。
    输入格式为包含start_date和end_date的字典。
    日期格式为: YYYY-MM-DD
    """
    
    def _run(self, dates: str) -> str:
        try:
            # 将输入的字符串解析为字典
            if isinstance(dates, str):
                dates = json.loads(dates)
                
            dxy = yf.download("DX-Y.NYB", 
                            start=dates['start_date'],
                            end=dates['end_date'])
            
            if dxy.empty:
                return "在指定时间范围内未找到美元指数数据"
            
            # 处理数据
            print("正在处理数据...")
            dxy = dxy.reset_index()
            dxy['Date'] = dxy['Date'].dt.strftime('%Y-%m-%d')
            
            for col in ['Open', 'High', 'Low', 'Close']:
                dxy[col] = dxy[col].round(4)
                
            # 保存数据
            print("正在保存数据...")
            output_dir = 'data'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            filename = f'DXY_{dates["start_date"]}_to_{dates["end_date"]}.csv'
            filepath = os.path.join(output_dir, filename)
            dxy.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            print(f"数据已保存到: {filepath}")
            
            start_price = dxy['Close'].iloc[0]
            end_price = dxy['Close'].iloc[-1]
            highest = dxy['High'].max()
            lowest = dxy['Low'].min()
            change = ((end_price - start_price) / start_price) * 100
            
            return (f"美元指数从 {dates['start_date']} 到 {dates['end_date']} 的数据已保存到{filepath}\n"
                   f"起始价格: {start_price:.2f}\n"
                   f"结束价格: {end_price:.2f}\n"
                   f"最高价: {highest:.2f}\n"
                   f"最低价: {lowest:.2f}\n"
                   f"涨跌幅: {change:.2f}%")
                   
        except json.JSONDecodeError:
            return "输入格式错误: 请提供正确的JSON格式字符串"
        except Exception as e:
            return f"获取美元指数数据时发生错误: {str(e)}"
            
    async def _arun(self, dates: str) -> str:
        return self._run(dates)

if __name__ == "__main__":
    llm = ChatOpenAI(
        model_name="deepseek-chat",
        base_url="https://api.deepseek.com/v1",
        api_key=os.getenv("DeepSeek_API_Key"),
    )

    tools = [ExchangeRateTool(), ExchangeRateSearch(llm=llm), DollarIndexTool()] # 传入 LLM 实例
    
    prompt = hub.pull("hwchase17/react")
    print(prompt)
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True # 添加这一行
    )
    
    try:
        user_query = input("请输入您想查询的汇率数据: ")
        print("\n开始处理查询...")
        response = agent_executor.invoke(
            {"input": user_query}
        )
        print("\n查询结果:")
        print(response["output"])
    except Exception as e:
        print(f"执行查询时发生错误: {str(e)}")
