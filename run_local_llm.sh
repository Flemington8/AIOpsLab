#!/bin/bash

nohup poetry run python3 clients/local_llm.py --use_wandb > /dev/null 2>&1 &

echo "client Local LLM has been launched in the background."