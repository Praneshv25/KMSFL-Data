# ESPN Fantasy Football Scraper

This folder contains all ESPN scraping functionality using AI-powered web scraping with Gemini Vision.

## Files

### Core Scrapers
- **`historical_scraper.py`** - Main ESPN scraper for historical data (2019-2024)
  - Scrapes all weeks, matchups, box scores, standings, draft recaps
  - Handles 2019 two-week playoff format
  - Uses Playwright for browser automation

- **`espn_scraper.py`** - Base ESPN scraping utilities
  - Cookie-based authentication
  - Browser management
  - Navigation helpers

### Support Modules
- **`gemini_client.py`** - Gemini Vision API client
  - Screenshot analysis
  - Data extraction from images
  - Retry logic and error handling

- **`auth_manager.py`** - ESPN authentication manager
  - Cookie storage and retrieval
  - Login session management

- **`data_extraction.py`** - Data extraction utilities
  - Parse ESPN HTML/screenshots
  - Structure data for storage

## Usage

### Run ESPN Scraper
```bash
cd /path/to/project
python scrapers/espn/historical_scraper.py
```

### Requirements
- ESPN account with league access
- Gemini API key (set in config.py)
- Playwright browsers installed

## Data Output
- JSON files: `data/espn_league_{LEAGUE_ID}_{YEAR}_historical.json`
- Screenshots: `data/screenshots/` (optional)

