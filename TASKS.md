# Solarpunk Story Bot - Believability & Tech Focus Overhaul (2024-04 v2)

## Implementation Plan

### Phase 1: Data Structure Updates
- [x] Update SETTINGS list with new environments (wetland, grassland, reef, etc.)
- [x] Update THEMES dictionary with new settings and their themes
- [x] Add X_THEMES (cross-cutting themes) as a new constant
- [x] Update ART_STYLES dictionary with new styles and descriptive modifiers

### Phase 2: Randomization & Story Generation Logic (Updates)
- [x] Implement new randomization rules for settings, styles, and secondary themes (with specified probabilities)
- [x] Update StoryParameters to support secondary theme
- [x] Update story prompt construction to append secondary theme when present
- [x] **Modify theme selection:** Before calling `generate_story`, explicitly choose *one* `primary_tech` from `THEMES[setting]` list. Store this `primary_tech`.
- [x] **Update StoryParameters/Prompt:** Ensure `generate_story` and its parameters/prompt reflect focus on a single `primary_tech`.

### Phase 3: Believability Check & Regeneration (New)
- [x] **Implement believability_check function:** Use LLM call to get 1-9 realism score; return True if >= 7.
- [x] **Implement Regeneration Loop:** In `run_generation`, loop `generate_story` up to 3 times, breaking if `believability_check` passes. Use last story if loop finishes.

### Phase 4: Image Prompt Extraction & Construction (Updates)
- [x] Redesign `extract_image_prompt` to request and parse structured JSON output
- [x] Add validation and default injection for 'negatives' field
- [x] **Update `extract_image_prompt`:** Require `tech` field in JSON. Accept `primary_tech` as argument and ensure it's in the output dict.
- [x] **Update Image Prompt Construction:** Use new f-string format including `featuring {tech}`.

### Phase 5: Seed Deduplication (Updates)
- [x] Implement recent seed deduplication using deque(maxlen=10)
- [x] **Update Seed Definition:** Change seed tuple to `(setting, primary_tech, secondary_theme, style)`.

### Phase 6: Testing & Validation (Updates)
- [ ] Add/expand unit tests for `believability_check` and updated logic.
- [ ] Run integration tests to verify regeneration, tech inclusion in prompts, and plausibility.
- [ ] Manually review sample outputs for quality and coherence.

---

# AI Agent Task List

## Phase 1: Project Setup and Infrastructure

### 1.1 Environment Setup
- [x] Create virtual environment
      - Created using `uv venv`
      - Tested by activating and installing dependencies successfully
- [x] Initialize git repository
      - Initialized with `git init`
      - Tested by successful initial commit with all project files
- [x] Set up project structure
      - Created src/, tests/, docs/, config/, logs/ directories
      - Added __init__.py files
      - Tested by verifying directory structure and file presence
- [x] Create initial requirements.txt
      - Upgraded to modern pyproject.toml
      - All dependencies specified with versions
      - Tested by successful package installation
- [x] Set up logging configuration
      - Added logging config in config/config.yaml
      - Configured structured logging with proper rotation
      - Tested through configuration validation
- [x] Create configuration management system
      - Created comprehensive config/config.yaml
      - Tested by validating YAML syntax and structure

### 1.2 API Integration Setup
- [x] Set up Google Cloud Platform project
      - Created GCP project "twitterstoryagent"
      - Enabled required APIs: Vertex AI (includes Gemini Pro and Imagen 2), Cloud Storage, Cloud Vision
      - Created service account with appropriate roles
      - Securely stored credentials with proper permissions (600)
      - Tested by verifying project ID and credentials file accessibility
- [x] Configure Gemini Pro API access
      - Completed as part of Vertex AI setup
      - Access enabled through service account permissions
      - Created test script to verify connectivity and prompt generation
      - Successfully tested and verified text generation functionality
      - Test output saved to output/api_test_results.txt
- [x] Configure Imagen 2 API access
      - Completed as part of Vertex AI setup
      - Access enabled through service account permissions
      - Requested and received quota increase for image generation
      - Created test script to verify image generation capabilities
      - Successfully tested using the imagen-3.0-generate-002 model
      - Test output saved to output/api_test_results.txt
- [x] Set up Twitter Developer account
      - Registered for a Twitter Developer account
      - Created project and app for AI story generation
      - Obtained API key, API secret, access token, and access token secret
      - Stored credentials securely in .env file
      - Verified through credential loading test
- [x] Configure Twitter API v2 access
      - Implemented TwitterClient class with v2 API support
      - Created methods for posting tweets with text and media
      - Added media upload functionality
      - Added tweet deletion capability
      - Verified through test framework
- [x] Implement secure credential management
      - Created CredentialManager class for secure handling of credentials
      - Implemented environment variable loading from .env file
      - Added support for configuration from YAML files
      - Created dedicated methods for retrieving different API credentials
      - Added proper error handling for missing required credentials
      - Verified through successful credential loading tests

## Phase 2: Core Functionality Implementation

### 2.1 Story Generation Module
- [x] Implement Gemini Pro API client
      - Created StoryGenerator class with Vertex AI integration
      - Added explicit GCP credentials loading
      - Implemented retry logic with exponential backoff
      - Successfully tested with real API calls
- [x] Create story generation prompts
      - Designed specialized prompts for solarpunk micro-stories
      - Included detailed instructions for structure and tone
      - Added requirements for character limits (280 chars for X)
      - Ensured content is uplifting and provides positive vision of the future
- [x] Implement genre selection system
      - Added support for different settings (urban, coastal, forest, desert, rural)
      - Implemented customizable themes appropriate for each setting
      - Created parameter system for generating varied stories
- [x] Add error handling and retries
      - Implemented comprehensive error handling with detailed logging
      - Added retry mechanism with exponential backoff
      - Added proper exception handling to prevent crashes
- [x] Create story validation system
      - Implemented character count validation
      - Added truncation to ensure stories fit within X character limits
      - Created metadata system to track generation parameters
- [x] Implement content filtering
      - Added filtering for problematic/dystopian themes
      - Ensured stories maintain a positive tone
      - Focused on uplifting, hopeful micro-narratives

### 2.2 Image Generation Module
- [x] Implement Imagen 2 API client
      - Created ImageGenerator class with Vertex AI integration
      - Used the imagen-3.0-generate-002 model
      - Implemented proper authentication with GCP credentials
      - Added image saving functionality
- [x] Create image generation prompts
      - Designed specialized prompts based on story content
      - Created setting-specific descriptors for different environments
      - Added style-specific enhancements for varied visual styles
      - Implemented content extraction to highlight key elements from stories
- [x] Implement style selection system
      - Added support for various artistic styles (photographic, digital-art, watercolor)
      - Created style-specific prompt enhancers
      - Implemented parameter validation system
      - Added metadata tracking for styles and settings
- [x] Add error handling and retries
      - Implemented comprehensive error handling with detailed logging
      - Added retry mechanism with exponential backoff
      - Added proper exception handling with specific error messages
- [x] Create image validation system
      - Added parameter validation for model, dimensions, and styles
      - Implemented file handling with proper error checking
      - Created output directory structure for organized image storage
- [x] Implement image post-processing
      - Added image saving functionality with timestamp-based naming
      - Implemented conversion between PIL images and bytes
      - Added metadata tracking for generated images
      - Created flexible output path handling

### 2.3 Twitter Integration Module
- [x] Implement Twitter API client (Tweepy)
- [x] Configure authentication with Twitter API
- [x] Create tweet posting functionality
- [x] Add media upload capabilities
- [x] Design error handling and retry mechanisms
- [x] Create test twitter account posting mechanics
- [x] Fix Twitter API authentication issues
- [x] Test and verify Twitter posting works correctly
- [x] Create TwitterTestPost helper for creating test posts about project progress

### 2.4 Scheduling System
- [x] Implement scheduling framework
  - [x] Create systemd service unit file
        - Created ai-solarpunk-story.service with proper configuration
        - Added service-specific logging
        - Configured for UV package manager
        - Tested and verified working
  - [x] Update main script for service compatibility
        - Added --service flag for service-specific configuration
        - Enhanced logging system
        - Added proper exit codes
        - Tested successfully
  - [x] Remove cron-specific components
        - Replaced with systemd timer
        - Timer configured for daily runs
        - Removed randomized delay for exact timing
  - [x] Test service operation
        - Verified service execution
        - Confirmed story generation
        - Validated image creation
        - Tested Twitter posting
        - Checked logging functionality
  - [x] Update documentation
        - Added service management script
        - Documented installation process
        - Added service status checking

- [x] Create configuration system for schedules
  - [x] Create bot-manager.sh script for service management
        - Added comprehensive timezone handling with DST support
        - Implemented schedule management interface
        - Added service status monitoring
        - Created log viewing system
  - [x] Add timezone-aware scheduling
        - Implemented automatic DST detection
        - Added timezone configuration system
        - Created timezone conversion utilities
        - Added clear timezone status display
  - [x] Implement service controls
        - Added manual service execution
        - Created schedule modification interface
        - Added service enable/disable functionality
        - Implemented log viewing with proper permissions
  - [x] Test and verify scheduling system
        - Validated timezone conversions
        - Tested schedule modifications
        - Verified service operation
        - Confirmed logging system works

### 2.5 Unified LLM-Based Image Prompt Construction
- [x] Refactor image prompt construction to always use LLM (OpenAI o3) for extracting image prompts from stories
      - All programmatic and Gemini/Imagen logic removed from story and image generation modules
      - Only OpenAI o3 is used for both story and image generation
      - Error notification stub added for image prompt failures
      - Full pipeline tested with `uv run src/ai_story_tweet_generator.py --setting urban --style digital-art --features story,image --preview`
      - Confirmed successful story, prompt, and image generation with OpenAI only
      - All outputs and logs verified

## Phase 3: Testing and Quality Assurance

### 3.1 Unit Testing
- [ ] Create test suite for story generation
- [ ] Create test suite for image generation
- [ ] Create test suite for Twitter integration
- [ ] Create test suite for scheduling system
- [ ] Implement mock API responses
- [ ] Create integration tests

### 3.2 Error Handling and Logging
- [ ] Implement comprehensive error handling
- [ ] Set up detailed logging system
- [ ] Create error reporting system
- [ ] Implement monitoring alerts
- [ ] Create debugging tools

## Phase 4: Enhancement and Optimization

### 4.1 Performance Optimization
- [ ] Optimize API calls
- [ ] Implement caching system
- [ ] Optimize image processing
- [ ] Improve error recovery
- [ ] Optimize scheduling system

### 4.2 Feature Enhancements
- [ ] Implement prompt variation system
- [ ] Add content diversity features
- [ ] Create web interface
- [ ] Implement advanced image processing
- [ ] Add analytics tracking

## Phase 5: Documentation and Deployment

### 5.1 Documentation
- [ ] Create API documentation
- [ ] Write deployment guide
- [ ] Create user manual
- [ ] Document configuration options
- [ ] Create troubleshooting guide

### 5.2 Deployment
- [ ] Set up CI/CD pipeline
- [ ] Create deployment scripts
- [ ] Implement monitoring system
- [ ] Create backup system
- [ ] Set up production environment

## Phase 6: OpenAI Provider Migration

### 6.1 Discovery & Baseline
- [ ] Catalogue all Gemini Pro and Imagen 2 references across the codebase and produce a short report
- [ ] Audit current unit and integration tests to identify provider-specific fixtures or mocks

### 6.2 OpenAI Client Layer (non-breaking)
- [x] Add `openai~=1.3` to `pyproject.toml` using `uv pip install --strict`
- [x] Implement `src/ai_solarpunk/clients/openai_story_client.py` with `generate_story()`
- [x] Implement `src/ai_solarpunk/clients/openai_image_client.py` with `generate_image()`
- [x] Write unit tests for both new clients in `tests/clients/`
- [x] Document new environment variables (`OPENAI_API_KEY`, `OPENAI_API_BASE`, `OPENAI_HTTP_TIMEOUT`) in `docs/` and `.env.sample`

      - OpenAI Python SDK added and locked in pyproject.toml
      - New async, typed, logged, and retried story/image client modules created
      - Full pytest test suites for both clients, using pytest-asyncio and pytest-mock
      - All tests pass (core logic, error, and retry)
      - Manual .env update for API key

### 6.3 Generation Pipeline Integration
- [ ] Introduce `USE_OPENAI` feature flag (default `false` during transition)
- [ ] Modify existing story and image services to delegate to OpenAI clients when the flag is enabled
- [ ] Update or create tests to cover flag switching and ensure backward compatibility

### 6.4 Systemd & Shell Updates
- [ ] Update `ai-solarpunk-story.service` to include OpenAI-specific environment variables and set `USE_OPENAI=true`
- [ ] Update `