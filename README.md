# Fantasy Football Data Dashboard

A comprehensive fantasy football data extraction and visualization system supporting both ESPN (2019-2024) and Sleeper (2025+) leagues.

## Features

- 🤖 **AI-Powered ESPN Scraping**: Uses Gemini 3 Flash vision to extract ESPN data
- 🔌 **Sleeper API Integration**: Official Sleeper REST API for 2025+ data
- 📊 **Comprehensive Data**: Standings, matchups, box scores, drafts, projections
- 🌐 **Web Dashboard**: Flask-based interface to view all historical data
- 💾 **Dual Storage**: JSON files + SQLite database for cloud deployment
- 📈 **Player Projections**: Half-PPR projections for all Sleeper matchups
- 🏆 **Playoff Tracking**: Bracket labels and two-week playoff support

## Quick Start

### 1. Install Dependencies

```bash
# Create conda environment (recommended)
conda create -n ff-dashboard python=3.10 -y
conda activate ff-dashboard

# Install packages
pip install -r requirements.txt

# For ESPN scraping only
playwright install firefox
```

### 2. Configure

Copy `.env.example` to `.env` and set:
- `GEMINI_API_KEY` - For ESPN scraping (get from https://aistudio.google.com/apikey)
- `LEAGUE_ID` - Your ESPN league ID
- `SEASON_YEAR` - Current season

### 3. Run Dashboard

```bash
cd legacy-dashboard
python3 app.py
# Visit http://127.0.0.1:5001
```

## Project Structure

```
.
├── legacy-dashboard/         # Original Flask dashboard (for testing)
│   ├── app.py               # Flask web application
│   ├── config.py            # Configuration
│   ├── templates/           # HTML templates
│   └── README.md
│
├── backend/                  # NEW - Production API (to be built)
│   └── README.md
│
├── frontend/                 # NEW - Modern frontend (to be built)
│   └── README.md
│
├── scrapers/                 # Shared scraping tools
│   ├── espn/                # ESPN scraper (AI-powered)
│   │   ├── historical_scraper.py
│   │   ├── espn_scraper.py
│   │   ├── gemini_client.py
│   │   ├── auth_manager.py
│   │   └── data_extraction.py
│   │
│   ├── sleeper/             # Sleeper API scraper
│   │   ├── sleeper_scraper.py
│   │   ├── sleeper_client.py
│   │   ├── run_sleeper_scrape.py
│   │   ├── fetch_sleeper_projections.py
│   │   └── enhance_sleeper_data.py
│   │
│   └── nfl_stats_fetcher.py # NFL player stats
│
├── scripts/                  # Utility scripts
│   ├── populate_database.py # Database population
│   ├── populate_nfl_stats.py # NFL stats population
│   └── data_manager.py      # Data management
│
├── data/                     # Generated data (gitignored)
│   ├── espn_fantasy.db      # SQLite database
│   ├── espn_league_*.json   # ESPN historical data
│   └── sleeper_*.json       # Sleeper data
│
├── docs/                     # Documentation
│   ├── DEPLOYMENT.md
│   ├── PROJECT_SUMMARY.md
│   ├── QUICKSTART.md
│   └── NFL_PLAYER_STATS_README.md
│
├── requirements.txt          # Python dependencies
└── .env                      # Environment variables
```

## Usage

### ESPN Scraping (2019-2024)

```bash
# First time: Browser opens, login manually
python scrapers/espn/historical_scraper.py

# Subsequent runs: Uses saved cookies
python scrapers/espn/historical_scraper.py
```

**Features:**
- Cookie-based authentication
- Full box score rosters with projections
- Draft recaps
- Transactions
- Handles 2019 two-week playoffs

### Sleeper Scraping (2025+)

```bash
# 1. Scrape league data
python scrapers/sleeper/run_sleeper_scrape.py

# 2. Fetch player projections
python scrapers/sleeper/fetch_sleeper_projections.py

# 3. View in dashboard
python app.py
```

**Features:**
- No authentication required
- Weekly matchups with rosters
- Half-PPR projections
- Draft picks
- Playoff brackets

### Database Mode (Cloud Deployment)

```bash
# Populate database from JSON files
python3 scripts/populate_database.py

# Run in database mode
cd legacy-dashboard
USE_DATABASE=true python3 app.py
```

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for cloud deployment instructions.

## Dashboard Pages

- **Standings** - League rankings, wins/losses, points
- **Matchups** - Weekly scores, box scores, playoff brackets
- **Draft Recap** - All draft picks by round
- **Transactions** - Trades, adds, drops (ESPN only)
- **Validation** - Compare extracted data with screenshots (ESPN only)

## Data Sources

### ESPN (2019-2024)
- **Method**: AI-powered web scraping with Gemini Vision
- **Auth**: Cookie-based (login once)
- **Data**: Complete historical data with player-level details

### Sleeper (2025+)
- **Method**: Official REST API
- **Auth**: None required (public data)
- **Data**: Real-time data with player projections

## Troubleshooting

### ESPN Scraper
- **Login issues**: Delete `espn_cookies.json` and re-login
- **Timeout errors**: Increase `PAGE_LOAD_TIMEOUT` in config.py
- **404 Gemini error**: Check model name is `gemini-3-flash-preview`

### Sleeper Scraper
- **No data**: Verify username and league ID in `run_sleeper_scrape.py`
- **Missing player names**: Run `enhance_sleeper_data.py`
- **Missing projections**: Run `fetch_sleeper_projections.py`

### Dashboard
- **Port conflict**: Change `FLASK_PORT` in config.py
- **Missing season**: Check JSON files exist in `data/` folder
- **Empty rosters**: Re-run scraper or populate database

## Configuration

Edit `config.py` for:
- `GEMINI_API_KEY` - Gemini API key
- `GEMINI_MODEL` - Model name (default: `gemini-3-flash-preview`)
- `LEAGUE_ID` - ESPN league ID
- `SEASON_YEAR` - Current season
- `FLASK_PORT` - Dashboard port (default: 5001)
- `USE_DATABASE` - Use DB instead of JSON (for cloud)

## Documentation

- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - Cloud deployment guide
- [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) - Detailed project documentation
- [docs/NFL_PLAYER_STATS_README.md](docs/NFL_PLAYER_STATS_README.md) - NFL stats documentation
- [scrapers/README.md](scrapers/README.md) - Scraper documentation

## Requirements

- Python 3.10+
- Gemini API key (for ESPN scraping)
- ESPN account with league access
- Sleeper username (for Sleeper scraping)

## License

MIT License - Use freely for personal fantasy football analysis!

## Notes

- Respects ESPN's terms of service
- Cookie-based auth (no password storage)
- Data stored locally only
- Sleeper API is rate-limited (~1000 req/min)
