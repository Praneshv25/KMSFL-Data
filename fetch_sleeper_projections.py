"""
Fetch player projections from Sleeper API and merge into existing 2025 data
"""
import json
import os
import sys
import time
import requests
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

def fetch_weekly_projections(season, week, season_type='regular'):
    """
    Fetch projections for a specific week
    URL: https://api.sleeper.com/projections/nfl/{season}/{week}?season_type={season_type}
    """
    url = f"https://api.sleeper.com/projections/nfl/{season}/{week}"
    params = {'season_type': season_type}
    
    print(f"Fetching projections for {season} Week {week}...")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        print(f"  ✓ Fetched {len(data)} player projections")
        return data
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error fetching projections: {e}")
        return []


def fetch_all_projections(season, weeks, season_type='regular'):
    """
    Fetch projections for all weeks in a season
    Returns: dict of {week: {player_id: projection_data}}
    """
    all_projections = {}
    
    for week in weeks:
        projections = fetch_weekly_projections(season, week, season_type)
        
        # Convert list to dict keyed by player_id
        week_projections = {}
        for proj in projections:
            player_id = proj.get('player_id')
            if player_id:
                # Extract the projected points (using Half PPR scoring)
                stats = proj.get('stats', {})
                week_projections[player_id] = {
                    'pts_half_ppr': stats.get('pts_half_ppr', 0),
                    'pts_ppr': stats.get('pts_ppr', 0),
                    'pts_std': stats.get('pts_std', 0),
                    'stats': stats
                }
        
        all_projections[str(week)] = week_projections
        time.sleep(0.5)  # Rate limiting
    
    return all_projections


def merge_projections_into_matchups(data_file, projections):
    """
    Merge projection data into the existing Sleeper matchup data
    """
    print(f"\nLoading {data_file}...")
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    matchups = data.get('matchups', {})
    updated_count = 0
    
    for week, week_matchups in matchups.items():
        week_projections = projections.get(week, {})
        
        if not week_projections:
            print(f"  No projections for week {week}")
            continue
        
        print(f"\n  Processing Week {week}...")
        week_updated = 0
        
        for matchup in week_matchups:
            # Update projections for all players in matchup
            if 'players_with_names' in matchup:
                for player in matchup['players_with_names']:
                    player_id = player.get('player_id')
                    if player_id and player_id in week_projections:
                        # Use pts_half_ppr for projections (Half PPR scoring)
                        player['projected'] = week_projections[player_id]['pts_half_ppr']
                        week_updated += 1
        
        updated_count += week_updated
        print(f"    ✓ Updated {week_updated} player projections")
    
    # Save updated data
    print(f"\n✓ Total projections merged: {updated_count}")
    print(f"Saving to {data_file}...")
    
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Done! Updated {data_file}")


def main():
    # Configuration
    season = 2025
    league_id = '1257893653083332608'
    data_file = os.path.join(config.DATA_DIR, f'sleeper_{league_id}_{season}.json')
    
    # Determine how many weeks we have in the data
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    matchup_weeks = sorted([int(w) for w in data.get('matchups', {}).keys()])
    print(f"Found matchup data for weeks: {matchup_weeks}")
    
    if not matchup_weeks:
        print("No matchups found in data!")
        return
    
    # Fetch projections for all weeks
    print(f"\nFetching projections for {season} season...")
    print("="*80)
    
    projections = fetch_all_projections(season, matchup_weeks, season_type='regular')
    
    # Merge projections into matchup data
    print("\n" + "="*80)
    print("MERGING PROJECTIONS INTO MATCHUP DATA")
    print("="*80)
    
    merge_projections_into_matchups(data_file, projections)
    
    print("\n" + "="*80)
    print("✓ ALL DONE!")
    print("="*80)
    print("\nProjections have been added to your matchup data.")
    print("Restart the Flask app to see the updated projections.")


if __name__ == "__main__":
    main()

