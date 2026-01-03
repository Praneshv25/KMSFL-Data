"""
Configuration file for ESPN Fantasy Football Scraper
Fill in your details below
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here")
GEMINI_MODEL = "gemini-3-flash-preview"  # Latest Gemini 3 Flash model (preview)

# ESPN League Configuration
LEAGUE_ID = int(os.getenv("LEAGUE_ID", "123456"))  # Replace with your league ID
SEASON_YEAR = int(os.getenv("SEASON_YEAR", "2024"))  # Current season

# File paths
COOKIES_FILE = "espn_cookies.json"
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "espn_fantasy.db")

# Scraper settings
HEADLESS = False  # Set to True to run browser in background
SCREENSHOT_DIR = os.path.join(DATA_DIR, "screenshots")
MAX_RETRIES = 3
PAGE_LOAD_TIMEOUT = 10000  # milliseconds

# Flask settings
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5001  # Changed from 5000 to avoid conflict with macOS AirPlay
FLASK_DEBUG = True
USE_DATABASE = os.getenv("USE_DATABASE", "false").lower() == "true"  # Set to true for cloud deployment

