#!/bin/bash
# This script launches vLLM in the background, redirecting output to a log file.

# Set the model directory/path and desired port
MODEL="Qwen/Qwen2.5-1.5B-Instruct"

# Launch vLLM in background using nohup and redirect both stdout and stderr to a log file.
nohup poetry run vllm serve "$MODEL" > log/vllm.log 2>&1 &

# Print a message indicating that vLLM is running.
echo "vLLM has been launched in the background with the $MODEL model. Check vllm.log for output."
