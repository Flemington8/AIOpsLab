#!/bin/bash

# Start sslocal in the background
nohup sslocal -c /etc/shadowsocks.json > sslocal.log 2>&1 &

# Check if the command was successful
echo "Shadowsocks local client started, check sslocal.log for output."
