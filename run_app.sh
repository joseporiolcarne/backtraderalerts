#!/bin/bash

# Backtrader Alerts System - Startup Script
echo "🚀 Starting Backtrader Alerts System..."
echo "========================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Check if Streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found in virtual environment!"
    echo "Please run: pip install streamlit plotly pandas"
    exit 1
fi

# Start the application
echo "🌐 Starting Streamlit application..."
echo "📱 Access the app at: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the application"
echo ""

streamlit run src/gui/streamlit_app.py \
    --server.headless true \
    --browser.gatherUsageStats false \
    --server.runOnSave true \
    --theme.base dark