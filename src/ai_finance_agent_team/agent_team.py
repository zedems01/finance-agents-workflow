from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.tools.duckduckgo import DuckDuckGoTools

from tools import *

from dotenv import load_dotenv

load_dotenv()


# Initialize the agents

web_agent = Agent(
    name="Web Agent",
    role="Search the web for information about companies",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
    instructions=[
                    "Search the latest news about the company provided",
                    "If there are more than one company, seach for at most 1 news for each one",
                    "Summarize the news, include sources urls",
                    "Give an analysis of the impact that the news could have on the stock price"
                ],
    storage=SqliteAgentStorage(table_name="web_agent", db_file="./storage/team_database.db"),
    structured_outputs=True,
    response_model=NewsResponse
)


finance_agent = Agent(
    name="Finance Agent",
    role="Get financial data",
    description="Get the historical prices of the companies provided",
    model=OpenAIChat(id="gpt-4o"),
    tools=[get_historical_prices],
    storage=SqliteAgentStorage(table_name="finance_agent", db_file="./storage/team_database.db"),
    structured_outputs=True,
    response_model=FinancialDataResponse
)


dataviz_agent = Agent(
    name="Data Visualization Agent",
    role="Create charts in html code",
    model=OpenAIChat(id="gpt-4o"),
    instructions=[
                    "You have to create a chart in html code from the data provided",
                    "Make sure the chart is well presented, readable and user friendly",
                    "You can use html, css and javascript to create a beautiful chart"
    ],
    storage=SqliteAgentStorage(table_name="dataviz_agent", db_file="./storage/team_database.db"),
    structured_outputs=True,
    response_model=ChartDataResponse
)


frontend_agent = Agent(
    name="Frontend Agent",
    role="Create html page to display the final page",
    model=OpenAIChat(id="gpt-4o"),
    instructions=[
                    "You will be provided information and you have to create a beautiful html page to present the report",
                    "Make sure the page is well presented, readable and user friendly",
                    "You can use html, css and javascript to create a beautiful page",
                ],
    storage=SqliteAgentStorage(table_name="front_end_agent", db_file="./storage/team_database.db"),
    structured_outputs=True,
    response_model=FrontEndResponse
)


manager_agent = Agent(
    team=[web_agent, finance_agent, dataviz_agent, frontend_agent],
    name="Manager Agent (Web + Finance + Data Visualization + Front End)",
    model=OpenAIChat(id="gpt-4o"),
    instructions=[
                    "You manage a team of agents that will work together to provide a report about companies stocks",
                    "First, use the web agent to get the latest news about the companies provided",
                    "Then, ask the Finance Agent for the history of the financial data for companies",
                    "Next, ask the Data Visualization Agent to create a chart in html code from the financial data you will get from the Finance Agent",
                    "Finally, provide the Front End Agent all the responses you got from the other agents to create a beautiful html page that will display a final report (You must include the chart).",
                ],
    storage=SqliteAgentStorage(table_name="manager_agent", db_file="./storage/team_database.db"),
    structured_outputs=True,
    response_model=ManagerResponse
)


