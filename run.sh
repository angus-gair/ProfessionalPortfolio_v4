#!/bin/bash

# Load environment variables
if [ -f .env ]; then
  export $(cat .env | sed 's/#.*//g' | xargs)
fi

# Activate virtual environment
source venv/bin/activate

# Run Flask application
python app.py 