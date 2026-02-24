# World-Building Document Schema & Parser Design (Draft)

## 1. Required & Optional Fields

**Required Fields:**
- `world_name`: Name of the world/setting.
- `description`: A paragraph or summary describing the world.
- `technology`: Description or list of key technologies present in the world.
- `social_structures`: Description or list of major social structures (e.g., government, family, organizations).
- `character_archetypes`: List or description of common character types/archetypes in this world.
- `cultures`: List or description of major cultures, subcultures, or factions.
- `environment`: Description of the world's environment (climate, geography, notable locations).
- `themes`: List of core themes (e.g., hope, rebellion, sustainability).

**Optional Fields:**
- `history`: Key historical events or timeline.
- `conflicts`: Ongoing or past conflicts.
- `notable_figures`: List of important characters or leaders.
- `aesthetics`: Visual or artistic style cues.
- `language`: Notes on language(s) or dialects.
- `custom_fields`: Any additional user-defined fields.

---

## 2. Example World Documents

### a) YAML (Structured)
```yaml
world_name: Verdant Skies
description: |
  A lush, floating archipelago where solar-powered airships connect eco-cities above a rejuvenated Earth.
technology:
  - Solar airships
  - Bioengineered crops
  - AI-driven weather control
social_structures:
  - Decentralized eco-communes
  - Guilds of engineers and botanists
character_archetypes:
  - Skyfarer
  - Bioengineer
  - Weather shaman
cultures:
  - Skyfolk
  - Rooted (ground dwellers)
environment:
  climate: temperate
  geography: floating islands, cloud forests
  notable_locations:
    - Sunspire City
    - The Hanging Gardens
themes:
  - Sustainability
  - Adventure
  - Harmony with nature
history:
  - The Great Rewilding
  - The Sky Exodus
```

### b) JSON (Structured)
```json
{
  "world_name": "Neon Roots",
  "description": "A cyberpunk city where nature reclaims the streets and AI gardeners rule the night.",
  "technology": ["Neural implants", "Bio-luminescent plants", "Drone pollinators"],
  "social_structures": ["Corporate clans", "Underground eco-cells"],
  "character_archetypes": ["Hacker-botanist", "Street shaman", "Corporate defector"],
  "cultures": ["Synths", "Greenwave"],
  "environment": {
    "climate": "humid",
    "geography": "urban jungle",
    "notable_locations": ["The Verdant Sprawl", "The Neon Canopy"]
  },
  "themes": ["Rebellion", "Regeneration", "Techno-nature"],
  "conflicts": ["AI vs. human gardeners", "Corporate land grabs"]
}
```

### c) Markdown/Narrative (Unstructured)
```
# World: The Sunlit Frontier

The Sunlit Frontier is a vast desert world where solar-powered caravans traverse ancient trade routes. Society is organized into nomadic tribes, each with their own customs and technologies. The environment is harsh but beautiful, with glass dunes and oasis cities.

**Key Technologies:**
- Solar caravans
- Water reclamation towers
- Sand-resistant robotics

**Social Structures:**
- Nomadic tribes
- Oasis city councils

**Character Archetypes:**
- Caravan leader
- Water seeker
- Sand engineer

**Cultures:**
- The Dune Walkers
- Oasis Dwellers

**Environment:**
- Climate: arid
- Geography: glass dunes, oasis cities
- Notable locations: The Shimmering Expanse, Oasis of Light

**Themes:**
- Survival
- Ingenuity
- Community

**History:**
- The Long Drought
- The Founding of the Oasis Cities
```

---

## 3. AI-Driven Extraction, Inference, and Completion

**Principle:**
- The AI is responsible for extracting, inferring, and inventing all required fields from any world-building document, regardless of its structure or format.
- The system will always produce a fully populated, valid schema document (e.g., JSON) as an intermediate step, even if the original document is incomplete, ambiguous, or unstructured.
- The AI prompt will instruct the model to:
  - Parse and extract as much as possible from the user's world-building document.
  - Invent or infer missing details to ensure all required fields are filled, using its own reasoning and creativity.
  - Output a complete, valid schema document that downstream code can always rely on for story/image generation.

---

## 4. AI Prompt Template for Schema Extraction & Completion

```
You are an expert world-building assistant. Your task is to read the following world-building document (which may be in any format: structured, narrative, or point form) and produce a fully populated JSON object matching the provided schema. 

- Extract as much information as possible from the document.
- For any required field that is missing or ambiguous, invent plausible details based on the document's style, genre, and context.
- Ensure all required fields are present and non-empty in your output.
- If the document is minimal or vague, use your own creativity to fill in the gaps.
- Output only a valid JSON object matching the schema below.

**Schema:**
{...insert JSON schema here...}

**World-Building Document:**
---
{...user's document here...}
---

**Your Output:**
```

---

## 5. Extraction & Validation Logic Outline

- **Format Detection:**
  - Accept any file format (JSON, YAML, Markdown, plain text, etc.).
  - Pass the raw document and the schema to the AI for extraction and completion.

- **AI-Driven Parsing:**
  - The AI reads the document and produces a fully populated JSON object matching the schema.
  - If the output is invalid or missing fields, prompt the AI again or alert the user.

- **Validation:**
  - Validate the AI's output against the schema.
  - If any required fields are missing, repeat the AI prompt with clarification or request user input.

- **Downstream Usage:**
  - All story/image/character generation uses the completed schema document, ensuring reliability and consistency.

- **Extensibility:**
  - Allow custom fields to be added and passed through to downstream systems.
  - Support for additional formats (e.g., TOML) can be added in the future.

---

## 6. Code Flow Outline

1. User provides a world-building document (any format).
2. System loads the document as a string.
3. System sends the document and the schema (as a JSON schema or field list) to the AI with the prompt template above.
4. AI returns a fully populated JSON object matching the schema.
5. System validates the output against the schema.
6. If valid, the schema document is used for all downstream generation.
7. If invalid, system prompts the AI again or requests user clarification.

---

**Review this updated draft and prompt template before implementation.** 