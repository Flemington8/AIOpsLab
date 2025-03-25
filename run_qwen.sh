#!/bin/bash

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create log directory if it doesn't exist
mkdir -p log

nohup poetry run python3 clients/qwen.py --use_wandb > log/qwen_output_${TIMESTAMP}.log 2>&1 &

# Print a message indicating that client Qwen is running.
echo "client Qwen has been launched in the background. Check qwen_output_${TIMESTAMP}.log for output."