"""
World Document Parser and Validator

This module ingests world-building documents in any format (JSON, YAML, Markdown, plain text),
uses an AI model to extract, infer, and invent all required schema fields, and validates the result.
Enhanced with story generation support.
"""
import os
import json
import yaml
import logging
import asyncio
import re
from typing import Any, Dict, Optional, List
import openai

logger = logging.getLogger(__name__)

# World schema definition (enhanced with genre and plot seeds)
WORLD_SCHEMA: Dict[str, Any] = {
    "world_name": str,
    "description": str,
    "genre": str,  # Should be specified in world document
    "technology": list,
    "social_structures": list,
    "character_archetypes": list,
    "cultures": list,
    "environment": dict,
    "themes": list,
    "plot_seeds": list,  # Story ideas and narrative hooks
    # Optional fields for richer world-building
    "history": list,
    "conflicts": list,
    "notable_figures": list,
    "aesthetics": str,
    "language": str,
    "custom_fields": dict,
}

# AI prompt template for world document parsing
AI_PROMPT_TEMPLATE = """
You are an expert world-building assistant. Your task is to read the following world-building document (which may be in any format: structured, narrative, or point form) and produce a fully populated JSON object matching the provided schema.

IMPORTANT INSTRUCTIONS:
- Extract as much information as possible from the document
- For any required field that is missing or ambiguous, invent plausible details based on the document's style, genre, and context
- Ensure all required fields are present and non-empty in your output
- If the document is minimal or vague, use your creativity to fill in the gaps
- For lists, provide at least 3-5 meaningful items
- For the environment field, include sub-fields like climate, geography, and notable_locations
- Keep everything consistent with the overall tone and genre of the source document
- Output ONLY a valid JSON object, no other text

**Required Schema Fields:**
{schema_fields}

**World-Building Document:**
---
{document}
---

Your response must be valid JSON only:
"""

def load_world_document(path: str) -> str:
    """
    Load a world-building document from a file as a string.
    Supports JSON, YAML, Markdown, and plain text.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"Successfully loaded world document: {path}")
        return content
    except Exception as e:
        logger.error(f"Failed to load world document {path}: {e}")
        raise

async def call_ai_to_populate_schema(document: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send the document and schema to the AI and return a fully populated schema dict.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY must be set in environment for world document parsing.")
    
    # Prepare schema fields description
    schema_fields = []
    for field, field_type in schema.items():
        if field_type == str:
            schema_fields.append(f'"{field}": "string description"')
        elif field_type == list:
            schema_fields.append(f'"{field}": ["list", "of", "items"]')
        elif field_type == dict:
            schema_fields.append(f'"{field}": {{"nested": "object"}}')
    
    schema_description = "{\n  " + ",\n  ".join(schema_fields) + "\n}"
    
    prompt = AI_PROMPT_TEMPLATE.format(
        schema_fields=schema_description,
        document=document
    )
    
    openai_client = openai.AsyncOpenAI(api_key=api_key)
    try:
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"[World Parser] Sending world document to AI for parsing (attempt {attempt})...")
                response = await openai_client.chat.completions.create(
                    model="gpt-4o",  # Use a reliable model for this task
                    messages=[{"role": "user", "content": prompt}],
                    timeout=120,  # Longer timeout for complex parsing
                    response_format={"type": "json_object"}  # Ensure JSON response
                )
                
                if response and response.choices and response.choices[0].message:
                    response_content = response.choices[0].message.content.strip()
                    if response_content:
                        try:
                            result = json.loads(response_content)
                            logger.info("[World Parser] Successfully parsed world document with AI")
                            logger.debug(f"[World Parser] AI parsed result: {json.dumps(result, indent=2)}")
                            return result
                        except json.JSONDecodeError as e:
                            logger.error(f"[World Parser] Invalid JSON from AI: {e}")
                            raise ValueError(f"AI returned invalid JSON: {e}")
                    else:
                        raise ValueError("AI returned empty response")
                else:
                    raise ValueError("Invalid response structure from AI")
                    
            except openai.APIConnectionError as e:
                logger.error(f"[World Parser] Connection error on attempt {attempt}: {e}")
            except openai.RateLimitError as e:
                logger.warning(f"[World Parser] Rate limit exceeded on attempt {attempt}: {e}")
            except openai.APIStatusError as e:
                logger.error(f"[World Parser] API status error on attempt {attempt}: {e.status_code}")
            except Exception as e:
                logger.warning(f"[World Parser] Attempt {attempt} failed: {e}")
            
            if attempt == max_retries:
                logger.error("[World Parser] All attempts failed for AI parsing")
                raise Exception(f"Failed to parse world document with AI after {max_retries} attempts")
            
            await asyncio.sleep(2 ** attempt)
        
        return {}
    finally:
        await openai_client.close()

def call_ai_to_populate_schema_sync(document: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronous wrapper for the async AI parsing function.
    """
    return asyncio.run(call_ai_to_populate_schema(document, schema))

def validate_schema_output(output: Dict[str, Any], schema: Dict[str, Any]) -> None:
    """
    Validate the AI's output against the schema.
    Raises ValueError if required fields are missing or empty.
    """
    required_fields = ["world_name", "description", "technology", "social_structures", 
                      "character_archetypes", "cultures", "environment", "themes"]
    
    missing = []
    for field in required_fields:
        if field not in output:
            missing.append(f"{field} (missing)")
        elif not output[field]:
            missing.append(f"{field} (empty)")
        elif isinstance(output[field], list) and len(output[field]) == 0:
            missing.append(f"{field} (empty list)")
    
    if missing:
        raise ValueError(f"Schema validation failed. Issues with fields: {', '.join(missing)}")
    
    logger.info("World document schema validation passed")

def parse_and_validate_world_document(path: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point: Load a world-building document, use AI to populate the schema, and validate the result.
    Raises ValueError if validation fails.
    """
    try:
        document = load_world_document(path)
        logger.info(f"Parsing world document with AI: {path}")
        ai_output = call_ai_to_populate_schema_sync(document, schema)
        validate_schema_output(ai_output, schema)
        logger.info("World document successfully parsed and validated")
        return ai_output
    except Exception as e:
        logger.error(f"Failed to parse and validate world document {path}: {e}")
        raise

def extract_plot_seeds(world_data: Dict[str, Any]) -> List[str]:
    """
    Extract or generate plot seeds from world data.
    
    Args:
        world_data: Parsed world document data
        
    Returns:
        List of plot seed strings for story generation
    """
    plot_seeds = []
    
    # First check if plot seeds are already in the data
    if 'plot_seeds' in world_data and world_data['plot_seeds']:
        return world_data['plot_seeds']
    
    # Generate plot seeds based on world elements
    characters = world_data.get('character_archetypes', [])
    technologies = world_data.get('technology', [])
    themes = world_data.get('themes', [])
    conflicts = world_data.get('conflicts', [])
    
    # Create basic plot seeds from combinations of elements
    if characters and len(characters) >= 2:
        plot_seeds.append(f"A {characters[0]} must work with a {characters[1]} to solve a crisis")
    
    if technologies and themes:
        plot_seeds.append(f"The discovery of {technologies[0]} challenges the world's understanding of {themes[0] if themes else 'reality'}")
    
    if conflicts:
        plot_seeds.append(f"An ancient conflict over {conflicts[0]} resurfaces in the modern era")
    
    # Add default if no seeds generated
    if not plot_seeds:
        plot_seeds.append("A reluctant hero discovers they hold the key to saving their world")
    
    return plot_seeds

def get_story_elements(world_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract key elements needed for story generation from world data.
    
    Args:
        world_data: Parsed world document data
        
    Returns:
        Dictionary of story elements ready for prompt generation
    """
    # Extract environment/setting
    environment = world_data.get('environment', {})
    if isinstance(environment, dict):
        setting = environment.get('notable_locations', ['unknown location'])[0] if environment.get('notable_locations') else 'unknown location'
    else:
        setting = str(environment) if environment else 'unknown location'
    
    return {
        'setting': setting,
        'characters': world_data.get('character_archetypes', [])[:2],  # First two character types
        'technology': world_data.get('technology', [])[:2],           # First two technologies
        'theme': world_data.get('themes', ['survival'])[0],          # Primary theme
        'genre': world_data.get('genre', 'sci-fi'),
        'plot_seed': world_data.get('plot_seeds', ['A hero emerges in times of need'])[0],
        'world_name': world_data.get('world_name', 'Unknown World'),
        'culture': world_data.get('cultures', ['diverse communities'])[0] if world_data.get('cultures') else 'diverse communities',
        'social_structure': world_data.get('social_structures', ['complex society'])[0] if world_data.get('social_structures') else 'complex society'
    }

def get_genre_specific_elements(world_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract genre-specific elements for enhanced story generation.
    
    Args:
        world_data: Parsed world document data
        
    Returns:
        Dictionary of genre-specific aesthetic and thematic elements
    """
    genre = world_data.get('genre', 'sci-fi').lower()
    elements = {}
    
    if 'fantasy' in genre:
        elements.update({
            'magic_system': 'arcane energies',
            'aesthetic': 'magical realism with ethereal lighting',
            'conflict_type': 'ancient prophecy or dark magic',
            'power_source': 'mystical forces'
        })
    elif 'sci-fi' in genre:
        elements.update({
            'tech_level': 'advanced futuristic',
            'aesthetic': 'cyberpunk with neon lighting and chrome',
            'conflict_type': 'technological advancement vs humanity',
            'power_source': 'advanced technology'
        })
    elif 'steampunk' in genre:
        elements.update({
            'tech_level': 'Victorian industrial',
            'aesthetic': 'brass and copper with steam and gears',
            'conflict_type': 'industrial revolution tensions',
            'power_source': 'steam and clockwork'
        })
    elif 'solarpunk' in genre:
        elements.update({
            'tech_level': 'sustainable advanced',
            'aesthetic': 'green technology with natural harmony',
            'conflict_type': 'balance between progress and nature',
            'power_source': 'renewable and bio-integrated'
        })
    else:
        elements.update({
            'aesthetic': 'contemporary realism',
            'conflict_type': 'human drama',
            'power_source': 'human determination'
        })
    
    return elements

def enhance_world_data_for_stories(world_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance parsed world data with story generation elements.
    
    Args:
        world_data: Basic parsed world data
        
    Returns:
        Enhanced world data with story elements and genre-specific details
    """
    # Add plot seeds if missing
    if 'plot_seeds' not in world_data or not world_data['plot_seeds']:
        world_data['plot_seeds'] = extract_plot_seeds(world_data)
    
    # Add story elements
    world_data['story_elements'] = get_story_elements(world_data)
    
    # Add genre-specific elements
    world_data['genre_elements'] = get_genre_specific_elements(world_data)
    
    return world_data

def parse_world_document_for_stories(path: str) -> Dict[str, Any]:
    """
    Main entry point for story generation: Parse world document and enhance for story generation.
    
    Args:
        path: Path to world document file
        
    Returns:
        Enhanced world data ready for story generation
    """
    try:
        # Use existing parser to get base world data
        world_data = parse_and_validate_world_document(path, WORLD_SCHEMA)
        
        # Enhance with story generation elements
        enhanced_data = enhance_world_data_for_stories(world_data)
        
        logger.info(f"[World Parser] Successfully parsed and enhanced world document for stories: {path}")
        logger.info(f"[World Parser] Genre from document: {enhanced_data['genre']}")
        logger.info(f"[World Parser] Plot seeds: {len(enhanced_data['plot_seeds'])}")
        
        return enhanced_data
        
    except Exception as e:
        logger.error(f"Failed to parse world document for stories {path}: {e}")
        raise

def main():
    """
    Demonstration entry point for manual testing.
    """
    import sys
    if len(sys.argv) < 2:
        print("Usage: python world_parser.py <path-to-world-document>")
        return
    path = sys.argv[1]
    try:
        result = parse_world_document_for_stories(path)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 