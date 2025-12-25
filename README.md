# ESPN Fantasy Football AI Scraper

An intelligent web scraper that uses Google's Gemini 3 Flash AI model to extract comprehensive data from your ESPN Fantasy Football league.

## Features

- 🤖 **AI-Powered Extraction**: Uses Gemini 3 Flash vision to intelligently read ESPN pages
- 🍪 **Cookie Authentication**: Login once, scraper remembers your session
- 📊 **Comprehensive Data**: Extracts standings, matchups, rosters, transactions, and player stats
- ✅ **Data Validation**: AI verifies extracted data matches what's visible on ESPN
- 🌐 **Web Dashboard**: Flask-based interface to view and validate all data
- 💾 **Dual Storage**: Saves to both JSON (easy inspection) and SQLite (historical queries)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure API Key

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
```

Edit `.env` and add:
- Your Gemini API key (get it from https://makersuite.google.com/app/apikey)
- Your ESPN league ID (find it in your league's URL)
- Current season year

### 3. First Run

```bash
python espn_scraper.py
```

On first run:
1. Browser will open to ESPN Fantasy
2. Manually log in with your credentials
3. Press Enter in terminal when logged in
4. Scraper will save cookies and begin extracting data

### 4. View Data in Dashboard

```bash
python app.py
```

Open your browser to `http://localhost:5000` to view the dashboard.

## Usage

### Scrape League Data

```bash
# Uses saved cookies (fast)
python espn_scraper.py
```

### Start Dashboard

```bash
python app.py
# Visit http://localhost:5000
```

## Project Structure

```
.
├── espn_scraper.py      # Main scraper with Gemini 3 vision
├── data_manager.py      # Database and JSON storage
├── app.py               # Flask web dashboard
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── templates/           # HTML templates for dashboard
│   ├── base.html
│   ├── index.html
│   ├── matchups.html
│   ├── rosters.html
│   ├── transactions.html
│   └── validation.html
└── data/               # Generated data (gitignored)
    ├── espn_fantasy.db
    ├── espn_league_*.json
    └── screenshots/
```

## How It Works

1. **Browser Automation**: Playwright controls a Chrome browser to navigate ESPN
2. **AI Vision**: Gemini 3 Flash analyzes screenshots to extract data
3. **Smart Navigation**: AI identifies buttons and tabs to click
4. **Data Extraction**: Structured data extracted from visual page content
5. **Validation**: AI cross-checks extracted data with screenshots
6. **Storage**: Data saved to both JSON and SQLite for flexibility
7. **Visualization**: Flask dashboard displays all extracted data

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
playwright install chromium
```

### Login issues
- Delete `espn_cookies.json` and run scraper again
- Manually log in when browser opens
- Make sure your ESPN account has access to the league

### Gemini API errors
- Check your API key in `.env`
- Verify you have API access at https://makersuite.google.com/

## Notes

- Scraper respects ESPN's terms of service
- Uses cookie-based authentication (no password storage)
- Data is stored locally only
- Requires manual login on first run or if cookies expire

## License

MIT License - Use freely for personal fantasy football analysis!

