# ESPN Fantasy Football Scraper - Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- ESPN Fantasy Football league access

## Installation (5 minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
# Your Gemini API key
GEMINI_API_KEY=your-actual-api-key-here

# Your ESPN league information
LEAGUE_ID=123456
SEASON_YEAR=2024
```

**Where to find your League ID:**
- Go to your ESPN Fantasy league
- Look at the URL: `https://fantasy.espn.com/football/league?leagueId=123456`
- The number after `leagueId=` is your League ID

### 3. Verify Setup

```bash
python test_connection.py
```

This will verify:
- ✓ Gemini API connection
- ✓ Playwright browser automation
- ✓ Database initialization
- ✓ All required files present

## Usage

### First Run: Scrape Your League Data

```bash
python espn_scraper.py
```

**What happens:**
1. Browser opens to ESPN Fantasy
2. You manually log in with your ESPN credentials
3. Press Enter in terminal when logged in
4. AI automatically navigates and extracts all data
5. Data saved to JSON and SQLite database

**First run takes:** 2-5 minutes depending on league size

### Subsequent Runs (Faster)

After the first run, your login cookies are saved:

```bash
python espn_scraper.py
```

No manual login needed - uses saved cookies. Much faster!

### View Your Data in Dashboard

```bash
python app.py
```

Open browser to: `http://localhost:5000`

**Dashboard pages:**
- 🏆 Standings - League rankings and records
- 📊 Matchups - Week-by-week scores
- 👥 Rosters - Team rosters with starters/bench
- 🔄 Transactions - All trades, adds, drops
- ✅ Validation - Compare screenshots with extracted data

## What Data is Extracted?

- ✓ Team standings (rank, record, points)
- ✓ Weekly matchups (all weeks, scores, projections)
- ✓ Team rosters (starters and bench players)
- ✓ Transaction history (trades, adds, drops)
- ✓ Player statistics

## How AI Extraction Works

1. **Navigate**: AI identifies buttons/tabs to click
2. **Capture**: Takes screenshots of each page
3. **Extract**: Gemini 3 Flash reads the screenshots
4. **Verify**: AI validates extracted data matches screenshots
5. **Save**: Stores to both JSON and SQLite

## Troubleshooting

### "Gemini API key not configured"
- Edit `.env` file and add your actual API key
- Get key from: https://makersuite.google.com/app/apikey

### "Login failed"
- Delete `espn_cookies.json` and try again
- Make sure you can access the league in your browser
- Some private leagues require specific permissions

### "Playwright not found"
```bash
python -m playwright install chromium
```

### Browser doesn't open
- Check `config.py` - set `HEADLESS = False`
- Make sure you have Chrome/Chromium installed

### Data looks incomplete
- Check the validation page (`/validation`)
- Compare screenshots with extracted data
- ESPN layout may have changed - AI adapts but may need guidance

## Data Storage

### JSON Files
```
data/espn_league_123456_2024_YYYYMMDD_HHMMSS.json
```
- Human-readable format
- Good for inspection and debugging
- One file per scrape run

### SQLite Database
```
data/espn_fantasy.db
```
- Historical data tracking
- Query with SQL
- Compare across multiple scrapes

### Screenshots
```
data/screenshots/*.png
```
- Visual record of each page
- Used for validation
- Useful for debugging

## Advanced Usage

### Custom Week Range

Edit `espn_scraper.py` or create custom script:

```python
from espn_scraper import ESPNFantasyScraper

scraper = ESPNFantasyScraper()
scraper.start()
scraper.authenticate()

# Extract specific weeks
for week in range(1, 15):
    matchups = scraper.extractor.extract_matchups(week)
    print(f"Week {week}: {len(matchups['matchups'])} matchups")

scraper.close()
```

### Query Historical Data

```python
from data_manager import DataManager

dm = DataManager()
standings = dm.get_latest_standings()

for team in standings:
    print(f"{team['team_name']}: {team['wins']}-{team['losses']}")
```

### API Access

Dashboard provides JSON API endpoints:

```bash
# All data
curl http://localhost:5000/api/data

# Just standings
curl http://localhost:5000/api/standings

# Specific week
curl http://localhost:5000/api/matchups/14
```

## Tips for Best Results

1. **Run weekly** to track changes over time
2. **Check validation page** after each scrape
3. **Stable internet** - scraping can take a few minutes
4. **Don't close browser** while scraping
5. **Gemini 3 Flash** is fast and accurate for this task

## Getting Help

If something doesn't work:

1. Run `python test_connection.py` to diagnose
2. Check `data/screenshots/` to see what AI saw
3. Look at validation page to compare data
4. Check console output for errors

## What's Next?

- View your data in the dashboard
- Run scraper weekly to track season progress
- Query database for custom analysis
- Use API endpoints in other applications

Enjoy your AI-powered fantasy football insights! 🏈

