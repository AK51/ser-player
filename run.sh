#!/bin/bash

echo "Starting SER File Viewer..."
python3 main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to start application"
    echo ""
    echo "Make sure you have run setup.sh first"
    echo ""
fi
