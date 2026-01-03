# Repository Structure

```
FF DATA/
│
├── 📱 Flask Application
│   ├── app.py                      # Main Flask web dashboard
│   ├── config.py                   # Configuration settings
│   ├── data_manager.py             # Database utilities
│   └── templates/                  # HTML templates
│       ├── base.html
│       ├── index.html              # Standings page
│       ├── matchups.html           # Weekly matchups & box scores
│       ├── draft.html              # Draft recap
│       ├── transactions.html       # Transactions history
│       └── validation.html         # Data validation view
│
├── 🤖 Data Scrapers
│   └── scrapers/
│       ├── README.md               # Scraper documentation
│       │
│       ├── espn/                   # ESPN AI-Powered Scraper
│       │   ├── README.md
│       │   ├── historical_scraper.py    # Main ESPN scraper
│       │   ├── espn_scraper.py          # Base scraper utilities
│       │   ├── gemini_client.py         # Gemini Vision API client
│       │   ├── auth_manager.py          # Cookie auth manager
│       │   └── data_extraction.py       # Data parsing utilities
│       │
│       └── sleeper/                # Sleeper API Scraper
│           ├── README.md
│           ├── sleeper_scraper.py       # Main Sleeper scraper
│           ├── sleeper_client.py        # Sleeper API client
│           ├── run_sleeper_scrape.py    # Convenience runner
│           ├── fetch_sleeper_projections.py  # Get projections
│           ├── enhance_sleeper_data.py  # Resolve player IDs
│           └── test_sleeper.py          # API testing
│
├── 💾 Data Storage
│   └── data/
│       ├── espn_fantasy.db         # SQLite database (all seasons)
│       ├── espn_league_*.json      # ESPN historical data (2019-2024)
│       ├── sleeper_*.json          # Sleeper data (2025)
│       └── sleeper_players.json    # Player ID mapping cache
│
├── 🛠️ Utilities
│   ├── populate_database.py        # Populate DB from JSON files
│   └── espn_cookies.json           # Saved ESPN login cookies
│
├── 📚 Documentation
│   ├── README.md                   # Main project README
│   ├── DEPLOYMENT.md               # Cloud deployment guide
│   ├── PROJECT_SUMMARY.md          # Detailed documentation
│   └── QUICKSTART.md               # Quick start guide
│
└── ⚙️ Configuration
    ├── requirements.txt            # Python dependencies
    ├── .env                        # Environment variables (gitignored)
    └── .gitignore                  # Git ignore rules
```

## File Counts

- **Core Application**: 2 files (app.py, data_manager.py)
- **ESPN Scraper**: 5 files
- **Sleeper Scraper**: 6 files
- **Templates**: 6 HTML files
- **Documentation**: 6 markdown files
- **Data Files**: 9 JSON files + 1 SQLite database

## Key Technologies

### Frontend
- Flask 3.0.0
- HTML/CSS (templates)

### ESPN Scraper
- Playwright 1.41.0 (browser automation)
- Gemini 3 Flash (AI vision)
- Python 3.10+

### Sleeper Scraper
- Requests 2.31.0 (HTTP)
- Sleeper REST API v1
- Python 3.10+

### Database
- SQLite3 (development)
- PostgreSQL/MySQL ready (production)

## Data Flow

```
ESPN Website
    ↓ (Gemini Vision AI)
ESPN Scraper → JSON Files → Database
    ↓
Flask Dashboard

Sleeper API
    ↓ (REST calls)
Sleeper Scraper → JSON Files → Database
    ↓
Flask Dashboard
```

## Clean & Organized ✨

All scraping code is organized in `scrapers/` with clear separation:
- ESPN → AI-powered web scraping
- Sleeper → REST API integration

All data in `data/` folder.
All presentation in Flask app at root level.

