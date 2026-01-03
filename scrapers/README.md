# Fantasy Football Data Scrapers

This folder contains all data scraping functionality for ESPN and Sleeper fantasy football leagues.

## Structure

```
scrapers/
├── espn/           # ESPN scraper (2019-2024)
│   ├── historical_scraper.py
│   ├── espn_scraper.py
│   ├── gemini_client.py
│   ├── auth_manager.py
│   ├── data_extraction.py
│   └── README.md
│
└── sleeper/        # Sleeper API scraper (2025+)
    ├── sleeper_scraper.py
    ├── sleeper_client.py
    ├── run_sleeper_scrape.py
    ├── fetch_sleeper_projections.py
    ├── enhance_sleeper_data.py
    ├── test_sleeper.py
    └── README.md
```

## ESPN Scraper (AI-Powered Web Scraping)

Uses Gemini Vision AI to extract data from ESPN Fantasy Football website.

**Technology:**
- Playwright browser automation
- Gemini 3 Flash for screenshot analysis
- Cookie-based authentication

**Data Collected:**
- League standings
- Weekly matchups with box scores
- Draft recaps
- Transactions
- Player stats

**Run:**
```bash
python scrapers/espn/historical_scraper.py
```

## Sleeper Scraper (REST API)

Uses official Sleeper REST API to fetch league data.

**Technology:**
- Python requests library
- Sleeper REST API v1
- No authentication required

**Data Collected:**
- League settings and standings
- Weekly matchups with rosters
- Draft picks
- Player projections
- Transactions

**Run:**
```bash
python scrapers/sleeper/run_sleeper_scrape.py
python scrapers/sleeper/fetch_sleeper_projections.py  # Get projections
```

## Configuration

Both scrapers use settings from `config.py` in the project root:
- `GEMINI_API_KEY` - For ESPN scraping
- `LEAGUE_ID` - ESPN league ID
- Edit individual scraper files for Sleeper league ID

## Output

All scrapers output to the `data/` folder:
- `data/espn_league_{ID}_{YEAR}_historical.json` - ESPN data
- `data/sleeper_{LEAGUE_ID}_{YEAR}.json` - Sleeper data
- `data/espn_fantasy.db` - Unified SQLite database (via populate_database.py)

## Next Steps After Scraping

1. **Populate Database** (for cloud deployment):
   ```bash
   python populate_database.py
   ```

2. **View Data** in Flask dashboard:
   ```bash
   python app.py
   ```
   Visit http://127.0.0.1:5001

## Troubleshooting

### ESPN Scraper
- **Login issues**: Delete `espn_cookies.json` and re-authenticate
- **Timeout errors**: Increase `PAGE_LOAD_TIMEOUT` in config.py
- **Missing data**: Check that Gemini API key is valid

### Sleeper Scraper
- **No data**: Verify username and league ID
- **Missing player names**: Run `enhance_sleeper_data.py`
- **Missing projections**: Run `fetch_sleeper_projections.py`

## Contributing

Each scraper folder has its own README with detailed documentation.

