#!/bin/bash
# AI Solarpunk Story Bot - Enhanced Management Interface

# Set environment variables for UV
export UV_HTTP_TIMEOUT=300  # 5 minutes timeout for downloads

# Set the directory where the script is located as the working directory
cd "$(dirname "$0")"

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Service configuration
SERVICE_NAME="ai-solarpunk-story"
SYSTEMD_DIR="/etc/systemd/system"

# Available settings and styles
SETTINGS=("urban" "coastal" "forest" "desert" "rural" "mountain" "arctic" "island")
STYLES=("digital-art" "watercolor" "stylized" "solarpunk-nouveau" "retro-futurism" "isometric")

# Function to display the script header
show_header() {
    clear
    echo -e "${CYAN}"
    echo "    █████╗ ██╗    ███████╗██╗   ██╗████████╗██╗   ██╗██████╗ ███████╗"
    echo "   ██╔══██╗██║    ██╔════╝██║   ██║╚══██╔══╝██║   ██║██╔══██╗██╔════╝"
    echo "   ███████║██║    █████╗  ██║   ██║   ██║   ██║   ██║██████╔╝█████╗  "
    echo "   ██╔══██║██║    ██╔══╝  ██║   ██║   ██║   ██║   ██║██╔══██╗██╔══╝  "
    echo "   ██║  ██║██║    ██║     ╚██████╔╝   ██║   ╚██████╔╝██║  ██║███████╗"
    echo "   ╚═╝  ╚═╝╚═╝    ╚═╝      ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝"
    echo -e "${NC}"
    echo -e "${YELLOW}============== Solarpunk Story Generator and Publisher ==============${NC}"
    echo -e "${GREEN}Using UV package manager with SystemD service${NC}"
}

# Function to select timezone
select_timezone() {
    echo -e "\n${CYAN}Timezone Selection${NC}"
    echo -e "${YELLOW}Please select your timezone:${NC}"
    
    # Common US timezones
    echo -e "${BLUE}US Timezones:${NC}"
    echo -e "1) Eastern (EST/EDT)"
    echo -e "2) Central (CST/CDT)"
    echo -e "3) Mountain (MST/MDT)"
    echo -e "4) Pacific (PST/PDT)"
    echo -e "5) Alaska (AKST/AKDT)"
    echo -e "6) Hawaii (HST)"
    
    # European/Other timezones
    echo -e "\n${BLUE}European/Other Timezones:${NC}"
    echo -e "7) UK/Ireland (GMT/BST)"
    echo -e "8) Central Europe (CET/CEST)"
    echo -e "9) Eastern Europe (EET/EEST)"
    echo -e "10) India (IST)"
    echo -e "11) Japan/Korea (JST/KST)"
    echo -e "12) Australia Eastern (AEST/AEDT)"
    
    # Custom option
    echo -e "\n13) Enter custom UTC offset"
    echo -e "14) Use server timezone (UTC)"
    
    read -p "Enter your choice (1-14): " tz_choice
    
    case $tz_choice in
        1)  USER_TZ="America/New_York"; USER_TZ_NAME="Eastern Time"; BASE_TZ_OFFSET="-0500" ;;
        2)  USER_TZ="America/Chicago"; USER_TZ_NAME="Central Time"; BASE_TZ_OFFSET="-0600" ;;
        3)  USER_TZ="America/Denver"; USER_TZ_NAME="Mountain Time"; BASE_TZ_OFFSET="-0700" ;;
        4)  USER_TZ="America/Los_Angeles"; USER_TZ_NAME="Pacific Time"; BASE_TZ_OFFSET="-0800" ;;
        5)  USER_TZ="America/Anchorage"; USER_TZ_NAME="Alaska Time"; BASE_TZ_OFFSET="-0900" ;;
        6)  USER_TZ="Pacific/Honolulu"; USER_TZ_NAME="Hawaii Time"; BASE_TZ_OFFSET="-1000" ;;
        7)  USER_TZ="Europe/London"; USER_TZ_NAME="UK Time"; BASE_TZ_OFFSET="+0000" ;;
        8)  USER_TZ="Europe/Paris"; USER_TZ_NAME="Central European"; BASE_TZ_OFFSET="+0100" ;;
        9)  USER_TZ="Europe/Helsinki"; USER_TZ_NAME="Eastern European"; BASE_TZ_OFFSET="+0200" ;;
        10) USER_TZ="Asia/Kolkata"; USER_TZ_NAME="India Time"; BASE_TZ_OFFSET="+0530" ;;
        11) USER_TZ="Asia/Tokyo"; USER_TZ_NAME="Japan Time"; BASE_TZ_OFFSET="+0900" ;;
        12) USER_TZ="Australia/Sydney"; USER_TZ_NAME="Australia Eastern"; BASE_TZ_OFFSET="+1000" ;;
        13) 
            echo -e "\n${YELLOW}Enter your UTC offset in ±HHMM format${NC}"
            echo -e "Examples: -0500 (EST), +0100 (CET), +0530 (IST)"
            read -p "UTC offset: " custom_offset
            
            # Validate format
            if [[ "$custom_offset" =~ ^[+-][0-1][0-9][0-5][0-9]$ ]]; then
                USER_TZ="Etc/GMT$(echo "$custom_offset" | sed 's/+/-/' | sed 's/-/+/' | sed 's/[0-9][0-9]$//')"
                USER_TZ_NAME="UTC$custom_offset"
                BASE_TZ_OFFSET="$custom_offset"
                USER_TZ_OFFSET="$custom_offset"  # For custom offset, base and current are the same
            else
                echo -e "${RED}Invalid offset format${NC}"
                return 1
            fi
            ;;
        14) USER_TZ="UTC"; USER_TZ_NAME="UTC"; BASE_TZ_OFFSET="+0000"; USER_TZ_OFFSET="+0000" ;;
        *) 
            echo -e "${RED}Invalid choice${NC}"
            return 1
            ;;
    esac
    
    # If not a custom or UTC timezone, get current offset including DST
    if [[ $tz_choice != "13" && $tz_choice != "14" ]]; then
        CURRENT_TZ_OFFSET=$(TZ=$USER_TZ date +%z)
        USER_TZ_OFFSET=$CURRENT_TZ_OFFSET
        
        # Check if we're in DST
        if [ "$BASE_TZ_OFFSET" != "$USER_TZ_OFFSET" ]; then
            echo -e "${BLUE}Detected Daylight Saving Time is active${NC}"
            USER_TZ_NAME="$USER_TZ_NAME (DST)"
        fi
    fi
    
    # Save timezone configuration
    mkdir -p config
    echo "USER_TZ=$USER_TZ" > "config/timezone.conf"
    echo "USER_TZ_NAME=$USER_TZ_NAME" >> "config/timezone.conf"
    echo "USER_TZ_OFFSET=$USER_TZ_OFFSET" >> "config/timezone.conf"
    echo "BASE_TZ_OFFSET=$BASE_TZ_OFFSET" >> "config/timezone.conf"
    echo -e "${GREEN}Timezone preference saved${NC}"
    
    return 0
}

# Function to load timezone configuration
load_timezone_config() {
    if [ -f "config/timezone.conf" ]; then
        # Use grep to extract values to avoid shell interpretation issues
        USER_TZ=$(grep "^USER_TZ=" config/timezone.conf | cut -d= -f2)
        USER_TZ_NAME=$(grep "^USER_TZ_NAME=" config/timezone.conf | cut -d= -f2)
        USER_TZ_OFFSET=$(grep "^USER_TZ_OFFSET=" config/timezone.conf | cut -d= -f2)
        
        # Verify values were loaded correctly
        if [ -n "$USER_TZ" ] && [ -n "$USER_TZ_NAME" ] && [ -n "$USER_TZ_OFFSET" ]; then
            # Get current timezone offset with DST if applicable
            if [[ "$USER_TZ" != "UTC" && "$USER_TZ" != Etc/* ]]; then
                # Get current offset including DST if applicable
                CURRENT_TZ_OFFSET=$(TZ=$USER_TZ date +%z)
                if [ -n "$CURRENT_TZ_OFFSET" ]; then
                    # Store both the base offset and current offset
                    BASE_TZ_OFFSET=$USER_TZ_OFFSET
                    USER_TZ_OFFSET=$CURRENT_TZ_OFFSET
                    
                    # Check if we're in DST
                    if [ "$BASE_TZ_OFFSET" != "$USER_TZ_OFFSET" ]; then
                        echo -e "${BLUE}Detected Daylight Saving Time is active${NC}"
                        USER_TZ_NAME="$USER_TZ_NAME (DST)"
                    fi
                fi
            fi
            
            echo -e "${BLUE}Loaded timezone: $USER_TZ_NAME ($USER_TZ_OFFSET)${NC}"
            return 0
        fi
    fi
    
    echo -e "${YELLOW}No timezone set or config is invalid - using UTC${NC}"
    USER_TZ="UTC"
    USER_TZ_NAME="UTC"
    USER_TZ_OFFSET="+0000"
    return 1
}

# Function to convert local time to UTC
convert_to_utc() {
    local local_hour=$1
    local local_minute=$2
    local offset_hours=${USER_TZ_OFFSET:0:3}
    local offset_minutes=${USER_TZ_OFFSET:3:2}
    
    # Convert offset to minutes (handle the sign properly)
    local sign=${offset_hours:0:1}
    local offset_hour_num=${offset_hours:1:2}
    local total_offset_minutes=$(( ${sign}1 * (offset_hour_num * 60 + offset_minutes) ))
    
    # Convert local time to minutes since midnight
    local local_minutes=$(( local_hour * 60 + local_minute ))
    
    # Subtract offset to get UTC
    local utc_minutes=$((local_minutes - total_offset_minutes))
    
    # Handle day wraparound
    while [ $utc_minutes -lt 0 ]; do
        utc_minutes=$((utc_minutes + 1440))  # Add 24 hours
    done
    while [ $utc_minutes -ge 1440 ]; do
        utc_minutes=$((utc_minutes - 1440))  # Subtract 24 hours
    done
    
    # Convert back to hours and minutes
    local utc_hour=$((utc_minutes / 60))
    local utc_minute=$((utc_minutes % 60))
    
    # Format output
    printf "%02d:%02d" $utc_hour $utc_minute
}

# Function to display timezone information
display_timezone_info() {
    if [ -n "$USER_TZ_NAME" ]; then
        echo -e "${BLUE}Current Timezone: $USER_TZ_NAME ($USER_TZ_OFFSET)${NC}"
        local current_time=$(TZ=$USER_TZ date +"%H:%M")
        local utc_time=$(TZ=UTC date +"%H:%M")
        echo -e "${GREEN}Current time: $current_time ($USER_TZ_NAME) / $utc_time (UTC)${NC}"
    else
        echo -e "${YELLOW}No timezone set - using UTC${NC}"
    fi
}

# Function to run the generator with specified options
run_generator() {
    local setting=$1
    local style=$2
    local preview=$3
    local additional_flag=$4
    local additional_value=$5

    # Ensure we're in the project directory
    cd "$(dirname "$0")"
    
    # Ensure virtual environment is activated
    if [[ -d ".venv" ]]; then
        source .venv/bin/activate
    else
        echo -e "${RED}Virtual environment not found. Creating one...${NC}"
        uv venv
        source .venv/bin/activate
    fi

    local cmd="uv run src/ai_story_tweet_generator.py"
    
    # Add arguments if provided
    [[ -n $setting && $setting != "" ]] && cmd="$cmd --setting $setting"
    [[ -n $style && $style != "" ]] && cmd="$cmd --style $style"
    [[ $preview == "true" ]] && cmd="$cmd --preview"
    
    # Add any additional flags and values
    if [[ -n $additional_flag && -n $additional_value ]]; then
        cmd="$cmd $additional_flag $additional_value"
    fi
    
    echo -e "${BLUE}Running command: $cmd${NC}"
    
    # Run the command and capture its output
    if ! output=$(eval "$cmd" 2>&1); then
        echo -e "${RED}Error running generator:${NC}"
        echo "$output"
        return 1
    fi
    
    # If we're in preview mode, make sure to display the output
    if [[ $preview == "true" ]]; then
        # Display the output, which should include the story and image path
        echo -e "${GREEN}Preview generated:${NC}"
        echo "$output"
        
        # Extract and display the image path if it exists
        if image_path=$(echo "$output" | grep "Image saved to:" | cut -d: -f2- | tr -d ' '); then
            echo -e "${YELLOW}Image was generated at:${NC} $image_path"
            
            # If we're in an interactive terminal, offer to display the image
            if [[ -t 1 ]] && command -v display &> /dev/null; then
                read -p "Would you like to view the image? (y/n) " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    display "$image_path"
                fi
            fi
        fi
    fi
    
    return 0
}

# Function to preview story and image side by side
preview_story_and_image() {
    local setting=$1
    local style=$2
    
    echo -e "${YELLOW}Generating preview with setting: $setting, style: $style${NC}"
    
    # Create/ensure the preview directory exists and is empty
    local preview_dir="output/preview_files"
    mkdir -p "$preview_dir"
    rm -f "$preview_dir"/*
    
    # Run the generator in preview mode with output to preview directory
    echo -e "${BLUE}Running generator...${NC}"
    uv run src/ai_story_tweet_generator.py --setting "$setting" --style "$style" --features "story,image" --output-dir "$preview_dir"
    
    # Wait a moment for files to be written
    sleep 2
    
    # Find the generated files
    local story_file=$(find "$preview_dir" -name "story_*.txt" | head -n 1)
    local image_file=$(find "$preview_dir" -name "image_*.png" | head -n 1)
    
    echo -e "${BLUE}Looking for files in: $preview_dir${NC}"
    ls -la "$preview_dir"
    
    if [[ -n "$story_file" && -f "$story_file" ]]; then
        echo -e "${GREEN}✓ Found story: $(basename "$story_file")${NC}"
    else
        echo -e "${RED}× Story file not found${NC}"
    fi
    
    if [[ -n "$image_file" && -f "$image_file" ]]; then
        echo -e "${GREEN}✓ Found image: $(basename "$image_file")${NC}"
    else
        echo -e "${RED}× Image file not found${NC}"
        
        # If we have a story but no image, try to generate the image separately
        if [[ -n "$story_file" && -f "$story_file" ]]; then
            echo -e "${YELLOW}Attempting to generate image from existing story...${NC}"
            
            # Call image generation directly
            uv run src/ai_story_tweet_generator.py --setting "$setting" --style "$style" --features "image" --story-file "$story_file" --output-dir "$preview_dir"
            sleep 2
            
            # Look for image again
            image_file=$(find "$preview_dir" -name "image_*.png" | head -n 1)
        fi
    fi
    
    if [[ -n "$story_file" && -n "$image_file" && -f "$story_file" && -f "$image_file" ]]; then
        echo -e "${GREEN}✓ Generation complete${NC}"
        
        # Get terminal dimensions
        local term_width=$(tput cols || echo 80)
        local term_height=$(tput lines || echo 24)
        
        # Ensure minimum dimensions
        if [ "$term_width" -lt 80 ]; then
            term_width=80
        fi
        if [ "$term_height" -lt 24 ]; then
            term_height=24
        fi
        
        # Calculate image width (use ~40% of terminal width)
        local img_width=$((term_width * 4 / 10))
        local text_width=$((term_width / 2 - 5))
        
        # Clear screen for better presentation
        clear
        
        # Print header
        echo -e "${CYAN}======= Solarpunk Story Preview =======${NC}\n"
        
        # Create a temporary file for the story with proper formatting
        local temp_story=$(mktemp)
        fold -s -w "$text_width" "$story_file" > "$temp_story"
        
        # Display story with padding
        echo -e "${YELLOW}Story:${NC}\n"
        cat "$temp_story"
        
        # Add vertical space
        echo -e "\n"
        
        # Display image
        echo -e "${YELLOW}Image:${NC}\n"
        if command -v timg &> /dev/null; then
            timg -g "${img_width}x$((term_height/2))" -U -F -C -p h "$image_file"
        else
            echo -e "${RED}timg not found. Cannot display image preview.${NC}"
            echo -e "${BLUE}Image saved at: $image_file${NC}"
        fi
        
        # Clean up temporary file
        rm "$temp_story"
        
        # Add visual separator
        echo -e "\n${CYAN}=========================================${NC}"
        echo -e "${YELLOW}Would you like to post this story and image? (y/n)${NC}"
        read -r response
        
        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}Posting story and image...${NC}"
            
            # Use the existing files directly instead of creating new ones
            echo -e "${GREEN}Using story: $story_file${NC}"
            echo -e "${GREEN}Using image: $image_file${NC}"
            
            # Post using the generator with the post-files flag
            uv run src/ai_story_tweet_generator.py --post-files "$story_file:$image_file"
            
            echo -e "${GREEN}Story and image have been posted${NC}"
        else
            echo -e "${YELLOW}Preview closed without posting.${NC}"
        fi
    else
        echo -e "${RED}Error: Could not find all required generated files in preview directory${NC}"
        echo -e "${YELLOW}Preview directory contents:${NC}"
        ls -la "$preview_dir"
        read -p "Press Enter to continue..."
    fi
}

# Function to check service status
check_service_status() {
    echo -e "${YELLOW}Checking AI Solarpunk Story Bot Service Status${NC}"
    
    # Display timezone information
    display_timezone_info
    
    # Check service status
    echo -e "\n${BLUE}Service Status:${NC}"
    systemctl status "$SERVICE_NAME.service" | head -n 5
    
    # Check timer status
    echo -e "\n${BLUE}Timer Status:${NC}"
    systemctl status "$SERVICE_NAME.timer" | head -n 5
    
    # Show next scheduled run
    echo -e "\n${BLUE}Next Scheduled Run:${NC}"
    systemctl list-timers "$SERVICE_NAME.timer" | grep "$SERVICE_NAME"
    
    # Show recent logs
    echo -e "\n${BLUE}Recent Logs:${NC}"
    journalctl -u "$SERVICE_NAME.service" -n 5
}

# Function to manage service schedule
manage_schedule() {
    local choice
    
    # First check if we have saved timezone settings
    if ! load_timezone_config; then
        echo -e "${YELLOW}No timezone configuration found${NC}"
        select_timezone
    fi
    
    while true; do
        echo -e "\n${YELLOW}Schedule Management${NC}"
        echo -e "${BLUE}Current timezone: $USER_TZ_NAME ($USER_TZ_OFFSET)${NC}"
        echo "1) View current schedule"
        echo "2) Change posting time"
        echo "3) Enable/disable service"
        echo "4) Change timezone"
        echo "5) Back to main menu"
        
        read -p "Enter your choice: " choice
        
        case $choice in
            1)
                display_timezone_info
                echo -e "\n${YELLOW}Current Schedule:${NC}"
                
                # Get the UTC time from the timer file
                local utc_time=""
                if [ -f "$SYSTEMD_DIR/$SERVICE_NAME.timer" ]; then
                    utc_time=$(grep "OnCalendar" "$SYSTEMD_DIR/$SERVICE_NAME.timer" | sed -E 's/.*\*-\*-\* ([0-9:]+).*/\1/')
                fi
                
                if [ -n "$utc_time" ]; then
                    # Extract hours and minutes from UTC time
                    local utc_hour=${utc_time%%:*}
                    local utc_minute=${utc_time#*:}
                    utc_minute=${utc_minute%%:*}  # Remove seconds if present
                    
                    # Convert UTC to local time
                    # For simplicity, we're assuming the offset format is always +/-HHMM
                    local sign=${USER_TZ_OFFSET:0:1}
                    local offset_hour_num=${USER_TZ_OFFSET:1:2}
                    local offset_minute=${USER_TZ_OFFSET:3:2}
                    local total_offset_minutes=$(( ${sign}1 * (offset_hour_num * 60 + offset_minute) ))
                    
                    # Convert UTC time to minutes since midnight
                    local utc_minutes=$(( utc_hour * 60 + utc_minute ))
                    
                    # Add offset to get local time
                    local local_minutes=$((utc_minutes + total_offset_minutes))
                    
                    # Handle day wraparound
                    while [ $local_minutes -lt 0 ]; do
                        local_minutes=$((local_minutes + 1440))  # Add 24 hours
                    done
                    while [ $local_minutes -ge 1440 ]; do
                        local_minutes=$((local_minutes - 1440))  # Subtract 24 hours
                    done
                    
                    # Convert back to hours and minutes
                    local local_hour=$((local_minutes / 60))
                    local local_minute=$((local_minutes % 60))
                    
                    # Display both UTC and local times
                    local formatted_local_time=$(printf "%02d:%02d" $local_hour $local_minute)
                    echo -e "${GREEN}Service is scheduled to run at:${NC}"
                    echo -e "  ${BLUE}$formatted_local_time ($USER_TZ_NAME)${NC}"
                    echo -e "  ${BLUE}$utc_time (UTC)${NC}"
                    
                    # Also show timer status
                    echo -e "\n${YELLOW}Timer Status:${NC}"
                    systemctl status "$SERVICE_NAME.timer" | head -n 3
                    echo -e "\n${YELLOW}Next Run:${NC}"
                    systemctl list-timers "$SERVICE_NAME.timer" | grep "$SERVICE_NAME" || echo -e "${RED}Cannot display timer status${NC}"
                else
                    echo -e "${RED}Could not determine schedule time from timer file${NC}"
                    systemctl list-timers "$SERVICE_NAME.timer" | grep "$SERVICE_NAME" || echo -e "${RED}Cannot display timer - it may have configuration issues${NC}"
                fi
                read -p "Press Enter to continue..."
                ;;
            2)
                echo -e "\n${BLUE}Enter time in YOUR timezone ($USER_TZ_NAME)${NC}"
                read -p "Enter posting time (HH:MM, 24h format): " local_time
                if [[ $local_time =~ ^([0-1][0-9]|2[0-3]):[0-5][0-9]$ ]]; then
                    local hour=${local_time%:*}
                    local minute=${local_time#*:}
                    # Remove leading zeros to avoid bash treating numbers as octal
                    hour=$((10#$hour))
                    minute=$((10#$minute))
                    local utc_time=$(convert_to_utc $hour $minute)
                    
                    # Validate timer file exists
                    if [ ! -f "$SYSTEMD_DIR/$SERVICE_NAME.timer" ]; then
                        echo -e "${RED}Timer file not found. Creating a new one...${NC}"
                        # Create a basic timer file if it doesn't exist
                        cat << EOF | sudo tee "$SYSTEMD_DIR/$SERVICE_NAME.timer" > /dev/null
[Unit]
Description=AI Solarpunk Story Bot Timer
Requires=ai-solarpunk-story.service

[Timer]
OnCalendar=*-*-* $utc_time:00
Persistent=true

[Install]
WantedBy=timers.target
EOF
                    else
                        # Update existing timer
                        sudo sed -i "s/OnCalendar=.*/OnCalendar=*-*-* $utc_time:00/" "$SYSTEMD_DIR/$SERVICE_NAME.timer"
                        # Remove RandomizedDelaySec if it exists
                        sudo sed -i '/RandomizedDelaySec=/d' "$SYSTEMD_DIR/$SERVICE_NAME.timer"
                    fi
                    
                    sudo systemctl daemon-reload
                    sudo systemctl restart "$SERVICE_NAME.timer"
                    
                    echo -e "${GREEN}Schedule updated successfully${NC}"
                    echo -e "${BLUE}Posts will occur exactly at $local_time $USER_TZ_NAME ($utc_time UTC)${NC}"
                    
                    # Verify timer status
                    if ! systemctl is-active "$SERVICE_NAME.timer" > /dev/null; then
                        echo -e "${YELLOW}Warning: Timer is not active. Enabling now...${NC}"
                        sudo systemctl enable --now "$SERVICE_NAME.timer"
                    fi
                    
                    echo -e "${YELLOW}Timer status:${NC}"
                    systemctl status "$SERVICE_NAME.timer" | head -n 5
                else
                    echo -e "${RED}Invalid time format${NC}"
                fi
                ;;
            3)
                if systemctl is-enabled "$SERVICE_NAME.timer" >/dev/null 2>&1; then
                    sudo systemctl disable --now "$SERVICE_NAME.timer"
                    echo -e "${YELLOW}Service disabled${NC}"
                else
                    sudo systemctl enable --now "$SERVICE_NAME.timer"
                    echo -e "${GREEN}Service enabled${NC}"
                fi
                ;;
            4)
                select_timezone
                ;;
            5)
                break
                ;;
            *)
                echo -e "${RED}Invalid choice${NC}"
                ;;
        esac
    done
}

# Function to test the service
test_service() {
    echo -e "${YELLOW}Running service test...${NC}"
    sudo systemctl start "$SERVICE_NAME.service"
    echo -e "${BLUE}Watching logs (Ctrl+C to stop):${NC}"
    journalctl -u "$SERVICE_NAME.service" -f
}

# Function to view logs with proper permissions
view_logs() {
    echo -e "${YELLOW}Viewing AI Solarpunk Story Bot Logs${NC}"
    echo -e "${BLUE}Log viewing options:${NC}"
    echo "1) View recent logs (last 50 lines)"
    echo "2) View today's logs"
    echo "3) View logs with follow mode (live updates)"
    echo "4) View service log file (detailed script output)"
    echo "5) Back to main menu"
    
    read -p "Enter your choice: " choice
    
    case $choice in
        1)
            echo -e "${YELLOW}Last 50 log entries:${NC}"
            echo -e "${GREEN}Please run this command:${NC}"
            echo -e "sudo journalctl -u $SERVICE_NAME.service -n 50 --no-pager"
            ;;
        2)
            echo -e "${YELLOW}Today's logs:${NC}"
            echo -e "${GREEN}Please run this command:${NC}"
            echo -e "sudo journalctl -u $SERVICE_NAME.service --since today --no-pager"
            ;;
        3)
            echo -e "${YELLOW}Following logs (press Ctrl+C to exit):${NC}"
            echo -e "${GREEN}Please run this command:${NC}"
            echo -e "sudo journalctl -u $SERVICE_NAME.service -f"
            ;;
        4)
            echo -e "${YELLOW}Service log file (actual script output):${NC}"
            
            # Check if logs directory exists
            if [ ! -d "logs" ]; then
                echo -e "${RED}Logs directory not found. Creating it...${NC}"
                mkdir -p logs
                touch logs/service.log
                echo "Log file created. No entries yet." > logs/service.log
            fi
            
            # Check if log file exists
            if [ ! -f "logs/service.log" ]; then
                echo -e "${RED}Log file not found. Creating it...${NC}"
                touch logs/service.log
                echo "Log file created. No entries yet." > logs/service.log
            fi
            
            # Display the log file contents
            echo -e "${GREEN}Contents of service log file (last 50 lines):${NC}"
            tail -n 50 logs/service.log
            ;;
        5)
            return
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            ;;
    esac
    
    read -p "Press Enter to continue..."
}

# Function to manually run the service (useful for testing)
run_service_manually() {
    echo -e "${YELLOW}Running AI Solarpunk Story Bot manually${NC}"
    echo -e "${BLUE}This will execute the service immediately without waiting for the schedule.${NC}"
    echo -e "${BLUE}Do you want to:${NC}"
    echo "1) Run with default settings"
    echo "2) Run with custom settings"
    echo "3) Cancel"
    
    read -p "Enter your choice: " choice
    
    case $choice in
        1)
            echo -e "${GREEN}Please run this command to start the service:${NC}"
            echo -e "sudo systemctl start $SERVICE_NAME.service"
            echo -e "\n${YELLOW}After running, check the logs with:${NC}"
            echo -e "sudo journalctl -u $SERVICE_NAME.service -n 50 --no-pager"
            ;;
        2)
            echo -e "\n${YELLOW}Select Setting:${NC}"
            select setting in "${SETTINGS[@]}" "random" "back"; do
                if [[ $setting == "back" ]]; then
                    return
                elif [[ -n $setting ]]; then
                    echo -e "\n${YELLOW}Select Style:${NC}"
                    select style in "${STYLES[@]}" "back"; do
                        if [[ $style == "back" ]]; then
                            break
                        elif [[ -n $style ]]; then
                            echo -e "${GREEN}Running the story generator directly:${NC}"
                            preview_story_and_image "$setting" "$style"
                            return
                        fi
                    done
                fi
                break
            done
            ;;
        3)
            return
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            ;;
    esac
    
    read -p "Press Enter to continue..."
}

# Function to view recent activity
view_recent_activity() {
    echo -e "\n${GREEN}Recent Activity${NC}"
    echo -e "${YELLOW}1)${NC} View recent posts"
    echo -e "${YELLOW}2)${NC} View recent images"
    echo -e "${YELLOW}3)${NC} View recent previews"
    echo -e "${YELLOW}4)${NC} View logs"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo -e "${YELLOW}q)${NC} Quit"

    read -p "Enter your choice: " activity_choice

    case $activity_choice in
        1)
            echo -e "${BLUE}Recent posts:${NC}"
            ls -lt output/stories/ | head -n 5
            ;;
        2)
            echo -e "${BLUE}Recent images:${NC}"
            ls -lt output/images/ | head -n 5
            ;;
        3)
            echo -e "${BLUE}Recent previews:${NC}"
            ls -lt output/previews/ | head -n 5
            read -p "View a preview? (enter number or 'n'): " preview_num
            if [[ $preview_num =~ ^[0-9]+$ ]]; then
                preview_file=$(ls -t output/previews/ | sed -n "${preview_num}p")
                if [ -n "$preview_file" ]; then
                    preview_path="output/previews/$preview_file"
                    cat "$preview_path"
                    
                    # Check if already posted
                    if grep -q '"posted": true' "$preview_path"; then
                        echo -e "\n${YELLOW}This preview has already been posted${NC}"
                    else
                        echo -e "\n${BLUE}Would you like to post this preview? [y/N]:${NC}"
                        read -p "" post_choice
                        if [[ $post_choice =~ ^[Yy]$ ]]; then
                            run_generator "" "" "" false "--post-preview" "$preview_path"
                        fi
                    fi
                fi
            fi
            ;;
        4)
            view_logs
            ;;
        b|B)
            return
            ;;
        q|Q)
            echo -e "${GREEN}Exiting.${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice.${NC}"
            ;;
    esac
}

# Function to clear only preview files
clear_preview_files() {
    echo -e "\n${BLUE}Clearing Preview Files${NC}"
    
    # Check if the preview directory exists
    local preview_dir="output/preview_files"
    if [ ! -d "$preview_dir" ]; then
        mkdir -p "$preview_dir"
        echo -e "${YELLOW}Preview directory created.${NC}"
        return
    fi
    
    # Count files before clearing
    local file_count=$(find "$preview_dir" -type f | wc -l)
    
    if [ $file_count -eq 0 ]; then
        echo -e "${YELLOW}No preview files to clear.${NC}"
        return
    fi
    
    echo -e "${YELLOW}Found $file_count preview files. What would you like to do?${NC}"
    echo -e "${CYAN}1)${NC} Delete all preview files"
    echo -e "${CYAN}2)${NC} Archive preview files before deleting"
    echo -e "${CYAN}b)${NC} Cancel operation"
    
    read -p "Enter your choice: " clear_choice
    
    case $clear_choice in
        1)
            # Delete files directly
            rm -f "$preview_dir"/*
            echo -e "${GREEN}✓${NC} Deleted $file_count preview files"
            ;;
        2)
            # Archive before deleting
            local timestamp=$(date +%Y%m%d_%H%M%S)
            local archive_dir="archive/preview_files_${timestamp}"
            mkdir -p "$archive_dir"
            
            # Move files to archive
            mv "$preview_dir"/* "$archive_dir/" 2>/dev/null
            
            echo -e "${GREEN}✓${NC} Archived $file_count preview files to $archive_dir"
            ;;
        b|B)
            echo -e "${YELLOW}Operation cancelled.${NC}"
            return
            ;;
        *)
            echo -e "${RED}Invalid choice.${NC}"
            return
            ;;
    esac
}

# Updated function to clean up and archive output folders
cleanup_outputs() {
    echo -e "\n${GREEN}Output Folder Cleanup and Archiving${NC}"
    
    # Create archive directory with timestamp
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local archive_dir="archive/${timestamp}"
    mkdir -p "$archive_dir/stories" "$archive_dir/images" "$archive_dir/previews" "$archive_dir/preview_files"
    
    echo -e "${BLUE}Select cleanup option:${NC}"
    echo -e "${YELLOW}1)${NC} Archive everything"
    echo -e "${YELLOW}2)${NC} Keep files from last 7 days, archive the rest"
    echo -e "${YELLOW}3)${NC} Keep files from last 30 days, archive the rest"
    echo -e "${YELLOW}4)${NC} Custom (select what to archive)"
    echo -e "${YELLOW}5)${NC} Clear preview files only"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    
    read -p "Enter your choice: " cleanup_choice
    
    case $cleanup_choice in
        1)
            # Archive everything
            echo -e "${BLUE}Archiving all output files...${NC}"
            
            # Count files before moving
            local stories_count=$(find output/stories -type f | wc -l)
            local images_count=$(find output/images -type f | wc -l)
            local previews_count=$(find output/previews -type f | wc -l)
            local preview_files_count=$(find output/preview_files -type f 2>/dev/null | wc -l)
            
            # Move all files to archive
            mv output/stories/* "$archive_dir/stories/" 2>/dev/null
            mv output/images/* "$archive_dir/images/" 2>/dev/null
            mv output/previews/* "$archive_dir/previews/" 2>/dev/null
            mv output/preview_files/* "$archive_dir/preview_files/" 2>/dev/null
            
            echo -e "${GREEN}✓${NC} Archived $stories_count stories, $images_count images, $previews_count previews, and $preview_files_count preview files"
            echo -e "${GREEN}✓${NC} Archive location: $archive_dir"
            ;;
            
        2|3)
            # Keep recent files, archive older ones
            local days=7
            [[ $cleanup_choice -eq 3 ]] && days=30
            
            echo -e "${BLUE}Keeping files from last $days days, archiving older files...${NC}"
            
            # Find files older than specified days
            find output/stories -type f -mtime +$days -exec mv {} "$archive_dir/stories/" \;
            find output/images -type f -mtime +$days -exec mv {} "$archive_dir/images/" \;
            find output/previews -type f -mtime +$days -exec mv {} "$archive_dir/previews/" \;
            find output/preview_files -type f -mtime +$days -exec mv {} "$archive_dir/preview_files/" \; 2>/dev/null
            
            # Count files in archive
            local archive_count=$(find "$archive_dir" -type f | wc -l)
            
            if [ $archive_count -eq 0 ]; then
                echo -e "${YELLOW}No files older than $days days were found.${NC}"
                rmdir -p "$archive_dir/stories" "$archive_dir/images" "$archive_dir/previews" "$archive_dir/preview_files" 2>/dev/null
            else
                echo -e "${GREEN}✓${NC} Archived $archive_count files older than $days days"
                echo -e "${GREEN}✓${NC} Archive location: $archive_dir"
            fi
            ;;
            
        4)
            # Custom archiving
            echo -e "\n${BLUE}Custom Archiving${NC}"
            echo -e "${YELLOW}a)${NC} Archive stories"
            echo -e "${YELLOW}b)${NC} Archive images"
            echo -e "${YELLOW}c)${NC} Archive previews"
            echo -e "${YELLOW}d)${NC} Archive preview_files"
            echo -e "${YELLOW}q)${NC} Cancel archiving"
            
            read -p "Select folders to archive (e.g., abc for stories, images, and previews): " archive_selection
            
            if [[ $archive_selection =~ [aA] ]]; then
                mv output/stories/* "$archive_dir/stories/" 2>/dev/null
                echo -e "${GREEN}✓${NC} Archived stories"
            fi
            
            if [[ $archive_selection =~ [bB] ]]; then
                mv output/images/* "$archive_dir/images/" 2>/dev/null
                echo -e "${GREEN}✓${NC} Archived images"
            fi
            
            if [[ $archive_selection =~ [cC] ]]; then
                mv output/previews/* "$archive_dir/previews/" 2>/dev/null
                echo -e "${GREEN}✓${NC} Archived previews"
            fi
            
            if [[ $archive_selection =~ [dD] ]]; then
                mv output/preview_files/* "$archive_dir/preview_files/" 2>/dev/null
                echo -e "${GREEN}✓${NC} Archived preview_files"
            fi
            
            # Check if any files were archived
            local archive_count=$(find "$archive_dir" -type f | wc -l)
            
            if [ $archive_count -eq 0 ]; then
                echo -e "${YELLOW}No files were archived.${NC}"
                rmdir -p "$archive_dir" 2>/dev/null
            else
                echo -e "${GREEN}✓${NC} Archive location: $archive_dir"
            fi
            ;;
            
        5)
            # Just clear preview files
            clear_preview_files
            ;;
            
        b|B)
            return
            ;;
            
        *)
            echo -e "${RED}Invalid choice.${NC}"
            ;;
    esac
    
    # Ensure output directories exist after cleanup
    mkdir -p output/stories output/images output/previews output/preview_files
}

# Main menu
main_menu() {
    local choice
    
    # Load timezone configuration if available
    load_timezone_config
    
    while true; do
        show_header
        display_timezone_info
        echo -e "\n${YELLOW}Main Menu${NC}"
        echo "1) Generate Preview"
        echo "2) Check Service Status"
        echo "3) Manage Schedule"
        echo "4) Test Service"
        echo "5) View Logs"
        echo "6) Run Service Now"
        echo "7) View Recent Activity"
        echo "8) Cleanup and Archive Outputs"
        echo "9) Exit"
        
        read -p "Enter your choice: " choice
        
        case $choice in
            1)
                echo -e "\n${YELLOW}Select Setting:${NC}"
                select setting in "${SETTINGS[@]}" "random" "back"; do
                    if [[ $setting == "back" ]]; then
                        break
                    elif [[ -n $setting ]]; then
                        echo -e "\n${YELLOW}Select Style:${NC}"
                        select style in "${STYLES[@]}" "back"; do
                            if [[ $style == "back" ]]; then
                                break
                            elif [[ -n $style ]]; then
                                preview_story_and_image "$setting" "$style"
                                break
                            fi
                        done
                    fi
                    break
                done
                ;;
            2)
                check_service_status
                read -p "Press Enter to continue..."
                ;;
            3)
                manage_schedule
                ;;
            4)
                test_service
                ;;
            5)
                view_logs
                ;;
            6)
                run_service_manually
                ;;
            7)
                view_recent_activity
                ;;
            8)
                cleanup_outputs
                ;;
            9)
                echo -e "${GREEN}Goodbye!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid choice${NC}"
                ;;
        esac
    done
}

# Check if running as root for service management
if [[ $1 == "service" ]]; then
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}Please run with sudo for service management${NC}"
        exit 1
    fi
fi

# Start the main menu
main_menu 