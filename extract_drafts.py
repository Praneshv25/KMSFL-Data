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
from gemini_client import GeminiVisionClient
from auth_manager import AuthManager, LoginHelper
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
        page.set_default_timeout(30000)  # 30 seconds default timeout
        
        # Initialize Gemini and Auth
        ai = GeminiVisionClient()
        auth = AuthManager()
        
        try:
            # Load and apply cookies for authentication
            cookies = auth.load_cookies()
            if cookies:
                auth.apply_cookies_to_context(context)
            else:
                print("⚠ No saved cookies found. You may need to login manually.")
                print("   Run historical_scraper.py first to authenticate.")
            
            # Navigate directly to draft recap page
            # Note: ESPN uses current/default season, we'll need to change the season in the UI if needed
            draft_url = f"https://fantasy.espn.com/football/league/draftrecap?leagueId={config.LEAGUE_ID}&seasonId={season_year}"
            print(f"Navigating to: {draft_url}")
            
            for attempt in range(3):
                try:
                    page.goto(draft_url, wait_until="networkidle", timeout=30000)
                    time.sleep(3)
                    break
                except Exception as e:
                    if attempt < 2:
                        print(f"⚠ Navigation attempt {attempt + 1} failed, retrying...")
                        time.sleep(2)
                    else:
                        raise
            
            # Scroll to load all picks first
            print("Scrolling to load all draft picks...")
            for i in range(10):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(0.5)
            
            # Scroll back to top
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(1)
            
            # Take multiple screenshots in chunks to avoid API timeout
            print("Taking screenshots in chunks...")
            num_chunks = 3  # Split into 3 chunks with increased API timeout
            all_picks = []
            draft_type = None
            draft_date = None
            
            # Define JSON schema for draft data
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
            
            page_height = page.evaluate("document.body.scrollHeight")
            viewport_height = page.evaluate("window.innerHeight")
            
            for chunk_num in range(num_chunks):
                # Calculate scroll position for this chunk
                scroll_position = int((page_height / num_chunks) * chunk_num)
                
                print(f"  Screenshot {chunk_num + 1}/{num_chunks} (scroll: {scroll_position}px)...")
                page.evaluate(f"window.scrollTo(0, {scroll_position})")
                time.sleep(1)
                
                # Take screenshot of current viewport
                screenshot = page.screenshot()
                
                # Extract draft picks from this chunk with retry logic
                chunk_success = False
                for retry in range(3):
                    try:
                        if retry > 0:
                            print(f"    Retry {retry}/2 for chunk {chunk_num + 1}...")
                            print(f"    Waiting 30 seconds before retry...")
                            time.sleep(30)  # Wait 30s before retry
                        
                        chunk_data = ai.extract_json_from_screenshot(
                            screenshot,
                            f"Extract draft picks from this ESPN Fantasy draft page screenshot (part {chunk_num + 1} of {num_chunks}). Include draft type, draft date, and ALL draft picks visible with: round number, pick number in round, overall pick number, team that drafted the player, player name, player position (RB/WR/QB/TE/etc), and NFL team.",
                            draft_schema
                        )
                        
                        chunk_draft = chunk_data.get('draft_data', {})
                        chunk_picks = chunk_draft.get('picks', [])
                        
                        # Save draft metadata from first chunk
                        if chunk_num == 0:
                            draft_type = chunk_draft.get('draft_type')
                            draft_date = chunk_draft.get('draft_date')
                        
                        print(f"    ✓ Extracted {len(chunk_picks)} picks from chunk {chunk_num + 1}")
                        all_picks.extend(chunk_picks)
                        chunk_success = True
                        break
                        
                    except Exception as e:
                        if "504" in str(e) or "Deadline" in str(e):
                            if retry < 2:
                                print(f"    ⚠ API timeout on chunk {chunk_num + 1}, will retry...")
                            else:
                                print(f"    ✗ API timeout on chunk {chunk_num + 1} after 3 attempts - skipping...")
                        else:
                            print(f"    ⚠ Error on chunk {chunk_num + 1}: {e}")
                            break
                
                # Wait between chunks to avoid rate limiting
                if chunk_success and chunk_num < num_chunks - 1:
                    print(f"    Waiting 30 seconds before next chunk...")
                    time.sleep(30)  # 30 seconds between chunks to avoid rate limits
            
            # Remove duplicates based on overall_pick
            print(f"  Removing duplicates...")
            unique_picks = {}
            for pick in all_picks:
                overall = pick.get('overall_pick')
                if overall and overall not in unique_picks:
                    unique_picks[overall] = pick
            
            # Sort by overall pick number
            sorted_picks = sorted(unique_picks.values(), key=lambda x: x.get('overall_pick', 999))
            
            draft_data = {
                'draft_type': draft_type,
                'draft_date': draft_date,
                'picks': sorted_picks
            }
            
            print(f"  ✓ Total unique picks: {len(sorted_picks)}")
            
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
            error_msg = str(e)
            if "504" in error_msg or "Deadline" in error_msg:
                print(f"✗ API timeout extracting draft for {season_year}")
                print(f"  (The full-page screenshot may be too large)")
            else:
                print(f"✗ Error extracting draft for {season_year}: {e}")
                import traceback
                traceback.print_exc()
            return None
        finally:
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
            print("\nWaiting 60 seconds before next season...")
            time.sleep(60)
    
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

