import pytest
from unittest.mock import patch, MagicMock

# Adjust the import path based on your project structure and how pytest discovers modules
from src.ai_finance_agent_team.app import generate_report, main as streamlit_main
from src.ai_finance_agent_team.tools import ManagerResponse
from datetime import datetime

@pytest.fixture
def mock_st():
    """Mocks streamlit UI components used in generate_report."""
    with patch('src.ai_finance_agent_team.app.st') as mock_streamlit:
        # Mock st.progress to return an object that has a progress method
        mock_progress_bar = MagicMock()
        mock_streamlit.progress.return_value = mock_progress_bar
        
        # Mock st.empty to return an object that has a text method
        mock_status_text = MagicMock()
        mock_streamlit.empty.return_value = mock_status_text
        
        # Mock st.error for error testing later
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

    # Prepare the mock response from manager_agent.run()
    mock_manager_response_content = ManagerResponse(complete_page_html_code=expected_html)
    mock_manager_agent_result = MagicMock()
    mock_manager_agent_result.content = mock_manager_response_content

    with patch('src.ai_finance_agent_team.app.manager_agent.run', return_value=mock_manager_agent_result) as mock_run_manager:
        actual_html = generate_report(companies, period)

        # Assertions for manager_agent call
        expected_query = f"I want an analysis of the companies {companies} stocks over the last {period} months."
        mock_run_manager.assert_called_once_with(expected_query)

        # Assertions for the returned HTML
        assert actual_html == expected_html

        # Assertions for Streamlit UI calls (optional, but good for coverage)
        mock_st.progress.assert_called_once_with(0)
        mock_st.empty.assert_called_once()
        
        # Check calls to the progress bar's 'progress' method
        mock_st.progress.return_value.progress.assert_any_call(10)
        mock_st.progress.return_value.progress.assert_any_call(90)
        mock_st.progress.return_value.progress.assert_any_call(100)

        # Check calls to the status text's 'text' method
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

        # Assertions for manager_agent call
        expected_query = f"I want an analysis of the companies {companies} stocks over the last {period} months."
        mock_run_manager.assert_called_once_with(expected_query)

        # Assert that the error message is in the output
        expected_error_html = f"<p>Error generating report: {error_message}</p>"
        assert actual_html_output == expected_error_html

        # Assert that st.error was called
        mock_st.error.assert_called_once_with(f"An error occurred: {error_message}")
        
        # Assertions for Streamlit UI calls during error
        mock_st.progress.return_value.progress.assert_called_with(100) # Should be set to 100 in except block
        mock_st.empty.return_value.text.assert_called_with(f"Error generating report: {error_message}") 

@pytest.fixture
def mock_st_for_main_function():
    """Mocks streamlit UI components used in the main() function of app.py."""
    # Path to streamlit in app.py is 'src.ai_finance_agent_team.app.st'
    # Path to components in app.py is 'src.ai_finance_agent_team.app.components'
    with patch('src.ai_finance_agent_team.app.st') as mock_st_instance, \
         patch('src.ai_finance_agent_team.app.components') as mock_components_instance, \
         patch('src.ai_finance_agent_team.app.generate_report') as mock_generate_report: # Also mock generate_report

        # Mock basic UI elements (called unconditionally)
        mock_st_instance.set_page_config = MagicMock()
        mock_st_instance.title = MagicMock()
        mock_st_instance.markdown = MagicMock()
        mock_st_instance.subheader = MagicMock()

        # Mock form elements
        mock_st_instance.form = MagicMock()
        # Make st.form usable as a context manager
        mock_form_context_manager = MagicMock()
        mock_st_instance.form.return_value = mock_form_context_manager
        mock_form_context_manager.__enter__.return_value = None # Or some mock object if needed
        mock_form_context_manager.__exit__.return_value = None

        mock_st_instance.text_input = MagicMock(return_value="Apple, Microsoft") # Default mocked input
        mock_st_instance.selectbox = MagicMock(return_value=3) # Default mocked period
        mock_st_instance.form_submit_button = MagicMock(return_value=False) # Default: button not clicked

        # Mock output elements
        mock_st_instance.error = MagicMock()
        mock_components_instance.html = MagicMock()
        mock_st_instance.download_button = MagicMock()

        # Mock generate_report (which is imported in app.py)
        mock_generate_report.return_value = "<p>Mocked HTML Report</p>"

        yield mock_st_instance, mock_components_instance, mock_generate_report

def test_main_app_form_submission_success(mock_st_for_main_function):
    """
    Tests the main app flow when the form is submitted with valid data.
    """
    mock_st, mock_components, mock_generate_report_func = mock_st_for_main_function

    # Simulate form submission: button is clicked
    mock_st.form_submit_button.return_value = True
    # Simulate user input for this test
    test_companies = "Tesla,Nvidia"
    test_period = 6
    mock_st.text_input.return_value = test_companies
    mock_st.selectbox.return_value = test_period

    # Expected HTML from the mocked generate_report
    expected_report_html = "<p>Report for Tesla,Nvidia</p>"
    mock_generate_report_func.return_value = expected_report_html

    streamlit_main() # Run the main function of the app

    # Assertions
    mock_st.set_page_config.assert_called_once()
    mock_st.title.assert_called_once_with("AI Finance Agent Team 💰")
    mock_st.form.assert_called_once_with("analysis_form")
    mock_st.text_input.assert_called_once_with(
        "Companies", 
        help="Enter company names separated by commas (e.g., 'Apple, Microsoft, Tesla')"
    )
    mock_st.selectbox.assert_called_once_with("Period", [1, 3, 6, 12, 24], index=1) # Default index for 3 months
    mock_st.form_submit_button.assert_called_once_with("Generate Report")

    # Check that generate_report was called with the correct (simulated) user inputs
    mock_generate_report_func.assert_called_once_with(test_companies, test_period)

    # Check that the report HTML is displayed
    mock_components.html.assert_called_once_with(expected_report_html, height=800, scrolling=True)

    # Check that the download button is displayed
    # We need to be careful about the timestamp in the filename
    # We can use mock_calls to inspect arguments or use ANY from unittest.mock
    assert mock_st.download_button.call_count == 1
    download_button_args = mock_st.download_button.call_args[1] # Get kwargs
    assert download_button_args['label'] == "Download HTML Report"
    assert download_button_args['data'] == expected_report_html
    assert download_button_args['mime'] == "text/html"
    assert download_button_args['file_name'].startswith("financial_report_")
    assert download_button_args['file_name'].endswith(".html")

    mock_st.error.assert_not_called() # Ensure no error was shown

def test_main_app_form_submission_no_companies(mock_st_for_main_function):
    """
    Tests the main app flow when form is submitted but no companies are entered.
    """
    mock_st, mock_components, mock_generate_report_func = mock_st_for_main_function

    # Simulate form submission: button is clicked
    mock_st.form_submit_button.return_value = True
    # Simulate empty company input
    mock_st.text_input.return_value = ""
    # Period can be anything, doesn't matter for this test path
    mock_st.selectbox.return_value = 1 

    streamlit_main() # Run the main function of the app

    # Assertions
    mock_st.text_input.assert_called_once()
    mock_st.form_submit_button.assert_called_once()

    # Check that st.error was called because companies input is empty
    mock_st.error.assert_called_once_with("Please enter at least one company name.")

    # Ensure report generation and display were NOT called
    mock_generate_report_func.assert_not_called()
    mock_components.html.assert_not_called()
    mock_st.download_button.assert_not_called()

def test_main_app_form_not_submitted(mock_st_for_main_function):
    """
    Tests the main app flow when the form is NOT submitted.
    """
    mock_st, mock_components, mock_generate_report_func = mock_st_for_main_function

    # Simulate form NOT submitted (default mock_st.form_submit_button.return_value is False)
    # mock_st.form_submit_button.return_value = False # Explicitly for clarity

    streamlit_main() # Run the main function of the app

    # Assert basic UI elements are called
    mock_st.set_page_config.assert_called_once()
    mock_st.title.assert_called_once()
    mock_st.form.assert_called_once()
    mock_st.text_input.assert_called_once()
    mock_st.selectbox.assert_called_once()
    mock_st.form_submit_button.assert_called_once()

    # Ensure these are NOT called if form isn't submitted
    mock_generate_report_func.assert_not_called()
    mock_components.html.assert_not_called()
    mock_st.download_button.assert_not_called()
    mock_st.error.assert_not_called() 