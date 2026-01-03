"""
Scrape 2025 Sleeper data for pvels
"""
import sys
sys.path.insert(0, '.')

from sleeper_scraper import SleeperScraper

# Your credentials
USERNAME = "pvels"
LEAGUE_ID = "1257893653083332608"

# Create scraper
scraper = SleeperScraper(username=USERNAME, league_id=LEAGUE_ID)

# Scrape all data
data = scraper.scrape_full_league(season="2025")

if data:
    # Save to JSON
    filepath = scraper.save_to_json(season="2025")
    print(f"\n{'='*80}")
    print("SUCCESS!")
    print(f"{'='*80}")
    print(f"\n✓ All 2025 Sleeper data saved to: {filepath}")
    print("\nData extracted:")
    print(f"  - League info")
    print(f"  - {len(data.get('users', []))} users")
    print(f"  - {len(data.get('rosters', []))} rosters")
    print(f"  - {len(data.get('matchups', {}))} weeks of matchups")
    print(f"  - {sum(len(t) for t in data.get('transactions', {}).values())} total transactions")
    if data.get('drafts'):
        for draft in data['drafts']:
            print(f"  - Draft with {len(draft.get('picks', []))} picks")
else:
    print("\n✗ Failed to scrape data")

