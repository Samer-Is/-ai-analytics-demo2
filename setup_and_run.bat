@echo off
echo =====================================
echo AI Data Analytics Tool - Setup
echo =====================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9+ and try again
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found
    echo Creating template .env file...
    echo OPENAI_API_KEY=your_actual_api_key_here > .env
    echo.
    echo Please edit .env file and add your OpenAI API key
    echo Then run this script again
    pause
    exit /b 1
)

echo [1/4] Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python packages
    pause
    exit /b 1
)

echo [2/4] Creating output directory...
if not exist "output" mkdir output

echo [3/4] Generating sample data...
python scripts/generate_simple_data.py
if %errorlevel% neq 0 (
    echo [ERROR] Failed to generate sample data
    pause
    exit /b 1
)

echo [4/4] Starting Streamlit application...
echo.
echo =====================================
echo Setup completed successfully!
echo Starting the application...
echo =====================================
echo.
streamlit run app.py
