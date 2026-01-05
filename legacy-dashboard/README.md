# Legacy Dashboard

Original Flask app with dashboard UI. Used for testing data scraping and debugging.

## Purpose

This dashboard provides a web interface to:
- View standings across all historical seasons (2019-2025)
- Browse weekly matchups with detailed box scores
- Review draft picks
- Validate scraped data

## Running the Dashboard

```bash
cd legacy-dashboard
python3 app.py
```

Visit http://localhost:5001 (configured to avoid macOS AirPlay conflict on port 5000)

## Note

This is the legacy dashboard kept for testing data scraping when adding new seasons. For production use, the new backend/frontend will be used once developed.
