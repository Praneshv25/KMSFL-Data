"""
Manually extract 2019 playoff data from provided screenshots and update JSON directly
"""
import json
import os

# MANUALLY EXTRACTED DATA FROM SCREENSHOTS

playoff_data = {
    "14": [
        # Matchup 1: Cheese Factory vs The Lamarvel Avengers (Week 14)
        {
            "week": 14,
            "season": 2019,
            "matchup_period_id": 14,
            "round": "Playoff Round 1 (NFL Week 14 - NFL Week 15)",
            "is_two_week_playoff": True,
            "home_team": "Cheese Factory",
            "away_team": "The Lamarvel Avengers",
            "home_score": 111.2,
            "away_score": 93.6,
            "home_total_score": 202.4,
            "away_total_score": 251.38,
            "home_roster": [
                {"slot": "QB", "player": "Ryan Tannehill", "team_pos": "Ten QB", "opp": "Oak", "status": "W 42-21", "proj": 18.7, "fpts": 27.54},
                {"slot": "RB", "player": "Dalvin Cook", "team_pos": "Min RB", "opp": "LAC", "status": "W 39-10", "proj": 19.7, "fpts": 13.5},
                {"slot": "RB", "player": "Leonard Fournette", "team_pos": "Jax RB", "opp": "Oak", "status": "W 20-16", "proj": 16.3, "fpts": 6.3},
                {"slot": "WR", "player": "Kenny Golladay", "team_pos": "Det WR", "opp": "Min", "status": "L 7-20", "proj": 9.6, "fpts": 11.8},
                {"slot": "WR", "player": "Michael Thomas", "team_pos": "NO WR", "opp": "SF", "status": "L 46-48", "proj": 12.7, "fpts": 19.4},
                {"slot": "TE", "player": "Darren Waller", "team_pos": "Oak TE", "opp": "Ten", "status": "L 21-42", "proj": 8.5, "fpts": 5.2},
                {"slot": "FLEX", "player": "Raheem Mostert", "team_pos": "SF RB", "opp": "Atl", "status": "L 22-29", "proj": 9.7, "fpts": 7.6},
                {"slot": "D/ST", "player": "Browns", "team_pos": "Cle D/ST", "opp": "Cin", "status": "W 27-19", "proj": 7.7, "fpts": 5.0},
                {"slot": "K", "player": "Matt Gay", "team_pos": "TB K", "opp": "Ind", "status": "W 38-35", "proj": 8.3, "fpts": 9.0}
            ],
            "home_bench": [
                {"slot": "Bench", "player": "Odell Beckham Jr.", "team_pos": "Cle WR", "opp": "Cin", "status": "W 27-19", "proj": 9.1, "fpts": 3.9},
                {"slot": "Bench", "player": "Le'Veon Bell", "team_pos": "NYJ RB", "opp": "Mia", "status": "W 22-21", "proj": 0.0, "fpts": 0.0},
                {"slot": "Bench", "player": "Miles Sanders", "team_pos": "Phi RB", "opp": "NYG", "status": "W 23-17", "proj": 13.4, "fpts": 6.9},
                {"slot": "Bench", "player": "Austin Hooper", "team_pos": "Atl TE", "opp": "Car", "status": "W 40-20", "proj": 8.8, "fpts": 3.2},
                {"slot": "Bench", "player": "Marlon Mack", "team_pos": "Ind RB", "opp": "TB", "status": "L 35-38", "proj": 12.1, "fpts": 9.8},
                {"slot": "Bench", "player": "Kyle Rudolph", "team_pos": "Min TE", "opp": "Det", "status": "W 20-7", "proj": 6.7, "fpts": 1.1},
                {"slot": "Bench", "player": "Darius Slayton", "team_pos": "NYG WR", "opp": "Mia", "status": "W 36-20", "proj": 9.1, "fpts": 9.1}
            ],
            "away_roster": [
                {"slot": "QB", "player": "Lamar Jackson", "team_pos": "Bal QB", "opp": "Buf", "status": "W 24-17", "proj": 22.4, "fpts": 19.8},
                {"slot": "RB", "player": "Saquon Barkley", "team_pos": "NYG RB", "opp": "Phi", "status": "L 17-23", "proj": 13.5, "fpts": 6.7},
                {"slot": "RB", "player": "Ezekiel Elliott", "team_pos": "Dal RB", "opp": "Chi", "status": "L 24-31", "proj": 15.3, "fpts": 21.3},
                {"slot": "WR", "player": "DeAndre Hopkins", "team_pos": "Hou WR", "opp": "Den", "status": "L 24-38", "proj": 10.7, "fpts": 19.2},
                {"slot": "WR", "player": "Keenan Allen", "team_pos": "LAC WR", "opp": "Jax", "status": "W 45-10", "proj": 8.8, "fpts": 7.5},
                {"slot": "TE", "player": "Hunter Henry", "team_pos": "LAC TE", "opp": "Jax", "status": "W 45-10", "proj": 8.6, "fpts": 9.3},
                {"slot": "FLEX", "player": "Josh Jacobs", "team_pos": "Oak RB", "opp": "Ten", "status": "L 21-42", "proj": 0.0, "fpts": 0.0},
                {"slot": "D/ST", "player": "Ravens", "team_pos": "Bal D/ST", "opp": "Buf", "status": "W 24-17", "proj": 6.1, "fpts": 11.0},
                {"slot": "K", "player": "Younghoe Koo", "team_pos": "Atl K", "opp": "Car", "status": "W 40-20", "proj": 8.2, "fpts": 18.0}
            ],
            "away_bench": [
                {"slot": "Bench", "player": "David Johnson", "team_pos": "Ari RB", "opp": "Cle", "status": "W 38-24", "proj": 5.0, "fpts": 11.3},
                {"slot": "Bench", "player": "Jaguars", "team_pos": "Jax D/ST", "opp": "Oak", "status": "L 16-20", "proj": 5.5, "fpts": -8.0},
                {"slot": "Bench", "player": "Mark Andrews", "team_pos": "Bal TE", "opp": "Buf", "status": "W 24-17", "proj": 8.0, "fpts": 1.4},
                {"slot": "Bench", "player": "Stefon Diggs", "team_pos": "Min WR", "opp": "Det", "status": "W 20-7", "proj": 9.4, "fpts": 9.2},
                {"slot": "Bench", "player": "Keenan Allen", "team_pos": "LAC WR", "opp": "Jax", "status": "W 45-10", "proj": 8.7, "fpts": 8.3},
                {"slot": "Bench", "player": "Joe Mixon", "team_pos": "Cin RB", "opp": "Cle", "status": "L 19-27", "proj": 11.3, "fpts": 24.6},
                {"slot": "Bench", "player": "DeAndre Washington", "team_pos": "Oak RB", "opp": "Ten", "status": "L 21-42", "proj": 11.8, "fpts": 15.6}
            ]
        },
        # Matchup 2: Lost 3 straight Fantasy finals vs Team Datta (Week 14)
        {
            "week": 14,
            "season": 2019,
            "matchup_period_id": 14,
            "round": "Playoff Round 1 (NFL Week 14 - NFL Week 15)",
            "is_two_week_playoff": True,
            "home_team": "Lost 3 straight Fantasy finals",
            "away_team": "Team Datta",
            "home_score": 106.9,
            "away_score": 113.7,
            "home_total_score": 214.6,
            "away_total_score": 212.48,
            "home_roster": [
                {"slot": "QB", "player": "Deshaun Watson", "team_pos": "Hou QB", "opp": "Den", "status": "L 24-38", "proj": 19.5, "fpts": 28.08},
                {"slot": "RB", "player": "Melvin Gordon", "team_pos": "LAC RB", "opp": "Jax", "status": "W 45-10", "proj": 13.0, "fpts": 14.4},
                {"slot": "RB", "player": "Devonta Freeman", "team_pos": "Atl RB", "opp": "Car", "status": "W 40-20", "proj": 13.2, "fpts": 15.4},
                {"slot": "WR", "player": "Davante Adams", "team_pos": "GB WR", "opp": "Wsh", "status": "W 20-15", "proj": 11.2, "fpts": 4.1},
                {"slot": "WR", "player": "Alshon Jeffery", "team_pos": "Phi WR", "opp": "NYG", "status": "W 23-17", "proj": 9.3, "fpts": 0.0},
                {"slot": "TE", "player": "Travis Kelce", "team_pos": "KC TE", "opp": "NE", "status": "W 23-16", "proj": 10.3, "fpts": 11.0},
                {"slot": "FLEX", "player": "Alvin Kamara", "team_pos": "NO RB", "opp": "SF", "status": "L 46-48", "proj": 13.0, "fpts": 2.3},
                {"slot": "D/ST", "player": "Packers", "team_pos": "GB D/ST", "opp": "Wsh", "status": "W 20-15", "proj": 7.3, "fpts": 9.0},
                {"slot": "K", "player": "Wil Lutz", "team_pos": "NO K", "opp": "SF", "status": "L 46-48", "proj": 10.3, "fpts": 13.0}
            ],
            "home_bench": [
                {"slot": "Bench", "player": "James Conner", "team_pos": "Pit RB", "opp": "Ari", "status": "W 23-17", "proj": 0.0, "fpts": 0.0},
                {"slot": "Bench", "player": "Amari Cooper", "team_pos": "Dal WR", "opp": "Chi", "status": "L 24-31", "proj": 9.8, "fpts": 14.3},
                {"slot": "Bench", "player": "Bills", "team_pos": "Buf D/ST", "opp": "Bal", "status": "L 17-24", "proj": 4.8, "fpts": 5.0},
                {"slot": "Bench", "player": "Tom Brady", "team_pos": "NE QB", "opp": "KC", "status": "L 16-23", "proj": 17.3, "fpts": 10.76},
                {"slot": "Bench", "player": "Harrison Butker", "team_pos": "KC K", "opp": "NE", "status": "W 23-16", "proj": 9.4, "fpts": 13.0},
                {"slot": "Bench", "player": "Jared Cook", "team_pos": "NO TE", "opp": "SF", "status": "L 46-48", "proj": 6.4, "fpts": 18.4},
                {"slot": "Bench", "player": "Aaron Rodgers", "team_pos": "GB QB", "opp": "Wsh", "status": "W 20-15", "proj": 18.4, "fpts": 11.4}
            ],
            "away_roster": [
                {"slot": "QB", "player": "Carson Wentz", "team_pos": "Phi QB", "opp": "NYG", "status": "W 23-17", "proj": 18.9, "fpts": 19.9},
                {"slot": "RB", "player": "Christian McCaffrey", "team_pos": "Car RB", "opp": "Atl", "status": "L 20-40", "proj": 21.7, "fpts": 13.5},
                {"slot": "RB", "player": "Mark Ingram II", "team_pos": "Bal RB", "opp": "Buf", "status": "W 24-17", "proj": 12.4, "fpts": 7.9},
                {"slot": "WR", "player": "Mike Evans", "team_pos": "TB WR", "opp": "Ind", "status": "W 38-35", "proj": 11.8, "fpts": 12.1},
                {"slot": "WR", "player": "Cooper Kupp", "team_pos": "LAR WR", "opp": "Sea", "status": "W 28-12", "proj": 8.7, "fpts": 10.5},
                {"slot": "TE", "player": "Zach Ertz", "team_pos": "Phi TE", "opp": "NYG", "status": "W 23-17", "proj": 8.9, "fpts": 21.1},
                {"slot": "FLEX", "player": "Derrick Henry", "team_pos": "Ten RB", "opp": "Oak", "status": "W 42-21", "proj": 17.3, "fpts": 22.9},
                {"slot": "D/ST", "player": "49ers", "team_pos": "SF D/ST", "opp": "NO", "status": "W 48-46", "proj": 5.8, "fpts": -8.0},
                {"slot": "K", "player": "Justin Tucker", "team_pos": "Bal K", "opp": "Buf", "status": "W 24-17", "proj": 8.2, "fpts": 6.0}
            ],
            "away_bench": [
                {"slot": "Bench", "player": "Adam Thielen", "team_pos": "Min WR", "opp": "Det", "status": "W 20-7", "proj": 0.0, "fpts": 3.0},
                {"slot": "Bench", "player": "Jacoby Brissett", "team_pos": "Ind QB", "opp": "TB", "status": "L 35-38", "proj": 17.7, "fpts": 22.64},
                {"slot": "Bench", "player": "Josh Lambo", "team_pos": "LAC K", "opp": "Jax", "status": "L 10-45", "proj": 8.8, "fpts": 4.0},
                {"slot": "Bench", "player": "Drew Brees", "team_pos": "NO QB", "opp": "SF", "status": "L 46-48", "proj": 16.1, "fpts": 40.06},
                {"slot": "Bench", "player": "Colts", "team_pos": "Ind D/ST", "opp": "TB", "status": "L 35-38", "proj": 2.8, "fpts": -4.0},
                {"slot": "Bench", "player": "Austin Ekeler", "team_pos": "LAC RB", "opp": "Jax", "status": "W 45-10", "proj": 10.2, "fpts": 27.3},
                {"slot": "Bench", "player": "Evan Engram", "team_pos": "NYG TE", "opp": "Phi", "status": "L 17-23", "proj": 0.0, "fpts": 0.0}
            ]
        },
        # Matchup 3: I have Kamikazed vs Team Saket (Week 14)
        {
            "week": 14,
            "season": 2019,
            "matchup_period_id": 14,
            "round": "Playoff Round 1 (NFL Week 14 - NFL Week 15)",
            "is_two_week_playoff": True,
            "home_team": "I have Kamikazed",
            "away_team": "Team Saket",
            "home_score": 34.4,
            "away_score": 98.6,
            "home_total_score": 151.64,
            "away_total_score": 233.02,
            "home_roster": [
                {"slot": "QB", "player": "Russell Wilson", "team_pos": "Sea QB", "opp": "LAR", "status": "L 12-28", "proj": 19.8, "fpts": 10.6},
                {"slot": "RB", "player": "Empty", "team_pos": "", "opp": "", "status": "", "proj": 0.0, "fpts": 0.0},
                {"slot": "RB", "player": "Empty", "team_pos": "", "opp": "", "status": "", "proj": 0.0, "fpts": 0.0},
                {"slot": "WR", "player": "Tyler Lockett", "team_pos": "Sea WR", "opp": "LAR", "status": "L 12-28", "proj": 8.9, "fpts": 4.3},
                {"slot": "WR", "player": "Empty", "team_pos": "", "opp": "", "status": "", "proj": 0.0, "fpts": 0.0},
                {"slot": "TE", "player": "Empty", "team_pos": "", "opp": "", "status": "", "proj": 0.0, "fpts": 0.0},
                {"slot": "FLEX", "player": "Empty", "team_pos": "", "opp": "", "status": "", "proj": 0.0, "fpts": 0.0},
                {"slot": "D/ST", "player": "Empty", "team_pos": "", "opp": "", "status": "", "proj": 0.0, "fpts": 0.0},
                {"slot": "K", "player": "Matt Prater", "team_pos": "Det K", "opp": "Min", "status": "L 7-20", "proj": 5.7, "fpts": 0.0}
            ],
            "home_bench": [
                {"slot": "Bench", "player": "George Kittle", "team_pos": "SF TE", "opp": "NO", "status": "W 48-46", "proj": 10.9, "fpts": 12.7},
                {"slot": "Bench", "player": "Julian Edelman", "team_pos": "NE WR", "opp": "KC", "status": "L 16-23", "proj": 10.8, "fpts": 16.3},
                {"slot": "Bench", "player": "Chris Carson", "team_pos": "Sea RB", "opp": "LAR", "status": "L 12-28", "proj": 12.2, "fpts": 9.1},
                {"slot": "Bench", "player": "Patriots", "team_pos": "NE D/ST", "opp": "KC", "status": "L 16-23", "proj": 3.8, "fpts": 7.0},
                {"slot": "Bench", "player": "Aaron Jones", "team_pos": "GB RB", "opp": "Wsh", "status": "W 20-15", "proj": 13.9, "fpts": 25.2},
                {"slot": "Bench", "player": "Sony Michel", "team_pos": "NE RB", "opp": "KC", "status": "L 16-23", "proj": 10.2, "fpts": 0.9},
                {"slot": "Bench", "player": "Julio Jones", "team_pos": "Atl WR", "opp": "Car", "status": "W 40-20", "proj": 11.2, "fpts": 6.6},
                {"slot": "Bench", "player": "Carlos Hyde", "team_pos": "Hou RB", "opp": "Den", "status": "L 24-38", "proj": 10.4, "fpts": 7.8},
                {"slot": "Bench", "player": "DJ Moore", "team_pos": "Car WR", "opp": "Atl", "status": "L 20-40", "proj": 10.9, "fpts": 8.1},
                {"slot": "Bench", "player": "Phillip Lindsay", "team_pos": "Den RB", "opp": "Hou", "status": "W 38-24", "proj": 11.4, "fpts": 3.2},
                {"slot": "Bench", "player": "David Montgomery", "team_pos": "Chi RB", "opp": "Dal", "status": "W 31-24", "proj": 9.9, "fpts": 4.9},
                {"slot": "Bench", "player": "Courtland Sutton", "team_pos": "Den WR", "opp": "Hou", "status": "W 38-24", "proj": 10.7, "fpts": 3.4}
            ],
            "away_roster": [
                {"slot": "QB", "player": "Patrick Mahomes", "team_pos": "KC QB", "opp": "NE", "status": "W 23-16", "proj": 18.5, "fpts": 13.92},
                {"slot": "RB", "player": "Todd Gurley II", "team_pos": "LAR RB", "opp": "Sea", "status": "W 28-12", "proj": 14.1, "fpts": 17.3},
                {"slot": "RB", "player": "Nick Chubb", "team_pos": "Cle RB", "opp": "Cin", "status": "W 27-19", "proj": 16.3, "fpts": 11.7},
                {"slot": "WR", "player": "Tyreek Hill", "team_pos": "KC WR", "opp": "NE", "status": "W 23-16", "proj": 11.1, "fpts": 7.0},
                {"slot": "WR", "player": "Chris Godwin", "team_pos": "TB WR", "opp": "Ind", "status": "W 38-35", "proj": 10.9, "fpts": 9.1},
                {"slot": "TE", "player": "Mike Gesicki", "team_pos": "Mia TE", "opp": "NYJ", "status": "L 21-22", "proj": 5.6, "fpts": 0.6},
                {"slot": "FLEX", "player": "Calvin Ridley", "team_pos": "Atl WR", "opp": "Car", "status": "W 40-20", "proj": 8.7, "fpts": 13.6},
                {"slot": "D/ST", "player": "Steelers", "team_pos": "Pit D/ST", "opp": "Ari", "status": "W 23-17", "proj": 7.4, "fpts": 20.0},
                {"slot": "K", "player": "Chris Boswell", "team_pos": "Pit K", "opp": "Ari", "status": "W 23-17", "proj": 6.0, "fpts": 11.0}
            ],
            "away_bench": [
                {"slot": "Bench", "player": "Greg Zuerlein", "team_pos": "LAR K", "opp": "Sea", "status": "W 28-12", "proj": 8.3, "fpts": 1.0},
                {"slot": "Bench", "player": "DK Metcalf", "team_pos": "Sea WR", "opp": "LAR", "status": "L 12-28", "proj": 8.8, "fpts": 9.6},
                {"slot": "Bench", "player": "Jimmy Garoppolo", "team_pos": "SF QB", "opp": "NO", "status": "W 48-46", "proj": 18.3, "fpts": 12.6},
                {"slot": "Bench", "player": "Jets", "team_pos": "NYJ D/ST", "opp": "Mia", "status": "W 22-21", "proj": 6.7, "fpts": 3.0},
                {"slot": "Bench", "player": "Saints", "team_pos": "NO D/ST", "opp": "SF", "status": "L 46-48", "proj": 6.3, "fpts": -6.0},
                {"slot": "Bench", "player": "Duke Johnson", "team_pos": "Hou RB", "opp": "Den", "status": "L 24-38", "proj": 7.6, "fpts": 4.5}
            ]
        }
    ],
    "15": [
        # Week 15 data continues with same 3 matchups...
        # I'll add this after confirming Week 14 works
    ],
    "16": [],
    "17": []
}

# Load existing 2019 data
json_file = "data/espn_league_31288798_2019_historical.json"
with open(json_file, 'r') as f:
    data = json.load(f)

# Add playoff data
for week, matchups in playoff_data.items():
    if week not in data["matchups"]:
        data["matchups"][week] = []
    data["matchups"][week].extend(matchups)

# Save
with open(json_file, 'w') as f:
    json.dump(data, f, indent=2)

print(f"✓ Added {sum(len(m) for m in playoff_data.values())} playoff matchups to {json_file}")
print("Added weeks:", list(playoff_data.keys()))

