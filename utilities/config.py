import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API keys
CUSTOM_SEARCH_API_KEY = os.environ.get("CUSTOM_SEARCH_API_KEY")
PROGRAMMABLE_SEARCH_ENGINE_ID = os.environ.get("PROGRAMMABLE_SEARCH_ENGINE_ID")