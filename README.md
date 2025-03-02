# 💲AI Real Time Finance Agent Team

This project showcases the creation of an AI-powered financial analyst team using the ``Agno`` framework. It integrates web search and financial data analysis to generate in-depth and real time insights.

## Key Features  

- Multi-agent orchestration:  
    - ***Manager Agent***: Orchestrate the workflow
    - ***Web Agent***: Conducts online research
    - ***Finance Agent***: Fetch financial data on Yahoo Finance 
    - ***Visualization Agent***: Create charts for visualization
    - ***Frontend Agent***: Create the final web page
- Real-time financial data via YFinance
- Web search powered by DuckDuckGo
- Persistent interaction storage using SQLite

## Get Started

### 1. Clone the repository from GitHub
```bash
git clone https://github.com/zedems-01/ai-finance-agent-team.git
cd ai-finance-agent-team
```

### 2.Install pdm (Python Development Master)
```bash
pip install pdm
``` 

### 3. Create a virtual environment and install the required dependencies
```bash
python -m pdm venv create
.venv\Scripts\activate
python -m pdm insatll
```

### 4. Run the AI agent team
```bash
python app.py
```
