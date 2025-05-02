# AI Solarpunk Story Bot: Story & Image Generation Flow

This document details the full flow for generating solarpunk micro-stories and matching images, including all themes, settings, and the prompt templates used at each stage.

---

## 1. Settings and Themes

### **Available Settings**
- `urban`: Modern city environments
- `coastal`: Seaside and ocean themes
- `forest`: Woodland and forest settings
- `desert`: Arid and desert landscapes
- `rural`: Countryside and farming
- `mountain`: Mountain and alpine settings
- `arctic`: Polar and ice regions
- `island`: Island and tropical settings

### **Theme Map (used for richer story context)**
Each setting can have one or more associated themes:

| Setting   | Themes                                                                 |
|-----------|------------------------------------------------------------------------|
| urban     | renewable energy, community gardens, local production                  |
| coastal   | ocean conservation, floating communities, tidal energy                 |
| forest    | forest stewardship, ecological monitoring, natural architecture        |
| desert    | water conservation, solar power, desert greening                      |
| rural     | sustainable agriculture, community ownership, regenerative practices   |
| mountain  | (typically uses 'sustainability' as a default)                        |
| arctic    | (typically uses 'sustainability' as a default)                        |
| island    | (typically uses 'sustainability' as a default)                        |

---

## 2. Story Generation Prompt

The story prompt is dynamically constructed based on the selected setting and theme(s). The goal is to produce a positive, hopeful micro-story that fits within Twitter's character limit.

**Prompt Template:**
```
Write a solarpunk micro-story set in a {setting} environment. Theme: {theme}. The story must be positive, hopeful, and fit within {max_chars} characters. It should be suitable for a Twitter post.
```

**Example:**
```
Write a solarpunk micro-story set in a mountain environment. Theme: sustainability. The story must be positive, hopeful, and fit within 280 characters. It should be suitable for a Twitter post.
```

- **Setting**: One of the available settings (see above)
- **Theme**: Either a default (e.g., 'sustainability') or one of the mapped themes
- **max_chars**: Usually 280 (Twitter/X limit)

**How it's used:**  
This prompt is sent to the OpenAI o3 model (or Gemini Pro, depending on configuration) to generate the story.

---

## 3. Image Prompt Extraction

After the story is generated, a second prompt is constructed to extract key visual elements from the story for image generation. This uses a system prompt and a user prompt, combined and sent to the LLM to create a concise, descriptive image prompt.

**System Prompt:**
```
You are an AI assistant helping to extract visual elements from a solarpunk micro-story to create an image prompt. Focus on:
1. The setting and environment
2. Key visual elements and objects
3. The overall mood and atmosphere
4. Colors, lighting, and time of day
5. Any distinctive architectural or technological features

Create a concise, descriptive prompt that captures the visual essence of the story.
The prompt should work well for digital art generation.
```

**User Prompt:**
```
Here is a solarpunk micro-story:

{story}

Extract the key visual elements and create a concise image generation prompt that captures the essence of this story. The prompt should be suitable for generating a digital art illustration.
```

**Combined Example:**
```
You are an AI assistant helping to extract visual elements from a solarpunk micro-story to create an image prompt. Focus on:
1. The setting and environment
2. Key visual elements and objects
3. The overall mood and atmosphere
4. Colors, lighting, and time of day
5. Any distinctive architectural or technological features

Create a concise, descriptive prompt that captures the visual essence of the story.
The prompt should work well for digital art generation.

Here is a solarpunk micro-story:

Alpine sunrise paints the terraced solar petals above Cloudhaven. Children glide on wind-lifted bikes, delivering seedpods to cliff gardens. Every harvest feeds the hydro battery below, every smile powers the next dawn. In these mountains, we grow tomorrow.

Extract the key visual elements and create a concise image generation prompt that captures the essence of this story. The prompt should be suitable for generating a digital art illustration.
```

**How it's used:**  
This combined prompt is sent to the OpenAI o3 model to generate a concise image prompt, which is then used for image generation.

---

## 4. Image Generation

The extracted image prompt is sent to the image generation model (e.g., DALL-E 3, Imagen 2), along with the selected art style and setting.

### **Available Art Styles**
- digital-art
- watercolor
- stylized
- solarpunk-nouveau
- retro-futurism
- isometric

**The image model uses the prompt and style to generate a matching image for the story.**

---

## 5. Summary Flow

1. **Select setting and theme** (random or user-specified)
2. **Build story prompt** → Generate story
3. **Build image prompt** (system + user prompt, using the story) → Generate image prompt
4. **Send image prompt** (plus style/setting) to image model → Generate image
5. **(Optional)** Post both to Twitter

---

## 6. Example End-to-End

**Input:**  
- Setting: `mountain`
- Theme: `sustainability`
- Style: `solarpunk-nouveau`

**Story Prompt:**  
```
Write a solarpunk micro-story set in a mountain environment. Theme: sustainability. The story must be positive, hopeful, and fit within 280 characters. It should be suitable for a Twitter post.
```

**Generated Story:**  
```
Alpine sunrise paints the terraced solar petals above Cloudhaven. Children glide on wind-lifted bikes, delivering seedpods to cliff gardens. Every harvest feeds the hydro battery below, every smile powers the next dawn. In these mountains, we grow tomorrow.
```

**Image Prompt Extraction (system + user prompt):**  
*(see above for full template)*

**Generated Image Prompt (example):**  
```
Solarpunk alpine village at golden sunrise, snow-capped peaks behind timber-and-glass chalets whose rooftops bloom with solar petals, children on wind-powered bikes, lush cliff gardens, hopeful and bright atmosphere.
```

**Image Generation:**  
- Model: DALL-E 3 or Imagen 2
- Style: solarpunk-nouveau
- Output: PNG image matching the story

---

## 7. Notes for Prompt Redesign

- The story prompt can be expanded to include more explicit instructions about tone, character, or narrative arc.
- The image prompt extraction can be tuned to emphasize specific visual motifs, color palettes, or compositional elements.
- Themes can be diversified or made more granular for richer outputs.

---

*This document is intended for prompt engineering and flow redesign collaboration. Please annotate or suggest improvements directly!* 