#!/usr/bin/env python3
import json
import os
import shutil
from pathlib import Path

def show_current_status():
    print("\n" + "="*50)
    print("📊 CURRENT DATA STATUS")
    print("="*50)
    
    # Check characters
    continuity_file = "output/continuity.json"
    char_count = 0
    if os.path.exists(continuity_file):
        try:
            with open(continuity_file) as f:
                data = json.load(f)
                char_count = len(data.get('characters', []))
        except:
            char_count = 0
    
    # Check archives
    archive_dir = Path("archive")
    dated_dirs = 0
    archive_backups = 0
    if archive_dir.exists():
        dated_dirs = len([d for d in archive_dir.iterdir() if d.is_dir() and d.name.startswith("20")])
        archive_backups = len(list(archive_dir.glob("continuity.json.backup_*")))
    
    # Check worlds
    worlds_dir = Path("examples/worlds")
    world_files = 0
    custom_worlds = 0
    if worlds_dir.exists():
        world_files = len(list(worlds_dir.glob("*")))
        custom_worlds = len([f for f in worlds_dir.glob("*") if not f.name.startswith("example_")])
    
    print(f"👥 Characters: {char_count}")
    print(f"📁 Archive directories: {dated_dirs}")
    print(f"💾 Archive backup files: {archive_backups}")
    print(f"🌍 World documents: {world_files} total ({custom_worlds} custom)")
    
    # Show sizes
    os.system("du -sh archive/ output/ examples/ 2>/dev/null | sed 's/^/💽 /'")

def clear_characters():
    print("\n🗑️  Clearing character data...")
    
    # Reset continuity.json
    continuity_path = "output/continuity.json"
    empty_continuity = {
        "last_story_id": 0,
        "characters": [],
        "story_log": []
    }
    
    with open(continuity_path, 'w') as f:
        json.dump(empty_continuity, f, indent=2)
    
    # Move backup files to archive
    backup_files = list(Path("output").glob("continuity.json.backup_*"))
    if backup_files:
        archive_backup_dir = Path("archive/continuity_backups")
        archive_backup_dir.mkdir(exist_ok=True)
        
        for backup_file in backup_files:
            dest = archive_backup_dir / backup_file.name
            shutil.move(str(backup_file), str(dest))
    
    print(f"✅ Reset continuity and moved {len(backup_files)} backups to archive")

def clear_archives():
    archive_dir = Path("archive")
    if not archive_dir.exists():
        print("❌ No archive directory found")
        return
    
    dated_dirs = [d for d in archive_dir.iterdir() if d.is_dir() and d.name.startswith("20")]
    backup_files = list(archive_dir.glob("continuity.json.backup_*"))
    
    total_size = sum(item.stat().st_size for item in archive_dir.rglob("*") if item.is_file())
    size_mb = total_size / (1024 * 1024)
    
    print(f"\n📁 Will remove {len(dated_dirs)} archive directories")
    print(f"�� Will remove {len(backup_files)} backup files") 
    print(f"💽 Will free ~{size_mb:.1f} MB")
    
    confirm = input("🤔 Proceed? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Cancelled")
        return
    
    for item in dated_dirs:
        shutil.rmtree(item)
    for item in backup_files:
        item.unlink()
    
    print(f"✅ Cleared archives - freed {size_mb:.1f} MB!")

def clear_custom_worlds():
    worlds_dir = Path("examples/worlds")
    if not worlds_dir.exists():
        print("❌ No worlds directory found")
        return
    
    custom_files = [f for f in worlds_dir.glob("*") if not f.name.startswith("example_")]
    
    if not custom_files:
        print("✅ No custom world files to remove")
        return
    
    print(f"\n📄 Custom world files to remove:")
    for f in custom_files:
        size_kb = f.stat().st_size / 1024
        print(f"  • {f.name} ({size_kb:.1f} KB)")
    
    confirm = input(f"🤔 Remove {len(custom_files)} custom world files? (y/N): ")
    if confirm.lower() == 'y':
        for f in custom_files:
            f.unlink()
        print(f"✅ Removed {len(custom_files)} custom world files!")
    else:
        print("❌ Cancelled")

def main():
    while True:
        show_current_status()
        
        print("\n" + "="*50)
        print("🧹 CLEANUP OPTIONS")
        print("="*50)
        print("1) Clear characters & continuity (reset story history)")
        print("2) Clear archives (free up 301MB of old stories/images)")
        print("3) Clear custom world documents (keep examples)")
        print("4) Clear everything (nuclear option)")
        print("5) Refresh status")
        print("q) Quit")
        
        choice = input("\nChoose an option (1-5, q): ").strip().lower()
        
        if choice == '1':
            clear_characters()
        elif choice == '2':
            clear_archives()
        elif choice == '3':
            clear_custom_worlds()
        elif choice == '4':
            print("\n💥 NUCLEAR OPTION - Clear EVERYTHING!")
            confirm = input("🚨 Are you SURE? This will remove all data! (type 'YES' to confirm): ")
            if confirm == 'YES':
                clear_characters()
                clear_archives()
                clear_custom_worlds()
                print("💥 Nuclear cleanup complete!")
            else:
                print("❌ Nuclear option cancelled")
        elif choice == '5':
            continue
        elif choice == 'q':
            break
        else:
            print("❌ Invalid choice")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
