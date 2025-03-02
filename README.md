# 💲AI Real Time Finance Agent Team

This project showcases the creation of an AI-powered financial analyst team using the ``Agno`` (formerly Phidata) framework. It integrates web search and financial data analysis to generate in-depth and real time insights.

## ⭐ Key Features  

- Multi-agent orchestration:  
    - ***Manager Agent*** 👨‍💼: orchestrates the entire workflow
    - ***Web Agent*** 🌐: searches for the latest news about the companies
    - ***Finance Agent*** 📊: fetches historical stock data from Yahoo Finance 
    - ***Visualization Agent*** 📈: creates charts for visualization
    - ***Frontend Agent*** 🎨: compiles all information into a comprehensive HTML report   

- Real-time financial data via YFinance
- Web search powered by DuckDuckGo
- Persistent interaction storage using SQLite
- User-friendly Streamlit interface


## 🚀 Get Started

### 1. Clone the repository from GitHub
```bash
>>  git clone https://github.com/zedems-01/ai-finance-agent-team.git
>>  cd ai-finance-agent-team
```

### 2.Install pdm (Python Development Master)
```bash
>>  pip install pdm
``` 

### 3. Create a virtual environment and install the required dependencies
```bash
>>  python -m pdm venv create
>>  .venv\Scripts\activate
>>  python -m pdm install
```

### 4. Run the AI Finance Agent Team Streamlit App
```bash
>> python run_app.py
```

### 5. Using the Streamlit Application

1. Enter company names (one or more) you want to analyze (e.g., Apple, Microsoft, Google)
2. Select an analysis period from the dropdown menu
3. Click "Generate Report" to start the analysis
4. Wait for the AI agents to process the data and generate the report ()
5. View the interactive report directly in the application
6. Download the HTML report for offline viewing or sharing

## 📝 License
Distributed under the MIT license. See `LICENSE` for more information.