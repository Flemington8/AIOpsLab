#!/bin/bash

nohup poetry run python3 clients/deepseek.py --use_wandb > log/deepseek_output.log 2>&1 &

echo "client DeepSeek has been launched in the background. Check deepseek_output.log for output."