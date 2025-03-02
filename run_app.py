"""
Simple script to run the application from this directory
"""

import os
import subprocess
from pathlib import Path

def main():
    # Get the directory where the app.py file is located
    app_path = Path(__file__).parent / "src" / "ai_finance_agent_team" / "app.py"
    
    # Run the Streamlit app
    subprocess.run(["streamlit", "run", str(app_path)])

if __name__ == "__main__":
    main() 