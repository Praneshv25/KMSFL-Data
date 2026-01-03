"""
Enhance Sleeper data with player names
Downloads player mapping from Sleeper API and enriches matchup/draft data
"""
import json
import os
import sys
sys.path.insert(0, '.')

from sleeper_client import SleeperAPIClient
import config


def load_or_fetch_players():
    """Load players from cache or fetch from API"""
    cache_file = os.path.join(config.DATA_DIR, "sleeper_players.json")
    
    # Check if we have a recent cache (less than 1 day old)
    if os.path.exists(cache_file):
        age_hours = (os.path.getmtime(cache_file) - os.path.getctime(cache_file)) / 3600
        if age_hours < 24:
            print("✓ Using cached player data")
            with open(cache_file, 'r') as f:
                return json.load(f)
    
    # Fetch from API
    print("Fetching player data from Sleeper API (5MB+, this may take a moment)...")
    client = SleeperAPIClient()
    players = client.get_all_players()
    
    if players:
        # Save to cache
        with open(cache_file, 'w') as f:
            json.dump(players, f)
        print(f"✓ Cached {len(players)} players")
    
    return players


def get_player_name(player_id, players):
    """Get player name from ID"""
    if not player_id:
        return "Unknown"
    
    # Handle defense teams (like 'DEN', 'KC', etc)
    if isinstance(player_id, str) and len(player_id) <= 3 and player_id.isupper():
        return f"{player_id} D/ST"
    
    player = players.get(str(player_id), {})
    if not player:
        return f"Player {player_id}"
    
    first = player.get('first_name', '')
    last = player.get('last_name', '')
    pos = player.get('position', '')
    team = player.get('team', '')
    
    name = f"{first} {last}".strip()
    if not name:
        name = f"Player {player_id}"
    
    if pos and team:
        return f"{name} ({team} {pos})"
    elif pos:
        return f"{name} ({pos})"
    return name


def enhance_sleeper_data(league_id, season="2025"):
    """Enhance Sleeper data file with player names"""
    
    print("="*80)
    print("ENHANCING SLEEPER DATA WITH PLAYER NAMES")
    print("="*80)
    
    # Load Sleeper data
    sleeper_file = os.path.join(config.DATA_DIR, f"sleeper_{league_id}_{season}.json")
    if not os.path.exists(sleeper_file):
        print(f"✗ Sleeper data file not found: {sleeper_file}")
        return
    
    print(f"\n1. Loading Sleeper data...")
    with open(sleeper_file, 'r') as f:
        data = json.load(f)
    
    # Load player mapping
    print(f"\n2. Loading player mapping...")
    players = load_or_fetch_players()
    
    if not players:
        print("✗ Failed to load players")
        return
    
    # Enhance matchups
    print(f"\n3. Enhancing matchups...")
    matchups = data.get('matchups', {})
    enhanced_count = 0
    
    for week, week_matchups in matchups.items():
        for matchup in week_matchups:
            # Add player names to starters
            if 'starters' in matchup:
                matchup['starters_with_names'] = [
                    {
                        'player_id': pid,
                        'player_name': get_player_name(pid, players),
                        'points': matchup.get('players_points', {}).get(pid, 0)
                    }
                    for pid in matchup['starters']
                ]
            
            # Add player names to all players (including bench)
            if 'players' in matchup:
                matchup['players_with_names'] = [
                    {
                        'player_id': pid,
                        'player_name': get_player_name(pid, players),
                        'points': matchup.get('players_points', {}).get(pid, 0),
                        'is_starter': pid in matchup.get('starters', [])
                    }
                    for pid in matchup['players']
                ]
            
            enhanced_count += 1
    
    print(f"   ✓ Enhanced {enhanced_count} matchups")
    
    # Enhance draft picks
    print(f"\n4. Enhancing draft picks...")
    drafts = data.get('drafts', [])
    pick_count = 0
    
    for draft in drafts:
        for pick in draft.get('picks', []):
            player_id = pick.get('player_id')
            if player_id:
                pick['player_name'] = get_player_name(player_id, players)
                pick['player_info'] = players.get(str(player_id), {})
                pick_count += 1
    
    print(f"   ✓ Enhanced {pick_count} draft picks")
    
    # Save enhanced data
    print(f"\n5. Saving enhanced data...")
    enhanced_file = sleeper_file.replace('.json', '_enhanced.json')
    with open(enhanced_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"   ✓ Saved to: {enhanced_file}")
    
    # Also update original file
    with open(sleeper_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"   ✓ Updated: {sleeper_file}")
    
    print("\n" + "="*80)
    print("ENHANCEMENT COMPLETE")
    print("="*80)
    print("\n✓ Sleeper data now includes player names!")
    print("  Restart the Flask app to see the changes.")


if __name__ == "__main__":
    # Your league info
    LEAGUE_ID = "1257893653083332608"
    SEASON = "2025"
    
    enhance_sleeper_data(LEAGUE_ID, SEASON)

