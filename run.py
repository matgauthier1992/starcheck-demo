import os
import subprocess
import sys

# Always start in project folder
project_dir = r"C:\Users\matga\OneDrive\StarCheck"
os.chdir(project_dir)

# Run streamlit app
subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
