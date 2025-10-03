import os
import subprocess
import sys
import webbrowser
import time

# Go to your StarCheck folder
os.chdir(r"C:\Users\matga\OneDrive\StarCheck")

# Run Streamlit without showing a console window
process = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "app.py"],
    creationflags=subprocess.CREATE_NO_WINDOW
)

# Wait a moment, then open browser
time.sleep(2)
webbrowser.open("http://localhost:8501")
