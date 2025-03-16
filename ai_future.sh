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
STYLES=("photographic" "digital-art" "watercolor")

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

# Function to preview generation without posting
preview_generation() {
    echo -e "\n${BLUE}Preview Generation${NC}"
    
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

    run_generator "$setting" "$style" "story image" true
}

# Function to manage scheduling
manage_scheduling() {
    echo -e "\n${GREEN}Scheduling Management${NC}"
    echo -e "${YELLOW}1)${NC} Set up daily schedule"
    echo -e "${YELLOW}2)${NC} Set up weekly schedule"
    echo -e "${YELLOW}3)${NC} View current schedule"
    echo -e "${YELLOW}4)${NC} Remove all schedules"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo -e "${YELLOW}q)${NC} Quit"

    read -p "Enter your choice: " schedule_choice

    case $schedule_choice in
        1)
            read -p "Enter time (HH:MM): " time
            (crontab -l 2>/dev/null; echo "$time * * * * cd $(pwd) && ./ai_future.sh generate random") | crontab -
            echo -e "${GREEN}Daily schedule set for $time${NC}"
            ;;
        2)
            read -p "Enter time (HH:MM): " time
            (crontab -l 2>/dev/null; echo "$time * * */7 * cd $(pwd) && ./ai_future.sh generate random") | crontab -
            echo -e "${GREEN}Weekly schedule set for $time${NC}"
            ;;
        3)
            echo -e "${BLUE}Current schedule:${NC}"
            crontab -l | grep "ai_future.sh" || echo "No schedules found"
            ;;
        4)
            echo -e "${RED}WARNING: This will remove all scheduled tasks!${NC}"
            read -p "Are you sure? (yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                crontab -l | grep -v "ai_future.sh" | crontab -
                echo -e "${GREEN}All schedules removed${NC}"
            fi
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

# Function to post a preview
post_preview() {
    local preview_file=$1
    
    if [ ! -f "$preview_file" ]; then
        echo -e "${RED}Preview file not found: $preview_file${NC}"
        return 1
    }
    
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

# Main menu function
show_menu() {
    echo -e "\n${GREEN}Select an action:${NC}"
    echo -e "${YELLOW}1)${NC} Generate content"
    echo -e "${YELLOW}2)${NC} Preview generation"
    echo -e "${YELLOW}3)${NC} Manage scheduling"
    echo -e "${YELLOW}4)${NC} View recent activity"
    echo -e "${YELLOW}5)${NC} Check system status"
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

# Function to check system status
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

    # Check scheduled tasks
    if crontab -l 2>/dev/null | grep -q "ai_future.sh"; then
        echo -e "${GREEN}✓${NC} Scheduled tasks found"
        echo -e "${BLUE}Current schedule:${NC}"
        crontab -l | grep "ai_future.sh"
    else
        echo -e "${YELLOW}!${NC} No scheduled tasks"
    fi

    # Show disk usage
    echo -e "\n${BLUE}Disk Usage:${NC}"
    du -sh output/* 2>/dev/null || echo "No output files yet"
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