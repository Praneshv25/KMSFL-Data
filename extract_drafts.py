#!/usr/bin/env python3
"""
Script to extract draft data for specific seasons
Usage: python3 extract_drafts.py [start_year] [end_year]
Example: python3 extract_drafts.py 2020 2024
"""

import sys
import json
import time
from pathlib import Path
from gemini_client import GeminiAIScraper
from auth_manager import save_cookies, load_cookies
from data_extraction import extract_draft_recap
from playwright.sync_api import sync_playwright
import config

def extract_draft_for_season(season_year):
    """Extract draft data for a single season"""
    print(f"\n{'='*60}")
    print(f"Extracting Draft Data for {season_year}")
    print(f"{'='*60}\n")
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.firefox.launch(
            headless=config.HEADLESS,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        # Initialize Gemini
        ai = GeminiAIScraper(page)
        ai.start()
        
        try:
            # Load cookies for authentication
            load_cookies(context, config.COOKIES_FILE)
            
            # Navigate directly to draft page
            draft_url = f"https://fantasy.espn.com/football/league/draft?leagueId={config.LEAGUE_ID}&seasonId={season_year}"
            print(f"Navigating to: {draft_url}")
            
            for attempt in range(3):
                try:
                    page.goto(draft_url, wait_until="load", timeout=40000)
                    time.sleep(3)
                    break
                except Exception as e:
                    if attempt < 2:
                        print(f"⚠ Navigation attempt {attempt + 1} failed, retrying...")
                        time.sleep(2)
                    else:
                        raise
            
            # Scroll to load all picks
            print("Scrolling to load all draft picks...")
            for i in range(10):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(0.5)
            
            # Scroll back to top
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(1)
            
            # Extract draft data
            print("Extracting draft data...")
            draft_data = extract_draft_recap(page, ai, season_year)
            
            if draft_data and 'picks' in draft_data and len(draft_data['picks']) > 0:
                print(f"✓ Extracted {len(draft_data['picks'])} draft picks")
                
                # Load existing data file
                data_file = Path(config.DATA_DIR) / f"espn_league_{config.LEAGUE_ID}_{season_year}_historical.json"
                
                if data_file.exists():
                    with open(data_file, 'r') as f:
                        existing_data = json.load(f)
                    
                    # Update draft data
                    existing_data['draft'] = draft_data
                    
                    # Save updated data
                    with open(data_file, 'w') as f:
                        json.dump(existing_data, f, indent=2)
                    
                    print(f"✓ Updated {data_file.name} with draft data")
                else:
                    print(f"⚠ Warning: Data file not found: {data_file}")
                    
                return draft_data
            else:
                print(f"✗ Failed to extract draft data for {season_year}")
                return None
                
        except Exception as e:
            print(f"✗ Error extracting draft for {season_year}: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            ai.close()
            browser.close()

def main():
    # Parse arguments
    if len(sys.argv) >= 3:
        start_year = int(sys.argv[1])
        end_year = int(sys.argv[2])
    elif len(sys.argv) == 2:
        start_year = end_year = int(sys.argv[1])
    else:
        # Default: extract 2020-2024
        start_year = 2020
        end_year = 2024
    
    print(f"\n{'='*60}")
    print(f"ESPN Fantasy Football Draft Extractor")
    print(f"Extracting drafts for seasons: {start_year}-{end_year}")
    print(f"League ID: {config.LEAGUE_ID}")
    print(f"{'='*60}\n")
    
    results = {}
    for year in range(start_year, end_year + 1):
        draft_data = extract_draft_for_season(year)
        results[year] = draft_data is not None
        
        # Wait between years to avoid rate limiting
        if year < end_year:
            print("\nWaiting 5 seconds before next season...")
            time.sleep(5)
    
    # Summary
    print(f"\n{'='*60}")
    print("EXTRACTION SUMMARY")
    print(f"{'='*60}")
    for year, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{year}: {status}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()

