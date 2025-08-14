import os
from datetime import datetime
from typing import Annotated
from pathlib import Path

import yfinance
from pydantic import Field

import pandas as pd
from requests.exceptions import HTTPError, ReadTimeout
from yfinance import download, Ticker

from hiagent_plugin_sdk import BasePlugin, set_meta, BuiltinCategory

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))


@set_meta(cn_name="雅虎财经")
class YahooPlugin(BasePlugin):
    """雅虎财经"""
    hiagent_tools = ["analytics", "news", "ticker"]
    hiagent_category = BuiltinCategory.News

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    def analytics(
            self,
            symbol: Annotated[str, Field(description="股票代号")],
            start_date: Annotated[str, Field(description="开始日期, eg: 2019-01-01")],
            end_date: Annotated[str, Field(description="结束日期, eg: 2020-01-01")],
    ) -> str:
        """
        invoke tools
        """
        if symbol == '':
            return f"Please input symbol"

        time_range = [None, None]
        if start_date != '':
            time_range[0] = start_date
        else:
            time_range[0] = "1800-01-01"

        if end_date != '':
            time_range[1] = end_date
        else:
            time_range[1] = datetime.now().strftime("%Y-%m-%d")

        stock_data = download(symbol, start=time_range[0], end=time_range[1])
        max_segments = min(15, len(stock_data))
        rows_per_segment = len(stock_data) // (max_segments or 1)
        summary_data = []
        for i in range(max_segments):
            start_idx = i * rows_per_segment
            end_idx = (i + 1) * rows_per_segment if i < max_segments - 1 else len(stock_data)
            segment_data = stock_data.iloc[start_idx:end_idx]
            segment_summary = {
                "Start Date": segment_data.index[0],
                "End Date": segment_data.index[-1],
                "Average Close": segment_data["Close"].mean(),
                "Average Volume": segment_data["Volume"].mean(),
                "Average Open": segment_data["Open"].mean(),
                "Average High": segment_data["High"].mean(),
                "Average Low": segment_data["Low"].mean(),
                "Average Adj Close": segment_data["Adj Close"].mean(),
                "Max Close": segment_data["Close"].max(),
                "Min Close": segment_data["Close"].min(),
                "Max Volume": segment_data["Volume"].max(),
                "Min Volume": segment_data["Volume"].min(),
                "Max Open": segment_data["Open"].max(),
                "Min Open": segment_data["Open"].min(),
                "Max High": segment_data["High"].max(),
                "Min High": segment_data["High"].min(),
            }

            summary_data.append(segment_summary)

        summary_df = pd.DataFrame(summary_data)

        try:
            return str(summary_df.to_dict())
        except (HTTPError, ReadTimeout):
            return f"There is a internet connection problem. Please try again later."

    def news(
            self,
            symbol: Annotated[str, Field(description="股票代号")],
    ) -> str:
        """
        invoke tools
        """

        if symbol == '':
            return f"Please input symbol"

        try:
            return self.run_news(self, ticker=symbol)
        except (HTTPError, ReadTimeout):
            return f"There is a internet connection problem. Please try again later."

    # todo: 新闻需要获取链接里的内容，并解析，由于网页内容格式繁多，解析比较复杂，时间原因暂时跳过
    # @staticmethod
    # def get_url(link):
    #     headers = {
    #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    #         " Chrome/91.0.4472.124 Safari/537.36"
    #     }
    #     try:
    #         response = requests.get(link, headers=headers)
    #         response.raise_for_status()  # 检查请求是否成功
    #         return response.text  # 返回响应内容
    #     except requests.exceptions.HTTPError as http_err:
    #         return f"HTTP error occurred: {http_err} for URL: {link}"
    #     except requests.RequestException as e:
    #         return f"Error fetching {link}: {e}"

    @staticmethod
    def run_news(self, ticker: str) -> str:
        company = yfinance.Ticker(ticker)
        try:
            if company.isin is None:
                return f"Company ticker {ticker} not found."
        except (HTTPError, ReadTimeout, ConnectionError):
            return f"Company ticker {ticker} not found."

        links = []
        try:
            links = [n["link"] for n in company.news if n["type"] == "STORY"]
        except (HTTPError, ReadTimeout, ConnectionError):
            if not links:
                return f"There is nothing about {ticker} ticker"
        if not links:
            return f"No news found for company that searched with {ticker} ticker."

        result = "\n\n".join([link for link in links])
        return result

    def ticker(
            self,
            symbol: Annotated[str, Field(description="股票代号")],
    ) -> str:
        """
        invoke tools
        """

        if symbol == '':
            return f"Please input symbol"

        try:
            return self.ticker_run(ticker=symbol)
        except (HTTPError, ReadTimeout):
            return f"There is a internet connection problem. Please try again later."

    @staticmethod
    def ticker_run(ticker: str) -> str:
        return str(Ticker(ticker).info)
