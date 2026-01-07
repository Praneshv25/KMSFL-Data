

import sqlite3
import difflib

def get_correct_team_name(db_path, season, owner):
    """Gets the correct team name for a given owner and season."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT team_name FROM teams WHERE season_year = ? AND owner = ?", (season, owner))
        result = cursor.fetchone()
        return result[0] if result else None

def find_owner_of_team(db_path, season, team_name):
    """Finds the owner of a team in a given season."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # First, try an exact match
        cursor.execute("SELECT owner FROM teams WHERE season_year = ? AND team_name = ?", (season, team_name))
        result = cursor.fetchone()
        if result:
            return result['owner']

        # If no exact match, try to find the closest team name for that season and get the owner
        cursor.execute("SELECT team_name, owner FROM teams WHERE season_year = ?", (season,))
        all_teams_for_season = cursor.fetchall()
        
        team_names = [row['team_name'] for row in all_teams_for_season]
        close_matches = difflib.get_close_matches(team_name, team_names, n=1, cutoff=0.6)
        
        if close_matches:
            for row in all_teams_for_season:
                if row['team_name'] == close_matches[0]:
                    return row['owner']
    return None

def clean_matchup_data():
    """
    Cleans the matchups table by correcting inconsistent team names.
    """
    db_path = '/Users/PV/PycharmProjects/FF DATA/data/espn_fantasy.db'
    
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get all matchups
        cursor.execute("SELECT * FROM matchups")
        all_matchups = cursor.fetchall()

        # Get all teams
        cursor.execute("SELECT * FROM teams")
        all_teams = cursor.fetchall()
        
        teams_by_season = {}
        for team in all_teams:
            season = team['season_year']
            if season not in teams_by_season:
                teams_by_season[season] = []
            teams_by_season[season].append(dict(team))

        updates_to_make = []

        for matchup in all_matchups:
            season = matchup['season_year']
            home_team_name = matchup['home_team']
            away_team_name = matchup['away_team']

            if season not in teams_by_season:
                print(f"Warning: No teams found for season {season}. Skipping matchup.")
                continue

            season_teams = teams_by_season[season]
            season_team_names = [t['team_name'] for t in season_teams]

            # Check home team
            if home_team_name not in season_team_names:
                close_matches = difflib.get_close_matches(home_team_name, season_team_names, n=1, cutoff=0.6)
                if close_matches:
                    correct_name = close_matches[0]
                    updates_to_make.append({
                        "matchup_id": matchup['matchup_id'],
                        "column": "home_team",
                        "old_name": home_team_name,
                        "new_name": correct_name
                    })

            # Check away team
            if away_team_name not in season_team_names:
                close_matches = difflib.get_close_matches(away_team_name, season_team_names, n=1, cutoff=0.6)
                if close_matches:
                    correct_name = close_matches[0]
                    updates_to_make.append({
                        "matchup_id": matchup['matchup_id'],
                        "column": "away_team",
                        "old_name": away_team_name,
                        "new_name": correct_name
                    })

        if not updates_to_make:
            print("No anomalies found. Database is clean.")
            return

        print(f"Found {len(updates_to_make)} anomalies to fix.")
        for update in updates_to_make:
            try:
                print(f"  - Matchup ID {update['matchup_id']}: Correcting {update['column']} from '{update['old_name']}' to '{update['new_name']}'")
                cursor.execute(f"UPDATE matchups SET {update['column']} = ? WHERE matchup_id = ?", (update['new_name'], update['matchup_id']))
            except sqlite3.IntegrityError:
                print(f"    - IntegrityError: Corrected matchup already exists. Deleting duplicate matchup ID {update['matchup_id']}.")
                cursor.execute("DELETE FROM matchups WHERE matchup_id = ?", (update['matchup_id'],))
        
        conn.commit()
        print("\nDatabase cleaning complete.")

if __name__ == '__main__':
    clean_matchup_data()

