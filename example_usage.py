"""
Example usage of ESPN Fantasy Football Scraper
Demonstrates different ways to use the scraper
"""
from espn_scraper import ESPNFantasyScraper
from data_manager import DataManager
import config

def example_basic_scrape():
    """
    Example 1: Basic scrape - get all data
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Full Scrape")
    print("="*60)
    
    scraper = ESPNFantasyScraper()
    
    try:
        scraper.start()
        
        if scraper.authenticate():
            # Extract all data
            data = scraper.extractor.extract_all_data()
            
            # Save it
            scraper.data_manager.save_all(data)
            
            print("\n✓ Scrape complete!")
            
    finally:
        scraper.close()


def example_standings_only():
    """
    Example 2: Extract just standings
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Standings Only")
    print("="*60)
    
    scraper = ESPNFantasyScraper()
    
    try:
        scraper.start()
        scraper.authenticate()
        
        # Extract just standings
        standings = scraper.extractor.extract_standings()
        
        # Display
        print("\nLeague Standings:")
        for team in standings:
            print(f"  {team['rank']}. {team['team_name']}: {team['wins']}-{team['losses']}")
        
    finally:
        scraper.close()


def example_specific_week():
    """
    Example 3: Extract matchups for specific week
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Specific Week Matchups")
    print("="*60)
    
    scraper = ESPNFantasyScraper()
    
    try:
        scraper.start()
        scraper.authenticate()
        
        # Extract week 14 matchups
        week = 14
        matchup_data = scraper.extractor.extract_matchups(week)
        
        print(f"\nWeek {week} Matchups:")
        for m in matchup_data['matchups']:
            print(f"  {m['home_team']} ({m['home_score']}) vs {m['away_team']} ({m['away_score']})")
        
    finally:
        scraper.close()


def example_query_database():
    """
    Example 4: Query existing data from database
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Query Database")
    print("="*60)
    
    dm = DataManager()
    
    # Get latest standings from database
    standings = dm.get_latest_standings()
    
    if standings:
        print(f"\nFound {len(standings)} teams in database:")
        for team in standings[:5]:
            print(f"  {team['team_name']}: {team['wins']}-{team['losses']}")
    else:
        print("\nNo data in database yet. Run scraper first!")


def example_custom_extraction():
    """
    Example 5: Custom extraction with verification
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: Custom Extraction with Verification")
    print("="*60)
    
    scraper = ESPNFantasyScraper()
    
    try:
        scraper.start()
        scraper.authenticate()
        
        # Navigate to a specific page
        scraper.navigate_intelligently("Go to league standings")
        
        # Get AI summary of current page
        summary = scraper.get_current_page_info()
        print(f"\nCurrent page: {summary}")
        
        # Extract data
        data = scraper.extract_with_vision(
            "Extract the top 3 teams with their records"
        )
        
        print("\nExtracted data:", data)
        
        # Verify the data
        verification = scraper.verify_extraction(data)
        print(f"\nVerification: {verification}")
        
    finally:
        scraper.close()


def example_weekly_automation():
    """
    Example 6: Automated weekly scrape
    This could be scheduled with cron or Task Scheduler
    """
    print("\n" + "="*60)
    print("EXAMPLE 6: Automated Weekly Scrape")
    print("="*60)
    
    scraper = ESPNFantasyScraper()
    
    try:
        scraper.start()
        
        # Authenticate (uses saved cookies)
        if not scraper.authenticate():
            print("Authentication failed - cookies may have expired")
            return
        
        # Extract current week's data
        data = {
            'standings': scraper.extractor.extract_standings(),
            'matchups': scraper.extractor.extract_matchups(),
            'scraped_at': scraper.scraped_data['scraped_at']
        }
        
        # Save with custom filename
        filename = f"weekly_update_{config.SEASON_YEAR}_week_current.json"
        scraper.data_manager.save_to_json(data, filename)
        
        print(f"\n✓ Weekly update saved: {filename}")
        
    finally:
        scraper.close()


if __name__ == "__main__":
    print("="*60)
    print("ESPN Fantasy Football Scraper - Usage Examples")
    print("="*60)
    print("\nAvailable examples:")
    print("  1. Basic full scrape")
    print("  2. Standings only")
    print("  3. Specific week matchups")
    print("  4. Query database")
    print("  5. Custom extraction with verification")
    print("  6. Automated weekly scrape")
    print("\nEdit this file to uncomment the example you want to run.")
    print("="*60)
    
    # Uncomment the example you want to run:
    
    # example_basic_scrape()
    # example_standings_only()
    # example_specific_week()
    example_query_database()  # Safe to run without browser
    # example_custom_extraction()
    # example_weekly_automation()

