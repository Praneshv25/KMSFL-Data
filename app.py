"""
Flask Web Dashboard for ESPN Fantasy Data
View and validate scraped data with historical seasons
"""
from flask import Flask, render_template, jsonify, request, send_from_directory
import json
import os
import glob
from datetime import datetime
import config
from data_manager import DataManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'espn-fantasy-scraper-secret-key'

# Initialize data manager
data_manager = DataManager()


def get_available_seasons():
    """Get list of all available seasons from JSON files"""
    json_files = glob.glob(os.path.join(config.DATA_DIR, "espn_league_*_historical.json"))
    seasons = []
    for f in json_files:
        try:
            filename = os.path.basename(f)
            # Extract year from filename: espn_league_LEAGUEID_YEAR_historical.json
            # Example: espn_league_31288798_2019_historical.json
            parts = filename.replace('.json', '').split('_')
            # parts will be: ['espn', 'league', '31288798', '2019', 'historical']
            # We want index 3 (the year)
            if len(parts) >= 4:
                year = parts[3]
                if year.isdigit() and len(year) == 4:  # Make sure it's a 4-digit year
                    seasons.append(int(year))
        except:
            continue
    return sorted(seasons, reverse=True)  # Most recent first


def load_json_data(season=None):
    """Load data for a specific season or most recent"""
    if season:
        # Load specific season
        pattern = os.path.join(config.DATA_DIR, f"espn_league_{config.LEAGUE_ID}_{season}_historical.json")
        files = glob.glob(pattern)
        if files:
            with open(files[0], 'r') as f:
                return json.load(f)
    
    # Load most recent if no season specified
    json_files = glob.glob(os.path.join(config.DATA_DIR, "espn_league_*_historical.json"))
    if not json_files:
        return None
    
    latest = max(json_files, key=os.path.getmtime)
    with open(latest, 'r') as f:
        return json.load(f)


@app.route('/')
def index():
    """Home page with league overview"""
    selected_season = request.args.get('season', type=int)
    available_seasons = get_available_seasons()
    
    if not selected_season and available_seasons:
        selected_season = available_seasons[0]
    
    data = load_json_data(selected_season)
    
    if not data:
        return render_template('index.html', 
                             error="No data found. Please run the scraper first.",
                             available_seasons=available_seasons,
                             selected_season=selected_season)
    
    standings = data.get('standings', [])
    matchups = data.get('matchups', {})
    scraped_at = data.get('scraped_at', 'Unknown')
    
    return render_template('index.html',
                         standings=standings,
                         total_teams=len(standings),
                         total_weeks=len(matchups),
                         scraped_at=scraped_at,
                         league_id=config.LEAGUE_ID,
                         season_year=selected_season,
                         available_seasons=available_seasons,
                         selected_season=selected_season)


@app.route('/matchups')
def matchups():
    """Matchups page with box score details"""
    selected_season = request.args.get('season', type=int)
    available_seasons = get_available_seasons()
    
    if not selected_season and available_seasons:
        selected_season = available_seasons[0]
    
    data = load_json_data(selected_season)
    
    if not data:
        return render_template('matchups.html', error="No data found",
                             available_seasons=available_seasons)
    
    matchups_data = data.get('matchups', {})
    
    # Get selected week
    selected_week = request.args.get('week', type=int)
    if not selected_week and matchups_data:
        week_nums = [int(w) for w in matchups_data.keys() if str(w).isdigit()]
        selected_week = max(week_nums) if week_nums else 1
    
    week_matchups = matchups_data.get(str(selected_week), matchups_data.get(selected_week, []))
    
    return render_template('matchups.html',
                         matchups=week_matchups,
                         selected_week=selected_week,
                         available_weeks=sorted([int(w) for w in matchups_data.keys() if str(w).isdigit()]),
                         scraped_at=data.get('scraped_at', 'Unknown'),
                         season_year=selected_season,
                         available_seasons=available_seasons,
                         selected_season=selected_season)


@app.route('/draft')
def draft():
    """Draft recap page"""
    selected_season = request.args.get('season', type=int)
    available_seasons = get_available_seasons()
    
    if not selected_season and available_seasons:
        selected_season = available_seasons[0]
    
    data = load_json_data(selected_season)
    
    if not data:
        return render_template('draft.html', error="No data found",
                             available_seasons=available_seasons)
    
    draft_data = data.get('draft', {})
    picks = draft_data.get('picks', [])
    
    return render_template('draft.html',
                         draft_data=draft_data,
                         picks=picks,
                         total_picks=len(picks),
                         season_year=selected_season,
                         available_seasons=available_seasons,
                         selected_season=selected_season,
                         scraped_at=data.get('scraped_at', 'Unknown'))


@app.route('/rosters')
def rosters():
    """Rosters page - removed since we have box score rosters per week"""
    return render_template('error.html', 
                         message="Rosters are now available in the Matchups view (click on any week to see weekly rosters)")


@app.route('/transactions')
def transactions():
    """Transactions page"""
    selected_season = request.args.get('season', type=int)
    available_seasons = get_available_seasons()
    
    if not selected_season and available_seasons:
        selected_season = available_seasons[0]
    
    data = load_json_data(selected_season)
    
    if not data:
        return render_template('transactions.html', error="No data found",
                             available_seasons=available_seasons)
    
    transactions_data = data.get('transactions', [])
    
    return render_template('transactions.html',
                         transactions=transactions_data,
                         scraped_at=data.get('scraped_at', 'Unknown'),
                         season_year=selected_season,
                         available_seasons=available_seasons,
                         selected_season=selected_season)


@app.route('/validation')
def validation():
    """Validation page with screenshots"""
    selected_season = request.args.get('season', type=int)
    available_seasons = get_available_seasons()
    
    if not selected_season and available_seasons:
        selected_season = available_seasons[0]
    
    data = load_json_data(selected_season)
    
    if not data:
        return render_template('validation.html', error="No data found",
                             available_seasons=available_seasons)
    
    # Get all screenshots
    screenshots = []
    if os.path.exists(config.SCREENSHOT_DIR):
        screenshot_files = glob.glob(os.path.join(config.SCREENSHOT_DIR, "*.png"))
        screenshots = [
            {
                'name': os.path.basename(f),
                'path': f,
                'timestamp': datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y-%m-%d %H:%M:%S')
            }
            for f in sorted(screenshot_files, key=os.path.getmtime, reverse=True)
        ]
    
    return render_template('validation.html',
                         data=data,
                         screenshots=screenshots,
                         scraped_at=data.get('scraped_at', 'Unknown'),
                         season_year=selected_season,
                         available_seasons=available_seasons,
                         selected_season=selected_season)


@app.route('/api/data')
def api_data():
    """API endpoint for full data"""
    season = request.args.get('season', type=int)
    data = load_json_data(season)
    if not data:
        return jsonify({'error': 'No data found'}), 404
    return jsonify(data)


@app.route('/api/seasons')
def api_seasons():
    """API endpoint for available seasons"""
    return jsonify({'seasons': get_available_seasons()})


@app.route('/screenshots/<filename>')
def screenshot(filename):
    """Serve screenshot files"""
    return send_from_directory(config.SCREENSHOT_DIR, filename)


@app.errorhandler(404)
def not_found(e):
    """404 error handler"""
    return render_template('base.html', error="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    """500 error handler"""
    return render_template('base.html', error="Server error"), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("ESPN Fantasy Football Dashboard")
    print("="*60)
    print(f"\nStarting server at http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    print("\nAvailable pages:")
    print("  - Home (Standings):  /")
    print("  - Matchups:          /matchups")
    print("  - Draft Recap:       /draft")
    print("  - Transactions:      /transactions")
    print("  - Validation:        /validation")
    print("\nPress Ctrl+C to stop")
    print("="*60 + "\n")
    
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )
