import pytest
from unittest.mock import patch, MagicMock

from src.ai_finance_agent_team.app import generate_report, main as streamlit_main
from src.ai_finance_agent_team.tools import ManagerResponse
from datetime import datetime

@pytest.fixture
def mock_st():
    """Mocks streamlit UI components used in generate_report."""
    with patch('src.ai_finance_agent_team.app.st') as mock_streamlit:
        mock_progress_bar = MagicMock()
        mock_streamlit.progress.return_value = mock_progress_bar
        
        mock_status_text = MagicMock()
        mock_streamlit.empty.return_value = mock_status_text
        
        mock_streamlit.error = MagicMock()
        yield mock_streamlit

def test_generate_report_success(mock_st):
    """
    Tests the generate_report function for a successful scenario.
    Mocks manager_agent.run() and streamlit UI calls.
    """
    companies = "TestCorp, AnotherCorp"
    period = 3
    expected_html = "<h1>Generated Report for TestCorp, AnotherCorp</h1><p>Analysis complete.</p>"

    mock_manager_response_content = ManagerResponse(complete_page_html_code=expected_html)
    mock_manager_agent_result = MagicMock()
    mock_manager_agent_result.content = mock_manager_response_content

    with patch('src.ai_finance_agent_team.app.manager_agent.run', return_value=mock_manager_agent_result) as mock_run_manager:
        actual_html = generate_report(companies, period)

        expected_query = f"I want an analysis of the companies {companies} stocks over the last {period} months."
        mock_run_manager.assert_called_once_with(expected_query)

        assert actual_html == expected_html

        mock_st.progress.assert_called_once_with(0)
        mock_st.empty.assert_called_once()
        
        mock_st.progress.return_value.progress.assert_any_call(10)
        mock_st.progress.return_value.progress.assert_any_call(90)
        mock_st.progress.return_value.progress.assert_any_call(100)

        mock_st.empty.return_value.text.assert_any_call("Starting the analysis process...")
        mock_st.empty.return_value.text.assert_any_call(f"Analyzing companies: {companies} for the last {period} months...")
        mock_st.empty.return_value.text.assert_any_call("Finalizing report...")
        mock_st.empty.return_value.text.assert_any_call("Report generated successfully!")

def test_generate_report_error(mock_st):
    """
    Tests the generate_report function when manager_agent.run() raises an exception.
    """
    companies = "ErrorCorp"
    period = 1
    error_message = "Simulated agent error"

    with patch('src.ai_finance_agent_team.app.manager_agent.run', side_effect=Exception(error_message)) as mock_run_manager:
        actual_html_output = generate_report(companies, period)

        expected_query = f"I want an analysis of the companies {companies} stocks over the last {period} months."
        mock_run_manager.assert_called_once_with(expected_query)

        expected_error_html = f"<p>Error generating report: {error_message}</p>"
        assert actual_html_output == expected_error_html

        mock_st.error.assert_called_once_with(f"An error occurred: {error_message}")
        
        mock_st.progress.return_value.progress.assert_called_with(100) # Should be set to 100 in except block
        mock_st.empty.return_value.text.assert_called_with(f"Error generating report: {error_message}") 

@pytest.fixture
def mock_st_for_main_function():
    """Mocks streamlit UI components used in the main() function of app.py."""
    # Path to streamlit in app.py is 'src.ai_finance_agent_team.app.st'
    # Path to components in app.py is 'src.ai_finance_agent_team.app.components'
    with patch('src.ai_finance_agent_team.app.st') as mock_st_instance, \
         patch('src.ai_finance_agent_team.app.components') as mock_components_instance, \
         patch('src.ai_finance_agent_team.app.generate_report') as mock_generate_report:

        mock_st_instance.set_page_config = MagicMock()
        mock_st_instance.title = MagicMock()
        mock_st_instance.markdown = MagicMock()
        mock_st_instance.subheader = MagicMock()

        mock_st_instance.form = MagicMock()
        mock_form_context_manager = MagicMock()
        mock_st_instance.form.return_value = mock_form_context_manager
        mock_form_context_manager.__enter__.return_value = None
        mock_form_context_manager.__exit__.return_value = None

        mock_st_instance.text_input = MagicMock(return_value="Apple, Microsoft")
        mock_st_instance.selectbox = MagicMock(return_value=3)
        mock_st_instance.form_submit_button = MagicMock(return_value=False)

        mock_st_instance.error = MagicMock()
        mock_components_instance.html = MagicMock()
        mock_st_instance.download_button = MagicMock()

        mock_generate_report.return_value = "<p>Mocked HTML Report</p>"

        yield mock_st_instance, mock_components_instance, mock_generate_report

def test_main_app_form_submission_success(mock_st_for_main_function):
    """
    Tests the main app flow when the form is submitted with valid data.
    """
    mock_st, mock_components, mock_generate_report_func = mock_st_for_main_function

    mock_st.form_submit_button.return_value = True
    test_companies = "Tesla,Nvidia"
    test_period = 6
    mock_st.text_input.return_value = test_companies
    mock_st.selectbox.return_value = test_period

    expected_report_html = "<p>Report for Tesla,Nvidia</p>"
    mock_generate_report_func.return_value = expected_report_html

    streamlit_main()

    mock_st.set_page_config.assert_called_once()
    mock_st.title.assert_called_once_with("AI Finance Agent Team 💰")
    mock_st.form.assert_called_once_with("analysis_form")
    mock_st.text_input.assert_called_once_with(
        "Companies", 
        help="Enter company names separated by commas (e.g., 'Apple, Microsoft, Tesla')"
    )
    mock_st.selectbox.assert_called_once_with("Period", [1, 3, 6, 12, 24], index=1) # Default index for 3 months
    mock_st.form_submit_button.assert_called_once_with("Generate Report")

    mock_generate_report_func.assert_called_once_with(test_companies, test_period)

    mock_components.html.assert_called_once_with(expected_report_html, height=800, scrolling=True)

    assert mock_st.download_button.call_count == 1
    download_button_args = mock_st.download_button.call_args[1]
    assert download_button_args['label'] == "Download HTML Report"
    assert download_button_args['data'] == expected_report_html
    assert download_button_args['mime'] == "text/html"
    assert download_button_args['file_name'].startswith("financial_report_")
    assert download_button_args['file_name'].endswith(".html")

    mock_st.error.assert_not_called()

def test_main_app_form_submission_no_companies(mock_st_for_main_function):
    """
    Tests the main app flow when form is submitted but no companies are entered.
    """
    mock_st, mock_components, mock_generate_report_func = mock_st_for_main_function

    mock_st.form_submit_button.return_value = True
    mock_st.text_input.return_value = ""
    # Period can be anything, doesn't matter for this test path
    mock_st.selectbox.return_value = 1 

    streamlit_main()

    mock_st.text_input.assert_called_once()
    mock_st.form_submit_button.assert_called_once()

    mock_st.error.assert_called_once_with("Please enter at least one company name.")

    mock_generate_report_func.assert_not_called()
    mock_components.html.assert_not_called()
    mock_st.download_button.assert_not_called()

def test_main_app_form_not_submitted(mock_st_for_main_function):
    """
    Tests the main app flow when the form is NOT submitted.
    """
    mock_st, mock_components, mock_generate_report_func = mock_st_for_main_function

    streamlit_main()

    mock_st.set_page_config.assert_called_once()
    mock_st.title.assert_called_once()
    mock_st.form.assert_called_once()
    mock_st.text_input.assert_called_once()
    mock_st.selectbox.assert_called_once()
    mock_st.form_submit_button.assert_called_once()

    mock_generate_report_func.assert_not_called()
    mock_components.html.assert_not_called()
    mock_st.download_button.assert_not_called()
    mock_st.error.assert_not_called()