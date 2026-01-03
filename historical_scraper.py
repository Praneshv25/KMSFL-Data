"""
Historical ESPN Fantasy Football Scraper
Extracts data from multiple seasons (2019-2024) with box score details
"""
import time
import re
from datetime import datetime
from typing import Dict, Any, List
from espn_scraper import ESPNFantasyScraper
from data_manager import DataManager
import config


class HistoricalESPNScraper(ESPNFantasyScraper):
    """
    Extended scraper for historical data with box score navigation
    """
    
    def extract_matchup_with_boxscore(self, week: int, season: int) -> List[Dict[str, Any]]:
        """
        Extract matchup data using direct box score URLs
        
        Args:
            week: Week number (matchupPeriodId)
            season: Season year
            
        Returns:
            List of detailed matchup data
        """
        print(f"\n  Extracting Week {week} (Season {season})...")
        
        # Check if this is a two-week playoff matchup (2019 matchupPeriodId 14 and 15)
        # matchupPeriodId=14 contains weeks 14-15, matchupPeriodId=15 contains weeks 16-17
        is_two_week_playoff = season == 2019 and week in [14, 15]
        
        # First, go to scoreboard to get team IDs
        # For two-week playoffs, add mSPID parameter to show the second week's matchups
        scoreboard_url = f"https://fantasy.espn.com/football/league/scoreboard?leagueId={config.LEAGUE_ID}&seasonId={season}&matchupPeriodId={week}"
        if is_two_week_playoff:
            # Show the second week's scores on scoreboard to see all matchups
            if week == 14:
                scoreboard_url += "&mSPID=15"  # Show week 15 scores
            elif week == 15:
                scoreboard_url += "&mSPID=17"  # Show week 17 scores
        
        self.page.goto(scoreboard_url, wait_until="networkidle", timeout=30000)
        time.sleep(3)
        
        # Scroll down the page to load all matchups (Championship, Consolation, etc.)
        print(f"    Scrolling to load all matchups...")
        for _ in range(5):
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(0.5)
        self.page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)
        
        # For playoffs, try to expand all bracket sections
        # This ensures we see all matchups, not just the main bracket
        try:
            # Look for common button/link text that might expand sections
            expand_keywords = ['Show', 'Expand', 'View', 'Consolation', 'Bracket', 'More']
            for keyword in expand_keywords:
                try:
                    buttons = self.page.locator(f'button:has-text("{keyword}"), a:has-text("{keyword}")').all()
                    for button in buttons[:3]:  # Limit to first 3 per keyword
                        try:
                            if button.is_visible():
                                button.click()
                                time.sleep(0.5)
                        except:
                            pass
                except:
                    pass
        except:
            pass
        
        time.sleep(2)
        
        # Get page content to find all box score links
        # ESPN box scores have URLs like: boxscore?leagueId=X&matchupPeriodId=Y&teamId=Z
        
        # Extract all unique box score links from the page
        try:
            # Find all links to box scores
            box_score_links = self.page.locator('a[href*="boxscore"]').all()
            
            if not box_score_links:
                print(f"    ⚠ No box score links found")
                return []
            
            # Get unique box score URLs
            # Note: Each matchup appears multiple times (one link per team), 
            # but we need to visit each matchup only once
            box_score_urls = []
            
            print(f"    Found {len(box_score_links)} total box score links on page")
            
            for link in box_score_links:
                try:
                    href = link.get_attribute('href')
                    if href and 'boxscore' in href:
                        # Make it a full URL if it's relative
                        if href.startswith('/'):
                            full_url = f"https://fantasy.espn.com{href}"
                        else:
                            full_url = href
                        
                        # Collect all URLs first
                        if full_url not in box_score_urls:
                            box_score_urls.append(full_url)
                except:
                    continue
            
            print(f"    Collected {len(box_score_urls)} unique URLs")
            
            # Deduplicate by removing teamId parameter to get unique matchups
            # Multiple URLs with different teamIds point to the same matchup
            final_urls = []
            seen_matchup_keys = set()
            
            for url in box_score_urls:
                # Create a key that identifies unique matchups
                # Remove teamId and view parameters to create the key
                key = re.sub(r'[&?]teamId=\d+', '', url)
                key = re.sub(r'[&?]view=[^&]*', '', key)
                
                if key not in seen_matchup_keys:
                    final_urls.append(url)
                    seen_matchup_keys.add(key)
            
            print(f"    Found {len(final_urls)} unique matchups")
            
            all_matchup_data = []
            
            # For two-week playoff matchups, we need to extract both weeks separately
            scoring_periods = []
            if is_two_week_playoff:
                # matchupPeriodId=14 contains weeks 14 and 15
                # matchupPeriodId=15 contains weeks 16 and 17
                if week == 14:
                    scoring_periods = [14, 15]
                elif week == 15:
                    scoring_periods = [16, 17]
                print(f"    Two-week playoff detected - will extract weeks {scoring_periods[0]} and {scoring_periods[1]} separately")
            else:
                scoring_periods = [week]
            
            # For each unique box score URL, navigate and extract
            for scoring_period in scoring_periods:
                for i, base_box_score_url in enumerate(final_urls):
                    retry_count = 0
                    max_retries = 2
                    
                    # Add or update the scoringPeriodId parameter in the URL
                    if '?' in base_box_score_url:
                        # Check if scoringPeriodId already exists
                        if 'scoringPeriodId=' in base_box_score_url:
                            box_score_url = re.sub(r'scoringPeriodId=\d+', f'scoringPeriodId={scoring_period}', base_box_score_url)
                        else:
                            box_score_url = f"{base_box_score_url}&scoringPeriodId={scoring_period}"
                    else:
                        box_score_url = f"{base_box_score_url}?scoringPeriodId={scoring_period}"
                    
                    week_label = f" (Week {scoring_period})" if is_two_week_playoff else ""
                    
                    while retry_count <= max_retries:
                        try:
                            print(f"    Extracting box score {i+1}/{len(final_urls)}{week_label}..." + (f" (retry {retry_count})" if retry_count > 0 else ""))
                            
                            # Navigate with timeout
                            self.page.goto(box_score_url, wait_until="load", timeout=40000)
                            time.sleep(3)  # Give extra time for page to settle
                            
                            # Scroll to load all players (bench + IR)
                            for _ in range(3):
                                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                                time.sleep(0.5)
                            self.page.evaluate("window.scrollTo(0, 0)")
                            time.sleep(1)
                            
                            # Take full-page screenshot to capture starters + bench + IR
                            box_screenshot = self.page.screenshot(full_page=True)
                            
                            # If we got here, navigation worked, break out of retry loop
                            break
                            
                        except Exception as nav_error:
                            retry_count += 1
                            if retry_count > max_retries:
                                print(f"      ✗ Failed after {max_retries} retries: {nav_error}")
                                raise  # Re-raise to be caught by outer try-except
                            else:
                                print(f"      ⚠ Timeout, retrying...")
                                time.sleep(3)
                                continue
                
                try:
                    # Extract box score data
                    box_schema = """
{
    "matchup": {
        "home_team": "Team Name",
        "home_score": 123.45,
        "home_projected": 125.0,
        "away_team": "Team Name", 
        "away_score": 98.76,
        "away_projected": 110.0,
        "bracket_type": "Championship|Consolation|Consolation Ladder|null",
        "home_roster": [
            {
                "player_name": "Player Name",
                "position": "QB",
                "nfl_team": "KC",
                "points": 25.3,
                "projected": 22.5,
                "started": true
            }
        ],
        "away_roster": [
            {
                "player_name": "Player Name",
                "position": "RB",
                "nfl_team": "SF",
                "points": 15.2,
                "projected": 18.0,
                "started": true
            }
        ]
    }
}
"""
                    
                    matchup_data = self.gemini.extract_json_from_screenshot(
                        box_screenshot,
                        f"Extract complete box score data from this full-page screenshot. Include: both team names, final scores, projected scores, and EVERY SINGLE PLAYER from BOTH teams including STARTERS, BENCH players, and IR players. For each player include: player name, position, NFL team, actual points scored, projected points, and whether they started (true) or were on bench/IR (false). This is a full-page screenshot so make sure to extract ALL players visible on the entire page, not just the starting lineup.",
                        box_schema
                    )
                    
                    matchup = matchup_data.get('matchup', {})
                    matchup['week'] = scoring_period  # Use the specific scoring period (actual week 14, 15, 16, or 17)
                    matchup['season'] = season
                    if is_two_week_playoff:
                        matchup['is_two_week_playoff'] = True
                        matchup['matchup_period_id'] = week  # Store the ESPN matchupPeriodId (14 or 15)
                    all_matchup_data.append(matchup)
                    
                    print(f"      ✓ {matchup.get('home_team')} ({len(matchup.get('home_roster', []))}) vs {matchup.get('away_team')} ({len(matchup.get('away_roster', []))})")
                    
                    # Add small delay between API calls to avoid rate limiting
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"      ✗ Error extracting matchup {i+1}: {e}")
                    if "504" in str(e) or "Deadline" in str(e):
                        print(f"      (API timeout - waiting 5 seconds before retry...)")
                        time.sleep(5)
                    continue
            
            return all_matchup_data
            
        except Exception as e:
            print(f"    ✗ Error extracting matchups: {e}")
            return []
    
    def _extract_from_screenshot(self, week: int, season: int) -> List[Dict[str, Any]]:
        """Fallback: Extract from scoreboard screenshot if box scores fail"""
        screenshot = self.page.screenshot()
        
        schema = """
{
    "matchups": [
        {
            "home_team": "Team Name",
            "home_score": 123.45,
            "away_team": "Team Name",
            "away_score": 98.76
        }
    ]
}
"""
        
        data = self.gemini.extract_json_from_screenshot(
            screenshot,
            "Extract basic matchup data from scoreboard",
            schema
        )
        
        matchups = data.get('matchups', [])
        for m in matchups:
            m['week'] = week
            m['season'] = season
        
        return matchups
    
    def extract_draft_recap(self, season: int) -> Dict[str, Any]:
        """
        Extract draft recap data for a season (scroll to get all picks)
        
        Args:
            season: Season year
            
        Returns:
            Draft data including picks, order, and player selections
        """
        print(f"\n  Extracting draft recap for {season}...")
        
        # Navigate to draft recap page
        url = f"https://fantasy.espn.com/football/league/draftrecap?leagueId={config.LEAGUE_ID}&seasonId={season}"
        self.page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(3)
        
        try:
            # Scroll down multiple times to load all picks
            print(f"    Scrolling to load all draft picks...")
            for i in range(10):  # Scroll 10 times to ensure we get everything
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(0.5)
            
            # Take a full page screenshot (includes all loaded content)
            print(f"    Taking full-page screenshot...")
            screenshot = self.page.screenshot(full_page=True)
            
            draft_schema = """
{
    "draft_data": {
        "draft_type": "Snake|Auction",
        "draft_date": "2024-08-25",
        "picks": [
            {
                "round": 1,
                "pick": 1,
                "overall_pick": 1,
                "team": "Team Name",
                "player_name": "Player Name",
                "position": "RB",
                "nfl_team": "SF"
            }
        ]
    }
}
"""
            
            # Extract all picks from full page screenshot (single API call)
            print(f"    Analyzing draft data...")
            draft_data = self.gemini.extract_json_from_screenshot(
                screenshot,
                "Extract the complete draft recap from this ESPN Fantasy page. Include draft type, draft date, and EVERY SINGLE draft pick visible with: round number, pick number in round, overall pick number, team that drafted the player, player name, player position (RB/WR/QB/TE/etc), and NFL team. This is a full-page screenshot so extract all picks from top to bottom.",
                draft_schema
            )
            
            draft_info = draft_data.get('draft_data', {})
            picks = draft_info.get('picks', [])
            
            print(f"    ✓ Extracted {len(picks)} draft picks")
            
            return draft_info
            
        except Exception as e:
            print(f"    ✗ Failed to extract draft recap: {e}")
            # Don't print full traceback for timeouts
            if "504" in str(e) or "Deadline" in str(e):
                print(f"    (API timeout - draft will be skipped for this season)")
            return {}
    
    def get_week_count(self, season: int) -> int:
        """
        Get number of regular season weeks for a given year
        
        Args:
            season: Season year
            
        Returns:
            Number of weeks (16 for 2020, 17 for others)
        """
        return 16 if season == 2020 else 17
    
    def identify_playoff_round(self, week: int, season: int) -> str:
        """
        Identify if a week is playoffs and what type
        
        Args:
            week: Week number
            season: Season year
            
        Returns:
            Round type: 'regular_season', 'semifinals', 'championship', 'consolation'
        """
        regular_weeks = self.get_week_count(season)
        
        if week <= regular_weeks - 2:
            return 'regular_season'
        elif week == regular_weeks - 1:
            return 'playoffs_semifinals'
        elif week == regular_weeks:
            return 'championship_consolation_finals'
        else:
            return 'extended_playoffs'
    
    def scrape_historical_data(self, start_year: int = 2019, end_year: int = 2024):
        """
        Scrape data for multiple seasons
        
        Args:
            start_year: First season to scrape
            end_year: Last season to scrape
        """
        print("\n" + "="*60)
        print(f"HISTORICAL DATA EXTRACTION: {start_year}-{end_year}")
        print("="*60)
        
        data_manager = DataManager()
        
        for season in range(start_year, end_year + 1):
            print("\n" + "="*60)
            print(f"SEASON {season}")
            print("="*60)
            
            # Determine week count for this season
            week_count = self.get_week_count(season)
            print(f"  Regular season weeks: {week_count}")
            
            season_data = {
                'league_id': config.LEAGUE_ID,
                'season_year': season,
                'scraped_at': datetime.now().isoformat(),
                'regular_season_weeks': week_count,
                'standings': [],
                'matchups': {},
                'draft': {}
            }
            
            # Extract standings for this season
            try:
                print(f"\nExtracting standings for {season}...")
                url = f"https://fantasy.espn.com/football/league/standings?leagueId={config.LEAGUE_ID}&seasonId={season}"
                self.page.goto(url, wait_until="networkidle")
                time.sleep(2)
                
                screenshot = self.page.screenshot()
                
                standings_schema = """
{
    "teams": [
        {
            "rank": 1,
            "team_name": "Team Name",
            "owner": "Owner Name",
            "wins": 10,
            "losses": 3,
            "points_for": 1234.56,
            "points_against": 1100.23
        }
    ]
}
"""
                
                standings_data = self.gemini.extract_json_from_screenshot(
                    screenshot,
                    "Extract team standings with rank, name, owner, wins, losses, points for, and points against",
                    standings_schema
                )
                
                season_data['standings'] = standings_data.get('teams', [])
                print(f"  ✓ Extracted {len(season_data['standings'])} teams")
                
            except Exception as e:
                print(f"  ✗ Failed to extract standings for {season}: {e}")
            
            # Extract draft recap (skip if it fails to avoid holding up everything)
            try:
                season_data['draft'] = self.extract_draft_recap(season)
                time.sleep(3)  # Add delay after draft extraction
            except Exception as e:
                print(f"  ✗ Failed to extract draft recap for {season}: {e}")
                season_data['draft'] = {}
            
            # Extract matchups week by week with box scores
            # Include playoffs (typically weeks 15-17 or 15-16 for 2020)
            total_weeks = week_count + 2  # Include playoff weeks
            
            for week in range(1, total_weeks + 1):
                try:
                    playoff_round = self.identify_playoff_round(week, season)
                    
                    if playoff_round == 'regular_season':
                        print(f"\n  Week {week} (Regular Season)")
                    elif playoff_round == 'playoffs_semifinals':
                        print(f"\n  Week {week} (PLAYOFFS - Semifinals)")
                    elif playoff_round == 'championship_consolation_finals':
                        print(f"\n  Week {week} (PLAYOFFS - Championship & Consolation)")
                    
                    matchups = self.extract_matchup_with_boxscore(week, season)
                    
                    # Add playoff round info to each matchup
                    for matchup in matchups:
                        matchup['playoff_round'] = playoff_round
                    
                    season_data['matchups'][week] = matchups
                    print(f"    ✓ Week {week}: {len(matchups)} matchups ({playoff_round})")
                    time.sleep(1.5)
                    
                except Exception as e:
                    print(f"    ✗ Week {week} failed: {e}")
                    season_data['matchups'][week] = []
            
            # Save this season's data
            filename = f"espn_league_{config.LEAGUE_ID}_{season}_historical.json"
            data_manager.save_to_json(season_data, filename)
            data_manager.save_to_database(season_data)
            
            print(f"\n✓ Season {season} complete!")
            time.sleep(2)
        
        print("\n" + "="*60)
        print("✓ HISTORICAL DATA EXTRACTION COMPLETE!")
        print("="*60)


def main():
    """Main entry point for historical scraper"""
    scraper = HistoricalESPNScraper()
    
    try:
        # Start browser
        scraper.start()
        
        # Authenticate
        if not scraper.authenticate():
            print("✗ Authentication failed")
            return
        
        # Scrape 2019-2024 data
        scraper.scrape_historical_data(start_year=2019, end_year=2024)
        
        print("\n✓ All historical data saved!")
        print("  - JSON files in data/ directory")
        print("  - SQLite database: data/espn_fantasy.db")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Scraping interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.close()


if __name__ == "__main__":
    main()

