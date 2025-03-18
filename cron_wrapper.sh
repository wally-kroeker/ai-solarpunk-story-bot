#!/bin/bash
# This script is automatically generated to run AI Future from cron
# It sets up the proper environment before running the main script

# Set working directory
cd /home/wally/ai-solarpunk-story-bot

# Set the PATH to include user's path where uv is available
export PATH=/home/wally/.local/bin:/home/wally/.cursor-server/cli/servers/Stable-ae378be9dc2f5f1a6a1a220c6e25f9f03c8d4e10/server/bin/remote-cli:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin

# Set the UV_HTTP_TIMEOUT environment variable
export UV_HTTP_TIMEOUT=300

# Run the actual command
/home/wally/ai-solarpunk-story-bot/ai_future.sh generate random random > /home/wally/ai-solarpunk-story-bot/logs/cron_$(date +%Y%m%d_%H%M%S).log 2>&1
