#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

def clear_archives():
    """Clear old generated content archives."""
    print("🗑️  Clearing old archives...")
    
    archive_dir = Path("archive")
    if not archive_dir.exists():
        print("❌ No archive directory found")
        return
    
    # Count and show what will be cleared
    dated_dirs = [d for d in archive_dir.iterdir() if d.is_dir() and d.name.startswith("20")]
    backup_files = list(archive_dir.glob("continuity.json.backup_*"))
    
    print(f"📁 Found {len(dated_dirs)} dated archive directories")
    print(f"💾 Found {len(backup_files)} continuity backup files")
    
    total_size = 0
    for item in archive_dir.rglob("*"):
        if item.is_file():
            total_size += item.stat().st_size
    
    size_mb = total_size / (1024 * 1024)
    print(f"💾 Total archive size: {size_mb:.1f} MB")
    
    # Ask for confirmation
    response = input("\n🤔 Clear all archives? This will delete generated stories and images. (y/N): ")
    if response.lower() != 'y':
        print("❌ Operation cancelled")
        return
    
    # Clear archives
    cleared_count = 0
    for item in dated_dirs:
        shutil.rmtree(item)
        cleared_count += 1
        print(f"🗑️  Removed {item.name}")
    
    for item in backup_files:
        item.unlink()
        print(f"🗑️  Removed {item.name}")
    
    print(f"🎉 Cleared {cleared_count} directories and {len(backup_files)} backup files!")
    print(f"�� Freed approximately {size_mb:.1f} MB of space")

if __name__ == "__main__":
    clear_archives()
