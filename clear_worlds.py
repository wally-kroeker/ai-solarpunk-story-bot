#!/usr/bin/env python3
import os
from pathlib import Path

def clear_custom_worlds():
    """Clear custom world documents."""
    print("🗑️  Managing world documents...")
    
    worlds_dir = Path("examples/worlds")
    if not worlds_dir.exists():
        print("❌ No worlds directory found")
        return
    
    # List all world files
    world_files = list(worlds_dir.glob("*"))
    example_files = [f for f in world_files if f.name.startswith("example_")]
    custom_files = [f for f in world_files if not f.name.startswith("example_")]
    
    print(f"📄 Found {len(example_files)} example world files")
    print(f"📄 Found {len(custom_files)} custom world files")
    
    if example_files:
        print("\n📋 Example files (will be kept):")
        for f in example_files:
            print(f"  ✅ {f.name}")
    
    if custom_files:
        print("\n📋 Custom files:")
        for f in custom_files:
            size_kb = f.stat().st_size / 1024
            print(f"  📄 {f.name} ({size_kb:.1f} KB)")
        
        response = input(f"\n🤔 Remove {len(custom_files)} custom world files? (y/N): ")
        if response.lower() == 'y':
            for f in custom_files:
                f.unlink()
                print(f"🗑️  Removed {f.name}")
            print(f"🎉 Removed {len(custom_files)} custom world files!")
        else:
            print("❌ Operation cancelled")
    else:
        print("✅ No custom world files to remove")

if __name__ == "__main__":
    clear_custom_worlds()
