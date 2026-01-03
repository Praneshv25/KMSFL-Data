"""
Populate SQLite database with all fantasy league data (ESPN 2019-2024 + Sleeper 2025)
"""
import json
import os
import glob
import sqlite3
from datetime import datetime
import config

def init_enhanced_database(db_path):
    """Create enhanced database schema with roster storage"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enhanced matchups table with additional fields
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matchups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            league_id TEXT,
            season_year INTEGER,
            week INTEGER,
            matchup_id TEXT,
            home_team TEXT,
            home_score REAL,
            home_projected REAL,
            away_team TEXT,
            away_score REAL,
            away_projected REAL,
            bracket_type TEXT,
            round TEXT,
            is_two_week_playoff BOOLEAN,
            home_total_score REAL,
            away_total_score REAL,
            data_source TEXT,
            scraped_at TIMESTAMP,
            UNIQUE(league_id, season_year, week, matchup_id, home_team, away_team)
        )
    """)
    
    # Matchup rosters table (stores all players in each matchup)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matchup_rosters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            league_id TEXT,
            season_year INTEGER,
            week INTEGER,
            matchup_id TEXT,
            team_name TEXT,
            player_name TEXT,
            position TEXT,
            nfl_team TEXT,
            points REAL,
            projected REAL,
            started BOOLEAN,
            UNIQUE(league_id, season_year, week, matchup_id, team_name, player_name)
        )
    """)
    
    # Teams/Standings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            league_id TEXT,
            season_year INTEGER,
            team_name TEXT,
            owner TEXT,
            rank INTEGER,
            wins INTEGER,
            losses INTEGER,
            ties INTEGER,
            points_for REAL,
            points_against REAL,
            data_source TEXT,
            UNIQUE(league_id, season_year, team_name)
        )
    """)
    
    # Draft picks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS draft_picks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            league_id TEXT,
            season_year INTEGER,
            round INTEGER,
            pick INTEGER,
            overall_pick INTEGER,
            team TEXT,
            player_name TEXT,
            position TEXT,
            nfl_team TEXT,
            data_source TEXT,
            UNIQUE(league_id, season_year, overall_pick)
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✓ Enhanced database initialized: {db_path}")


def populate_from_json(json_file, data_source, db_path):
    """Populate database from a single JSON file"""
    print(f"\nProcessing: {os.path.basename(json_file)} ({data_source})")
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Normalize data (using app's normalize_data function for both ESPN and Sleeper)
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from app import normalize_data
    data = normalize_data(data, data_source)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Extract metadata
    if data_source == 'espn':
        league_id = str(data.get('league_id', config.LEAGUE_ID))
        season_year = data.get('season', 0) or data.get('season_year', 0)
    else:  # sleeper
        league_id = data.get('league', {}).get('league_id', '')
        season_year = data.get('season', 2025)
    
    scraped_at = data.get('scraped_at', datetime.now().isoformat())
    
    # Insert standings
    standings = data.get('standings', [])
    for team in standings:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO teams 
                (league_id, season_year, team_name, owner, rank, wins, losses, ties, 
                 points_for, points_against, data_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                league_id, season_year,
                team.get('team_name'),
                team.get('owner'),
                team.get('rank'),
                team.get('wins'),
                team.get('losses'),
                team.get('ties', 0),
                team.get('points_for'),
                team.get('points_against'),
                data_source
            ))
        except Exception as e:
            print(f"  Error inserting team: {e}")
    
    print(f"  ✓ Inserted {len(standings)} teams")
    
    # Insert matchups and rosters
    matchups = data.get('matchups', {})
    matchup_count = 0
    roster_count = 0
    
    for week, week_matchups in matchups.items():
        for matchup in week_matchups:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO matchups
                    (league_id, season_year, week, matchup_id, home_team, home_score, 
                     home_projected, away_team, away_score, away_projected, bracket_type,
                     round, is_two_week_playoff, home_total_score, away_total_score,
                     data_source, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    league_id, season_year, int(week),
                    str(matchup.get('matchup_id', '')),
                    matchup.get('home_team'),
                    matchup.get('home_score'),
                    matchup.get('home_projected'),
                    matchup.get('away_team'),
                    matchup.get('away_score'),
                    matchup.get('away_projected'),
                    matchup.get('bracket_type'),
                    matchup.get('round'),
                    matchup.get('is_two_week_playoff'),
                    matchup.get('home_total_score'),
                    matchup.get('away_total_score'),
                    data_source,
                    scraped_at
                ))
                matchup_count += 1
                
                # Insert home roster
                for player in matchup.get('home_roster', []):
                    try:
                        cursor.execute("""
                            INSERT OR REPLACE INTO matchup_rosters
                            (league_id, season_year, week, matchup_id, team_name,
                             player_name, position, nfl_team, points, projected, started)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            league_id, season_year, int(week),
                            str(matchup.get('matchup_id', '')),
                            matchup.get('home_team'),
                            player.get('player_name'),
                            player.get('position'),
                            player.get('nfl_team'),
                            player.get('points'),
                            player.get('projected'),
                            player.get('started')
                        ))
                        roster_count += 1
                    except Exception as e:
                        print(f"  Error inserting home player: {e}")
                
                # Insert away roster
                for player in matchup.get('away_roster', []):
                    try:
                        cursor.execute("""
                            INSERT OR REPLACE INTO matchup_rosters
                            (league_id, season_year, week, matchup_id, team_name,
                             player_name, position, nfl_team, points, projected, started)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            league_id, season_year, int(week),
                            str(matchup.get('matchup_id', '')),
                            matchup.get('away_team'),
                            player.get('player_name'),
                            player.get('position'),
                            player.get('nfl_team'),
                            player.get('points'),
                            player.get('projected'),
                            player.get('started')
                        ))
                        roster_count += 1
                    except Exception as e:
                        print(f"  Error inserting away player: {e}")
                        
            except Exception as e:
                print(f"  Error inserting matchup: {e}")
    
    print(f"  ✓ Inserted {matchup_count} matchups with {roster_count} player entries")
    
    # Insert draft picks
    draft = data.get('draft', {})
    picks = draft.get('picks', [])
    pick_count = 0
    
    for pick in picks:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO draft_picks
                (league_id, season_year, round, pick, overall_pick, team,
                 player_name, position, nfl_team, data_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                league_id, season_year,
                pick.get('round'),
                pick.get('pick'),
                pick.get('overall_pick'),
                pick.get('team'),
                pick.get('player_name'),
                pick.get('position'),
                pick.get('nfl_team'),
                data_source
            ))
            pick_count += 1
        except Exception as e:
            print(f"  Error inserting pick: {e}")
    
    print(f"  ✓ Inserted {pick_count} draft picks")
    
    conn.commit()
    conn.close()


def main():
    db_path = config.DB_FILE
    
    print("="*80)
    print("POPULATING DATABASE WITH ALL FANTASY DATA")
    print("="*80)
    
    # Initialize enhanced database
    init_enhanced_database(db_path)
    
    # Process ESPN files (2019-2024)
    espn_files = sorted(glob.glob(os.path.join(config.DATA_DIR, "espn_league_*_historical.json")))
    print(f"\nFound {len(espn_files)} ESPN data files")
    
    for espn_file in espn_files:
        populate_from_json(espn_file, 'espn', db_path)
    
    # Process Sleeper files (2025)
    sleeper_files = sorted(glob.glob(os.path.join(config.DATA_DIR, "sleeper_*.json")))
    # Filter out sleeper_players.json
    sleeper_files = [f for f in sleeper_files if 'players.json' not in f]
    print(f"\nFound {len(sleeper_files)} Sleeper data files")
    
    for sleeper_file in sleeper_files:
        populate_from_json(sleeper_file, 'sleeper', db_path)
    
    print("\n" + "="*80)
    print("✓ DATABASE POPULATION COMPLETE")
    print("="*80)
    print(f"\nDatabase location: {db_path}")
    
    # Show summary
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM teams")
    team_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM matchups")
    matchup_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM matchup_rosters")
    roster_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM draft_picks")
    draft_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT DISTINCT season_year FROM matchups ORDER BY season_year")
    seasons = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    print(f"\nDatabase Summary:")
    print(f"  Seasons: {', '.join(map(str, seasons))}")
    print(f"  Teams: {team_count}")
    print(f"  Matchups: {matchup_count}")
    print(f"  Player Entries: {roster_count}")
    print(f"  Draft Picks: {draft_count}")


if __name__ == "__main__":
    main()

