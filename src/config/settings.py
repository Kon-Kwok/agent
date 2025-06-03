import os
from dotenv import load_dotenv; load_dotenv()

# SerpApi API Key
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "YOUR_SERPER_API_KEY_HERE")

# API Key for Gemini model
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "YOUR_GOOGLE_API_KEY_HERE")
