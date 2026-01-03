"""
Update 2025 Sleeper league final standings
"""
import json

# Final standings mapping (display name → rank)
final_standings = {
    'kushagras481': 1,
    'pvels': 2,
    'tulireed': 3,  # Atul
    'georgegino': 4,  # George
    'datta69420': 5,  # Varun
    'SlingaMalinga': 6,  # Slingamaliga
    'adityam05': 7,  # adityam
    'iyerland': 8,
    'thobothehobo': 9,  # Thobothehobo
    'jacobkg189': 10,  # Jacobkg
    'mihirk': 11,  # Mihir
    'vadathemala': 12
}

# Load data
with open('data/sleeper_1257893653083332608_2025.json', 'r') as f:
    data = json.load(f)

# Create user_id to display_name mapping
users = data.get('users', [])
user_id_to_name = {u['user_id']: u['display_name'] for u in users}

# Update rosters with final rankings
rosters = data.get('rosters', [])
updated = 0

for roster in rosters:
    owner_id = roster.get('owner_id')
    display_name = user_id_to_name.get(owner_id)
    
    if display_name in final_standings:
        final_rank = final_standings[display_name]
        
        # Add final_rank to roster settings
        if 'settings' not in roster:
            roster['settings'] = {}
        
        roster['settings']['final_rank'] = final_rank
        print(f"✓ Updated {display_name}: Final Rank #{final_rank}")
        updated += 1
    else:
        print(f"⚠ Could not find {display_name} in final standings")

print(f"\n✓ Updated {updated} rosters with final rankings")

# Save updated data
with open('data/sleeper_1257893653083332608_2025.json', 'w') as f:
    json.dump(data, f, indent=2)

print("✓ Saved updated data to sleeper_1257893653083332608_2025.json")

