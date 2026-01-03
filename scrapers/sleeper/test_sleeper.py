"""
Test Sleeper API connection
"""
from sleeper_client import SleeperAPIClient

# Initialize client
client = SleeperAPIClient()

# Test 1: Get NFL state
print("\n1. Testing NFL State endpoint...")
nfl_state = client.get_nfl_state()
if nfl_state:
    print(f"✓ Success!")
    print(f"   Season: {nfl_state.get('season')}")
    print(f"   Week: {nfl_state.get('week')}")
    print(f"   Season Type: {nfl_state.get('season_type')}")
else:
    print("✗ Failed to get NFL state")

# Test 2: Get a known user (test with yourself)
print("\n2. Enter your Sleeper username to test:")
username = input("> ").strip()

if username:
    user = client.get_user(username)
    if user:
        print(f"✓ Found user!")
        print(f"   User ID: {user.get('user_id')}")
        print(f"   Display Name: {user.get('display_name')}")
        
        # Get leagues
        user_id = user.get('user_id')
        print(f"\n3. Fetching 2025 leagues...")
        leagues = client.get_user_leagues(user_id, "nfl", "2025")
        
        if leagues:
            print(f"✓ Found {len(leagues)} league(s):")
            for league in leagues:
                print(f"\n   League: {league.get('name')}")
                print(f"   ID: {league.get('league_id')}")
                print(f"   Status: {league.get('status')}")
                print(f"   Rosters: {league.get('total_rosters')}")
        else:
            print("   No 2025 leagues found")
    else:
        print(f"✗ User '{username}' not found")

print("\n✓ API connection successful!")

