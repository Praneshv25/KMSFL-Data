"""
Populate NFL Stats Database
Fetches NFL weekly stats and populates the database
"""
import sys
import os
import sqlite3
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from scrapers.nfl_stats_fetcher import NFLStatsFetcher


def get_fantasy_player_names():
    """
    Extract all unique player names from existing fantasy data
    
    Returns:
        Set of player names
    """
    player_names = set()
    
    # Get from database if it exists
    if os.path.exists(config.DB_FILE):
        try:
            conn = sqlite3.connect(config.DB_FILE)
            cursor = conn.cursor()
            
            # Get from matchup rosters
            cursor.execute("SELECT DISTINCT player_name FROM matchup_rosters")
            for row in cursor.fetchall():
                if row[0]:
                    player_names.add(row[0])
            
            # Get from draft picks
            cursor.execute("SELECT DISTINCT player_name FROM draft_picks")
            for row in cursor.fetchall():
                if row[0]:
                    player_names.add(row[0])
            
            conn.close()
            print(f"✓ Found {len(player_names)} unique players in database")
        except Exception as e:
            print(f"⚠ Could not read from database: {e}")
    
    # Also get from JSON files
    json_files = [
        f for f in os.listdir(config.DATA_DIR)
        if f.endswith('.json') and ('espn_league' in f or 'sleeper' in f)
    ]
    
    for json_file in json_files:
        try:
            filepath = os.path.join(config.DATA_DIR, json_file)
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Extract from matchups
            matchups = data.get('matchups', {})
            for week, week_matchups in matchups.items():
                for matchup in week_matchups:
                    for player in matchup.get('home_roster', []):
                        if player.get('player_name'):
                            player_names.add(player['player_name'])
                    for player in matchup.get('away_roster', []):
                        if player.get('player_name'):
                            player_names.add(player['player_name'])
            
            # Extract from draft
            draft = data.get('draft', {})
            for pick in draft.get('picks', []):
                if pick.get('player_name'):
                    player_names.add(pick['player_name'])
        
        except Exception as e:
            print(f"⚠ Error reading {json_file}: {e}")
    
    print(f"✓ Total unique players found: {len(player_names)}")
    return list(player_names)


def check_existing_data(db_path):
    """
    Check what NFL data already exists in the database
    
    Args:
        db_path: Path to database
        
    Returns:
        Dict with existing data info
    """
    if not os.path.exists(db_path):
        return {'seasons': [], 'total_records': 0}
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='nfl_weekly_stats'
    """)
    
    if not cursor.fetchone():
        conn.close()
        return {'seasons': [], 'total_records': 0}
    
    # Get existing seasons
    cursor.execute("SELECT DISTINCT season FROM nfl_weekly_stats ORDER BY season")
    seasons = [row[0] for row in cursor.fetchall()]
    
    # Get total records
    cursor.execute("SELECT COUNT(*) FROM nfl_weekly_stats")
    total_records = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'seasons': seasons,
        'total_records': total_records
    }


def main():
    """
    Main function to populate NFL stats
    """
    print("\n" + "="*60)
    print("NFL STATS DATABASE POPULATION")
    print("="*60 + "\n")
    
    # Check existing data
    print("📊 Checking existing data...")
    existing = check_existing_data(config.DB_FILE)
    
    if existing['total_records'] > 0:
        print(f"✓ Found existing data: {existing['total_records']} records")
        print(f"  Seasons: {existing['seasons']}")
        
        response = input("\n⚠  NFL stats already exist. Re-fetch and update? (y/n): ")
        if response.lower() != 'y':
            print("Skipping NFL stats fetch.")
            
            # Just update player mappings
            print("\n📝 Updating player mappings...")
            fetcher = NFLStatsFetcher()
            
            # Get fantasy player names
            player_names = get_fantasy_player_names()
            
            if player_names:
                # Get all weekly stats for mapping
                conn = sqlite3.connect(config.DB_FILE)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT player_id, player_display_name, position, recent_team
                    FROM nfl_weekly_stats
                """)
                
                # Create a simple DataFrame-like structure for matching
                class SimpleDF:
                    def __init__(self, data):
                        self.data = data
                    
                    def __getitem__(self, mask):
                        return SimpleDF([d for d, m in zip(self.data, mask) if m])
                    
                    @property
                    def empty(self):
                        return len(self.data) == 0
                    
                    def iloc(self, idx):
                        return self.data[idx]
                
                weekly_data = [dict(zip(['player_id', 'player_display_name', 'position', 'recent_team'], row)) 
                              for row in cursor.fetchall()]
                conn.close()
                
                # Map using a simpler approach
                conn = sqlite3.connect(config.DB_FILE)
                cursor = conn.cursor()
                mapping_count = 0
                
                for fantasy_name in player_names:
                    # Try to find exact match
                    matches = [p for p in weekly_data 
                              if p['player_display_name'].lower() == fantasy_name.lower()]
                    
                    if matches:
                        match = matches[0]
                        try:
                            cursor.execute("""
                                INSERT OR REPLACE INTO nfl_player_mapping (
                                    fantasy_player_name, nfl_player_id, nfl_player_name,
                                    nfl_player_display_name, position, team,
                                    confidence_score, created_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                fantasy_name,
                                match['player_id'],
                                match['player_display_name'],
                                match['player_display_name'],
                                match['position'],
                                match['recent_team'],
                                1.0,
                                datetime.now().isoformat()
                            ))
                            mapping_count += 1
                        except Exception as e:
                            print(f"⚠ Error mapping {fantasy_name}: {e}")
                
                conn.commit()
                conn.close()
                print(f"✓ Created {mapping_count} player mappings")
            
            return
    
    # Initialize fetcher
    print("\n🏈 Initializing NFL Stats Fetcher...")
    try:
        fetcher = NFLStatsFetcher()
    except ImportError as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease install nflreadpy and polars:")
        print("  pip install nflreadpy polars")
        return
    
    # Determine seasons to fetch
    # Get seasons from existing fantasy data
    seasons_to_fetch = set()
    
    # Check database for fantasy seasons
    if os.path.exists(config.DB_FILE):
        conn = sqlite3.connect(config.DB_FILE)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT DISTINCT season_year FROM teams")
            for row in cursor.fetchall():
                if row[0]:
                    seasons_to_fetch.add(row[0])
        except:
            pass
        
        conn.close()
    
    # Also check JSON files
    json_files = [
        f for f in os.listdir(config.DATA_DIR)
        if f.endswith('.json') and 'espn_league' in f
    ]
    
    for json_file in json_files:
        # Extract year from filename (e.g., espn_league_31288798_2019_historical.json)
        parts = json_file.replace('.json', '').split('_')
        for part in parts:
            if part.isdigit() and len(part) == 4 and 2019 <= int(part) <= 2025:
                seasons_to_fetch.add(int(part))
    
    if not seasons_to_fetch:
        # Default to last few seasons if no data found
        current_year = datetime.now().year
        # Don't include current year if we're early in the year (data might not be available)
        current_month = datetime.now().month
        end_year = current_year if current_month >= 4 else current_year - 1
        seasons_to_fetch = set(range(2019, end_year + 1))
    
    seasons_to_fetch = sorted(list(seasons_to_fetch))
    
    print(f"\n📅 Seasons to fetch: {seasons_to_fetch}")
    
    # Fetch weekly stats with error handling for unavailable years
    print(f"\n📊 Fetching NFL player stats...")
    
    # Try to fetch all seasons, but handle individual failures
    successful_seasons = []
    failed_seasons = []
    weekly_stats = None
    
    for season in seasons_to_fetch:
        try:
            print(f"   Attempting to fetch {season}...")
            season_stats = fetcher.fetch_weekly_stats([season])
            if season_stats is not None and len(season_stats) > 0:
                if weekly_stats is None:
                    weekly_stats = season_stats
                else:
                    # Polars DataFrames use vstack for vertical concatenation
                    import polars as pl
                    weekly_stats = pl.concat([weekly_stats, season_stats], how="vertical")
                successful_seasons.append(season)
        except Exception as e:
            print(f"   ⚠ Could not fetch {season}: {e}")
            failed_seasons.append(season)
    
    if failed_seasons:
        print(f"\n⚠ Failed to fetch data for seasons: {failed_seasons}")
        print(f"   (This is normal if data isn't available yet)")
    
    if not successful_seasons:
        print("\n✗ No data could be fetched for any season")
        return
    
    print(f"\n✓ Successfully fetched data for seasons: {successful_seasons}")
    
    if weekly_stats is None or len(weekly_stats) == 0:
        print("✗ Failed to fetch NFL stats")
        return
    
    # Store in database
    print(f"\n💾 Storing stats in database...")
    stored_count = fetcher.store_weekly_stats(weekly_stats)
    
    if stored_count == 0:
        print("✗ Failed to store stats")
        return
    
    # Get fantasy player names
    print(f"\n📝 Creating player name mappings...")
    player_names = get_fantasy_player_names()
    
    if player_names:
        mapping_count = fetcher.create_player_mappings(player_names, weekly_stats)
        print(f"✓ Created {mapping_count} mappings")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"✓ NFL Stats Records: {stored_count}")
    print(f"✓ Player Mappings: {mapping_count if player_names else 0}")
    print(f"✓ Seasons: {seasons_to_fetch}")
    print(f"✓ Database: {config.DB_FILE}")
    print("\n✓ NFL stats population complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

