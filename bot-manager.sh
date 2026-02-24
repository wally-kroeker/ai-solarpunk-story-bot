#!/bin/bash
# shellcheck shell=bash
# AI Solarpunk Story Bot - Simplified Single Story Generator using O3

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
SETTINGS=("urban" "coastal" "forest" "desert" "rural" "mountain" "arctic" "island" \
  "wetland" "grassland" "reef" "reclaimed-industrial" "geothermal" "sky-city" "subterranean" "orbital")
STYLES=("digital-art" "watercolor" "stylized" "solarpunk-nouveau" "retro-futurism" "isometric" \
  "paper-cut" "low-poly" "ukiyo-e" "stained-glass" "claymation" "pixel-art" "flat-vector" "impressionist" "holo-neon")

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
    echo -e "${YELLOW}============== Solarpunk Story Generator (O3 Model) ==============${NC}"
    echo -e "${GREEN}Generating 250-word stories with OpenAI O3${NC}"
}

# Function to generate a 250-word story using o3
generate_story() {
    local setting=$1
    local style=$2
    local post_mode=$3  # "preview", "post", or empty for prompt
    
    echo -e "${YELLOW}Generating 250-word solarpunk story with O3 model${NC}"
    echo -e "${BLUE}Setting: $setting | Style: $style${NC}"
    
    # Ensure proper output directories exist
    mkdir -p "output/stories" "output/images" "output/previews"
    
    # Determine features based on post mode
    local features="story,image"
    local cmd_args="--story-mode extended"
    
    if [[ "$post_mode" == "post" ]]; then
        features="story,image,post,thread"
        echo -e "${YELLOW}Will post as Twitter thread after generation${NC}"
    elif [[ "$post_mode" == "preview" ]]; then
        cmd_args="$cmd_args --preview"
        echo -e "${BLUE}Preview mode - will not post to Twitter${NC}"
    else
        # Ask user what they want to do
        echo -e "\n${YELLOW}Choose action:${NC}"
        echo "1) Preview only (generate but don't post)"
        echo "2) Generate and post to Twitter as thread"
        echo "3) Cancel"
        
        read -p "Enter your choice: " action_choice
        
        case $action_choice in
            1)
                cmd_args="$cmd_args --preview"
                echo -e "${BLUE}Preview mode selected${NC}"
                ;;
            2)
                features="story,image,post,thread"
                echo -e "${YELLOW}Will post as Twitter thread after generation${NC}"
                ;;
            3)
                echo -e "${YELLOW}Cancelled${NC}"
                return
                ;;
            *)
                echo -e "${RED}Invalid choice, defaulting to preview${NC}"
                cmd_args="$cmd_args --preview"
                ;;
        esac
    fi
    
    echo -e "${BLUE}Running O3 story generator...${NC}"
    
    # Generate the extended story using o3 model
    local cmd="uv run src/ai_story_tweet_generator.py --setting \"$setting\" --style \"$style\" --features \"$features\" $cmd_args"
    
    echo -e "${CYAN}Command: $cmd${NC}"
    
    # Run the command and capture its output
    if ! output=$(eval "$cmd" 2>&1); then
        echo -e "${RED}Error running O3 generator:${NC}"
        echo "$output"
        return 1
    fi
    
    echo -e "${GREEN}O3 Story generation completed!${NC}"
    echo "$output"
    
    # Find and display the generated story
    local story_file=$(find "output/stories" -name "story_${setting}_${style}_*.txt" -type f | head -n 1)
    if [[ -n "$story_file" && -f "$story_file" ]]; then
        echo -e "\n${CYAN}======= Generated 250-Word Story (O3 Model) =======${NC}"
        cat "$story_file"
        echo -e "\n${CYAN}===============================================${NC}"
        
        # Show character count
        local char_count=$(wc -c < "$story_file")
        echo -e "${YELLOW}Story length: $char_count characters (~$(echo $((char_count / 5)) | bc 2>/dev/null || echo $((char_count / 5))) words)${NC}"
        
        # Show image location
        local image_file=$(find "output/images" -name "${setting}_${style}_*.png" -type f | head -n 1)
        if [[ -n "$image_file" && -f "$image_file" ]]; then
            echo -e "${GREEN}Image saved: $image_file${NC}"
        fi
        
        # Check if it was posted
        if [[ "$features" == *"post"* ]]; then
            if echo "$output" | grep -q "Posted to Twitter\|tweet ID"; then
                echo -e "${GREEN}✓ Successfully posted to Twitter as thread!${NC}"
            else
                echo -e "${RED}× Posting may have failed - check output above${NC}"
            fi
        fi
    else
        echo -e "${RED}Story file not found${NC}"
    fi
    
    echo -e "\n${GREEN}Generation complete! Files saved in output/ directory.${NC}"
    read -p "Press Enter to continue..."
}

# Main menu - simplified
main_menu() {
    while true; do
        show_header
        echo -e "\n${YELLOW}Choose Generation Method:${NC}"
        echo "1) Preview only (select setting and style)"
        echo "2) Generate and post to Twitter (select setting and style)"
        echo "3) Random preview (random setting and style)"
        echo "4) Random post to Twitter (random setting and style)"
        echo "5) Exit"
        
        read -p "Enter your choice: " choice
        
        case $choice in
            1)
                echo -e "\n${YELLOW}Select Setting:${NC}"
                select setting in "${SETTINGS[@]}" "back"; do
                    if [[ $setting == "back" ]]; then
                        break
                    elif [[ -n $setting ]]; then
                        echo -e "\n${YELLOW}Select Style:${NC}"
                        select style in "${STYLES[@]}" "back"; do
                            if [[ $style == "back" ]]; then
                                break
                            elif [[ -n $style ]]; then
                                generate_story "$setting" "$style" "preview"
                                break
                            fi
                        done
                    fi
                    break
                done
                ;;
            2)
                echo -e "\n${YELLOW}Select Setting:${NC}"
                select setting in "${SETTINGS[@]}" "back"; do
                    if [[ $setting == "back" ]]; then
                        break
                    elif [[ -n $setting ]]; then
                        echo -e "\n${YELLOW}Select Style:${NC}"
                        select style in "${STYLES[@]}" "back"; do
                            if [[ $style == "back" ]]; then
                                break
                            elif [[ -n $style ]]; then
                                generate_story "$setting" "$style" "post"
                                break
                            fi
                        done
                    fi
                    break
                done
                ;;
            3)
                local random_setting=${SETTINGS[$RANDOM % ${#SETTINGS[@]}]}
                local random_style=${STYLES[$RANDOM % ${#STYLES[@]}]}
                echo -e "${YELLOW}Randomly selected: $random_setting + $random_style${NC}"
                generate_story "$random_setting" "$random_style" "preview"
                ;;
            4)
                local random_setting=${SETTINGS[$RANDOM % ${#SETTINGS[@]}]}
                local random_style=${STYLES[$RANDOM % ${#STYLES[@]}]}
                echo -e "${YELLOW}Randomly selected: $random_setting + $random_style${NC}"
                echo -e "${RED}⚠️  This will post to Twitter automatically!${NC}"
                read -p "Are you sure? (y/n): " confirm
                if [[ $confirm =~ ^[Yy]$ ]]; then
                    generate_story "$random_setting" "$random_style" "post"
                else
                    echo -e "${YELLOW}Cancelled${NC}"
                fi
                ;;
            5)
                echo -e "${GREEN}Goodbye!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid choice${NC}"
                ;;
        esac
    done
}

# Start the main menu
main_menu
