#!/bin/bash

# SSH connection details
REMOTE_USER="root"
REMOTE_HOST="region-42.seetacloud.com"
REMOTE_PORT="49446"
LOCAL_PORT="8000"
REMOTE_FORWARD_PORT="8000"

# Establish the SSH port forwarding in the background
nohup ssh -N -L ${LOCAL_PORT}:localhost:${REMOTE_FORWARD_PORT} -p ${REMOTE_PORT} ${REMOTE_USER}@${REMOTE_HOST} > ssh_tunnel.log 2>&1 &

echo "SSH port forwarding is set up. Access the remote service at http://localhost:${LOCAL_PORT} on your local machine."
