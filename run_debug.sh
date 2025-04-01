#!/bin/bash

# Enable Python debug output
export PYTHONUNBUFFERED=1
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run the application with debug output and pipe to log.txt
python3 -v pokemon_quiz.py 2>&1 | tee log.txt

# Check if the application crashed
if [ $? -ne 0 ]; then
    echo "Application crashed! Check log.txt for details."
    echo "Last 50 lines of debug output:"
    tail -n 50 log.txt
fi 