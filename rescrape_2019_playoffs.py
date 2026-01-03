#!/usr/bin/env python3
"""
Re-scrape 2019 playoff weeks (14-17) to capture two-week playoff matchups
Extracts individual week data for each two-week playoff round
"""
import json
import time
from pathlib import Path
from historical_scraper import HistoricalESPNScraper
import config

def main():
    print("\n" + "="*60)
    print("Re-scraping 2019 Playoffs (Weeks 14-17)")
    print("Two-week playoff matchups")
    print("="*60 + "\n")
    
    season = 2019
    # ESPN 2019 playoffs use matchupPeriodId that don't match week numbers:
    # matchupPeriodId=14 contains weeks 14 and 15 (Round 1)
    # matchupPeriodId=15 contains weeks 16 and 17 (Finals)
    
    scraper = HistoricalESPNScraper()
    
    try:
        scraper.start()
        scraper.authenticate()
        
        # Load existing data
        data_file = Path(config.DATA_DIR) / f"espn_league_{config.LEAGUE_ID}_{season}_historical.json"
        
        if data_file.exists():
            with open(data_file, 'r') as f:
                existing_data = json.load(f)
            print(f"✓ Loaded existing data (preserving standings and draft)\n")
        else:
            print("✗ No existing 2019 data file found")
            return
        
        # Extract matchups for playoff weeks
        # Note: ESPN uses matchupPeriodId, which doesn't match week numbers in playoffs
        # Round 1 (weeks 14-15): matchupPeriodId=14
        # Finals (weeks 16-17): matchupPeriodId=15
        matchup_periods = [
            (14, [14, 15]),  # matchupPeriodId=14 contains weeks 14 and 15
            (15, [16, 17])   # matchupPeriodId=15 contains weeks 16 and 17
        ]
        
        for matchup_period, weeks in matchup_periods:
            print(f"\n{'='*60}")
            print(f"Visiting matchupPeriodId={matchup_period} (Weeks {weeks[0]}-{weeks[1]})")
            print(f"{'='*60}\n")
            
            # Use the matchupPeriodId for navigation
            matchups = scraper.extract_matchup_with_boxscore(matchup_period, season)
            
            if matchups:
                # The matchups list will contain data for multiple weeks
                for matchup in matchups:
                    actual_week = matchup.get('week')
                    print(f"  ✓ Extracted week {actual_week}: {matchup.get('home_team')} vs {matchup.get('away_team')}")
                    
                    # Add to existing data under the correct week
                    week_key = str(actual_week)
                    if week_key not in existing_data['matchups']:
                        existing_data['matchups'][week_key] = []
                    
                    # Check if this matchup already exists (avoid duplicates)
                    existing_matchups = existing_data['matchups'][week_key]
                    teams = {matchup.get('home_team'), matchup.get('away_team')}
                    is_duplicate = any(
                        {m.get('home_team'), m.get('away_team')} == teams 
                        for m in existing_matchups
                    )
                    
                    if not is_duplicate:
                        existing_data['matchups'][week_key].append(matchup)
                        print(f"    Added to week {actual_week}")
                    else:
                        # Update existing matchup with new data
                        for idx, m in enumerate(existing_matchups):
                            if {m.get('home_team'), m.get('away_team')} == teams:
                                existing_data['matchups'][week_key][idx] = matchup
                                print(f"    Updated week {actual_week}")
                                break
            else:
                print(f"  ✗ No matchups extracted for matchupPeriodId={matchup_period}")
            
            time.sleep(5)
        
        # Update timestamp
        existing_data['scraped_at'] = time.strftime("%Y-%m-%dT%H:%M:%S")
        
        # Save updated data
        with open(data_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        print(f"\n" + "="*60)
        print(f"✓ COMPLETED 2019 PLAYOFFS")
        print(f"="*60)
        print(f"\n✓ Updated {data_file.name}")
        print(f"  Preserved: standings, draft, regular season")
        print(f"  Updated: playoff weeks 14-17 with individual week data")
        
        # Show final week counts
        print(f"\n  Week 14: {len(existing_data['matchups'].get('14', []))} matchups")
        print(f"  Week 15: {len(existing_data['matchups'].get('15', []))} matchups")
        print(f"  Week 16: {len(existing_data['matchups'].get('16', []))} matchups")
        print(f"  Week 17: {len(existing_data['matchups'].get('17', []))} matchups")
        
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

