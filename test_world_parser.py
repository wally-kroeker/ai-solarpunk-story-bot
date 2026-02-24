#!/usr/bin/env python3
"""
Test script for world document parsing functionality
"""

from src.ai_solarpunk.world_parser import parse_and_validate_world_document, WORLD_SCHEMA
import tempfile
import os
import sys

def test_world_parsing():
    """Test the world document parsing with a simple example"""
    
    # Test content
    test_content = '''# Floating Cities of Aquatica

A water world where humanity lives on floating bio-cities.

Technology:
- Living coral foundations
- Algae-powered engines  
- Tidal energy harvesting
- Bio-luminescent street lamps

Society:
- Water shepherds maintain the cities
- Storm riders navigate between settlements
- Deep divers explore the ruins below

Conflicts:
- Rising sea levels threaten settlements
- Competition for pure water sources
- Ancient AI systems awakening underwater

Environment:
The endless ocean dotted with massive floating bio-cities that glow with natural light.
'''

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        temp_file = f.name

    try:
        print('Testing world document parsing...')
        print(f'Input content length: {len(test_content)} characters')
        
        result = parse_and_validate_world_document(temp_file, WORLD_SCHEMA)
        
        print('✅ SUCCESS! World document parsed successfully')
        print(f'📖 World name: {result.get("world_name", "Unknown")}')
        print(f'🔧 Technology count: {len(result.get("technology", []))}')
        print(f'👥 Character archetypes: {len(result.get("character_archetypes", []))}')
        print(f'🏛️ Social structures: {len(result.get("social_structures", []))}')
        print(f'🎭 Cultures: {len(result.get("cultures", []))}')
        print(f'⚔️ Conflicts: {len(result.get("conflicts", []))}')
        
        # Show some sample content
        print('\n📋 Sample extracted content:')
        if result.get("technology"):
            print(f'  First technology: {result["technology"][0]}')
        if result.get("character_archetypes"):
            print(f'  First archetype: {result["character_archetypes"][0]}')
            
        return True
        
    except Exception as e:
        print(f'❌ FAILED: {e}')
        return False
        
    finally:
        os.unlink(temp_file)

if __name__ == "__main__":
    success = test_world_parsing()
    sys.exit(0 if success else 1) 