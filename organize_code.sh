#!/bin/bash

# Script to organize story generation modules
# This script preserves the main src/story_generator.py file and archives the duplicates

echo "Organizing story generation modules..."

# Create a backup directory
mkdir -p backup/src
mkdir -p backup/src/story_generation

# Check if the duplicate files exist and move them to the backup directory
if [ -f "src/story_generation.py" ]; then
    echo "Moving src/story_generation.py to backup directory..."
    mv src/story_generation.py backup/src/
fi

if [ -d "src/story_generation" ]; then
    echo "Moving src/story_generation directory contents to backup directory..."
    cp -r src/story_generation/* backup/src/story_generation/
fi

# Verify that src/story_generator.py exists and is being used
if [ ! -f "src/story_generator.py" ]; then
    echo "ERROR: Main story generator module src/story_generator.py does not exist!"
    exit 1
fi

echo "Verifying that src/story_generator.py is imported by ai_story_tweet_generator.py..."
grep -q "from src.story_generator import" src/ai_story_tweet_generator.py
if [ $? -ne 0 ]; then
    echo "WARNING: src/story_generator.py may not be imported by ai_story_tweet_generator.py!"
    echo "Please check the imports in ai_story_tweet_generator.py manually."
    exit 1
fi

echo "Organization complete!"
echo "The main story generation module is src/story_generator.py"
echo "Duplicate modules have been backed up to the backup/ directory"
echo "You can safely delete the backup directory if everything is working correctly."

exit 0 