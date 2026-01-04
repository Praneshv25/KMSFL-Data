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

# Database query functions
def load_from_database(season, source):
    """Load data from SQLite database"""
    import sqlite3
    
    conn = sqlite3.connect(config.DB_FILE)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    cursor = conn.cursor()
    
    data = {
        '_source': source,
        'season_year': season,
        'standings': [],
        'matchups': {},
        'draft': {'picks': []},
        'scraped_at': datetime.now().isoformat()
    }
    
    # Load standings
    cursor.execute("""
        SELECT * FROM teams 
        WHERE season_year = ? AND data_source = ?
        ORDER BY rank
    """, (season, source))
    
    for row in cursor.fetchall():
        data['standings'].append({
            'rank': row['rank'],
            'team_name': row['team_name'],
            'owner': row['owner'],
            'wins': row['wins'],
            'losses': row['losses'],
            'ties': row['ties'],
            'points_for': row['points_for'],
            'points_against': row['points_against']
        })
    
    # Load matchups with rosters
    cursor.execute("""
        SELECT DISTINCT week FROM matchups 
        WHERE season_year = ? AND data_source = ?
        ORDER BY week
    """, (season, source))
    
    weeks = [row['week'] for row in cursor.fetchall()]
    
    for week in weeks:
        cursor.execute("""
            SELECT * FROM matchups
            WHERE season_year = ? AND data_source = ? AND week = ?
        """, (season, source, week))
        
        week_matchups = []
        for matchup_row in cursor.fetchall():
            matchup = {
                'week': matchup_row['week'],
                'season': matchup_row['season_year'],
                'matchup_id': matchup_row['matchup_id'],
                'home_team': matchup_row['home_team'],
                'away_team': matchup_row['away_team'],
                'home_score': matchup_row['home_score'],
                'away_score': matchup_row['away_score'],
                'home_projected': matchup_row['home_projected'],
                'away_projected': matchup_row['away_projected'],
                'home_roster': [],
                'away_roster': []
            }
            
            # Add optional fields
            if matchup_row['bracket_type']:
                matchup['bracket_type'] = matchup_row['bracket_type']
            if matchup_row['round']:
                matchup['round'] = matchup_row['round']
            if matchup_row['is_two_week_playoff']:
                matchup['is_two_week_playoff'] = matchup_row['is_two_week_playoff']
                matchup['home_total_score'] = matchup_row['home_total_score']
                matchup['away_total_score'] = matchup_row['away_total_score']
            
            # Load rosters for this matchup
            cursor.execute("""
                SELECT * FROM matchup_rosters
                WHERE season_year = ? AND week = ? AND matchup_id = ? AND team_name = ?
                ORDER BY started DESC, position
            """, (season, week, matchup_row['matchup_id'], matchup_row['home_team']))
            
            for player_row in cursor.fetchall():
                matchup['home_roster'].append({
                    'player_name': player_row['player_name'],
                    'position': player_row['position'],
                    'nfl_team': player_row['nfl_team'],
                    'points': player_row['points'],
                    'projected': player_row['projected'],
                    'started': bool(player_row['started'])
                })
            
            cursor.execute("""
                SELECT * FROM matchup_rosters
                WHERE season_year = ? AND week = ? AND matchup_id = ? AND team_name = ?
                ORDER BY started DESC, position
            """, (season, week, matchup_row['matchup_id'], matchup_row['away_team']))
            
            for player_row in cursor.fetchall():
                matchup['away_roster'].append({
                    'player_name': player_row['player_name'],
                    'position': player_row['position'],
                    'nfl_team': player_row['nfl_team'],
                    'points': player_row['points'],
                    'projected': player_row['projected'],
                    'started': bool(player_row['started'])
                })
            
            week_matchups.append(matchup)
        
        data['matchups'][str(week)] = week_matchups
    
    # Load draft picks
    cursor.execute("""
        SELECT * FROM draft_picks
        WHERE season_year = ? AND data_source = ?
        ORDER BY overall_pick
    """, (season, source))
    
    for row in cursor.fetchall():
        data['draft']['picks'].append({
            'round': row['round'],
            'pick': row['pick'],
            'overall_pick': row['overall_pick'],
            'team': row['team'],
            'player_name': row['player_name'],
            'position': row['position'],
            'nfl_team': row['nfl_team']
        })
    
    conn.close()
    return data


def get_available_seasons():
    """Get list of all available seasons from JSON files (both ESPN and Sleeper)"""
    seasons = []
    
    # Get ESPN seasons (2019-2024)
    espn_files = glob.glob(os.path.join(config.DATA_DIR, "espn_league_*_historical.json"))
    for f in espn_files:
        try:
            filename = os.path.basename(f)
            parts = filename.replace('.json', '').split('_')
            if len(parts) >= 4:
                year = parts[3]
                if year.isdigit() and len(year) == 4:
                    seasons.append({'year': int(year), 'source': 'espn'})
        except:
            continue
    
    # Get Sleeper seasons (2025+)
    sleeper_files = glob.glob(os.path.join(config.DATA_DIR, "sleeper_*_*.json"))
    for f in sleeper_files:
        try:
            filename = os.path.basename(f)
            # Format: sleeper_LEAGUEID_YEAR.json
            parts = filename.replace('.json', '').split('_')
            if len(parts) >= 3:
                year = parts[2]
                if year.isdigit() and len(year) == 4:
                    seasons.append({'year': int(year), 'source': 'sleeper'})
        except:
            continue
    
    # Sort by year, most recent first
    return sorted(seasons, key=lambda x: x['year'], reverse=True)


def load_json_data(season=None, source=None):
    """Load data for a specific season (ESPN or Sleeper)"""
    if season and source:
        # Use database if configured (for cloud deployment)
        if config.USE_DATABASE:
            return load_from_database(season, source)
        
        # Otherwise load from JSON files
        if source == 'espn':
            pattern = os.path.join(config.DATA_DIR, f"espn_league_*_{season}_historical.json")
        else:  # sleeper
            pattern = os.path.join(config.DATA_DIR, f"sleeper_*_{season}.json")
        
        files = glob.glob(pattern)
        if files:
            with open(files[0], 'r') as f:
                data = json.load(f)
                data['_source'] = source  # Add source info
                return normalize_data(data, source)
    
    # Load most recent if no season specified
    all_files = (
        glob.glob(os.path.join(config.DATA_DIR, "espn_league_*_historical.json")) +
        glob.glob(os.path.join(config.DATA_DIR, "sleeper_*.json"))
    )
    
    if not all_files:
        return None
    
    latest = max(all_files, key=os.path.getmtime)
    with open(latest, 'r') as f:
        data = json.load(f)
        # Determine source from filename
        if 'sleeper_' in os.path.basename(latest):
            data['_source'] = 'sleeper'
            return normalize_data(data, 'sleeper')
        else:
            data['_source'] = 'espn'
            return normalize_data(data, 'espn')


def clean_sleeper_player_name(name):
    """Remove (TEAM POS) suffix from Sleeper player names"""
    if name and '(' in name and ')' in name:
        return name.split('(')[0].strip()
    return name


def load_sleeper_players():
    """Load Sleeper player data for position/team lookups"""
    players_file = os.path.join(config.DATA_DIR, 'sleeper_players.json')
    if os.path.exists(players_file):
        with open(players_file, 'r') as f:
            return json.load(f)
    return {}


def sort_roster_by_position(roster):
    """
    Sort roster with starters first (in position order), then bench.
    Position order: QB, RB, WR, TE, FLEX, D/ST, K
    """
    # Define position order
    position_order = {
        'QB': 1,
        'RB': 2,
        'WR': 3,
        'TE': 4,
        'FLEX': 5,
        'D/ST': 6,
        'DEF': 6,  # Defense alias
        'K': 7
    }
    
    # Separate starters and bench
    starters = [p for p in roster if p.get('started')]
    bench = [p for p in roster if not p.get('started')]
    
    # Sort starters by position order
    def get_sort_key(player):
        pos = player.get('position', 'ZZ')
        return position_order.get(pos, 99)
    
    starters.sort(key=get_sort_key)
    bench.sort(key=get_sort_key)
    
    # Combine: starters first, then bench
    return starters + bench


def normalize_espn_roster(roster, is_bench=False):
    """Convert old ESPN roster format (2019) to new format"""
    normalized = []
    for player in roster:
        # Handle old format (2019) - has 'player' instead of 'player_name'
        if 'player' in player and 'player_name' not in player:
            # Parse team_pos like "Ten QB" to get team and position
            team_pos = player.get('team_pos') or ''
            parts = team_pos.split() if team_pos else []
            nfl_team = parts[0] if parts else ''
            position = parts[1] if len(parts) > 1 else player.get('slot', 'N/A')
            
            normalized_player = {
                'player_name': player.get('player'),
                'position': position,
                'nfl_team': nfl_team,
                'points': player.get('fpts', 0),
                'projected': player.get('proj', 0),
                'started': not is_bench and player.get('slot', '').lower() != 'bench'
            }
            normalized.append(normalized_player)
        else:
            # Already in new format
            normalized.append(player)
    
    return normalized


def normalize_espn_data(data):
    """Normalize ESPN data to handle different field name formats (2019 vs later years)"""
    matchups = data.get('matchups', {})
    
    for week, week_matchups in matchups.items():
        for matchup in week_matchups:
            # Normalize home_roster
            if matchup.get('home_roster'):
                matchup['home_roster'] = normalize_espn_roster(matchup['home_roster'])
            
            # Normalize away_roster  
            if matchup.get('away_roster'):
                matchup['away_roster'] = normalize_espn_roster(matchup['away_roster'])
            
            # Normalize home_bench (if exists as separate field)
            if matchup.get('home_bench'):
                bench_normalized = normalize_espn_roster(matchup['home_bench'], is_bench=True)
                matchup['home_roster'].extend(bench_normalized)
                del matchup['home_bench']
            
            # Normalize away_bench (if exists as separate field)
            if matchup.get('away_bench'):
                bench_normalized = normalize_espn_roster(matchup['away_bench'], is_bench=True)
                matchup['away_roster'].extend(bench_normalized)
                del matchup['away_bench']
    
    return data


def normalize_data(data, source):
    """Normalize data structure between ESPN and Sleeper formats"""
    if source == 'sleeper':
        # Convert Sleeper format to match ESPN structure for display
        # Load player data for position/team lookups
        sleeper_players = load_sleeper_players()
        
        # Get draft info
        drafts = data.get('drafts', [])
        draft_info = drafts[0] if drafts else {}
        draft_type = draft_info.get('type', 'snake')
        draft_start_time = draft_info.get('start_time')
        
        # Format draft date
        if draft_start_time:
            from datetime import datetime
            draft_date = datetime.fromtimestamp(draft_start_time / 1000).strftime('%B %d, %Y')
        else:
            draft_date = 'Unknown'
        
        normalized = {
            '_source': 'sleeper',
            'scraped_at': data.get('scraped_at', ''),
            'season_year': int(data.get('season', 2025)),
            'league_id': data.get('league', {}).get('league_id', ''),
            'standings': [],
            'matchups': {},
            'draft': {
                'picks': [],
                'draft_type': draft_type.capitalize(),
                'draft_date': draft_date
            },
            'transactions': [],
            '_raw_sleeper': data  # Keep raw data for advanced views
        }
        
        # Convert rosters to standings
        rosters = data.get('rosters', [])
        users = {u['user_id']: u for u in data.get('users', [])}
        
        for roster in rosters:
            settings = roster.get('settings', {})
            owner_id = roster.get('owner_id')
            user = users.get(owner_id, {})
            
            normalized['standings'].append({
                'rank': settings.get('final_rank', 0),  # Use final_rank if available
                'team_name': user.get('metadata', {}).get('team_name') or user.get('display_name', 'Unknown'),
                'owner': user.get('display_name', 'Unknown'),
                'wins': settings.get('wins', 0),
                'losses': settings.get('losses', 0),
                'ties': settings.get('ties', 0),
                'points_for': settings.get('fpts', 0) + settings.get('fpts_decimal', 0) / 100,
                'points_against': settings.get('fpts_against', 0) + settings.get('fpts_against_decimal', 0) / 100,
                'roster_id': roster.get('roster_id'),
                'final_rank': settings.get('final_rank')  # Keep final_rank for sorting
            })
        
        # Sort standings by final_rank if available, otherwise by wins then points
        has_final_ranks = any(team.get('final_rank') for team in normalized['standings'])
        
        if has_final_ranks:
            # Sort by final_rank (ascending - 1st place first)
            normalized['standings'] = sorted(
                normalized['standings'],
                key=lambda x: x.get('final_rank', 999)
            )
        else:
            # Sort by wins then points (descending)
            normalized['standings'] = sorted(
                normalized['standings'],
                key=lambda x: (x['wins'], x['points_for']),
                reverse=True
            )
            # Add ranks if no final_rank
            for i, team in enumerate(normalized['standings'], 1):
                team['rank'] = i
        
        # Convert matchups to ESPN-like format
        roster_to_team = {s['roster_id']: s['team_name'] for s in normalized['standings']}
        
        for week, week_matchups in data.get('matchups', {}).items():
            # Group matchups by matchup_id
            matchup_groups = {}
            for m in week_matchups:
                mid = m.get('matchup_id')
                if mid not in matchup_groups:
                    matchup_groups[mid] = []
                matchup_groups[mid].append(m)
            
            # Convert to ESPN format
            normalized_week_matchups = []
            for matchup_id, teams in matchup_groups.items():
                if len(teams) == 2:
                    team1, team2 = teams
                    
                    # Build rosters in ESPN format (combine starters and bench with 'started' flag)
                    home_roster = []
                    away_roster = []
                    
                    # Process all players for home team
                    for p in team1.get('players_with_names', []):
                        player_id = p.get('player_id')
                        player_info = sleeper_players.get(player_id, {})
                        
                        home_roster.append({
                            'player_name': clean_sleeper_player_name(p.get('player_name', 'Unknown')),
                            'position': player_info.get('position', 'N/A'),
                            'nfl_team': player_info.get('team', ''),
                            'points': p.get('points', 0),
                            'projected': p.get('projected', 0),
                            'started': p.get('is_starter', False)
                        })
                    
                    # Process all players for away team
                    for p in team2.get('players_with_names', []):
                        player_id = p.get('player_id')
                        player_info = sleeper_players.get(player_id, {})
                        
                        away_roster.append({
                            'player_name': clean_sleeper_player_name(p.get('player_name', 'Unknown')),
                            'position': player_info.get('position', 'N/A'),
                            'nfl_team': player_info.get('team', ''),
                            'points': p.get('points', 0),
                            'projected': p.get('projected', 0),
                            'started': p.get('is_starter', False)
                        })
                    
                    # Sort rosters: starters first (by position order), then bench
                    home_roster = sort_roster_by_position(home_roster)
                    away_roster = sort_roster_by_position(away_roster)
                    
                    # Calculate projected totals (sum of started players only)
                    home_projected = sum(p['projected'] for p in home_roster if p.get('started'))
                    away_projected = sum(p['projected'] for p in away_roster if p.get('started'))
                    
                    # Get bracket type (if any) from either team's matchup data
                    bracket_type = team1.get('bracket_type') or team2.get('bracket_type')
                    
                    normalized_matchup = {
                        'week': int(week),
                        'season': normalized['season_year'],
                        'matchup_id': matchup_id,
                        'home_team': roster_to_team.get(team1.get('roster_id'), f"Team {team1.get('roster_id')}"),
                        'away_team': roster_to_team.get(team2.get('roster_id'), f"Team {team2.get('roster_id')}"),
                        'home_score': team1.get('points', 0),
                        'away_score': team2.get('points', 0),
                        'home_projected': home_projected,
                        'away_projected': away_projected,
                        'home_roster': home_roster,
                        'away_roster': away_roster
                    }
                    
                    # Add bracket_type if it exists
                    if bracket_type:
                        normalized_matchup['bracket_type'] = bracket_type
                    
                    normalized_week_matchups.append(normalized_matchup)
            
            normalized['matchups'][week] = normalized_week_matchups
        
        # Convert draft picks
        roster_to_team = {s['roster_id']: s['team_name'] for s in normalized['standings']}
        
        for draft in data.get('drafts', []):
            for idx, pick in enumerate(draft.get('picks', []), 1):
                # Extract player info
                player_info = pick.get('player_info', {})
                metadata = pick.get('metadata', {})
                
                # Get the team that made the pick (use roster_id from the pick)
                roster_id = pick.get('roster_id')
                team_name = roster_to_team.get(roster_id, f"Team {roster_id}")
                
                # Clean player name - remove "(TEAM POS)" suffix from Sleeper format
                player_name = clean_sleeper_player_name(pick.get('player_name', 'Unknown'))
                
                normalized['draft']['picks'].append({
                    'round': pick.get('round'),
                    'pick': pick.get('pick_no'),
                    'overall_pick': idx,
                    'team': team_name,
                    'player_name': player_name,
                    'position': player_info.get('position') or metadata.get('position', 'N/A'),
                    'nfl_team': player_info.get('team') or metadata.get('team', ''),
                    'player_id': pick.get('player_id'),
                    'picked_by': pick.get('picked_by'),
                    'roster_id': roster_id,
                    'metadata': metadata,
                    'player_info': player_info
                })
        
        return normalized
    else:
        # ESPN data - normalize field names (handles 2019 format)
        data['_source'] = 'espn'
        return normalize_espn_data(data)


@app.route('/')
def index():
    """Home page with league overview"""
    available_seasons = get_available_seasons()
    
    # Get selected season (year and source)
    selected_year = request.args.get('season', type=int)
    if not selected_year and available_seasons:
        selected_year = available_seasons[0]['year']
    
    # Find source for selected year
    season_info = next((s for s in available_seasons if s['year'] == selected_year), None)
    if not season_info:
        return render_template('index.html', 
                             error="Season not found",
                             available_seasons=available_seasons,
                             selected_season=selected_year)
    
    data = load_json_data(selected_year, season_info['source'])
    
    if not data:
        return render_template('index.html', 
                             error="No data found. Please run the scraper first.",
                             available_seasons=available_seasons,
                             selected_season=selected_year)
    
    standings = data.get('standings', [])
    matchups = data.get('matchups', {})
    scraped_at = data.get('scraped_at', 'Unknown')
    
    return render_template('index.html',
                         standings=standings,
                         total_teams=len(standings),
                         total_weeks=len(matchups),
                         scraped_at=scraped_at,
                         league_id=data.get('league_id', config.LEAGUE_ID),
                         season_year=selected_year,
                         data_source=data.get('_source', 'espn'),
                         available_seasons=available_seasons,
                         selected_season=selected_year)


@app.route('/matchups')
def matchups():
    """Matchups page with box score details"""
    available_seasons = get_available_seasons()
    
    selected_year = request.args.get('season', type=int)
    if not selected_year and available_seasons:
        selected_year = available_seasons[0]['year']
    
    season_info = next((s for s in available_seasons if s['year'] == selected_year), None)
    if not season_info:
        return render_template('matchups.html', error="Season not found",
                             available_seasons=available_seasons)
    
    data = load_json_data(selected_year, season_info['source'])
    
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
                         season_year=selected_year,
                         data_source=data.get('_source', 'espn'),
                         available_seasons=available_seasons,
                         selected_season=selected_year)


@app.route('/draft')
def draft():
    """Draft recap page"""
    available_seasons = get_available_seasons()
    
    # Get selected season (year and source)
    selected_year = request.args.get('season', type=int)
    if not selected_year and available_seasons:
        selected_year = available_seasons[0]['year']
    
    # Find source for selected year
    season_info = next((s for s in available_seasons if s['year'] == selected_year), None)
    if not season_info:
        return render_template('draft.html', 
                             error="Season not found",
                             available_seasons=available_seasons,
                             selected_season=selected_year)
    
    data = load_json_data(selected_year, season_info['source'])
    
    if not data:
        return render_template('draft.html', error="No data found",
                             available_seasons=available_seasons,
                             selected_season=selected_year)
    
    draft_data = data.get('draft', {})
    picks = draft_data.get('picks', [])
    
    return render_template('draft.html',
                         draft_data=draft_data,
                         picks=picks,
                         total_picks=len(picks),
                         season_year=selected_year,
                         available_seasons=available_seasons,
                         selected_season=selected_year,
                         data_source=season_info['source'],
                         scraped_at=data.get('scraped_at', 'Unknown'))


@app.route('/rosters')
def rosters():
    """Rosters page - removed since we have box score rosters per week"""
    return render_template('error.html', 
                         message="Rosters are now available in the Matchups view (click on any week to see weekly rosters)")


@app.route('/transactions')
def transactions():
    """Transactions page"""
    available_seasons = get_available_seasons()
    
    # Get selected season (year and source)
    selected_year = request.args.get('season', type=int)
    if not selected_year and available_seasons:
        selected_year = available_seasons[0]['year']
    
    # Find source for selected year
    season_info = next((s for s in available_seasons if s['year'] == selected_year), None)
    if not season_info:
        return render_template('transactions.html', 
                             error="Season not found",
                             available_seasons=available_seasons,
                             selected_season=selected_year)
    
    data = load_json_data(selected_year, season_info['source'])
    
    if not data:
        return render_template('transactions.html', error="No data found",
                             available_seasons=available_seasons,
                             selected_season=selected_year)
    
    transactions_data = data.get('transactions', [])
    
    return render_template('transactions.html',
                         transactions=transactions_data,
                         scraped_at=data.get('scraped_at', 'Unknown'),
                         season_year=selected_year,
                         available_seasons=available_seasons,
                         selected_season=selected_year,
                         data_source=season_info['source'])


@app.route('/validation')
def validation():
    """Validation page with screenshots"""
    available_seasons = get_available_seasons()
    
    # Get selected season (year and source)
    selected_year = request.args.get('season', type=int)
    if not selected_year and available_seasons:
        selected_year = available_seasons[0]['year']
    
    # Find source for selected year
    season_info = next((s for s in available_seasons if s['year'] == selected_year), None)
    if not season_info:
        return render_template('validation.html', 
                             error="Season not found",
                             available_seasons=available_seasons,
                             selected_season=selected_year)
    
    data = load_json_data(selected_year, season_info['source'])
    
    if not data:
        return render_template('validation.html', error="No data found",
                             available_seasons=available_seasons,
                             selected_season=selected_year)
    
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
                         season_year=selected_year,
                         available_seasons=available_seasons,
                         selected_season=selected_year,
                         data_source=season_info['source'])


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


@app.route('/api/dst-stats/<team_identifier>')
def api_dst_stats(team_identifier):
    """
    API endpoint specifically for D/ST stats (avoids URL routing issues)
    
    Args:
        team_identifier: Team code (JAX, CIN, etc.) or team name
        
    Query params:
        season: Optional season year to filter by
    """
    from scrapers.nfl_stats_fetcher import NFLStatsFetcher, TEAM_ABBR_TO_NAME
    import sqlite3
    
    season = request.args.get('season', type=int)
    
    try:
        fetcher = NFLStatsFetcher()
        
        # Extract team code
        team_code = fetcher.extract_team_code(team_identifier)
        
        if not team_code:
            return jsonify({
                'error': 'D/ST team not found',
                'message': f'Could not identify team from: {team_identifier}'
            }), 404
        
        # Fetch D/ST stats from database
        conn = sqlite3.connect(config.DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get weekly D/ST stats
        if season:
            cursor.execute("""
                SELECT * FROM nfl_team_defense_stats
                WHERE team_abbr = ? AND season = ? AND season_type = 'REG'
                ORDER BY week
            """, (team_code, season))
        else:
            cursor.execute("""
                SELECT * FROM nfl_team_defense_stats
                WHERE team_abbr = ? AND season_type = 'REG'
                ORDER BY season DESC, week
            """, (team_code,))
        
        weekly_stats = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if not weekly_stats:
            return jsonify({
                'error': 'No D/ST stats found',
                'message': f'No stats available for {TEAM_ABBR_TO_NAME.get(team_code, team_code)} defense'
            }), 404
        
        # Group by season
        seasons_data = {}
        for stat in weekly_stats:
            season_year = stat['season']
            if season_year not in seasons_data:
                seasons_data[season_year] = []
            seasons_data[season_year].append(stat)
        
        # Calculate season totals
        season_totals = {}
        for season_year, season_stats in seasons_data.items():
            totals = {
                'season': season_year,
                'games': len(season_stats),
                'def_sacks': sum(s['def_sacks'] or 0 for s in season_stats),
                'def_interceptions': sum(s['def_interceptions'] or 0 for s in season_stats),
                'def_fumbles_recovered': sum(s['def_fumbles_recovered'] or 0 for s in season_stats),
                'def_fumbles_forced': sum(s['def_fumbles_forced'] or 0 for s in season_stats),
                'def_touchdowns': sum(s['def_touchdowns'] or 0 for s in season_stats),
                'special_teams_tds': sum(s['special_teams_tds'] or 0 for s in season_stats),
                'def_safeties': sum(s['def_safeties'] or 0 for s in season_stats),
                'points_allowed': sum(s['points_allowed'] or 0 for s in season_stats),
                'avg_points_allowed': sum(s['points_allowed'] or 0 for s in season_stats) / len(season_stats) if season_stats else 0,
                'fantasy_points': sum(s['fantasy_points'] or 0 for s in season_stats),
                'fantasy_points_ppr': sum(s['fantasy_points_ppr'] or 0 for s in season_stats)
            }
            season_totals[season_year] = totals
        
        # Get team info
        player_info = {
            'player_id': f'DST_{team_code}',
            'player_name': TEAM_ABBR_TO_NAME.get(team_code, team_code),
            'player_display_name': f'{TEAM_ABBR_TO_NAME.get(team_code, team_code)} D/ST',
            'position': 'DST',
            'team': team_code
        }
        
        return jsonify({
            'player_info': player_info,
            'weekly_stats': weekly_stats,
            'seasons_data': seasons_data,
            'season_totals': season_totals,
            'total_games': len(weekly_stats),
            'is_dst': True
        })
    
    except ImportError:
        return jsonify({
            'error': 'NFL stats module not available',
            'message': 'Please run: pip install nflreadpy polars'
        }), 503
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch D/ST stats',
            'message': str(e)
        }), 500



@app.route('/api/player-stats/<player_name>')
def api_player_stats(player_name):
    """
    API endpoint for player NFL stats (including D/ST)
    
    Args:
        player_name: Player name or D/ST team name (from fantasy roster)
        
    Query params:
        season: Optional season year to filter by
    """
    from scrapers.nfl_stats_fetcher import NFLStatsFetcher
    import sqlite3
    
    season = request.args.get('season', type=int)
    
    try:
        fetcher = NFLStatsFetcher()
        
        # Check if this is a D/ST query
        is_dst = any(keyword in player_name.upper() for keyword in ['D/ST', 'DEF', 'DST', 'DEFENSE'])
        
        if is_dst:
            # Extract team code from D/ST name
            team_code = fetcher.extract_team_code(player_name)
            
            if not team_code:
                return jsonify({
                    'error': 'D/ST team not found',
                    'message': f'Could not identify team from: {player_name}'
                }), 404
            
            # Fetch D/ST stats from database
            conn = sqlite3.connect(config.DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get weekly D/ST stats
            if season:
                cursor.execute("""
                    SELECT * FROM nfl_team_defense_stats
                    WHERE team_abbr = ? AND season = ? AND season_type = 'REG'
                    ORDER BY week
                """, (team_code, season))
            else:
                cursor.execute("""
                    SELECT * FROM nfl_team_defense_stats
                    WHERE team_abbr = ? AND season_type = 'REG'
                    ORDER BY season DESC, week
                """, (team_code,))
            
            weekly_stats = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            if not weekly_stats:
                from scrapers.nfl_stats_fetcher import TEAM_ABBR_TO_NAME
                return jsonify({
                    'error': 'No D/ST stats found',
                    'message': f'No stats available for {TEAM_ABBR_TO_NAME.get(team_code, team_code)} defense'
                }), 404
            
            # Group by season
            seasons_data = {}
            for stat in weekly_stats:
                season_year = stat['season']
                if season_year not in seasons_data:
                    seasons_data[season_year] = []
                seasons_data[season_year].append(stat)
            
            # Calculate season totals
            season_totals = {}
            for season_year, season_stats in seasons_data.items():
                totals = {
                    'season': season_year,
                    'games': len(season_stats),
                    'def_sacks': sum(s['def_sacks'] or 0 for s in season_stats),
                    'def_interceptions': sum(s['def_interceptions'] or 0 for s in season_stats),
                    'def_fumbles_recovered': sum(s['def_fumbles_recovered'] or 0 for s in season_stats),
                    'def_fumbles_forced': sum(s['def_fumbles_forced'] or 0 for s in season_stats),
                    'def_touchdowns': sum(s['def_touchdowns'] or 0 for s in season_stats),
                    'special_teams_tds': sum(s['special_teams_tds'] or 0 for s in season_stats),
                    'def_safeties': sum(s['def_safeties'] or 0 for s in season_stats),
                    'points_allowed': sum(s['points_allowed'] or 0 for s in season_stats),
                    'avg_points_allowed': sum(s['points_allowed'] or 0 for s in season_stats) / len(season_stats) if season_stats else 0,
                    'fantasy_points': sum(s['fantasy_points'] or 0 for s in season_stats),
                    'fantasy_points_ppr': sum(s['fantasy_points_ppr'] or 0 for s in season_stats)
                }
                season_totals[season_year] = totals
            
            # Get team info
            from scrapers.nfl_stats_fetcher import TEAM_ABBR_TO_NAME
            player_info = {
                'player_id': f'DST_{team_code}',
                'player_name': TEAM_ABBR_TO_NAME.get(team_code, team_code),
                'player_display_name': f'{TEAM_ABBR_TO_NAME.get(team_code, team_code)} D/ST',
                'position': 'DST',
                'team': team_code
            }
            
            return jsonify({
                'player_info': player_info,
                'weekly_stats': weekly_stats,
                'seasons_data': seasons_data,
                'season_totals': season_totals,
                'total_games': len(weekly_stats),
                'is_dst': True
            })
        
        # Regular player stats
        stats_data = fetcher.get_player_stats(player_name, season)
        
        if 'error' in stats_data:
            return jsonify(stats_data), 404
        
        # Organize stats by season for easier display
        weekly_stats = stats_data.get('weekly_stats', [])
        
        # Group by season
        seasons_data = {}
        for stat in weekly_stats:
            season_year = stat['season']
            if season_year not in seasons_data:
                seasons_data[season_year] = []
            seasons_data[season_year].append(stat)
        
        # Calculate season totals
        season_totals = {}
        for season_year, season_stats in seasons_data.items():
            totals = {
                'season': season_year,
                'games': len(season_stats),
                'passing_yards': sum(s['passing_yards'] or 0 for s in season_stats),
                'passing_tds': sum(s['passing_tds'] or 0 for s in season_stats),
                'interceptions': sum(s['interceptions'] or 0 for s in season_stats),
                'rushing_yards': sum(s['rushing_yards'] or 0 for s in season_stats),
                'rushing_tds': sum(s['rushing_tds'] or 0 for s in season_stats),
                'receptions': sum(s['receptions'] or 0 for s in season_stats),
                'receiving_yards': sum(s['receiving_yards'] or 0 for s in season_stats),
                'receiving_tds': sum(s['receiving_tds'] or 0 for s in season_stats),
                # Kicker stats
                'fg_made': sum(s.get('fg_made') or 0 for s in season_stats),
                'fg_att': sum(s.get('fg_att') or 0 for s in season_stats),
                'fg_pct': sum(s.get('fg_made') or 0 for s in season_stats) / sum(s.get('fg_att') or 0 for s in season_stats) if sum(s.get('fg_att') or 0 for s in season_stats) > 0 else 0,
                'fg_long': max((s.get('fg_long') or 0 for s in season_stats), default=0),
                'pat_made': sum(s.get('pat_made') or 0 for s in season_stats),
                'pat_att': sum(s.get('pat_att') or 0 for s in season_stats),
                'pat_pct': sum(s.get('pat_made') or 0 for s in season_stats) / sum(s.get('pat_att') or 0 for s in season_stats) if sum(s.get('pat_att') or 0 for s in season_stats) > 0 else 0,
                'fantasy_points': sum(s['fantasy_points'] or 0 for s in season_stats),
                'fantasy_points_ppr': sum(s['fantasy_points_ppr'] or 0 for s in season_stats)
            }
            season_totals[season_year] = totals
        
        return jsonify({
            'player_info': stats_data['player_info'],
            'weekly_stats': weekly_stats,
            'seasons_data': seasons_data,
            'season_totals': season_totals,
            'total_games': stats_data['total_games'],
            'is_dst': False
        })
    
    except ImportError:
        return jsonify({
            'error': 'NFL stats module not available',
            'message': 'Please run: pip install nflreadpy polars'
        }), 503
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch player stats',
            'message': str(e)
        }), 500


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
