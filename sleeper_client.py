"""
Sleeper API Client for fetching fantasy football data
Clean REST API - no web scraping needed!
"""
import requests
import json
import time
from typing import Dict, List, Optional


class SleeperAPIClient:
    """Client for interacting with the Sleeper Fantasy Football API"""
    
    BASE_URL = "https://api.sleeper.app/v1"
    
    def __init__(self):
        """Initialize the Sleeper API client"""
        self.session = requests.Session()
        print("✓ Initialized Sleeper API client")
    
    def _get(self, endpoint: str) -> Optional[Dict]:
        """Make a GET request to the Sleeper API"""
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"✗ API request failed: {e}")
            return None
    
    # USER ENDPOINTS
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        return self._get(f"user/{username}")
    
    def get_user_leagues(self, user_id: str, sport: str = "nfl", season: str = "2025") -> List[Dict]:
        """Get all leagues for a user in a given season"""
        result = self._get(f"user/{user_id}/leagues/{sport}/{season}")
        return result if result else []
    
    # LEAGUE ENDPOINTS
    
    def get_league(self, league_id: str) -> Optional[Dict]:
        """Get league details"""
        return self._get(f"league/{league_id}")
    
    def get_rosters(self, league_id: str) -> List[Dict]:
        """Get all rosters in a league"""
        result = self._get(f"league/{league_id}/rosters")
        return result if result else []
    
    def get_users(self, league_id: str) -> List[Dict]:
        """Get all users in a league"""
        result = self._get(f"league/{league_id}/users")
        return result if result else []
    
    def get_matchups(self, league_id: str, week: int) -> List[Dict]:
        """Get matchups for a specific week"""
        result = self._get(f"league/{league_id}/matchups/{week}")
        return result if result else []
    
    def get_winners_bracket(self, league_id: str) -> List[Dict]:
        """Get winners bracket for playoffs"""
        result = self._get(f"league/{league_id}/winners_bracket")
        return result if result else []
    
    def get_losers_bracket(self, league_id: str) -> List[Dict]:
        """Get losers bracket for playoffs"""
        result = self._get(f"league/{league_id}/losers_bracket")
        return result if result else []
    
    def get_transactions(self, league_id: str, round_num: int) -> List[Dict]:
        """Get transactions for a specific round (week)"""
        result = self._get(f"league/{league_id}/transactions/{round_num}")
        return result if result else []
    
    def get_traded_picks(self, league_id: str) -> List[Dict]:
        """Get all traded picks in a league"""
        result = self._get(f"league/{league_id}/traded_picks")
        return result if result else []
    
    # DRAFT ENDPOINTS
    
    def get_drafts_for_league(self, league_id: str) -> List[Dict]:
        """Get all drafts for a league"""
        result = self._get(f"league/{league_id}/drafts")
        return result if result else []
    
    def get_draft(self, draft_id: str) -> Optional[Dict]:
        """Get draft details"""
        return self._get(f"draft/{draft_id}")
    
    def get_draft_picks(self, draft_id: str) -> List[Dict]:
        """Get all picks in a draft"""
        result = self._get(f"draft/{draft_id}/picks")
        return result if result else []
    
    def get_traded_draft_picks(self, draft_id: str) -> List[Dict]:
        """Get traded picks in a draft"""
        result = self._get(f"draft/{draft_id}/traded_picks")
        return result if result else []
    
    # PLAYER ENDPOINTS
    
    def get_all_players(self) -> Dict:
        """Get all NFL players (5MB+ response, use sparingly)"""
        print("Fetching all players (this may take a moment)...")
        return self._get("players/nfl") or {}
    
    def get_trending_players(self, add_or_drop: str = "add", lookback_hours: int = 24, limit: int = 25) -> List[Dict]:
        """Get trending players based on adds/drops"""
        result = self._get(f"players/nfl/trending/{add_or_drop}?lookback_hours={lookback_hours}&limit={limit}")
        return result if result else []
    
    # NFL STATE
    
    def get_nfl_state(self) -> Optional[Dict]:
        """Get current state of the NFL season (current week, season type, etc)"""
        return self._get("state/nfl")


if __name__ == "__main__":
    # Quick test
    client = SleeperAPIClient()
    
    # Test with a known user
    print("\nTesting API...")
    nfl_state = client.get_nfl_state()
    if nfl_state:
        print(f"✓ NFL State: Week {nfl_state.get('week')}, Season {nfl_state.get('season')}")
    else:
        print("✗ Failed to get NFL state")

