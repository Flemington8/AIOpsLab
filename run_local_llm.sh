#!/bin/bash

nohup poetry run python3 clients/local_llm.py --use_wandb > log/local_llm_output.log 2>&1 &

echo "client Local LLM has been launched in the background. Check local_llm_output.log for output."