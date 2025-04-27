#!/bin/bash

# Find the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the script directory before running the server
cd "$SCRIPT_DIR"

# Create the output directory if it doesn't exist
if command -v python3 &> /dev/null; then
    python3 -c "
import os, pathlib
output_dir = pathlib.Path('${SCRIPT_DIR}').parent / 'debate-agent' / 'output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f'Created output directory: {output_dir}')
    "
elif command -v python &> /dev/null; then
    python -c "
import os, pathlib
output_dir = pathlib.Path('${SCRIPT_DIR}').parent / 'debate-agent' / 'output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f'Created output directory: {output_dir}')
    "
fi

# Check if Python 3 is installed
if command -v python3 &> /dev/null; then
    echo "Starting AI Debate Viewer server..."
    python3 server.py
elif command -v python &> /dev/null; then
    echo "Starting AI Debate Viewer server with 'python' command..."
    python server.py
else
    echo "Error: Python 3 not found. Please install Python 3 to run this application."
    exit 1
fi
