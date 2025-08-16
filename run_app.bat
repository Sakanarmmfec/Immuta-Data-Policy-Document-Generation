@echo off
echo Starting Immuta x MFEC Helper Web UI...
streamlit run Home.py --server.port 8501 --server.address localhost
pause