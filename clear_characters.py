#!/usr/bin/env python3
import json
import os
import shutil
from pathlib import Path

def clear_character_data():
    """Clear all character and continuity data."""
    print("🗑️  Clearing character and continuity data...")
    
    # Reset continuity.json to empty state
    continuity_path = "output/continuity.json"
    if os.path.exists(continuity_path):
        empty_continuity = {
            "last_story_id": 0,
            "characters": [],
            "story_log": []
        }
        with open(continuity_path, 'w') as f:
            json.dump(empty_continuity, f, indent=2)
        print(f"✅ Reset {continuity_path}")
    
    # Move backup files to archive
    backup_files = []
    for file in Path("output").glob("continuity.json.backup_*"):
        backup_files.append(file)
    
    if backup_files:
        archive_backup_dir = Path("archive/continuity_backups")
        archive_backup_dir.mkdir(exist_ok=True)
        
        for backup_file in backup_files:
            dest = archive_backup_dir / backup_file.name
            shutil.move(str(backup_file), str(dest))
            print(f"📦 Moved {backup_file.name} to archive")
    
    print(f"🎉 Cleared {len(backup_files)} backup files and reset continuity!")

if __name__ == "__main__":
    clear_character_data()
