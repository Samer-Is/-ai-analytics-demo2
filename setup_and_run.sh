#!/bin/bash

echo "====================================="
echo "AI Data Analytics Tool - Setup"
echo "====================================="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH"
    echo "Please install Python 3.9+ and try again"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "[WARNING] .env file not found"
    echo "Creating template .env file..."
    echo "OPENAI_API_KEY=your_actual_api_key_here" > .env
    echo
    echo "Please edit .env file and add your OpenAI API key"
    echo "Then run this script again"
    exit 1
fi

echo "[1/4] Installing Python dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install Python packages"
    exit 1
fi

echo "[2/4] Creating output directory..."
mkdir -p output

echo "[3/4] Generating sample data..."
python3 scripts/generate_simple_data.py
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to generate sample data"
    exit 1
fi

echo "[4/4] Starting Streamlit application..."
echo
echo "====================================="
echo "Setup completed successfully!"
echo "Starting the application..."
echo "====================================="
echo
streamlit run app.py
