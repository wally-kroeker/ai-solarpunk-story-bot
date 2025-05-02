import logging
from pathlib import Path
from google.oauth2 import service_account
import vertexai
from vertexai.preview.generative_models import GenerativeModel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Update these paths as needed for your project
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"
CREDENTIALS_PATH = PROJECT_ROOT / "credentials" / "gcp-credentials.json"
MODEL_NAME = "gemini-2.5-pro-preview-03-25"

# Hardcoded for test; update if needed
PROJECT_ID = None
LOCATION = "us-central1"

# Try to load project_id from config if available
def load_project_id() -> str:
    import yaml
    try:
        with open(CONFIG_PATH, "r") as f:
            config = yaml.safe_load(f)
            return config.get("api", {}).get("google_cloud", {}).get("project_id")
    except Exception as e:
        logger.warning(f"Could not load project_id from config: {e}")
        return None

if __name__ == "__main__":
    logger.info("Starting Gemini 2.5 minimal test...")
    project_id = load_project_id() or PROJECT_ID
    if not project_id:
        logger.error("No project_id found. Please set it in config.yaml or hardcode it in this script.")
        exit(1)
    try:
        credentials = service_account.Credentials.from_service_account_file(str(CREDENTIALS_PATH))
        vertexai.init(project=project_id, location=LOCATION, credentials=credentials)
        model = GenerativeModel(MODEL_NAME)
        prompt = "Write a short story about a cat who lives in a solarpunk city."
        logger.info(f"Sending prompt: {prompt}")
        response = model.generate_content(prompt)
        logger.info(f"Raw Gemini response: {response}")
        text = getattr(response, 'text', None)
        if text:
            print("\n=== Gemini 2.5 Response ===\n")
            print(text.strip())
        else:
            print("\n[No text returned in response]")
    except Exception as e:
        logger.error(f"Error during Gemini test: {e}", exc_info=True)
        print(f"[ERROR] {e}") 