#!/usr/bin/env python3
"""
Re-populate kicker data for existing NFL stats
Deletes existing kicker records and re-fetches them with kicker stats
"""
import sys
sys.path.insert(0, '.')

import sqlite3
import config
from scrapers.nfl_stats_fetcher import NFLStatsFetcher
import nflreadpy as nfl
import polars as pl

def repopulate_kicker_data():
    print("\n" + "="*60)
    print("RE-POPULATE KICKER DATA")
    print("="*60 + "\n")
    
    conn = sqlite3.connect(config.DB_FILE)
    cursor = conn.cursor()
    
    # Get list of seasons with kicker data
    cursor.execute("SELECT DISTINCT season FROM nfl_weekly_stats WHERE position = 'K' ORDER BY season")
    seasons = [row[0] for row in cursor.fetchall()]
    
    print(f"📊 Found kicker data for seasons: {seasons}")
    
    # Delete existing kicker records
    cursor.execute("DELETE FROM nfl_weekly_stats WHERE position = 'K'")
    deleted_count = cursor.rowcount
    conn.commit()
    print(f"🗑️  Deleted {deleted_count} existing kicker records (they had 0s)\n")
    
    conn.close()
    
    # Re-fetch kicker data for each season
    fetcher = NFLStatsFetcher()
    total_stored = 0
    
    for season in seasons:
        print(f"📥 Fetching {season} player stats...")
        try:
            stats = nfl.load_player_stats(seasons=[season])
            kickers = stats.filter(pl.col('position') == 'K')
            
            if len(kickers) > 0:
                stored = fetcher.store_weekly_stats(kickers)
                total_stored += stored
                print(f"   ✓ Stored {stored} kicker records for {season}")
            else:
                print(f"   ⚠ No kickers found for {season}")
        except Exception as e:
            print(f"   ✗ Error fetching {season}: {e}")
    
    print("\n" + "="*60)
    print(f"✅ COMPLETE: Stored {total_stored} total kicker records")
    print("="*60 + "\n")
    
    # Verify
    conn = sqlite3.connect(config.DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) as total, 
               COUNT(CASE WHEN fg_att > 0 THEN 1 END) as with_data
        FROM nfl_weekly_stats WHERE position = 'K'
    """)
    total, with_data = cursor.fetchone()
    conn.close()
    
    print(f"📊 Verification:")
    print(f"   Total kicker records: {total}")
    print(f"   Records with FG data: {with_data}")
    print(f"   Percentage with data: {(with_data/total*100 if total > 0 else 0):.1f}%\n")

if __name__ == "__main__":
    response = input("This will delete and re-fetch all kicker data. Continue? (y/n): ")
    if response.lower() == 'y':
        repopulate_kicker_data()
    else:
        print("Cancelled.")
