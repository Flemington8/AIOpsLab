#!/bin/bash

nohup poetry run python3 clients/qwen.py --use_wandb > log/qwen_output.log 2>&1 &

# Print a message indicating that client Qwen is running.
echo "client Qwen has been launched in the background. Check qwen_output.log for output."