#!/bin/bash

nohup poetry run python3 clients/gpt.py --use_wandb > /dev/null 2>&1 &

echo "client gpt has been launched in the background."