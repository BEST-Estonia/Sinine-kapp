#!/bin/bash

set -e
# Navigate to the script's directory (e.g., /home/sinine-pi/smart_cabinet)
# This ensures it runs from the correct folder
cd "$(dirname "$0")"

# 1. Get the latest code from GitHub
echo "Pulling latest code from GitHub..."
git pull

# 2. Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# 3. Install/update any new requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# 4. Run the main application
echo "Starting smart cabinet application..."
python3 main.py
