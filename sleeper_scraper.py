"""
Sleeper Fantasy Football Data Scraper for 2025 Season
Fetches all league data via the Sleeper API
"""
import json
import os
import sys
from datetime import datetime
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sleeper_client import SleeperAPIClient
import config


class SleeperScraper:
    """Scraper for fetching complete league data from Sleeper"""
    
    def __init__(self, username: str = None, league_id: str = None):
        """
        Initialize scraper
        
        Args:
            username: Your Sleeper username (optional if you have league_id)
            league_id: Your league ID (optional if you have username)
        """
        self.client = SleeperAPIClient()
        self.username = username
        self.league_id = league_id
        self.data = {}
    
    def scrape_full_league(self, season: str = "2025"):
        """Scrape all data for a league"""
        
        print("="*80)
        print(f"SLEEPER API DATA EXTRACTION - {season} Season")
        print("="*80)
        
        # Step 1: Get user and find league
        if not self.league_id and self.username:
            print(f"\n1. Getting user info for: {self.username}")
            user = self.client.get_user(self.username)
            if not user:
                print("✗ Failed to get user info")
                return
            
            user_id = user.get("user_id")
            print(f"✓ User ID: {user_id}")
            
            print(f"\n2. Fetching leagues for {season}...")
            leagues = self.client.get_user_leagues(user_id, "nfl", season)
            
            if not leagues:
                print(f"✗ No leagues found for {season}")
                return
            
            print(f"✓ Found {len(leagues)} league(s):")
            for i, league in enumerate(leagues, 1):
                print(f"   {i}. {league.get('name')} (ID: {league.get('league_id')})")
            
            # Use first league or let user choose
            if len(leagues) == 1:
                self.league_id = leagues[0].get("league_id")
                print(f"\n✓ Using league: {leagues[0].get('name')}")
            else:
                print("\nMultiple leagues found. Please set league_id in config.py")
                return
        
        if not self.league_id:
            print("✗ No league ID provided")
            return
        
        # Step 2: Get league details
        print(f"\n3. Fetching league details...")
        league = self.client.get_league(self.league_id)
        if league:
            print(f"✓ League: {league.get('name')}")
            print(f"   Season: {league.get('season')}")
            print(f"   Status: {league.get('status')}")
            print(f"   Total Rosters: {league.get('total_rosters')}")
            self.data["league"] = league
        
        # Step 3: Get NFL state (current week)
        print(f"\n4. Fetching NFL state...")
        nfl_state = self.client.get_nfl_state()
        if nfl_state:
            current_week = nfl_state.get("week")
            print(f"✓ Current NFL Week: {current_week}")
            self.data["nfl_state"] = nfl_state
        else:
            current_week = 18  # Default to 18 weeks
        
        # Step 4: Get users
        print(f"\n5. Fetching league users...")
        users = self.client.get_users(self.league_id)
        if users:
            print(f"✓ Found {len(users)} users")
            self.data["users"] = users
        
        # Step 5: Get rosters
        print(f"\n6. Fetching rosters...")
        rosters = self.client.get_rosters(self.league_id)
        if rosters:
            print(f"✓ Found {len(rosters)} rosters")
            self.data["rosters"] = rosters
        
        # Step 6: Get all matchups (week by week)
        print(f"\n7. Fetching matchups for all weeks...")
        all_matchups = {}
        for week in range(1, current_week + 1):
            matchups = self.client.get_matchups(self.league_id, week)
            if matchups:
                all_matchups[str(week)] = matchups
                print(f"   Week {week}: {len(matchups)} matchups")
            time.sleep(0.5)  # Rate limiting
        self.data["matchups"] = all_matchups
        
        # Step 7: Get transactions
        print(f"\n8. Fetching transactions...")
        all_transactions = {}
        for week in range(1, current_week + 1):
            transactions = self.client.get_transactions(self.league_id, week)
            if transactions:
                all_transactions[str(week)] = transactions
                print(f"   Week {week}: {len(transactions)} transactions")
            time.sleep(0.5)  # Rate limiting
        self.data["transactions"] = all_transactions
        
        # Step 8: Get traded picks
        print(f"\n9. Fetching traded picks...")
        traded_picks = self.client.get_traded_picks(self.league_id)
        if traded_picks:
            print(f"✓ Found {len(traded_picks)} traded picks")
            self.data["traded_picks"] = traded_picks
        
        # Step 9: Get drafts
        print(f"\n10. Fetching drafts...")
        drafts = self.client.get_drafts_for_league(self.league_id)
        if drafts:
            print(f"✓ Found {len(drafts)} draft(s)")
            
            # Get picks for each draft
            for draft in drafts:
                draft_id = draft.get("draft_id")
                print(f"   Fetching picks for draft {draft_id}...")
                picks = self.client.get_draft_picks(draft_id)
                draft["picks"] = picks
                print(f"   ✓ Got {len(picks)} picks")
                time.sleep(0.5)
            
            self.data["drafts"] = drafts
        
        # Step 10: Get playoff brackets (if in playoffs)
        if league and league.get("status") in ["in_season", "complete"]:
            print(f"\n11. Fetching playoff brackets...")
            winners_bracket = self.client.get_winners_bracket(self.league_id)
            losers_bracket = self.client.get_losers_bracket(self.league_id)
            
            if winners_bracket:
                print(f"✓ Winners bracket: {len(winners_bracket)} matchups")
                self.data["winners_bracket"] = winners_bracket
            
            if losers_bracket:
                print(f"✓ Losers bracket: {len(losers_bracket)} matchups")
                self.data["losers_bracket"] = losers_bracket
        
        # Step 11: Get all players (optional - large file)
        print(f"\n12. Fetching player data...")
        print("   (Skipping full player list - 5MB+. Enable if needed)")
        # players = self.client.get_all_players()
        # self.data["players"] = players
        
        print("\n" + "="*80)
        print("DATA EXTRACTION COMPLETE")
        print("="*80)
        
        return self.data
    
    def save_to_json(self, season: str = "2025"):
        """Save scraped data to JSON file"""
        
        if not self.data:
            print("✗ No data to save")
            return
        
        # Ensure data directory exists
        os.makedirs(config.DATA_DIR, exist_ok=True)
        
        # Create filename
        league_name = self.data.get("league", {}).get("name", "unknown").replace(" ", "_")
        filename = f"sleeper_{self.league_id}_{season}.json"
        filepath = os.path.join(config.DATA_DIR, filename)
        
        # Add metadata
        self.data["scraped_at"] = datetime.now().isoformat()
        self.data["season"] = season
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(self.data, f, indent=2)
        
        print(f"\n✓ Saved to: {filepath}")
        print(f"   File size: {os.path.getsize(filepath) / 1024:.1f} KB")
        
        return filepath


if __name__ == "__main__":
    print("\n" + "="*80)
    print("SLEEPER FANTASY FOOTBALL DATA SCRAPER")
    print("="*80)
    
    # Get username from user
    print("\nEnter your Sleeper username (or press Enter to use league ID directly):")
    username = input("> ").strip()
    
    league_id = None
    if not username:
        print("\nEnter your league ID:")
        league_id = input("> ").strip()
    
    if not username and not league_id:
        print("✗ Must provide either username or league ID")
        exit(1)
    
    # Create scraper and fetch data
    scraper = SleeperScraper(username=username or None, league_id=league_id or None)
    
    # Scrape data
    data = scraper.scrape_full_league(season="2025")
    
    if data:
        # Save to JSON
        scraper.save_to_json(season="2025")
        
        print("\n✓ SUCCESS! All 2025 Sleeper data has been extracted.")
    else:
        print("\n✗ Failed to extract data")

