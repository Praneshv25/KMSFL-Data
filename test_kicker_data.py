#!/usr/bin/env python3
"""
Test script to verify kicker data retrieval and storage
Tests with Justin Tucker (one of the most consistent kickers)
"""
import sys
sys.path.insert(0, '.')

import nflreadpy as nfl
import polars as pl
import sqlite3
from scrapers.nfl_stats_fetcher import NFLStatsFetcher
import config

def test_kicker_data():
    print("\n" + "="*60)
    print("KICKER DATA RETRIEVAL TEST")
    print("="*60 + "\n")
    
    # Fetch 2023 season data
    print("📊 Fetching 2023 player stats...")
    stats = nfl.load_player_stats(seasons=[2023])
    
    # Filter for kickers
    kickers = stats.filter(pl.col('position') == 'K')
    print(f"✓ Found {len(kickers)} kicker records\n")
    
    # Look for Justin Tucker (BAL kicker)
    tucker = kickers.filter(pl.col('player_display_name') == 'Justin Tucker')
    
    if len(tucker) == 0:
        print("⚠ Justin Tucker not found, trying Matt Prater...")
        tucker = kickers.filter(pl.col('player_display_name') == 'Matt Prater')
    
    if len(tucker) == 0:
        print("⚠ Specific kickers not found, using first kicker with data...")
        # Find a kicker with actual field goal attempts
        tucker = kickers.filter(pl.col('fg_att') > 0).head(1)
    
    if len(tucker) == 0:
        print("✗ No kickers found with field goal data!")
        return
    
    # Get first game
    first_game = tucker.head(1).to_dicts()[0]
    
    print(f"🏈 Testing with: {first_game['player_display_name']}")
    print(f"   Team: {first_game['team']}")
    print(f"   Week: {first_game['week']}, Season: {first_game['season']}")
    print("\n" + "-"*60)
    print("KICKING STATS FROM NFLREADPY:")
    print("-"*60)
    print(f"FG Made:     {first_game.get('fg_made', 0)}")
    print(f"FG Att:      {first_game.get('fg_att', 0)}")
    print(f"FG %:        {first_game.get('fg_pct', 0):.1%}")
    print(f"FG Long:     {first_game.get('fg_long', 0)}")
    print(f"FG 0-19:     {first_game.get('fg_made_0_19', 0)}/{first_game.get('fg_made_0_19', 0) + first_game.get('fg_missed_0_19', 0)}")
    print(f"FG 20-29:    {first_game.get('fg_made_20_29', 0)}/{first_game.get('fg_made_20_29', 0) + first_game.get('fg_missed_20_29', 0)}")
    print(f"FG 30-39:    {first_game.get('fg_made_30_39', 0)}/{first_game.get('fg_made_30_39', 0) + first_game.get('fg_missed_30_39', 0)}")
    print(f"FG 40-49:    {first_game.get('fg_made_40_49', 0)}/{first_game.get('fg_made_40_49', 0) + first_game.get('fg_missed_40_49', 0)}")
    print(f"FG 50+:      {first_game.get('fg_made_50_59', 0) + first_game.get('fg_made_60_', 0)}/{first_game.get('fg_made_50_59', 0) + first_game.get('fg_made_60_', 0) + first_game.get('fg_missed_50_59', 0) + first_game.get('fg_missed_60_', 0)}")
    print(f"XP Made:     {first_game.get('pat_made', 0)}")
    print(f"XP Att:      {first_game.get('pat_att', 0)}")
    print(f"XP %:        {first_game.get('pat_pct', 0):.1%}")
    print(f"Fantasy Pts: {first_game.get('fantasy_points_ppr', 0):.1f}")
    
    # Store in database
    print("\n" + "-"*60)
    print("STORING IN DATABASE...")
    print("-"*60)
    
    fetcher = NFLStatsFetcher()
    result = fetcher.store_weekly_stats(tucker.head(1))
    print(f"✓ Stored {result} record(s)")
    
    # Query back from database
    print("\n" + "-"*60)
    print("QUERYING FROM DATABASE:")
    print("-"*60)
    
    conn = sqlite3.connect(config.DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT player_display_name, week, season, recent_team,
               fg_made, fg_att, fg_pct, fg_long,
               fg_made_20_29, fg_made_30_39, fg_made_40_49, fg_made_50_59,
               pat_made, pat_att, pat_pct,
               fantasy_points_ppr
        FROM nfl_weekly_stats
        WHERE player_display_name = ?
        AND season = ? AND week = ?
    """, (first_game['player_display_name'], first_game['season'], first_game['week']))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        print(f"Player: {result[0]}")
        print(f"Week {result[1]}, {result[2]} ({result[3]})")
        print(f"\nFG Made:     {result[4]}")
        print(f"FG Att:      {result[5]}")
        print(f"FG %:        {result[6]:.1%}")
        print(f"FG Long:     {result[7]}")
        print(f"FG 20-29:    {result[8]}")
        print(f"FG 30-39:    {result[9]}")
        print(f"FG 40-49:    {result[10]}")
        print(f"FG 50+:      {result[11]}")
        print(f"XP Made:     {result[12]}")
        print(f"XP Att:      {result[13]}")
        print(f"XP %:        {result[14]:.1%}")
        print(f"Fantasy Pts: {result[15]:.1f}")
        
        # Verify non-zero data
        if result[4] > 0 or result[5] > 0:
            print("\n✅ SUCCESS: Kicker data has non-zero values!")
        else:
            print("\n⚠ WARNING: Kicker data is still showing zeros")
    else:
        print("✗ Failed to retrieve data from database")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_kicker_data()
