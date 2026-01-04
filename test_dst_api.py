#!/usr/bin/env python3
"""
Direct test of D/ST API functionality
"""
import sys
sys.path.insert(0, '/Users/PV/PycharmProjects/FF DATA')

from app import app
import json

print("Testing D/ST API endpoint...")
print("="*60)

with app.test_request_context():
    with app.test_client() as client:
        # Test 1: Jacksonville Jaguars D/ST
        print("\n1. Testing 'Jacksonville Jaguars D/ST' for season 2022...")
        response = client.get('/api/player-stats/Jacksonville%20Jaguars%20D/ST?season=2022')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   ✓ Is DST: {data.get('is_dst')}")
            print(f"   ✓ Player: {data.get('player_info', {}).get('player_display_name')}")
            print(f"   ✓ Total games: {data.get('total_games')}")
            
            if 'season_totals' in data and 2022 in data['season_totals']:
                totals = data['season_totals'][2022]
                print(f"\n   2022 Totals:")
                print(f"     - Sacks: {totals.get('def_sacks')}")
                print(f"     - Interceptions: {totals.get('def_interceptions')}")
                print(f"     - Fumbles Recovered: {totals.get('def_fumbles_recovered')}")
        else:
            print(f"   ✗ Error: {response.data.decode()[:200]}")
        
        # Test 2: Simple "JAX" (should work with D/ST detection)
        print("\n2. Testing 'JAX D/ST' for season 2022...")
        response = client.get('/api/player-stats/JAX%20D/ST?season=2022')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   ✓ Success! Total games: {data.get('total_games')}")
        else:
            print(f"   ✗ Error")

print("\n" + "="*60)
