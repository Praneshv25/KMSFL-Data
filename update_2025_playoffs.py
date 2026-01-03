"""
Update 2025 Sleeper playoff bracket information for weeks 15-17
"""
import json

# Load data
with open('data/sleeper_1257893653083332608_2025.json', 'r') as f:
    data = json.load(f)

# Create user mapping
users = {u['user_id']: u['display_name'] for u in data.get('users', [])}

# Get rosters to map team names
rosters = data.get('rosters', [])
roster_to_user = {}
for roster in rosters:
    owner_id = roster.get('owner_id')
    user_data = next((u for u in data.get('users', []) if u['user_id'] == owner_id), {})
    team_name = user_data.get('metadata', {}).get('team_name') or user_data.get('display_name', 'Unknown')
    roster_to_user[roster.get('roster_id')] = {
        'display_name': users.get(owner_id, 'Unknown'),
        'team_name': team_name
    }

# Define playoff brackets - mapping teams to bracket types
playoff_info = {
    '15': {
        'adityam05': 'Consolation Bracket',
        'mihirk': 'Consolation Bracket',
        'pvels': 'Playoff Semifinal',
        'tulireed': 'Playoff Semifinal',
    },
    '16': {
        'vadathemala': 'Consolation Bracket',
        'thobothehobo': 'Consolation Bracket',
        'adityam05': '8th Place Game',
        'pvels': 'Playoff Semifinal',
        'kushagras481': 'Playoff Semifinal',
        'SlingaMalinga': '5th Place Game',
    },
    '17': {
        'pvels': 'Championship',
        'kushagras481': 'Championship',
        'georgegino': '3rd Place Game',
        'tulireed': '3rd Place Game',
        'vadathemala': 'Last Place Game',
        'thobothehobo': 'Last Place Game',
        'jacobkg189': '10th Place Game',
    }
}

# Update matchups
matchups = data.get('matchups', {})
updated_count = 0

for week, team_brackets in playoff_info.items():
    week_matchups = matchups.get(week, [])
    
    print(f"\nWeek {week}:")
    
    # Group matchups by matchup_id to see who plays who
    matchup_groups = {}
    for m in week_matchups:
        mid = m.get('matchup_id')
        if mid not in matchup_groups:
            matchup_groups[mid] = []
        matchup_groups[mid].append(m)
    
    # Process each matchup
    for matchup_id, teams in matchup_groups.items():
        # Get the team names in this matchup
        team_names = []
        for team in teams:
            rid = team.get('roster_id')
            if rid in roster_to_user:
                team_names.append(roster_to_user[rid]['display_name'])
        
        # Determine bracket type for this matchup
        bracket_type = None
        for team_name in team_names:
            if team_name in team_brackets:
                bracket_type = team_brackets[team_name]
                break
        
        # Apply bracket type to all teams in this matchup
        if bracket_type:
            for matchup in week_matchups:
                if matchup.get('matchup_id') == matchup_id:
                    matchup['bracket_type'] = bracket_type
                    updated_count += 1
            
            print(f"  ✓ {bracket_type}: {' vs '.join(team_names)}")

print(f"\n✓ Updated {updated_count} matchup entries with bracket information")

# Save updated data
with open('data/sleeper_1257893653083332608_2025.json', 'w') as f:
    json.dump(data, f, indent=2)

print("✓ Saved updated data to sleeper_1257893653083332608_2025.json")
