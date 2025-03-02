import os
import subprocess

def main():
    # Get the directory of the current file and change to the directory containing the app.py file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    
    # Run the Streamlit app
    subprocess.run(["streamlit", "run", "app.py"])

if __name__ == "__main__":
    main() 