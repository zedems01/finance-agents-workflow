import pytest
from unittest.mock import patch, MagicMock

from src.ai_finance_agent_team.agent_team import web_agent, finance_agent, dataviz_agent, frontend_agent, manager_agent
from src.ai_finance_agent_team.tools import (
    NewsResponse, NewsList, News,
    FinancialDataResponse, FinancialDataList, DayFinancialData, StockMetric,
    FrontEndResponse,
    ManagerResponse
)

# Since agents are instantiated globally in agent_team.py,
# we will patch their model's generation method directly.
# We also need to consider the SqliteAgentStorage. For isolated tests,
# it's best if this doesn't write to a shared DB. We might need to
# patch SqliteAgentStorage or ensure agno handles test environments.
# For now, let's focus on mocking the LLM interaction.

def test_web_agent_success():
    """
    Tests that the web_agent can process a mocked LLM response
    and return the expected NewsResponse.
    """
    mock_news_item = News(
        title="Test News Title",
        summary="This is a test news summary.",
        source="http://testnews.com",
        analysis="This news will positively impact TestCorp stock."
    )
    mock_news_list = NewsList(company_name="TestCorp", news=[mock_news_item])
    expected_response = NewsResponse(company_news=[mock_news_list])

    with patch.object(web_agent.model, 'chat') as mock_model_chat:
        # agent.run() often returns a response object,
        # and the actual Pydantic model is in `response.content`.
        mock_llm_response = MagicMock()
        mock_llm_response.content = expected_response
        mock_model_chat.return_value = mock_llm_response

        user_query = "Get news for TestCorp"
        actual_response_object = web_agent.run(user_query)

        mock_model_chat.assert_called_once()
        
        assert actual_response_object is not None
        assert actual_response_object.content == expected_response
        assert isinstance(actual_response_object.content, NewsResponse)
        assert actual_response_object.content.company_news[0].company_name == "TestCorp"
        assert actual_response_object.content.company_news[0].news[0].title == "Test News Title"

def test_finance_agent_success():
    """
    Tests that the finance_agent can process a mocked LLM response
    and return the expected FinancialDataResponse.
    """
    mock_stock_metric = StockMetric(Close=150.75)
    mock_day_data = DayFinancialData(date="2023-01-01T00:00:00Z", metrics=mock_stock_metric)
    mock_financial_data_list = FinancialDataList(
        company_name="TestCorp",
        financial_data=[mock_day_data]
    )
    expected_response = FinancialDataResponse(companies_financial_data=[mock_financial_data_list])

    with patch.object(finance_agent.model, 'chat') as mock_model_chat:
        mock_llm_response = MagicMock()
        mock_llm_response.content = expected_response
        mock_model_chat.return_value = mock_llm_response

        user_query = "Get financial data for TestCorp for 1 month"
        actual_response_object = finance_agent.run(user_query)

        mock_model_chat.assert_called_once()
        assert actual_response_object is not None
        assert actual_response_object.content == expected_response
        assert isinstance(actual_response_object.content, FinancialDataResponse)
        assert actual_response_object.content.companies_financial_data[0].company_name == "TestCorp"
        assert actual_response_object.content.companies_financial_data[0].financial_data[0].metrics.Close == 150.75

def test_frontend_agent_success():
    """
    Tests that the frontend_agent can process a mocked LLM response
    and return the expected FrontEndResponse.
    """
    mock_html_content = "<h1>Test Report</h1><p>Details...</p><img src='test_plot.png'>"
    expected_response = FrontEndResponse(html_code=mock_html_content)

    with patch.object(frontend_agent.model, 'chat') as mock_model_chat:
        mock_llm_response = MagicMock()
        mock_llm_response.content = expected_response
        mock_model_chat.return_value = mock_llm_response

        user_query = "Create HTML page with given data"
        actual_response_object = frontend_agent.run(user_query)

        mock_model_chat.assert_called_once()
        assert actual_response_object is not None
        assert actual_response_object.content == expected_response
        assert isinstance(actual_response_object.content, FrontEndResponse)
        assert actual_response_object.content.html_code == mock_html_content

def test_manager_agent_orchestration():
    """
    Tests the manager_agent's orchestration capabilities.
    It mocks the .run() method of each worker agent and the .chat() method of the manager's own model.
    """
    mock_news_item = News(title="MngTest News", summary="S", source="U", analysis="A")
    mock_news_list = NewsList(company_name="MngTestCorp", news=[mock_news_item])
    worker_news_response_content = NewsResponse(company_news=[mock_news_list])

    mock_stock_metric = StockMetric(Close=100.0)
    mock_day_data = DayFinancialData(date="2023-02-01T00:00:00Z", metrics=mock_stock_metric)
    mock_financial_data_list = FinancialDataList(company_name="MngTestCorp", financial_data=[mock_day_data])
    worker_financial_response_content = FinancialDataResponse(companies_financial_data=[mock_financial_data_list])

    final_html_content = "<h1>Managed Report</h1><p>News and data.</p>"
    worker_frontend_response_content = FrontEndResponse(html_code=final_html_content)
    
    # This is what the manager_agent's own LLM is expected to produce as its final structured output content.
    expected_manager_final_response_content = ManagerResponse(complete_page_html_code=final_html_content)

    with patch.object(web_agent, 'run', return_value=MagicMock(content=worker_news_response_content)) as mock_web_run,\
         patch.object(finance_agent, 'run', return_value=MagicMock(content=worker_financial_response_content)) as mock_finance_run,\
         patch.object(frontend_agent, 'run', return_value=MagicMock(content=worker_frontend_response_content)) as mock_frontend_run,\
         patch.object(manager_agent.model, 'chat') as mock_manager_model_chat:

        mock_manager_llm_call_output = MagicMock()
        mock_manager_llm_call_output.content = expected_manager_final_response_content
        mock_manager_model_chat.return_value = mock_manager_llm_call_output

        user_query = "Generate a full report for MngTestCorp for 3 months"
        actual_manager_response_object = manager_agent.run(user_query)

        mock_manager_model_chat.assert_called_once()
        
        mock_web_run.assert_called_once()
        mock_finance_run.assert_called_once()
        mock_frontend_run.assert_called_once()

        assert actual_manager_response_object is not None
        assert actual_manager_response_object.content == expected_manager_final_response_content
        assert isinstance(actual_manager_response_object.content, ManagerResponse)
        assert actual_manager_response_object.content.complete_page_html_code == final_html_content
