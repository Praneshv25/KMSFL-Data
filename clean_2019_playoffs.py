"""
Extract 2019 playoff data directly from the screenshots provided in chat
"""
import json
import os
import sys

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

def extract_from_chat_screenshots():
    """
    REMOVED - not needed for cleanup
    """
    pass


def save_playoff_data_simple(season=2019):
    """
    Save extracted playoff data to the season JSON file.
    Since we can see the basic matchup info but need detailed rosters,
    let's mark these matchups as placeholders that need AI extraction.
    """
    
    json_file = os.path.join(config.DATA_DIR, f"espn_league_{config.LEAGUE_ID}_{season}_historical.json")
    
    # Load existing data
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)
    else:
        data = {
            "season": season,
            "league_id": config.LEAGUE_ID,
            "matchups": []
        }
    
    # Remove existing playoff weeks (14-17 for 2019)
    print(f"\nRemoving existing playoff data (weeks 14-17)...")
    matchups = data.get("matchups", {})
    
    # The matchups are organized as a dict with week numbers as keys
    removed_weeks = []
    for week in ['14', '15', '16', '17']:
        if week in matchups:
            del matchups[week]
            removed_weeks.append(week)
    
    print(f"Removed weeks: {', '.join(removed_weeks) if removed_weeks else 'None found'}")
    print(f"\n✓ Cleaned playoff data from {json_file}")
    print(f"Remaining weeks with data: {sorted(matchups.keys())}")
    
    # Save back
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return data


if __name__ == "__main__":
    print("="*80)
    print("CLEANING 2019 PLAYOFF DATA")
    print("="*80)
    print("\nThis will remove weeks 14-17 from the 2019 data file.")
    print("You can then manually add the correct data or re-scrape.")
    print("\nProceed? (y/n): ", end="")
    
    response = input().strip().lower()
    if response == 'y':
        save_playoff_data_simple(season=2019)
        print("\n✓ Done! Playoff weeks 14-17 have been removed from 2019 data.")
    else:
        print("Cancelled.")

