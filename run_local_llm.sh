#!/bin/bash

# # Set proxy environment variables
# export http_proxy="http://172.17.0.1:8118"
# export https_proxy="http://172.17.0.1:8118"
# export no_proxy=localhost

nohup poetry run python3 clients/local_llm.py --use_wandb > /dev/null 2>&1 &

echo "client Local LLM has been launched in the background."