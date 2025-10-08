#!/bin/bash

# Script to run the FastAPI application
# Navigate to the project root directory
cd "$(dirname "$0")/.." || exit 1

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null; then
    echo "Error: uvicorn is not installed."
    echo "Please install it with: pip install uvicorn"
    exit 1
fi

# Run the FastAPI application with uvicorn
echo "Starting FastAPI application..."
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8080
