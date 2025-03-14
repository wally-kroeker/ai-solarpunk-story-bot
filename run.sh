#!/bin/bash

# AI Solarpunk Story Twitter Bot - Management Script
# This script provides functions for generating stories, images, and posting to Twitter

# Configuration
VENV_DIR=".venv"
CONFIG_DIR="config"
OUTPUT_DIR="output"
ENV_FILE=".env"

# Ensure directories exist
mkdir -p "${OUTPUT_DIR}/stories"
mkdir -p "${OUTPUT_DIR}/images"
mkdir -p "logs"

# Load environment if available
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# Activate virtual environment if it exists
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
fi

# Logging function
log() {
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] $1"
    echo "[$timestamp] $1" >> "logs/run-$(date +"%Y-%m-%d").log"
}

# Generate a story
generate_story() {
    local setting=${1:-"random"}
    log "Generating story with setting: $setting"
    
    uv run src/story_generator.py "$setting"
    
    if [ $? -eq 0 ]; then
        log "Story generation completed successfully"
    else
        log "ERROR: Story generation failed"
        return 1
    fi
}

# Generate an image
generate_image() {
    local setting=${1:-"urban"}
    local style=${2:-"photographic"}
    
    log "Generating image for setting '$setting' with style '$style'"
    
    uv run src/image_generator.py "$setting" "$style"
    
    if [ $? -eq 0 ]; then
        log "Image generation completed successfully"
    else
        log "ERROR: Image generation failed"
        return 1
    fi
}

# Post to Twitter
post_to_twitter() {
    local feature=${1:-"story_generation"}
    local with_image=${2:-"image"}
    
    log "Posting to Twitter about feature '$feature' with image option '$with_image'"
    
    uv run src/twitter_client.py update "$feature" "$with_image"
    
    if [ $? -eq 0 ]; then
        log "Twitter post completed successfully"
    else
        log "ERROR: Twitter post failed"
        return 1
    fi
}

# Generate story and image, then post to Twitter
generate_and_post() {
    local setting=${1:-"random"}
    local style=${2:-"photographic"}
    local feature=${3:-"story_generation"}
    
    log "Starting full generation and posting pipeline"
    
    # Generate story
    generate_story "$setting"
    if [ $? -ne 0 ]; then
        log "Pipeline aborted at story generation step"
        return 1
    fi
    
    # Generate image
    generate_image "$setting" "$style"
    if [ $? -ne 0 ]; then
        log "Pipeline aborted at image generation step"
        return 1
    fi
    
    # Post to Twitter
    post_to_twitter "$feature" "image"
    if [ $? -ne 0 ]; then
        log "Pipeline aborted at Twitter posting step"
        return 1
    fi
    
    log "Full pipeline completed successfully"
}

# Run the unified AI story-to-tweet flow
run_unified_flow() {
    local setting=${1:-"random"}
    
    log "Starting unified AI solarpunk story-to-tweet flow"
    log "Using setting: $setting, style: digital-art"
    
    # Run the unified Python script
    uv run src/ai_story_tweet_generator.py --setting "$setting"
    
    if [ $? -eq 0 ]; then
        log "Unified flow completed successfully"
    else
        log "ERROR: Unified flow failed"
        return 1
    fi
}

# Set up scheduling
setup_scheduling() {
    local frequency=${1:-"daily"}
    local time=${2:-"09:00"}
    
    log "Setting up $frequency posting schedule at $time"
    
    case "$frequency" in
        hourly)
            cron_schedule="0 * * * *"
            ;;
        daily)
            # Extract hour and minute from time
            hour=$(echo "$time" | cut -d':' -f1)
            minute=$(echo "$time" | cut -d':' -f2)
            cron_schedule="$minute $hour * * *"
            ;;
        weekly)
            hour=$(echo "$time" | cut -d':' -f1)
            minute=$(echo "$time" | cut -d':' -f2)
            cron_schedule="$minute $hour * * 0"  # Sunday
            ;;
        *)
            log "Unknown frequency: $frequency. Using daily."
            hour=$(echo "$time" | cut -d':' -f1)
            minute=$(echo "$time" | cut -d':' -f2)
            cron_schedule="$minute $hour * * *"
            ;;
    esac
    
    log "Creating cron job with schedule: $cron_schedule"
    
    # Get absolute path to script
    script_path=$(realpath "$0")
    project_dir=$(dirname "$script_path")
    
    # Create cron entry
    cron_cmd="$cron_schedule cd $project_dir && $script_path run-unified > /dev/null 2>&1"
    
    # Add to crontab if not already present
    (crontab -l 2>/dev/null | grep -v "$script_path run-unified"; echo "$cron_cmd") | crontab -
    
    log "Scheduling set up successfully"
}

# Check status
check_status() {
    log "Checking status of AI Solarpunk Story Twitter Bot"
    
    # Check if Twitter credentials are valid
    log "Testing Twitter API connection..."
    uv run src/twitter_client.py test
    
    # Count generated stories
    story_count=$(find "${OUTPUT_DIR}/stories" -type f | wc -l)
    log "Stories generated: $story_count"
    
    # Count generated images
    image_count=$(find "${OUTPUT_DIR}/images" -type f | wc -l)
    log "Images generated: $image_count"
    
    # Check cron job
    cron_job=$(crontab -l 2>/dev/null | grep -q "$0 run-unified" && echo "Yes" || echo "No")
    log "Scheduled posting: $cron_job"
    
    log "Status check completed"
}

# Clean test files
clean_tests() {
    log "Cleaning up test files..."
    
    # Remove test scripts we created earlier
    rm -f elon_tweets_test.py
    rm -f check_credentials.py
    rm -f python_twitter_test.py
    rm -f direct_twitter_test.py
    rm -f twitter_api_test.py
    rm -f tweepy_test.py
    rm -f twitter_post_test.py
    rm -f oauth1_post_test.py
    
    log "Test files cleaned up"
}

# Help function
show_help() {
    echo "AI Solarpunk Story Twitter Bot - Management Script"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  generate-story [setting]       Generate a story (urban, coastal, forest, desert, rural, random)"
    echo "  generate-image [setting] [style] Generate an image (photographic, digital-art, watercolor)"
    echo "  post [feature] [with_image]    Post to Twitter"
    echo "  generate-and-post [setting] [style] [feature]  Run full pipeline"
    echo "  run-unified [setting]          Run unified flow with AI image prompt generation (always digital-art)"
    echo "  schedule [frequency] [time]    Set up scheduled posting (hourly, daily, weekly)"
    echo "  status                         Check bot status"
    echo "  clean-tests                    Remove test scripts"
    echo "  help                           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 generate-story urban        Generate an urban solarpunk story"
    echo "  $0 generate-image coastal watercolor Generate a coastal watercolor image"
    echo "  $0 generate-and-post forest digital-art Generate and post with forest setting and digital art style"
    echo "  $0 run-unified random          Run complete unified flow with random setting"
    echo "  $0 schedule daily 15:30        Schedule daily posts at 3:30 PM"
}

# Main command handling
case "$1" in
    generate-story)
        generate_story "$2"
        ;;
    generate-image)
        generate_image "$2" "$3"
        ;;
    post)
        post_to_twitter "$2" "$3"
        ;;
    generate-and-post)
        generate_and_post "$2" "$3" "$4"
        ;;
    run-unified)
        run_unified_flow "$2"
        ;;
    schedule)
        setup_scheduling "$2" "$3"
        ;;
    status)
        check_status
        ;;
    clean-tests)
        clean_tests
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac

# Return success
exit 0 