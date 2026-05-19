#!/bin/bash
set -e

echo "Python startup script starting..."
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"

echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Dependencies installed successfully"
echo "Starting the application with gunicorn..."
gunicorn --bind=0.0.0.0 --timeout 600 --workers 4 --access-logfile - --error-logfile - app:app
