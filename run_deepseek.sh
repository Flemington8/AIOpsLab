#!/bin/bash

nohup poetry run python3 clients/deepseek.py --use_wandb > /dev/null 2>&1 &

echo "client DeepSeek has been launched in the background."