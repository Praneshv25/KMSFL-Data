"""
Data Extraction Methods for ESPN Fantasy Football
Specific extraction logic for each data type
"""
from typing import Dict, Any, List, Optional
import time


class DataExtractor:
    """
    Extraction methods for different ESPN Fantasy data types
    """
    
    def __init__(self, scraper):
        """
        Initialize extractor with scraper instance
        
        Args:
            scraper: ESPNFantasyScraper instance
        """
        self.scraper = scraper
    
    def extract_standings(self) -> List[Dict[str, Any]]:
        """
        Extract team standings/records
        
        Returns:
            List of team standings
        """
        print("\n" + "="*60)
        print("EXTRACTING STANDINGS")
        print("="*60)
        
        # Navigate directly to standings page
        url = f"https://fantasy.espn.com/football/league/standings?leagueId={self.scraper.scraped_data['league_id']}&seasonId={self.scraper.scraped_data['season_year']}"
        print(f"  Navigating to: {url}")
        self.scraper.page.goto(url, wait_until="networkidle")
        time.sleep(3)
        
        # Take screenshot for debugging
        self.scraper.take_screenshot("standings")
        
        # Define schema for extraction
        schema = """
{
    "teams": [
        {
            "rank": 1,
            "team_name": "Team Name",
            "owner": "Owner Name",
            "wins": 10,
            "losses": 3,
            "ties": 0,
            "points_for": 1234.56,
            "points_against": 1100.23,
            "streak": "W3"
        }
    ]
}
"""
        
        # Extract data
        data = self.scraper.extract_with_vision(
            "Extract all team standings including rank, team name, owner, record (wins/losses/ties), points for, points against, and current streak",
            schema
        )
        
        teams = data.get('teams', [])
        
        # Verify data
        if teams:
            print(f"\n✓ Extracted {len(teams)} teams:")
            for team in teams[:3]:  # Show first 3
                print(f"  {team.get('rank')}. {team.get('team_name')} ({team.get('wins')}-{team.get('losses')})")
            if len(teams) > 3:
                print(f"  ... and {len(teams) - 3} more")
        
        return teams
    
    def extract_matchups(self, week: Optional[int] = None) -> Dict[str, Any]:
        """
        Extract matchup data for a specific week
        
        Args:
            week: Week number (None for current week)
            
        Returns:
            Dict with week and matchups
        """
        print("\n" + "="*60)
        week_str = f"WEEK {week}" if week else "CURRENT WEEK"
        print(f"EXTRACTING MATCHUPS - {week_str}")
        print("="*60)
        
        # Direct URL navigation to scoreboard (more reliable than AI clicking)
        base_url = f"https://fantasy.espn.com/football/league/scoreboard"
        params = f"?leagueId={self.scraper.scraped_data['league_id']}&seasonId={self.scraper.scraped_data['season_year']}"
        if week:
            params += f"&matchupPeriodId={week}"
        
        url = base_url + params
        print(f"  Navigating to: {url}")
        self.scraper.page.goto(url, wait_until="networkidle")
        time.sleep(3)
        
        # Take screenshot
        screenshot_name = f"matchups_week_{week}" if week else "matchups_current"
        self.scraper.take_screenshot(screenshot_name)
        
        # Define schema
        schema = """
{
    "week": 14,
    "matchups": [
        {
            "matchup_id": 1,
            "home_team": "Team Name",
            "home_score": 123.45,
            "home_projected": 125.0,
            "away_team": "Team Name",
            "away_score": 98.76,
            "away_projected": 110.0,
            "is_complete": true
        }
    ]
}
"""
        
        # Extract data
        data = self.scraper.extract_with_vision(
            f"Extract ALL matchup data visible on this ESPN scoreboard page. For each matchup, extract: team names, actual scores (the larger numbers), projected scores (smaller numbers in parentheses or lighter text), and completion status. If projected scores are not visible, use null. Include all matchups shown on the page.",
            schema
        )
        
        matchups = data.get('matchups', [])
        week_num = data.get('week', week or 'current')
        
        # Display summary
        if matchups:
            print(f"\n✓ Extracted {len(matchups)} matchups for week {week_num}:")
            for m in matchups:
                status = "✓" if m.get('is_complete') else "⏱"
                print(f"  {status} {m.get('home_team')} ({m.get('home_score')}) vs {m.get('away_team')} ({m.get('away_score')})")
        
        return {
            'week': week_num,
            'matchups': matchups
        }
    
    def extract_all_matchups(self, max_week: int = 18) -> Dict[int, List[Dict]]:
        """
        Extract matchups for all weeks in the season
        
        Args:
            max_week: Maximum week number to scrape
            
        Returns:
            Dict mapping week numbers to matchup data
        """
        print("\n" + "="*60)
        print(f"EXTRACTING ALL MATCHUPS (Weeks 1-{max_week})")
        print("="*60)
        
        all_matchups = {}
        
        for week in range(1, max_week + 1):
            try:
                matchup_data = self.extract_matchups(week)
                all_matchups[week] = matchup_data.get('matchups', [])
                time.sleep(2)  # Be nice to ESPN's servers
            except Exception as e:
                print(f"  ✗ Failed to extract week {week}: {e}")
                continue
        
        print(f"\n✓ Extracted matchups for {len(all_matchups)} weeks")
        return all_matchups
    
    def extract_rosters(self, team_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract roster data for a team or all teams
        
        Args:
            team_name: Specific team name (None for all teams)
            
        Returns:
            Roster data
        """
        print("\n" + "="*60)
        print(f"EXTRACTING ROSTERS")
        print("="*60)
        
        # Navigate directly to rosters page
        url = f"https://fantasy.espn.com/football/league/rosters?leagueId={self.scraper.scraped_data['league_id']}&seasonId={self.scraper.scraped_data['season_year']}"
        print(f"  Navigating to: {url}")
        self.scraper.page.goto(url, wait_until="networkidle")
        time.sleep(3)
        
        self.scraper.take_screenshot("rosters")
        
        # Define schema
        schema = """
{
    "teams": [
        {
            "team_name": "Team Name",
            "starters": [
                {
                    "player_name": "Player Name",
                    "position": "QB",
                    "nfl_team": "KC",
                    "points": 25.3,
                    "status": "Active"
                }
            ],
            "bench": [
                {
                    "player_name": "Player Name",
                    "position": "RB",
                    "nfl_team": "SF",
                    "points": 0.0,
                    "status": "Active"
                }
            ]
        }
    ]
}
"""
        
        # Extract data
        data = self.scraper.extract_with_vision(
            "Extract roster data for all visible teams. Include starters and bench players with their names, positions, NFL teams, points, and status",
            schema
        )
        
        teams_rosters = data.get('teams', [])
        
        # Display summary
        if teams_rosters:
            print(f"\n✓ Extracted rosters for {len(teams_rosters)} teams:")
            for team in teams_rosters[:2]:
                starters = len(team.get('starters', []))
                bench = len(team.get('bench', []))
                print(f"  {team.get('team_name')}: {starters} starters, {bench} bench")
        
        return {'teams': teams_rosters}
    
    def extract_transactions(self) -> List[Dict[str, Any]]:
        """
        Extract transaction history (trades, adds, drops)
        
        Returns:
            List of transactions
        """
        print("\n" + "="*60)
        print("EXTRACTING TRANSACTIONS")
        print("="*60)
        
        # Navigate directly to recent activity
        url = f"https://fantasy.espn.com/football/league/recentactivity?leagueId={self.scraper.scraped_data['league_id']}&seasonId={self.scraper.scraped_data['season_year']}"
        print(f"  Navigating to: {url}")
        self.scraper.page.goto(url, wait_until="networkidle")
        time.sleep(3)
        
        self.scraper.take_screenshot("transactions")
        
        # Define schema
        schema = """
{
    "transactions": [
        {
            "date": "2024-12-20",
            "type": "trade|add|drop",
            "team": "Team Name",
            "players_added": ["Player Name"],
            "players_dropped": ["Player Name"],
            "description": "Team traded Player A for Player B"
        }
    ]
}
"""
        
        # Extract data
        data = self.scraper.extract_with_vision(
            "Extract all visible transaction history including date, type (trade/add/drop), team involved, players added/dropped, and a brief description",
            schema
        )
        
        transactions = data.get('transactions', [])
        
        # Display summary
        if transactions:
            print(f"\n✓ Extracted {len(transactions)} transactions:")
            for txn in transactions[:5]:
                print(f"  {txn.get('date')} - {txn.get('team')}: {txn.get('type')}")
            if len(transactions) > 5:
                print(f"  ... and {len(transactions) - 5} more")
        
        return transactions
    
    def extract_player_stats(self) -> List[Dict[str, Any]]:
        """
        Extract player statistics
        
        Returns:
            List of player stats
        """
        print("\n" + "="*60)
        print("EXTRACTING PLAYER STATS")
        print("="*60)
        
        # Navigate directly to players page
        url = f"https://fantasy.espn.com/football/league/players?leagueId={self.scraper.scraped_data['league_id']}&seasonId={self.scraper.scraped_data['season_year']}"
        print(f"  Navigating to: {url}")
        self.scraper.page.goto(url, wait_until="networkidle")
        time.sleep(3)
        
        self.scraper.take_screenshot("player_stats")
        
        # Define schema
        schema = """
{
    "players": [
        {
            "player_name": "Player Name",
            "position": "QB",
            "nfl_team": "KC",
            "owned_by": "Team Name or FA",
            "total_points": 234.5,
            "average_points": 15.6,
            "last_week_points": 25.3
        }
    ]
}
"""
        
        # Extract data
        data = self.scraper.extract_with_vision(
            "Extract player statistics for all visible players including name, position, NFL team, owned by which fantasy team (or FA for free agent), total points, average points, and last week's points",
            schema
        )
        
        players = data.get('players', [])
        
        # Display summary
        if players:
            print(f"\n✓ Extracted stats for {len(players)} players:")
            for player in players[:5]:
                print(f"  {player.get('player_name')} ({player.get('position')}): {player.get('total_points')} pts")
            if len(players) > 5:
                print(f"  ... and {len(players) - 5} more")
        
        return players
    
    def extract_all_data(self) -> Dict[str, Any]:
        """
        Extract comprehensive league data
        
        Returns:
            Complete league data
        """
        print("\n" + "="*60)
        print("EXTRACTING ALL LEAGUE DATA")
        print("="*60)
        
        all_data = {
            'standings': [],
            'matchups': {},
            'rosters': {},
            'transactions': [],
            'player_stats': []
        }
        
        try:
            # Extract standings
            all_data['standings'] = self.extract_standings()
            time.sleep(2)
            
            # Extract matchups for all weeks (1-17 for regular season)
            print("\n" + "="*60)
            print("EXTRACTING ALL WEEKS OF MATCHUPS")
            print("="*60)
            for week_num in range(1, 18):  # Weeks 1-17
                try:
                    matchup_data = self.extract_matchups(week_num)
                    all_data['matchups'][week_num] = matchup_data.get('matchups', [])
                    print(f"  ✓ Week {week_num}: {len(all_data['matchups'][week_num])} matchups")
                    time.sleep(1.5)  # Be nice to ESPN servers
                except Exception as e:
                    print(f"  ✗ Week {week_num} failed: {e}")
                    all_data['matchups'][week_num] = []
            
            time.sleep(2)
            
            # Extract rosters
            roster_data = self.extract_rosters()
            all_data['rosters'] = roster_data.get('teams', [])
            time.sleep(2)
            
            # Extract transactions
            all_data['transactions'] = self.extract_transactions()
            time.sleep(2)
            
            # Extract player stats
            all_data['player_stats'] = self.extract_player_stats()
            
            print("\n" + "="*60)
            print("✓ ALL DATA EXTRACTION COMPLETE")
            print("="*60)
            
        except Exception as e:
            print(f"\n✗ Error during data extraction: {e}")
            import traceback
            traceback.print_exc()
        
        return all_data

