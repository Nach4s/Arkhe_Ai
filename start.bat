@echo off
echo ========================================
echo   Starting Arkhe AI Bot
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Check if dependencies are installed
echo Checking dependencies...
pip show aiogram >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please create .env file from .env.example
    echo.
    pause
    exit /b 1
)

REM Start the bot
echo Starting bot...
echo.
python bot.py

pause
