#!/bin/bash

nohup poetry run python3 clients/qwen.py --use_wandb > /dev/null 2>&1 &

# Print a message indicating that client Qwen is running.
echo "client Qwen has been launched in the background."