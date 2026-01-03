# Sleeper Fantasy Football Scraper

This folder contains all Sleeper API scraping functionality for the 2025+ seasons.

## Files

### Core Scrapers
- **`sleeper_scraper.py`** - Main Sleeper data scraper
  - Fetches league, roster, matchup, draft, and transaction data
  - Uses official Sleeper REST API
  - No authentication required (public data)

- **`sleeper_client.py`** - Sleeper API client wrapper
  - Clean Python interface for Sleeper endpoints
  - Methods for users, leagues, rosters, matchups, drafts
  - Error handling and retries

- **`run_sleeper_scrape.py`** - Convenience script to run scraper
  - Pre-configured with username and league ID
  - Non-interactive execution

### Enhancement Tools
- **`fetch_sleeper_projections.py`** - Fetches player projections
  - Gets weekly Half-PPR projections from Sleeper API
  - Merges projections into matchup data
  - Updates existing JSON files

- **`enhance_sleeper_data.py`** - Resolves player IDs to names
  - Fetches global player mapping
  - Enriches matchup/draft data with player names
  - Caches player data locally

### Testing
- **`test_sleeper.py`** - Interactive test script for API calls

## Usage

### Run Sleeper Scraper
```bash
cd /path/to/project
python scrapers/sleeper/run_sleeper_scrape.py
```

### Fetch Projections (After Scraping)
```bash
python scrapers/sleeper/fetch_sleeper_projections.py
```

### Configuration
Edit `run_sleeper_scrape.py` to set:
- `username` - Your Sleeper username
- `league_id` - Your Sleeper league ID

## Data Output
- JSON files: `data/sleeper_{LEAGUE_ID}_{YEAR}.json`
- Player cache: `data/sleeper_players.json`

## API Documentation
- Sleeper API: https://docs.sleeper.com/
- No API key required
- Rate limiting: ~1000 requests/minute

