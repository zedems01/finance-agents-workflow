import streamlit as st
from datetime import datetime
import streamlit.components.v1 as components

from agent_team import manager_agent

# Page configuration
st.set_page_config(
    page_title="AI Finance Agent Team",
    page_icon="💲",
    layout="wide",
)

def generate_report(companies, period):
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("Starting the analysis process...")
    progress_bar.progress(10)
    
    # Call the manager agent to orchestrate the entire process

    if period == 1:
        status_text.text(f"Analyzing companies: {companies} for the last month...")
    else:
        status_text.text(f"Analyzing companies: {companies} for the last {period} months...")
    
    try:
        user_query = f"I want an analysis of the companies {companies} stocks over the last {period} months."
        result = manager_agent.run(user_query)
        
        progress_bar.progress(90)

        status_text.text("Finalizing report...")
        html_content = result.content.complete_page_html_code
        
        # Update progress to completion
        progress_bar.progress(100)
        status_text.text("Report generated successfully!")
        
        return html_content
    
    except Exception as e:
        progress_bar.progress(100)
        status_text.text(f"Error generating report: {str(e)}")
        st.error(f"An error occurred: {str(e)}")
        return f"<p>Error generating report: {str(e)}</p>"

# Main function to run the Streamlit app
def main():
    st.title("AI Finance Agent Team 💲")
    
    st.markdown("""
    This application uses AI agents to analyze financial data and news for companies you're interested in.
    Enter company names and select an analysis period to generate a comprehensive report.
    """)
    
    # Create form
    with st.form("analysis_form"):
        st.subheader("Enter Companies to Get Stocks Analysis")
        companies_input = st.text_input(
            "Companies", 
            help="Enter company names separated by commas (e.g., 'Apple, Microsoft, Tesla')"
        )
        
        # Period selection
        st.subheader("Select Analysis Period (in months)")
        period_options = [1, 3, 6, 12, 24]
        period = st.selectbox("Period", period_options, index=period_options.index(3))
        
        submit_button = st.form_submit_button("Generate Report")
    
    # Process form submission
    if submit_button:
        companies = companies_input
        if not companies:
            st.error("Please enter at least one company name.")
        else:
            st.subheader("Financial Analysis Report")
            
            # Generate and display the report
            html_content = generate_report(companies, period)            
            components.html(html_content, height=800, scrolling=True)
            
            # Download button for the HTML report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"financial_report_{timestamp}.html"
            
            st.download_button(
                label="Download HTML Report",
                data=html_content,
                file_name=filename,
                mime="text/html"
            )

if __name__ == "__main__":
    main()
