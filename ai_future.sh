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
    echo -e "${GREEN}Using UV package manager${NC}"
}

# Function to run the generator with specified options
run_generator() {
    local setting=$1
    local style=$2
    local features=$3
    local preview=$4
    local extra_arg=$5
    local extra_value=$6

    local cmd="uv run src/ai_story_tweet_generator.py"
    
    # Add arguments if provided
    [[ -n $setting ]] && cmd="$cmd --setting $setting"
    [[ -n $style ]] && cmd="$cmd --style $style"
    [[ -n $features ]] && cmd="$cmd --features $features"
    [[ $preview == true ]] && cmd="$cmd --preview"
    [[ -n $extra_arg ]] && cmd="$cmd $extra_arg $extra_value"

    echo -e "${BLUE}Running command: $cmd${NC}"
    eval $cmd
}

# Function to generate and post content
generate_and_post() {
    echo -e "\n${GREEN}Story Generation and Posting${NC}"
    echo -e "${YELLOW}1)${NC} Quick post (random everything)"
    echo -e "${YELLOW}2)${NC} Choose setting and style"
    echo -e "${YELLOW}3)${NC} Advanced options"
    echo -e "${YELLOW}4)${NC} Preview mode"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo -e "${YELLOW}q)${NC} Quit"

    read -p "Enter your choice: " gen_choice

    case $gen_choice in
        1)
            run_generator "random" "random" "story image post" false
            ;;
        2)
            # Setting selection
            echo -e "\n${BLUE}Choose Setting:${NC}"
            for i in "${!SETTINGS[@]}"; do
                echo -e "${CYAN}$((i+1)))${NC} ${SETTINGS[$i]}"
            done
            echo -e "${CYAN}$((${#SETTINGS[@]}+1)))${NC} random"
            
            read -p "Select setting (1-$((${#SETTINGS[@]}+1))): " setting_num
            
            if [[ $setting_num -le ${#SETTINGS[@]} ]]; then
                setting="${SETTINGS[$((setting_num-1))]}"
            else
                setting="random"
            fi
            
            # Style selection
            echo -e "\n${BLUE}Choose Style:${NC}"
            for i in "${!STYLES[@]}"; do
                echo -e "${CYAN}$((i+1)))${NC} ${STYLES[$i]}"
            done
            echo -e "${CYAN}$((${#STYLES[@]}+1)))${NC} random"
            
            read -p "Select style (1-$((${#STYLES[@]}+1))): " style_num
            
            if [[ $style_num -le ${#STYLES[@]} ]]; then
                style="${STYLES[$((style_num-1))]}"
            else
                style="random"
            fi
            
            run_generator "$setting" "$style" "story image post" false
            ;;
        3)
            advanced_generation
            ;;
        4)
            preview_generation
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

# Function for advanced generation options
advanced_generation() {
    echo -e "\n${GREEN}Advanced Generation Options${NC}"
    
    # Setting selection
    echo -e "\n${BLUE}Select setting:${NC}"
    for i in "${!SETTINGS[@]}"; do
        echo -e "${CYAN}$((i+1)))${NC} ${SETTINGS[$i]}"
    done
    echo -e "${CYAN}$((${#SETTINGS[@]}+1)))${NC} random"
    
    read -p "Enter setting number [$((${#SETTINGS[@]}+1))]: " setting_num
    if [[ $setting_num -le ${#SETTINGS[@]} ]]; then
        setting="${SETTINGS[$((setting_num-1))]}"
    else
        setting="random"
    fi

    # Style selection
    echo -e "\n${BLUE}Select style:${NC}"
    for i in "${!STYLES[@]}"; do
        echo -e "${CYAN}$((i+1)))${NC} ${STYLES[$i]}"
    done
    echo -e "${CYAN}$((${#STYLES[@]}+1)))${NC} random"
    
    read -p "Enter style number [$((${#STYLES[@]}+1))]: " style_num
    if [[ $style_num -le ${#STYLES[@]} ]]; then
        style="${STYLES[$((style_num-1))]}"
    else
        style="random"
    fi

    # Feature selection
    echo -e "\n${BLUE}Select features:${NC}"
    echo -e "${CYAN}1)${NC} Story only"
    echo -e "${CYAN}2)${NC} Story + Image"
    echo -e "${CYAN}3)${NC} Complete (Story + Image + Post)"
    
    read -p "Enter feature set [3]: " feature_num
    case $feature_num in
        1) features="story" ;;
        2) features="story image" ;;
        *) features="story image post" ;;
    esac

    # Preview option
    echo -e "\n${BLUE}Preview mode?${NC}"
    read -p "Generate preview only (no posting) [y/N]: " preview_choice
    preview=false
    [[ $preview_choice =~ ^[Yy]$ ]] && preview=true

    run_generator "$setting" "$style" "$features" "$preview"
}

# Function to preview story and image side by side
preview_story_and_image() {
    local story_file="$1"
    local image_file="$2"

    # Validate inputs
    if [ ! -f "$story_file" ]; then
        echo -e "${RED}Error: Story file not found: $story_file${NC}"
        return 1
    fi

    if [ ! -f "$image_file" ]; then
        echo -e "${RED}Error: Image file not found: $image_file${NC}"
        return 1
    fi

    # Get terminal width and height with fallbacks
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
    local text_width=$((term_width / 2 - 5))  # Reduced width for text to ensure padding
    
    # Clear screen for better presentation
    clear
    
    # Print header
    echo -e "${CYAN}======= Solarpunk Story Preview =======${NC}\n"
    
    # Create a temporary file for the story with proper formatting
    local temp_story=$(mktemp)
    fold -s -w "$text_width" "$story_file" > "$temp_story"
    
    # Add padding after story
    local story_lines=$(wc -l < "$temp_story")
    local padding_needed=$((term_height - story_lines - 10))  # 10 lines for header and footer
    
    # Use a more reliable approach for side-by-side display
    # First display story with some right padding
    echo -e "${YELLOW}Story:${NC}\n"
    cat "$temp_story"
    
    # Add some vertical space
    echo -e "\n"
    
    # Display image centered below story
    echo -e "${YELLOW}Image:${NC}\n"
    # Use the best timg settings - high quality, auto adjust
    timg -g "${img_width}x$((term_height/2))" -U -F -C -p h "$image_file"
    
    # Clean up
    rm "$temp_story"
    
    # Add a visual separator
    echo -e "\n${CYAN}=========================================${NC}"
    echo -e "${YELLOW}Would you like to post this story and image? (y/n)${NC}"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Posting story and image...${NC}"
        
        # Move files to permanent locations
        local timestamp=$(date +%s)
        local setting=$(basename "$story_file" | sed -n 's/story_\([^_]*\)_.*/\1/p')
        local style=$(basename "$image_file" | sed -n 's/image_[^_]*_\([^_]*\)_.*/\1/p')
        
        # Create permanent filenames
        local perm_story="output/stories/story_${setting}_${timestamp}.txt"
        local perm_image="output/images/image_${setting}_${style}_${timestamp}.png"
        
        # Move files
        cp "$story_file" "$perm_story"
        cp "$image_file" "$perm_image"
        
        # Post using the regular command
        run_generator "" "" "" false "--post-files" "$perm_story:$perm_image"
        
        echo -e "${GREEN}Story and image have been posted and saved to permanent storage${NC}"
    else
        echo -e "${YELLOW}Preview closed without posting.${NC}"
    fi
}

# Function to preview generation without posting
preview_generation() {
    echo -e "\n${BLUE}Preview Generation${NC}"
    
    # Create/ensure the preview directory exists and is empty
    local preview_dir="output/preview_files"
    mkdir -p "$preview_dir"
    rm -f "$preview_dir"/*
    
    # Setting selection
    echo -e "\n${BLUE}Select setting (or 'random'):${NC}"
    for i in "${!SETTINGS[@]}"; do
        echo -e "${CYAN}$((i+1)))${NC} ${SETTINGS[$i]}"
    done
    echo -e "${CYAN}$((${#SETTINGS[@]}+1)))${NC} random"
    
    read -p "Enter setting number [$((${#SETTINGS[@]}+1))]: " setting_num
    if [[ $setting_num -le ${#SETTINGS[@]} ]]; then
        setting="${SETTINGS[$((setting_num-1))]}"
    else
        setting="random"
    fi

    # Style selection
    echo -e "\n${BLUE}Select style (or 'random'):${NC}"
    for i in "${!STYLES[@]}"; do
        echo -e "${CYAN}$((i+1)))${NC} ${STYLES[$i]}"
    done
    echo -e "${CYAN}$((${#STYLES[@]}+1)))${NC} random"
    
    read -p "Enter style number [$((${#STYLES[@]}+1))]: " style_num
    if [[ $style_num -le ${#STYLES[@]} ]]; then
        style="${STYLES[$((style_num-1))]}"
    else
        style="random"
    fi

    # Generate content with output to preview directory
    echo -e "${BLUE}Generating new story and image...${NC}"
    run_generator "$setting" "$style" "story image" true "--output-dir" "$preview_dir"
    
    # Find the story and image files in the preview directory
    local story_file=$(find "$preview_dir" -name "story_*.txt" | head -n 1)
    local image_file=$(find "$preview_dir" -name "image_*.png" | head -n 1)
    
    if [[ -n "$story_file" && -n "$image_file" && -f "$story_file" && -f "$image_file" ]]; then
        echo -e "${GREEN}Found story: $(basename "$story_file")${NC}"
        echo -e "${GREEN}Found image: $(basename "$image_file")${NC}"
        
        preview_story_and_image "$story_file" "$image_file"
    else
        echo -e "${RED}Error: Could not find generated files in preview directory${NC}"
        echo -e "${YELLOW}Preview directory contents:${NC}"
        ls -la "$preview_dir"
    fi
}

# Function to display timezone information with user timezone
display_timezone_info() {
    local utc_time=$(TZ=UTC date +"%H:%M")
    local server_time=$(date +"%H:%M")
    local server_tz_name=$(date +"%Z")
    local server_tz_offset=$(date +"%z")
    
    echo -e "${BLUE}Timezone Information:${NC}"
    echo -e "  • Server time: ${server_time} ${server_tz_name} (${server_tz_offset})"
    echo -e "  • UTC time:    ${utc_time} UTC"
    
    # If user timezone is set, show it
    if [ -n "$USER_TZ" ]; then
        local user_time=$(TZ="$USER_TZ" date +"%H:%M")
        echo -e "  • Your time:   ${user_time} $USER_TZ_NAME ($USER_TZ_OFFSET)"
    fi
    echo ""
}

# Function to convert between user local time and UTC
convert_user_to_utc() {
    local local_hour=$1
    local local_minute=$2
    
    # Use specified offset instead of system offset
    local tz_offset="$USER_TZ_OFFSET"
    local sign=${tz_offset:0:1}
    local tz_hours=${tz_offset:1:2}
    local tz_mins=${tz_offset:3:2}
    
    # Calculate total minutes offset
    local total_offset_mins=$((tz_hours * 60 + tz_mins))
    if [ "$sign" = "+" ]; then
        total_offset_mins=$((0 - total_offset_mins))
    fi
    
    # Convert local time to minutes since midnight
    local local_mins=$((local_hour * 60 + local_minute))
    
    # Apply offset to get UTC minutes
    local utc_mins=$((local_mins + total_offset_mins))
    
    # Handle day boundaries
    while [ $utc_mins -lt 0 ]; do
        utc_mins=$((utc_mins + 1440))  # Add 24 hours in minutes
    done
    while [ $utc_mins -ge 1440 ]; do
        utc_mins=$((utc_mins - 1440))  # Subtract 24 hours in minutes
    done
    
    # Convert back to hours and minutes
    local utc_hour=$((utc_mins / 60))
    local utc_minute=$((utc_mins % 60))
    
    echo "$utc_hour $utc_minute"
}

# Function to convert UTC time to user local time
convert_utc_to_user() {
    local utc_hour=$1
    local utc_minute=$2
    
    # Use specified offset instead of system offset
    local tz_offset="$USER_TZ_OFFSET"
    local sign=${tz_offset:0:1}
    local tz_hours=${tz_offset:1:2}
    local tz_mins=${tz_offset:3:2}
    
    # Calculate total minutes offset
    local total_offset_mins=$((tz_hours * 60 + tz_mins))
    if [ "$sign" = "-" ]; then
        total_offset_mins=$((0 - total_offset_mins))
    fi
    
    # Convert UTC time to minutes since midnight
    local utc_mins=$((utc_hour * 60 + utc_minute))
    
    # Apply offset to get local minutes
    local local_mins=$((utc_mins + total_offset_mins))
    
    # Handle day boundaries
    local day_shift="same day"
    if [ $local_mins -lt 0 ]; then
        local_mins=$((local_mins + 1440))  # Add 24 hours in minutes
        day_shift="previous day"
    elif [ $local_mins -ge 1440 ]; then
        local_mins=$((local_mins - 1440))  # Subtract 24 hours in minutes
        day_shift="next day"
    fi
    
    # Convert back to hours and minutes
    local local_hour=$((local_mins / 60))
    local local_minute=$((local_mins % 60))
    
    echo "$local_hour $local_minute $day_shift"
}

# Function to prompt for timezone selection
select_timezone() {
    echo -e "\n${CYAN}Timezone Selection${NC}"
    echo -e "${YELLOW}Please select your timezone:${NC}"
    
    # Common US timezones
    echo -e "${BLUE}US Timezones:${NC}"
    echo -e "1) Eastern (UTC-05:00/UTC-04:00 DST)"
    echo -e "2) Central (UTC-06:00/UTC-05:00 DST)"
    echo -e "3) Mountain (UTC-07:00/UTC-06:00 DST)"
    echo -e "4) Pacific (UTC-08:00/UTC-07:00 DST)"
    echo -e "5) Alaska (UTC-09:00/UTC-08:00 DST)"
    echo -e "6) Hawaii (UTC-10:00)"
    
    # European/Other timezones
    echo -e "\n${BLUE}European/Other Timezones:${NC}"
    echo -e "7) UK/Ireland (UTC+00:00/UTC+01:00 DST)"
    echo -e "8) Central Europe (UTC+01:00/UTC+02:00 DST)"
    echo -e "9) Eastern Europe (UTC+02:00/UTC+03:00 DST)"
    echo -e "10) India (UTC+05:30)"
    echo -e "11) Japan/Korea (UTC+09:00)"
    echo -e "12) Australia Eastern (UTC+10:00/UTC+11:00 DST)"
    
    # Custom option
    echo -e "\n13) Enter custom UTC offset"
    echo -e "14) Use server timezone (UTC)"
    
    read -p "Enter your choice (1-14): " tz_choice
    
    case $tz_choice in
        1)  USER_TZ="America/New_York"; USER_TZ_NAME="Eastern Time"; USER_TZ_OFFSET="-0500" ;;
        2)  USER_TZ="America/Chicago"; USER_TZ_NAME="Central Time"; USER_TZ_OFFSET="-0600" ;;
        3)  USER_TZ="America/Denver"; USER_TZ_NAME="Mountain Time"; USER_TZ_OFFSET="-0700" ;;
        4)  USER_TZ="America/Los_Angeles"; USER_TZ_NAME="Pacific Time"; USER_TZ_OFFSET="-0800" ;;
        5)  USER_TZ="America/Anchorage"; USER_TZ_NAME="Alaska Time"; USER_TZ_OFFSET="-0900" ;;
        6)  USER_TZ="Pacific/Honolulu"; USER_TZ_NAME="Hawaii Time"; USER_TZ_OFFSET="-1000" ;;
        7)  USER_TZ="Europe/London"; USER_TZ_NAME="UK Time"; USER_TZ_OFFSET="+0000" ;;
        8)  USER_TZ="Europe/Paris"; USER_TZ_NAME="Central European"; USER_TZ_OFFSET="+0100" ;;
        9)  USER_TZ="Europe/Helsinki"; USER_TZ_NAME="Eastern European"; USER_TZ_OFFSET="+0200" ;;
        10) USER_TZ="Asia/Kolkata"; USER_TZ_NAME="India Time"; USER_TZ_OFFSET="+0530" ;;
        11) USER_TZ="Asia/Tokyo"; USER_TZ_NAME="Japan Time"; USER_TZ_OFFSET="+0900" ;;
        12) USER_TZ="Australia/Sydney"; USER_TZ_NAME="Australia Eastern"; USER_TZ_OFFSET="+1000" ;;
        13) 
            echo -e "\n${YELLOW}Enter your UTC offset in ±HHMM format${NC}"
            echo -e "Examples: -0500 (EST), +0100 (CET), +0530 (IST)"
            read -p "UTC offset: " custom_offset
            
            # Validate format
            if [[ "$custom_offset" =~ ^[+-][0-1][0-9][0-5][0-9]$ ]]; then
                USER_TZ="Etc/GMT$(echo "$custom_offset" | sed 's/+/-/' | sed 's/-/+/' | sed 's/[0-9][0-9]$//')"
                USER_TZ_NAME="UTC$custom_offset"
                USER_TZ_OFFSET="$custom_offset"
            else
                echo -e "${RED}Invalid format. Using UTC.${NC}"
                USER_TZ="UTC"
                USER_TZ_NAME="UTC"
                USER_TZ_OFFSET="+0000"
            fi
            ;;
        14)
            USER_TZ="UTC"
            USER_TZ_NAME="UTC"
            USER_TZ_OFFSET="+0000"
            ;;
        *)
            echo -e "${RED}Invalid choice. Using UTC.${NC}"
            USER_TZ="UTC"
            USER_TZ_NAME="UTC" 
            USER_TZ_OFFSET="+0000"
            ;;
    esac
    
    # Check current time in the selected timezone
    local user_time=$(TZ="$USER_TZ" date +"%H:%M")
    echo -e "\n${GREEN}Timezone set to $USER_TZ_NAME ($USER_TZ_OFFSET)${NC}"
    echo -e "${BLUE}Your current time: $user_time${NC}"
    
    # Save to configuration if possible
    if [ -d "config" ] || mkdir -p "config" 2>/dev/null; then
        echo "USER_TZ=$USER_TZ" > "config/timezone.conf"
        echo "USER_TZ_NAME=$USER_TZ_NAME" >> "config/timezone.conf"
        echo "USER_TZ_OFFSET=$USER_TZ_OFFSET" >> "config/timezone.conf"
        echo -e "${GREEN}Timezone preference saved${NC}"
    fi
}

# Function to load timezone configuration
load_timezone_config() {
    if [ -f "config/timezone.conf" ]; then
        source "config/timezone.conf"
        local user_time=$(TZ="$USER_TZ" date +"%H:%M")
        echo -e "${BLUE}Loaded timezone: $USER_TZ_NAME ($USER_TZ_OFFSET)${NC}"
        echo -e "${BLUE}Your current time: $user_time${NC}"
        return 0
    else
        # No saved timezone
        return 1
    fi
}

# Function to check cron status and debug issues
check_cron_status() {
    echo -e "\n${BLUE}Checking cron service status...${NC}"
    
    # Check if cron service is running
    if systemctl is-active --quiet cron 2>/dev/null || service cron status >/dev/null 2>&1 || pgrep -x crond >/dev/null; then
        echo -e "${GREEN}✓ Cron service is running${NC}"
    else
        echo -e "${RED}✗ Cron service appears to be inactive${NC}"
        echo -e "${YELLOW}Try running: sudo service cron start${NC}"
        return 1
    fi
    
    # Check if the user has cron permissions
    if command -v getfacl >/dev/null && getfacl /usr/bin/crontab 2>/dev/null | grep -q "$(whoami)"; then
        echo -e "${GREEN}✓ User has crontab permissions${NC}"
    elif groups | grep -qE 'crontab|sudo|root|admin'; then
        echo -e "${GREEN}✓ User is in a group with crontab permissions${NC}"
    else
        echo -e "${YELLOW}⚠ Cannot verify crontab permissions${NC}"
    fi
    
    # Verify crontab entries
    if crontab -l 2>/dev/null | grep -q "AI_FUTURE"; then
        echo -e "${GREEN}✓ AI Future crontab entries exist${NC}"
        
        # Show the actual crontab entry for verification
        echo -e "${BLUE}Current crontab entry:${NC}"
        crontab -l | grep "AI_FUTURE" | sed 's/^/    /'
    else
        echo -e "${RED}✗ No AI Future entries in crontab${NC}"
        return 1
    fi
    
    # Check scheduler script permissions
    local scheduler_scripts=$(find scheduler -name "*.sh" 2>/dev/null)
    if [ -n "$scheduler_scripts" ]; then
        for script in $scheduler_scripts; do
            if [ -x "$script" ]; then
                echo -e "${GREEN}✓ Scheduler script is executable: $script${NC}"
            else
                echo -e "${RED}✗ Scheduler script is NOT executable: $script${NC}"
                echo -e "${YELLOW}  Fix with: chmod +x $script${NC}"
            fi
        done
    else
        echo -e "${RED}✗ No scheduler scripts found${NC}"
        return 1
    fi
    
    # Check for cron logs
    local cron_log=""
    for log_file in /var/log/syslog /var/log/cron /var/log/cron.log /var/log/messages; do
        if [ -f "$log_file" ] && grep -q "CRON" "$log_file" 2>/dev/null; then
            cron_log="$log_file"
            break
        fi
    done
    
    if [ -n "$cron_log" ]; then
        echo -e "${GREEN}✓ Found cron logs in $cron_log${NC}"
        echo -e "${YELLOW}  You can check cron activity with: sudo grep CRON $cron_log | tail${NC}"
    else
        echo -e "${YELLOW}⚠ Could not locate cron logs${NC}"
    fi
    
    # Add a test cron job to run in 2 minutes
    echo -e "\n${BLUE}Would you like to add a test cron job to run in 2 minutes?${NC}"
    echo -e "${YELLOW}This will help verify if cron is working correctly${NC}"
    read -p "Add test job? (y/n): " add_test
    
    if [[ "$add_test" =~ ^[Yy]$ ]]; then
        # Create a test script
        mkdir -p debug
        local test_script="debug/cron_test_$(date +%s).sh"
        
        cat > "$test_script" << 'EOF'
#!/bin/bash
echo "Cron test executed at $(date)" > "debug/cron_test_result.txt"
# Try to write to the logs directory if it exists
if [ -d "logs" ]; then
    echo "Cron test executed at $(date)" > "logs/cron_test_result.txt"
fi
# Try to create a flag file with more debug info
{
    echo "=== CRON TEST RESULTS ==="
    echo "Date: $(date)"
    echo "User: $(whoami)"
    echo "Working Directory: $(pwd)"
    echo "PATH: $PATH"
    echo "Environment Variables:"
    env | sort
    echo "========================="
} > "debug/cron_debug_$(date +%s).txt"
EOF
        
        chmod +x "$test_script"
        
        # Calculate a time 2 minutes from now
        local current_min=$(date +%M)
        local current_hour=$(date +%H)
        local test_min=$((current_min + 2))
        local test_hour=$current_hour
        
        if [ $test_min -ge 60 ]; then
            test_min=$((test_min - 60))
            test_hour=$((test_hour + 1))
            if [ $test_hour -ge 24 ]; then
                test_hour=0
            fi
        fi
        
        # Add to crontab
        local cron_cmd="$test_min $test_hour * * * $(pwd)/$test_script # AI_FUTURE_TEST"
        (crontab -l 2>/dev/null | grep -v "AI_FUTURE_TEST"; echo "$cron_cmd") | crontab -
        
        echo -e "${GREEN}Test job scheduled for $(date -d "$test_hour:$test_min" +"%H:%M")${NC}"
        echo -e "${YELLOW}Check debug/cron_test_result.txt in 2-3 minutes${NC}"
        echo -e "${YELLOW}If the file doesn't appear, cron is not running correctly${NC}"
    fi
    
    echo -e "\n${BLUE}Scheduler Troubleshooting Tips:${NC}"
    echo -e "1. ${YELLOW}Make sure all scheduler scripts are executable (chmod +x)${NC}"
    echo -e "2. ${YELLOW}Use absolute paths in crontab entries${NC}"
    echo -e "3. ${YELLOW}Check if cron service is running${NC}"
    echo -e "4. ${YELLOW}Look for errors in system logs${NC}"
    echo -e "5. ${YELLOW}Verify that the script can run manually${NC}"
    echo -e "6. ${YELLOW}Try running: sudo service cron restart${NC}"
}

# Add a crontab debugging function
diagnose_scheduler() {
    echo -e "\n${CYAN}Scheduler Diagnostics${NC}"
    echo -e "${BLUE}This will help diagnose issues with scheduled tasks${NC}"
    
    # Create a diagnostic output directory
    local diag_dir="diagnostics"
    mkdir -p "$diag_dir"
    local diag_file="$diag_dir/scheduler_diagnostics_$(date +%s).txt"
    
    # Start collecting diagnostic info
    {
        echo "=== AI FUTURE SCHEDULER DIAGNOSTICS ==="
        echo "Date: $(date)"
        echo "User: $(whoami)"
        echo "Working Directory: $(pwd)"
        echo ""
        
        echo "=== CRONTAB ENTRIES ==="
        if crontab -l 2>/dev/null; then
            crontab -l 2>/dev/null | grep -v "^#" | grep .
        else
            echo "No crontab entries or cannot access crontab"
        fi
        echo ""
        
        echo "=== SCHEDULER SCRIPTS ==="
        find . -path "*/scheduler/*.sh" -type f -ls 2>/dev/null || echo "No scheduler scripts found"
        echo ""
        
        echo "=== SCRIPT PERMISSIONS ==="
        for script in $(find . -path "*/scheduler/*.sh" -type f 2>/dev/null); do
            ls -la "$script"
            echo "File is executable: $([ -x "$script" ] && echo "Yes" || echo "No")"
            echo "File contents (first 10 lines):"
            head -10 "$script"
            echo "..."
        done
        echo ""
        
        echo "=== ENVIRONMENT ==="
        echo "PATH=$PATH"
        echo "SHELL=$SHELL"
        echo "HOME=$HOME"
        which uv || echo "uv command not found"
        echo ""
        
        echo "=== CRON SERVICE STATUS ==="
        systemctl status cron 2>/dev/null || service cron status 2>/dev/null || echo "Could not check cron service status"
        echo ""
        
        echo "=== RECENT LOGS ==="
        find logs -name "scheduler_*.log" -type f -mtime -1 2>/dev/null | sort -r | head -3 | while read -r log; do
            echo "=== $log ==="
            cat "$log" 2>/dev/null || echo "Could not read log file"
            echo ""
        done
        
        echo "=== SYSTEM CRON LOGS ==="
        for log in /var/log/syslog /var/log/cron /var/log/cron.log /var/log/messages; do
            if [ -f "$log" ] && grep -q "CRON" "$log" 2>/dev/null; then
                echo "=== Recent entries from $log ==="
                sudo grep CRON "$log" 2>/dev/null | tail -20 || echo "Could not access log (try running as root)"
                break
            fi
        done
        
        echo "=== END OF DIAGNOSTICS ==="
    } > "$diag_file"
    
    echo -e "${GREEN}Diagnostic information saved to: $diag_file${NC}"
    echo -e "${YELLOW}Please check this file for insights into scheduler issues${NC}"
    
    # Offer to run the most recent scheduler script manually
    local latest_script=$(find scheduler -name "*.sh" -type f -exec ls -t {} \; 2>/dev/null | head -1)
    if [ -n "$latest_script" ]; then
        echo -e "\n${BLUE}Would you like to run the latest scheduler script manually?${NC}"
        echo -e "${YELLOW}This will help determine if the script itself works correctly${NC}"
        read -p "Run script? (y/n): " run_script
        
        if [[ "$run_script" =~ ^[Yy]$ ]]; then
            echo -e "${GREEN}Running: $latest_script${NC}"
            "$latest_script"
            echo -e "${YELLOW}Check the logs directory for results${NC}"
        fi
    fi
    
    # Run the cron status check
    check_cron_status
}

# Function to manage scheduling with improved reliability and timezone awareness
manage_scheduling() {
    # First check if we have saved timezone settings
    if ! load_timezone_config; then
        echo -e "${YELLOW}No timezone configuration found${NC}"
        select_timezone
    fi
    
    while true; do
    echo -e "\n${GREEN}Scheduling Management${NC}"
        
        # Display timezone information
        display_timezone_info
        echo -e "${BLUE}Scheduled posts will be published automatically at the specified times${NC}"
    echo -e "${YELLOW}1)${NC} Set up daily schedule"
        echo -e "${YELLOW}2)${NC} Set up weekly schedule (specific day)"
    echo -e "${YELLOW}3)${NC} View current schedule"
    echo -e "${YELLOW}4)${NC} Remove all schedules"
        echo -e "${YELLOW}5)${NC} Test scheduler now (for debugging)"
        echo -e "${YELLOW}6)${NC} Change your timezone"
        echo -e "${YELLOW}7)${NC} Diagnose scheduler issues"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo -e "${YELLOW}q)${NC} Quit"

    read -p "Enter your choice: " schedule_choice

    case $schedule_choice in
            1|2)
                # Common code for daily (1) or weekly (2) schedule
                if [ "$schedule_choice" -eq 1 ]; then
                    echo -e "\n${CYAN}Daily Post Schedule${NC}"
                    schedule_type="daily"
                else
                    echo -e "\n${CYAN}Weekly Post Schedule${NC}"
                    echo -e "${BLUE}Select day of week:${NC}"
                    echo -e "${YELLOW}0)${NC} Sunday"
                    echo -e "${YELLOW}1)${NC} Monday"
                    echo -e "${YELLOW}2)${NC} Tuesday"
                    echo -e "${YELLOW}3)${NC} Wednesday"
                    echo -e "${YELLOW}4)${NC} Thursday"
                    echo -e "${YELLOW}5)${NC} Friday"
                    echo -e "${YELLOW}6)${NC} Saturday"
                    read -p "Enter day (0-6): " weekday
                    
                    if ! [[ "$weekday" =~ ^[0-6]$ ]]; then
                        echo -e "${RED}Invalid day. Please enter a number between 0-6.${NC}"
                        continue
                    fi
                    schedule_type="weekly"
                    day_names=("Sunday" "Monday" "Tuesday" "Wednesday" "Thursday" "Friday" "Saturday")
                fi
                
                # Time entry in user's local timezone
                echo -e "\n${BLUE}Enter time in YOUR timezone ($USER_TZ_NAME)${NC}"
                echo -e "${BLUE}Your current time: $(TZ="$USER_TZ" date +"%H:%M")${NC}"
                read -p "Enter hour (0-23): " local_hour
                read -p "Enter minute (0-59): " local_minute
                
                # Validate input
                if ! [[ "$local_hour" =~ ^[0-9]+$ ]] || [ "$local_hour" -lt 0 ] || [ "$local_hour" -gt 23 ]; then
                    echo -e "${RED}Invalid hour. Please enter a number between 0-23.${NC}"
                    continue
                fi
                
                if ! [[ "$local_minute" =~ ^[0-9]+$ ]] || [ "$local_minute" -lt 0 ] || [ "$local_minute" -gt 59 ]; then
                    echo -e "${RED}Invalid minute. Please enter a number between 0-59.${NC}"
                    continue
                fi
                
                # Convert to UTC
                IFS=' ' read -r hour minute <<< "$(convert_user_to_utc "$local_hour" "$local_minute")"
                echo -e "${GREEN}Converting your local time ${local_hour}:$(printf "%02d" $local_minute) to UTC ${hour}:$(printf "%02d" $minute)${NC}"
                
                # Get absolute paths
                script_path="$(readlink -f "$0")"
                script_dir="$(dirname "$script_path")"
                
                # Create crontab entry using the direct command approach
                if [ "$schedule_type" = "daily" ]; then
                    cron_comment="# AI_FUTURE_DAILY"
                    cron_cmd="$minute $hour * * * cd $script_dir && ./$(basename "$script_path") generate random random $cron_comment"
                else  # weekly
                    cron_comment="# AI_FUTURE_WEEKLY_${weekday}"
                    cron_cmd="$minute $hour * * $weekday cd $script_dir && ./$(basename "$script_path") generate random random $cron_comment"
                fi

                # Remove any existing entries with the same comment
                (crontab -l 2>/dev/null | grep -v "$cron_comment"; echo "$cron_cmd") | crontab -
                
                # Confirm settings
                if [ "$schedule_type" = "daily" ]; then
                    echo -e "${GREEN}Daily post scheduled for ${hour}:$(printf "%02d" $minute) UTC${NC}"
                    echo -e "${GREEN}(${local_hour}:$(printf "%02d" $local_minute) in your $USER_TZ_NAME timezone)${NC}"
                else
                    echo -e "${GREEN}Weekly post scheduled for ${hour}:$(printf "%02d" $minute) UTC every ${day_names[$weekday]}${NC}"
                    echo -e "${GREEN}(${local_hour}:$(printf "%02d" $local_minute) in your $USER_TZ_NAME timezone)${NC}"
                fi
                
                echo -e "${BLUE}Schedule details:${NC}"
                echo -e "  • Scheduler script: $script_path"
                echo -e "  • Log files will be created in: $script_dir/logs"
                echo -e "  • The script will automatically use reliable environment setup"
                echo -e "${YELLOW}You can test the scheduler immediately with option 5${NC}"
                ;;
                
            3)
                echo -e "\n${BLUE}Current Schedule:${NC}"
                if crontab -l 2>/dev/null | grep -q "AI_FUTURE"; then
                    echo -e "${CYAN}Found the following scheduled tasks:${NC}"
                    crontab -l | grep "AI_FUTURE" | while read -r line; do
                        # Parse the crontab entry for better display
                        min=$(echo "$line" | awk '{print $1}')
                        hour=$(echo "$line" | awk '{print $2}')
                        dow=$(echo "$line" | awk '{print $5}')
                        
                        # Get local time equivalent
                        IFS=' ' read -r local_hour local_minute day_shift <<< "$(convert_utc_to_user "$hour" "$min")"
                        
                        # Format display based on schedule type
                        if [[ "$line" == *"AI_FUTURE_DAILY"* ]]; then
                            echo -e "${CYAN}• Daily at ${hour}:$(printf "%02d" $min) UTC${NC}"
                            echo -e "${CYAN}  (${local_hour}:$(printf "%02d" $local_minute) in your $USER_TZ_NAME timezone, ${day_shift})${NC}"
                        elif [[ "$line" == *"AI_FUTURE_WEEKLY"* ]]; then
                            day_num=$(echo "$line" | sed -n 's/.*AI_FUTURE_WEEKLY_\([0-6]\).*/\1/p')
                            if [ -z "$day_num" ]; then day_num="$dow"; fi
                            day_names=("Sunday" "Monday" "Tuesday" "Wednesday" "Thursday" "Friday" "Saturday")
                            day_name="${day_names[$day_num]}"
                            echo -e "${CYAN}• Weekly on $day_name at ${hour}:$(printf "%02d" $min) UTC${NC}"
                            echo -e "${CYAN}  (${local_hour}:$(printf "%02d" $local_minute) in your $USER_TZ_NAME timezone, ${day_shift})${NC}"
                        else
                            echo -e "${CYAN}• Custom: $min $hour * * $dow${NC}"
                            echo -e "${CYAN}  (${local_hour}:$(printf "%02d" $local_minute) in your $USER_TZ_NAME timezone, ${day_shift})${NC}"
                        fi
                    done
                    
                    # Check logs directory for recent runs
                    if [ -d "logs" ]; then
                        recent_logs=$(find "logs" -name "scheduler_*" -type f -mtime -1 | sort -r | head -3)
                        if [ -n "$recent_logs" ]; then
                            echo -e "\n${BLUE}Recent scheduler logs:${NC}"
                            for log in $recent_logs; do
                                log_time=$(echo "$log" | sed -n 's/.*scheduler_\([0-9]\{8\}_[0-9]\{6\}\).log/\1/p')
                                log_time_fmt=$(date -d "${log_time:0:8} ${log_time:9:2}:${log_time:11:2}:${log_time:13:2}" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)
                                
                                if [ -n "$log_time_fmt" ]; then
                                    echo -e "${YELLOW}• $log_time_fmt${NC}"
                                else
                                    echo -e "${YELLOW}• $log${NC}"
                                fi
                                
                                # Check if log contains errors
                                if grep -q "ERROR" "$log"; then
                                    echo -e "${RED}  Contains errors! Check $log${NC}"
                                else
                                    echo -e "${GREEN}  No errors detected${NC}"
                                fi
                            done
                        else
                            echo -e "\n${YELLOW}No recent scheduler logs found${NC}"
                        fi
                    fi
                else
                    echo -e "${YELLOW}No schedules found${NC}"
                fi
                ;;
                
            4)
                echo -e "\n${RED}WARNING: This will remove all scheduled AI Future tasks!${NC}"
            read -p "Are you sure? (yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                    crontab -l 2>/dev/null | grep -v "AI_FUTURE" | crontab -
                    echo -e "${GREEN}All AI Future schedules removed${NC}"
                else
                    echo -e "${YELLOW}Operation cancelled${NC}"
                fi
                ;;
                
            5)
                echo -e "\n${BLUE}Testing scheduler...${NC}"
                
                # Find the most recent scheduler script
                script_dir="scheduler"
                if [ ! -d "$script_dir" ]; then
                    echo -e "${RED}No scheduler scripts found. Please set up a schedule first.${NC}"
                    continue
                fi
                
                latest_script=$(find "$script_dir" -name "*.sh" -type f -exec ls -t {} \; | head -1)
                
                if [ -z "$latest_script" ]; then
                    echo -e "${RED}No scheduler scripts found. Please set up a schedule first.${NC}"
                    continue
                fi
                
                echo -e "${YELLOW}Running scheduler script: $latest_script${NC}"
                echo -e "${BLUE}This will generate and post content immediately${NC}"
                read -p "Continue? (y/n): " test_confirm
                
                if [[ "$test_confirm" =~ ^[Yy]$ ]]; then
                    echo -e "${GREEN}Executing scheduler - check logs folder for results${NC}"
                    "$latest_script" &
                    echo -e "${YELLOW}Scheduler is running in background.${NC}"
                    echo -e "${YELLOW}Check logs directory in a few moments for results.${NC}"
                else
                    echo -e "${YELLOW}Test cancelled${NC}"
                fi
                ;;
                
            6)
                select_timezone
                ;;
                
            7)
                # Run the scheduler diagnostics
                diagnose_scheduler
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
        
        # Pause after each action
        read -p "Press Enter to continue..."
    done
}

# Function to post a preview
post_preview() {
    local preview_file=$1
    
    if [ ! -f "$preview_file" ]; then
        echo -e "${RED}Preview file not found: $preview_file${NC}"
        return 1
    fi
    
    echo -e "${BLUE}Preview content:${NC}"
    cat "$preview_file"
    
    echo -e "\n${YELLOW}Would you like to post this content to Twitter? [y/N]:${NC}"
    read -p "" post_choice
    
    if [[ $post_choice =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Posting preview content...${NC}"
        run_generator "" "" "" false "--post-preview" "$preview_file"
    else
        echo -e "${YELLOW}Posting cancelled${NC}"
    fi
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
                            post_preview "$preview_path"
                        fi
                    fi
                fi
            fi
            ;;
        4)
            echo -e "${BLUE}Recent logs:${NC}"
            ls -lt logs/ | head -n 5
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

# Updated check_system_status function to properly detect schedules
check_system_status() {
    echo -e "\n${BLUE}System Status${NC}"
    
    # Check if credentials exist
    if [ -f ".env" ]; then
        echo -e "${GREEN}✓${NC} Credentials file found"
    else
        echo -e "${RED}✗${NC} Credentials file missing"
    fi

    # Check output directories
    for dir in "output/stories" "output/images" "output/previews"; do
        if [ -d "$dir" ]; then
            echo -e "${GREEN}✓${NC} $dir exists"
            echo -e "   Files: $(ls -1 "$dir" | wc -l)"
        else
            echo -e "${RED}✗${NC} $dir missing"
        fi
    done

    # Check scheduled tasks using the AI_FUTURE marker
    if crontab -l 2>/dev/null | grep -q "AI_FUTURE"; then
        echo -e "${GREEN}✓${NC} Scheduled tasks found"
        echo -e "${BLUE}Current schedule:${NC}"
        crontab -l | grep "AI_FUTURE" | while read -r line; do
            # Parse the crontab entry for better display
            min=$(echo "$line" | awk '{print $1}')
            hour=$(echo "$line" | awk '{print $2}')
            
            # Format display based on schedule type
            if [[ "$line" == *"AI_FUTURE_DAILY"* ]]; then
                echo -e "  • Daily at ${hour}:$(printf "%02d" $min)"
            elif [[ "$line" == *"AI_FUTURE_WEEKLY"* ]]; then
                dow=$(echo "$line" | awk '{print $5}')
                day_names=("Sunday" "Monday" "Tuesday" "Wednesday" "Thursday" "Friday" "Saturday")
                day_name="${day_names[$dow]}"
                echo -e "  • Weekly on $day_name at ${hour}:$(printf "%02d" $min)"
            else
                echo -e "  • Custom schedule"
            fi
        done
    else
        echo -e "${YELLOW}!${NC} No scheduled tasks"
    fi

    # Show disk usage
    echo -e "\n${BLUE}Disk Usage:${NC}"
    du -sh output/* 2>/dev/null || echo "No output files yet"
}

# Function to show help
show_help() {
    echo -e "\n${BLUE}AI Solarpunk Story Bot - Help${NC}"
    echo -e "Available commands:"
    echo -e "  ${YELLOW}./ai_future.sh${NC} - Interactive mode"
    echo -e "  ${YELLOW}./ai_future.sh generate [setting] [style]${NC} - Generate and post content"
    echo -e "  ${YELLOW}./ai_future.sh preview [setting] [style]${NC} - Generate preview without posting"
    echo -e "  ${YELLOW}./ai_future.sh status${NC} - Check system status"
    echo
    echo -e "Settings: ${CYAN}${SETTINGS[*]}${NC}"
    echo -e "Styles: ${CYAN}${STYLES[*]}${NC}"
}

# Main menu function
show_menu() {
    echo -e "\n${GREEN}Select an action:${NC}"
    echo -e "${YELLOW}1)${NC} Generate content"
    echo -e "${YELLOW}2)${NC} Preview generation"
    echo -e "${YELLOW}3)${NC} Manage scheduling"
    echo -e "${YELLOW}4)${NC} View recent activity"
    echo -e "${YELLOW}5)${NC} Check system status"
    echo -e "${YELLOW}6)${NC} Cleanup and archive outputs"
    echo -e "${YELLOW}7)${NC} Clear preview files only"
    echo -e "${YELLOW}h)${NC} Show help"
    echo -e "${YELLOW}q)${NC} Quit"

    read -p "Enter your choice: " choice

    case $choice in
        1)
            generate_and_post
            ;;
        2)
            preview_generation
            ;;
        3)
            manage_scheduling
            ;;
        4)
            view_recent_activity
            ;;
        5)
            check_system_status
            ;;
        6)
            cleanup_outputs
            ;;
        7)
            clear_preview_files
            ;;
        h|H)
            show_help
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

# Main function
main() {
    show_header

    # If command-line arguments were provided
    if [ $# -gt 0 ]; then
        case "$1" in
            "generate")
                setting=${2:-"random"}
                style=${3:-"random"}
                run_generator "$setting" "$style" "story image post" false
                ;;
            "preview")
                setting=${2:-"random"}
                style=${3:-"random"}
                run_generator "$setting" "$style" "story image" true
                ;;
            "status")
                check_system_status
                ;;
            *)
                echo -e "${RED}Unknown command: $1${NC}"
                show_help
                exit 1
                ;;
        esac
        exit 0
    fi

    # Interactive mode
    while true; do
        show_menu
        echo
        read -p "Press Enter to continue..."
        clear
        show_header
    done
}

# Run the script
main "$@" 