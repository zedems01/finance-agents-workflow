import pytest
from unittest.mock import patch, MagicMock

# Assuming 'src' is configured in PYTHONPATH or discovered by pytest
from src.ai_finance_agent_team.agent_team import web_agent, finance_agent, dataviz_agent, frontend_agent, manager_agent
from src.ai_finance_agent_team.tools import (
    NewsResponse, NewsList, News,
    FinancialDataResponse, FinancialDataList, DayFinancialData, StockMetric,
    ChartDataResponse,
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
    # 1. Prepare a mock NewsResponse that the LLM (mocked) will return
    mock_news_item = News(
        title="Test News Title",
        summary="This is a test news summary.",
        source="http://testnews.com",
        analysis="This news will positively impact TestCorp stock."
    )
    mock_news_list = NewsList(company_name="TestCorp", news=[mock_news_item])
    expected_response = NewsResponse(company_news=[mock_news_list])

    # 2. Mock the method on the agent's model that generates the response.
    #    The exact method might depend on 'agno's OpenAIChat wrapper.
    #    Common names could be 'run', 'invoke', 'chat', 'generate_structured_output', etc.
    #    Let's assume 'web_agent.model.run' or a similar method is called by 'web_agent.run()'.
    #    If 'web_agent.model' is an OpenAIChat instance, it might have a 'chat' or 'invoke' method.
    #    Since 'web_agent' itself has a 'run' method, we're mocking one level deeper.
    #    Let's try to mock 'web_agent.model.chat' as a starting point.
    #    The 'Agent.run' method from 'agno' likely calls a method on its 'self.model'.
    
    # We need to find what 'web_agent.model.chat' (or equivalent) returns.
    # The Agent class likely uses a method that returns a Pydantic object directly
    # when structured_outputs=True.
    # Let's assume 'web_agent.model.generate_structured_output' for now,
    # or if not, we can mock the 'run' method of the model and make it return
    # an object that has a 'content' attribute which is our Pydantic model.
    
    # Simpler: The Agent class's 'run' method itself might return an object
    # which has a 'content' attribute that is the Pydantic model.
    # Let's assume the agent's model will be called and its response will be wrapped.

    with patch.object(web_agent.model, 'chat') as mock_model_chat:
        # The 'chat' method of OpenAIChat in agno might return a response object
        # that the Agent class then processes to extract the Pydantic model.
        # Let's assume the mocked 'chat' method needs to return an object
        # that, when its '.content' is accessed, gives our Pydantic model.
        # Or, if the agent's .run() directly returns the pydantic model or an
        # object whose .content is the pydantic model.
        
        # Based on `agno` examples, agent.run() often returns a response object,
        # and the actual Pydantic model is in `response.content`.
        mock_llm_response = MagicMock()
        mock_llm_response.content = expected_response # The Pydantic model
        mock_model_chat.return_value = mock_llm_response

        # 3. Run the agent
        user_query = "Get news for TestCorp"
        actual_response_object = web_agent.run(user_query)

        # 4. Assertions
        mock_model_chat.assert_called_once() # Check if the LLM was called
        
        # Check that the content of the response is our expected Pydantic model
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
    # 1. Prepare mock FinancialDataResponse
    mock_stock_metric = StockMetric(Close=150.75)
    mock_day_data = DayFinancialData(date="2023-01-01T00:00:00Z", metrics=mock_stock_metric)
    mock_financial_data_list = FinancialDataList(
        company_name="TestCorp",
        financial_data=[mock_day_data]
    )
    expected_response = FinancialDataResponse(companies_financial_data=[mock_financial_data_list])

    # 2. Mock the finance_agent.model.chat method
    with patch.object(finance_agent.model, 'chat') as mock_model_chat:
        mock_llm_response = MagicMock()
        mock_llm_response.content = expected_response
        mock_model_chat.return_value = mock_llm_response

        # 3. Run the agent
        user_query = "Get financial data for TestCorp for 1 month"
        actual_response_object = finance_agent.run(user_query)

        # 4. Assertions
        mock_model_chat.assert_called_once()
        assert actual_response_object is not None
        assert actual_response_object.content == expected_response
        assert isinstance(actual_response_object.content, FinancialDataResponse)
        assert actual_response_object.content.companies_financial_data[0].company_name == "TestCorp"
        assert actual_response_object.content.companies_financial_data[0].financial_data[0].metrics.Close == 150.75


def test_dataviz_agent_success():
    """
    Tests that the dataviz_agent can process a mocked LLM response
    and return the expected ChartDataResponse.
    Recall: agent_team.py dataviz_agent gets instructions to make HTML chart,
    but its response_model is ChartDataResponse(image_name: str).
    So, the LLM is expected to return a JSON like {"image_name": "plot.png"}.
    """
    # 1. Prepare mock ChartDataResponse
    expected_response = ChartDataResponse(image_name="test_plot.png")

    # 2. Mock the dataviz_agent.model.chat method
    with patch.object(dataviz_agent.model, 'chat') as mock_model_chat:
        mock_llm_response = MagicMock()
        mock_llm_response.content = expected_response
        mock_model_chat.return_value = mock_llm_response

        # 3. Run the agent (it would typically receive data as input from manager)
        # For this direct test, the input query might be less critical as we mock the direct LLM output.
        user_query = "Create a chart for TestCorp data"
        actual_response_object = dataviz_agent.run(user_query)

        # 4. Assertions
        mock_model_chat.assert_called_once()
        assert actual_response_object is not None
        assert actual_response_object.content == expected_response
        assert isinstance(actual_response_object.content, ChartDataResponse)
        assert actual_response_object.content.image_name == "test_plot.png"


def test_frontend_agent_success():
    """
    Tests that the frontend_agent can process a mocked LLM response
    and return the expected FrontEndResponse.
    """
    # 1. Prepare mock FrontEndResponse
    mock_html_content = "<h1>Test Report</h1><p>Details...</p><img src='test_plot.png'>"
    expected_response = FrontEndResponse(html_code=mock_html_content)

    # 2. Mock the frontend_agent.model.chat method
    with patch.object(frontend_agent.model, 'chat') as mock_model_chat:
        mock_llm_response = MagicMock()
        mock_llm_response.content = expected_response
        mock_model_chat.return_value = mock_llm_response

        # 3. Run the agent
        user_query = "Create HTML page with given data"
        actual_response_object = frontend_agent.run(user_query)

        # 4. Assertions
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
    # 1. Define mock responses for each worker agent's .run() method's content
    mock_news_item = News(title="MngTest News", summary="S", source="U", analysis="A")
    mock_news_list = NewsList(company_name="MngTestCorp", news=[mock_news_item])
    worker_news_response_content = NewsResponse(company_news=[mock_news_list])

    mock_stock_metric = StockMetric(Close=100.0)
    mock_day_data = DayFinancialData(date="2023-02-01T00:00:00Z", metrics=mock_stock_metric)
    mock_financial_data_list = FinancialDataList(company_name="MngTestCorp", financial_data=[mock_day_data])
    worker_financial_response_content = FinancialDataResponse(companies_financial_data=[mock_financial_data_list])

    worker_chart_response_content = ChartDataResponse(image_name="mng_test_plot.png")
    
    final_html_content = "<h1>Managed Report</h1><p>News, data, and chart.</p><img src='mng_test_plot.png'>"
    worker_frontend_response_content = FrontEndResponse(html_code=final_html_content)
    
    # This is what the manager_agent's own LLM is expected to produce as its final structured output content.
    expected_manager_final_response_content = ManagerResponse(complete_page_html_code=final_html_content)

    # 2. Patch the 'run' methods of worker agents and the 'chat' method of the manager's model
    with patch.object(web_agent, 'run', return_value=MagicMock(content=worker_news_response_content)) as mock_web_run,\
         patch.object(finance_agent, 'run', return_value=MagicMock(content=worker_financial_response_content)) as mock_finance_run,\
         patch.object(dataviz_agent, 'run', return_value=MagicMock(content=worker_chart_response_content)) as mock_dataviz_run,\
         patch.object(frontend_agent, 'run', return_value=MagicMock(content=worker_frontend_response_content)) as mock_frontend_run,\
         patch.object(manager_agent.model, 'chat') as mock_manager_model_chat:

        # Configure the mock for the manager_agent's own LLM call
        # Its LLM will be prompted and is expected to return an object whose .content is the ManagerResponse structure.
        mock_manager_llm_call_output = MagicMock()
        mock_manager_llm_call_output.content = expected_manager_final_response_content
        mock_manager_model_chat.return_value = mock_manager_llm_call_output

        # 3. Run the manager_agent
        user_query = "Generate a full report for MngTestCorp for 3 months"
        actual_manager_response_object = manager_agent.run(user_query)

        # 4. Assertions
        # Check that the manager's own LLM was invoked
        mock_manager_model_chat.assert_called_once()
        
        # Check that the worker agents' run methods were called
        mock_web_run.assert_called_once()
        mock_finance_run.assert_called_once()
        mock_dataviz_run.assert_called_once()
        mock_frontend_run.assert_called_once()

        # Check the final output from the manager_agent
        assert actual_manager_response_object is not None
        assert actual_manager_response_object.content == expected_manager_final_response_content
        assert isinstance(actual_manager_response_object.content, ManagerResponse)
        assert actual_manager_response_object.content.complete_page_html_code == final_html_content
