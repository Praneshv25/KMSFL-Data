"""
Extract a single week's data for a specific season
Useful for filling in missing weeks
"""
import json
import sys
from historical_scraper import HistoricalESPNScraper
import config


def extract_single_week(season, week):
    """
    Extract data for a single week and merge it with existing season data
    
    Args:
        season: Season year (e.g., 2023)
        week: Week number (e.g., 6)
    """
    print(f"\n{'='*60}")
    print(f"EXTRACTING WEEK {week} OF {season} SEASON")
    print(f"{'='*60}\n")
    
    scraper = HistoricalESPNScraper()
    
    try:
        # Start browser and authenticate
        scraper.start()
        
        if not scraper.authenticate():
            print("✗ Authentication failed")
            return
        
        # Extract just this week
        matchup_data = scraper.extract_matchup_with_boxscore(week, season)
        
        print(f"\n✓ Extracted {len(matchup_data)} matchups for Week {week}")
        
        # Load existing season data
        season_file = f"data/espn_league_{config.LEAGUE_ID}_{season}_historical.json"
        
        try:
            with open(season_file, 'r') as f:
                season_data = json.load(f)
            print(f"✓ Loaded existing {season} season data")
        except FileNotFoundError:
            print(f"⚠ No existing file found, creating new season data")
            season_data = {
                'league_id': config.LEAGUE_ID,
                'season_year': season,
                'matchups': {}
            }
        
        # Update the specific week
        season_data['matchups'][week] = matchup_data
        
        # Save back to file
        with open(season_file, 'w') as f:
            json.dump(season_data, f, indent=2)
        
        print(f"\n✓ Updated Week {week} in {season_file}")
        print(f"\nWeek {week} now has {len(matchup_data)} matchups:")
        for m in matchup_data:
            home_roster_size = len(m.get('home_roster', []))
            away_roster_size = len(m.get('away_roster', []))
            print(f"  • {m.get('home_team')} ({home_roster_size}) vs {m.get('away_team')} ({away_roster_size})")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.close()


if __name__ == "__main__":
    # Default to Week 6, 2023
    season = int(sys.argv[1]) if len(sys.argv) > 1 else 2023
    week = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    
    print(f"\nExtracting Week {week} of {season} season")
    print("Usage: python extract_single_week.py [season] [week]")
    print(f"Example: python extract_single_week.py 2023 6\n")
    
    extract_single_week(season, week)

