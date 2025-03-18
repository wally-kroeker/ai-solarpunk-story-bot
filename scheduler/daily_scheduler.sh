#!/bin/bash
# Scheduler script for AI Future - do not edit directly

# Record the start time
START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
SCRIPT_DIR="$(dirname "$(dirname "$0")")"
LOG_FILE="${SCRIPT_DIR}/logs/scheduler_$(date +%Y%m%d_%H%M%S).log"

# Redirect all output to the log file
exec > "$LOG_FILE" 2>&1

echo "========================================"
echo "AI Future Scheduler - Starting execution"
echo "Started at: $START_TIME"
echo "Working directory: $SCRIPT_DIR"
echo "========================================"

# Print environment information for debugging
echo "Environment details:"
echo "PATH=$PATH"
echo "PWD=$(pwd)"
echo "USER=$(whoami)"

# Export needed environment variables
export UV_HTTP_TIMEOUT=300

# Change to the script directory
cd "$SCRIPT_DIR" || { echo "ERROR: Could not change to script directory"; exit 1; }

# Check if we can run uv
if ! command -v uv &> /dev/null; then
    echo "ERROR: 'uv' command not found"
    # Try to find uv in common locations
    for dir in "$HOME/.local/bin" "/usr/local/bin" "$HOME/.cargo/bin"; do
        if [ -x "$dir/uv" ]; then
            echo "Found uv at $dir/uv, adding to PATH"
            export PATH="$PATH:$dir"
            break
        fi
    done
fi

# Verify the main script exists
MAIN_SCRIPT="/home/wally/ai-solarpunk-story-bot/ai_future.sh"
if [ ! -x "$MAIN_SCRIPT" ]; then
    echo "ERROR: Main script not found or not executable: $MAIN_SCRIPT"
    exit 1
fi

echo "Running main script: $MAIN_SCRIPT generate random random"
"$MAIN_SCRIPT" generate random random

# Record completion time
END_TIME=$(date +"%Y-%m-%d %H:%M:%S")
echo "========================================"
echo "AI Future Scheduler - Completed execution"
echo "Ended at: $END_TIME"
echo "========================================"
