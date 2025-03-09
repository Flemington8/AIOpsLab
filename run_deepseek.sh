#!/bin/bash

nohup poetry run python3 clients/deepseek.py --use_wandb > deepseek_output.log 2>&1 &

