import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import json
from datetime import datetime

# Make sure to adjust the import path if your project structure is different
# or if PDM/pytest has a specific way of discovering modules.
# Assuming 'src' is a top-level directory recognized by Python's import system
# or pytest is configured to find it.
from src.ai_finance_agent_team.tools import get_historical_prices, FinancialDataResponse, FinancialDataList, DayFinancialData, StockMetric

@pytest.fixture
def mock_stock_data():
    """Provides a sample pandas DataFrame similar to yfinance history."""
    data = {
        'Open': [150.0, 151.0],
        'High': [152.0, 152.5],
        'Low': [149.0, 150.5],
        'Close': [151.5, 152.0],
        'Volume': [1000000, 1200000]
    }
    # yfinance uses Timestamps as index
    index = [
        pd.Timestamp('2023-01-01T00:00:00.000Z'),
        pd.Timestamp('2023-01-08T00:00:00.000Z') # Assuming weekly interval for 6mo
    ]
    return pd.DataFrame(data, index=index)

def test_get_historical_prices_success(mock_stock_data):
    """
    Tests get_historical_prices for a successful data retrieval.
    Mocks yfinance.Ticker and its history method.
    """
    mock_ticker_instance = MagicMock()
    mock_ticker_instance.history.return_value = mock_stock_data

    # The patch should target where 'yf.Ticker' is looked up,
    # which is within the 'src.ai_finance_agent_team.tools' module.
    with patch('src.ai_finance_agent_team.tools.yf.Ticker', return_value=mock_ticker_instance) as mock_yf_ticker:
        symbol = "AAPL"
        period = 6 # Corresponds to "6mo"

        result_json = get_historical_prices(symbol, period)
        result_data = json.loads(result_json)

        # Assertions
        mock_yf_ticker.assert_called_once_with(symbol)
        mock_ticker_instance.history.assert_called_once_with(period="6mo", interval="1wk")

        # Check if the structure of the JSON matches the mocked data
        expected_dates = [ts.isoformat() + "Z" for ts in mock_stock_data.index]
        
        # Convert keys in result_data (which are string timestamps) to pd.Timestamp for comparison if needed,
        # or compare string forms. yfinance returns integer timestamps in ms.
        # The to_json(orient="index", date_format="iso") will produce ISO 8601 strings.
        
        assert list(result_data.keys()) == [str(dt.value // 10**6) for dt in mock_stock_data.index] # yfinance default index format in to_json

        # Check one entry
        first_timestamp_key_ms = str(mock_stock_data.index[0].value // 10**6)

        # Reconstruct expected JSON based on mock_stock_data and how to_json(orient="index") works
        # yfinance.to_json(orient="index") uses millisecond epoch timestamps as keys
        expected_json_dict = {}
        for timestamp, row in mock_stock_data.iterrows():
            # Convert pandas Timestamp to milliseconds since epoch, as string keys
            epoch_ms = str(timestamp.value // 10**6)
            expected_json_dict[epoch_ms] = row.to_dict()
        
        expected_json_str = json.dumps(expected_json_dict)
        # We need to parse our result_json again to compare dicts, as order might differ in string
        assert json.loads(result_json) == expected_json_dict

        # More specific check for values if necessary
        assert result_data[first_timestamp_key_ms]['Close'] == mock_stock_data['Close'].iloc[0]
        assert result_data[first_timestamp_key_ms]['Open'] == mock_stock_data['Open'].iloc[0]

def test_get_historical_prices_yfinance_error():
    """
    Tests get_historical_prices when yfinance.Ticker().history() raises an exception.
    """
    mock_ticker_instance = MagicMock()
    mock_ticker_instance.history.side_effect = Exception("Test yfinance error")

    with patch('src.ai_finance_agent_team.tools.yf.Ticker', return_value=mock_ticker_instance) as mock_yf_ticker:
        symbol = "FAIL"
        period = 1

        with pytest.raises(ValueError, match=f"Error fetching historical data for {symbol}: Test yfinance error"):
            get_historical_prices(symbol, period)
        
        mock_yf_ticker.assert_called_once_with(symbol)
        mock_ticker_instance.history.assert_called_once_with(period="1mo", interval="1d")

def test_get_historical_prices_invalid_period():
    """
    Tests get_historical_prices with an invalid period value.
    This should ideally raise a KeyError due to the period_mapping.
    """
    symbol = "MSFT"
    invalid_period = 99 # Not in period_mapping

    with pytest.raises(KeyError): # Expecting KeyError from period_mapping[invalid_period]
        get_historical_prices(symbol, invalid_period)

# --- Pydantic Model Unit Tests ---

def test_stock_metric_valid():
    metric = StockMetric(Close=123.45)
    assert metric.Close == 123.45

def test_stock_metric_invalid():
    with pytest.raises(ValueError): # Pydantic raises ValueError for validation errors
        StockMetric(Close="not-a-float")

def test_day_financial_data_valid():
    metric = StockMetric(Close=150.0)
    data = DayFinancialData(date="2023-01-01", metrics=metric)
    assert data.date == "2023-01-01"
    assert data.metrics.Close == 150.0

def test_financial_data_list_valid():
    metric1 = StockMetric(Close=100.0)
    day_data1 = DayFinancialData(date="2023-01-01", metrics=metric1)
    metric2 = StockMetric(Close=102.0)
    day_data2 = DayFinancialData(date="2023-01-02", metrics=metric2)
    
    fdl = FinancialDataList(
        company_name="TestCorp",
        financial_data=[day_data1, day_data2]
    )
    assert fdl.company_name == "TestCorp"
    assert len(fdl.financial_data) == 2
    assert fdl.financial_data[0].metrics.Close == 100.0

def test_financial_data_response_valid():
    metric = StockMetric(Close=200.0)
    day_data = DayFinancialData(date="2023-01-01", metrics=metric)
    fdl = FinancialDataList(company_name="CompA", financial_data=[day_data])
    
    response = FinancialDataResponse(companies_financial_data=[fdl])
    assert len(response.companies_financial_data) == 1
    assert response.companies_financial_data[0].company_name == "CompA"

# Example for News and NewsResponse (can be expanded)
def test_news_valid():
    news_item = News(
        title="Big News!",
        summary="Something important happened.",
        source="http://example.com",
        analysis="Stock will go up."
    )
    assert news_item.title == "Big News!"

def test_news_list_valid():
    news_item = News(title="T1", summary="S1", source="U1", analysis="A1")
    news_list = NewsList(company_name="TestCo", news=[news_item])
    assert news_list.company_name == "TestCo"
    assert len(news_list.news) == 1

def test_news_response_valid():
    news_item = News(title="T1", summary="S1", source="U1", analysis="A1")
    news_list = NewsList(company_name="TestCo", news=[news_item])
    news_response = NewsResponse(company_news=[news_list])
    assert len(news_response.company_news) == 1
    assert news_response.company_news[0].company_name == "TestCo"

# ChartDataResponse, FrontEndResponse, ManagerResponse are simpler structures
def test_chart_data_response_valid():
    response = ChartDataResponse(image_name="plot.png")
    assert response.image_name == "plot.png"

def test_front_end_response_valid():
    response = FrontEndResponse(html_code="<h1>Hello</h1>")
    assert response.html_code == "<h1>Hello</h1>"

def test_manager_response_valid():
    response = ManagerResponse(complete_page_html_code="<html>...</html>")
    assert response.complete_page_html_code == "<html>...</html>" 