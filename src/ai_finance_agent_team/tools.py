from pydantic import BaseModel, Field
from typing import List, Dict

import yfinance as yf



# Define the pydantic models for the data we want to get from the LLM model

class News(BaseModel):
    "Schema for an extracted news from the web"
    title: str = Field(description="The title of the news")
    summary: str = Field(description="A summary of the news in maximum 3 sentences")
    source: str = Field(description="The url source of the news")
    analysis: str = Field(description="An analysis of the impact of the news on the stock price")


class NewsList(BaseModel):
    "Schema for a list of news for a company"
    company_name: str = Field(description="The name of the company")
    news: List[News] = Field(description="A list of news for a company")


class NewsResponse(BaseModel):
    "Schema for the response of the web agent"
    company_news: List[NewsList] = Field(description="A list of news for each company")
    

class StockMetric(BaseModel):
    "Schema for the stock metric for a day, only getting the closing price"
    Close: float = Field(description="The closing price of the stock")


class DayFinancialData(BaseModel):
    "Schema for the stock metric for a day"
    date: str = Field(description="The date for the stock data")
    metrics: StockMetric = Field(description="Stock metric for the day")
    
class FinancialDataList(BaseModel):
    "Schema for the financial data for a company over a period"
    company_name: str = Field(description="The name of the company")
    financial_data: List[DayFinancialData] = Field(description="A list of financial data for a company over a period")


class FinancialDataResponse(BaseModel):
    "Schema for the response of the finance agent"
    companies_financial_data: List[FinancialDataList] = Field(description="A list of financial data for each company over a period")


class ChartDataResponse(BaseModel):
    "Schema for the response of the visualization agent"
    company_name: str = Field(description="The name of the company")
    period: str = Field(description="The period for which the chart data is for")
    html_code: str = Field(description="The html code for the chart")

# class ChartDataResponse(BaseModel):
#     "Schema for the response of the visualization agent"
#     # company_name: str = Field(description="The name of the company")
#     # period: str = Field(description="The period for which the chart data is for")
#     # python_code: str = Field(description="The Python code for the plot")
#     image_name: str = Field(description="The name of the plot image")


class FrontEndResponse(BaseModel):
    "Schema for the response of the front end agent"
    html_code: str = Field(description="The html code of the page")


class ManagerResponse(BaseModel):
    "Schema for the response of the manager agent"
    complete_page_html_code: str = Field(description="The complete html code of the page, including analysis, charts, and conclusion")



def get_historical_prices(symbol: str, period: int = 6):
    """
        Use this function to get the historical stock price for a given symbol.

        Args:
            symbol (str): The stock symbol.
            period (int): The period for which to retrieve historical prices. Defaults to 6.
                        Valid periods: 1,3,6,12,24 in months

        Returns:
          str: JSON formated string containing the historical prices of the company stock over the specified period
    """
    
    period_mapping = {
        1: "1mo",
        3: "3mo",
        6: "6mo",
        12: "1y",
        24: "2y"
    }
    interval_mapping = {
        "1mo": "1d",
        "3mo": "1wk",
        "6mo": "1wk",
        "1y": "1wk",
        "2y": "1mo",
    }
    period_str = period_mapping[period]
    interval = interval_mapping[period_str]

    try:
        stock = yf.Ticker(symbol)
        historical_price = stock.history(period=period_str, interval=interval)
        return historical_price.to_json(orient="index", date_format="iso")
    
    except Exception as e:
        raise ValueError(f"Error fetching historical data for {symbol}: {e}")
