#!/bin/bash

echo "========================================"
echo "  Starting Arkhe AI Bot"
echo "========================================"
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo

# Check if dependencies are installed
echo "Checking dependencies..."
if ! pip show aiogram > /dev/null 2>&1; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please create .env file from .env.example"
    echo
    exit 1
fi

# Start the bot
echo "Starting bot..."
echo
python bot.py
