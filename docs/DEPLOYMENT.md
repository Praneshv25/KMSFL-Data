# Cloud Deployment Guide

This guide explains how to deploy your Fantasy Football Dashboard to the cloud using the SQLite database.

## Overview

The application supports two modes:
- **JSON Mode** (default): Reads data from JSON files in the `data/` folder
- **Database Mode**: Reads data from SQLite database (recommended for cloud deployment)

## Preparing for Cloud Deployment

### 1. Populate the Database

Run the population script to load all your fantasy data into the database:

```bash
python populate_database.py
```

This will:
- Create/recreate `data/espn_fantasy.db`
- Load all ESPN data (2019-2024)
- Load all Sleeper data (2025)
- Normalize and structure everything for efficient querying

**Database Contents:**
- Teams/Standings for each season
- All matchups with detailed box score rosters
- Draft picks for each season
- Supports both ESPN and Sleeper data sources

### 2. Enable Database Mode

Set the environment variable:

```bash
export USE_DATABASE=true
```

Or add to your `.env` file:

```
USE_DATABASE=true
```

### 3. Test Locally

Start Flask with database mode:

```bash
USE_DATABASE=true python app.py
```

Visit `http://127.0.0.1:5001` and verify all data loads correctly.

## Cloud Platform Setup

### Option 1: Heroku

1. **Create Heroku app:**
   ```bash
   heroku create your-app-name
   ```

2. **Set environment variables:**
   ```bash
   heroku config:set USE_DATABASE=true
   heroku config:set GEMINI_API_KEY=your-key-here
   ```

3. **Add files to deploy:**
   - Upload `data/espn_fantasy.db` (or use Heroku Postgres)
   - Ensure `requirements.txt` is up to date

4. **Deploy:**
   ```bash
   git push heroku main
   ```

### Option 2: Render/Railway/Fly.io

1. **Connect your GitHub repo**

2. **Set environment variables:**
   - `USE_DATABASE=true`
   - `GEMINI_API_KEY=your-key`

3. **Build command:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start command:**
   ```bash
   gunicorn app:app
   ```

### Option 3: AWS/GCP/Azure

1. **Use managed database service:**
   - AWS RDS (PostgreSQL/MySQL)
   - Google Cloud SQL
   - Azure Database

2. **Migrate from SQLite:**
   - Export data from SQLite
   - Import to cloud database
   - Update connection string in `config.py`

3. **Deploy Flask app:**
   - Use Elastic Beanstalk (AWS)
   - Use App Engine (GCP)
   - Use App Service (Azure)

## Database vs JSON Mode

### JSON Mode (USE_DATABASE=false)
- ✅ Simple setup
- ✅ No database required
- ❌ Slower for large datasets
- ❌ Not ideal for cloud (file storage)

### Database Mode (USE_DATABASE=true)
- ✅ Fast queries
- ✅ Cloud-friendly
- ✅ Scalable
- ✅ Better for production
- ❌ Requires database setup

## Files to Deploy

### Required Files:
- `app.py` - Flask application
- `config.py` - Configuration
- `data_manager.py` - Database utilities
- `requirements.txt` - Python dependencies
- `templates/` - HTML templates
- `static/` - CSS/JS assets (if any)
- `data/espn_fantasy.db` - SQLite database

### Optional (for re-scraping):
- `historical_scraper.py`
- `sleeper_scraper.py`
- `gemini_client.py`

### Not Needed for Cloud:
- JSON data files (if using database mode)
- Screenshot files
- Utility scripts

## Security Notes

1. **Never commit sensitive data:**
   - Add `.env` to `.gitignore`
   - Keep `GEMINI_API_KEY` in environment variables

2. **Database security:**
   - Use read-only connection for Flask app
   - Separate write access for data updates

3. **Access control:**
   - Add authentication if needed
   - Use environment-based access rules

## Updating Data

To update data in production:

1. **Run scrapers locally:**
   ```bash
   python historical_scraper.py  # For ESPN
   python run_sleeper_scrape.py  # For Sleeper
   ```

2. **Repopulate database:**
   ```bash
   python populate_database.py
   ```

3. **Deploy updated database:**
   - Replace `espn_fantasy.db` in production
   - Or run migration scripts

## Performance Tips

1. **Add indexes for common queries:**
   ```sql
   CREATE INDEX idx_matchups_season ON matchups(season_year, week);
   CREATE INDEX idx_rosters_matchup ON matchup_rosters(season_year, week, matchup_id);
   ```

2. **Enable connection pooling** for high traffic

3. **Consider caching** frequently accessed data

## Monitoring

- Monitor database size (currently ~5-10 MB)
- Log query performance
- Track API response times
- Set up alerts for errors

## Support

For issues or questions, check:
- Application logs
- Database connection status
- Environment variable configuration

