
import sqlite3
import difflib

def get_owner_teams(db_path):
    """Gets all teams for the two owners, organized by season."""
    owner_teams = {}
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teams WHERE owner IN ('Pranesh Velmurugan', 'Kush Srivastava')")
        rows = cursor.fetchall()
        for row in rows:
            season = row['season_year']
            if season not in owner_teams:
                owner_teams[season] = {}
            owner_teams[season][row['owner']] = row['team_name']
    return owner_teams

def find_and_fix_matchups(db_path, owner_teams):
    """Finds and fixes matchups for the two owners."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        for season, teams in owner_teams.items():
            if 'Pranesh Velmurugan' not in teams or 'Kush Srivastava' not in teams:
                continue

            pranesh_team = teams['Pranesh Velmurugan']
            kush_team = teams['Kush Srivastava']

            # Find all matchups in the season that are likely between these two teams
            # This is a bit of a guess, we look for matchups where the teams are "close" to the correct names
            cursor.execute("SELECT * FROM matchups WHERE season_year = ?", (season,))
            season_matchups = cursor.fetchall()

            for matchup in season_matchups:
                matchup_id = matchup[4]
                week = matchup[3]
                home_team = matchup[5]
                away_team = matchup[8]

                # Check if this matchup is between the two owners, using fuzzy matching
                home_is_pranesh = difflib.get_close_matches(home_team, [pranesh_team], n=1, cutoff=0.6)
                home_is_kush = difflib.get_close_matches(home_team, [kush_team], n=1, cutoff=0.6)
                away_is_pranesh = difflib.get_close_matches(away_team, [pranesh_team], n=1, cutoff=0.6)
                away_is_kush = difflib.get_close_matches(away_team, [kush_team], n=1, cutoff=0.6)

                # Debugging output
                print(f"Season: {season}, Week: {week}")
                print(f"  Matchup: {home_team} vs {away_team}")
                print(f"  Correct: {pranesh_team} vs {kush_team}")
                print(f"  Scores: H_P:{home_is_pranesh}, H_K:{home_is_kush}, A_P:{away_is_pranesh}, A_K:{away_is_kush}")


                is_match = (home_is_pranesh and away_is_kush) or (home_is_kush and away_is_pranesh)

                if is_match:
                    # We found a matchup. Now, let's correct the names if they are wrong.
                    correct_home = ''
                    correct_away = ''
                    if home_is_pranesh:
                        correct_home = pranesh_team
                        correct_away = kush_team
                    else:
                        correct_home = kush_team
                        correct_away = pranesh_team

                    if home_team != correct_home or away_team != correct_away:
                        print(f"Fixing matchup in season {season}, week {week}:")
                        print(f"  Old: {home_team} vs {away_team}")
                        print(f"  New: {correct_home} vs {correct_away}")
                        cursor.execute("UPDATE matchups SET home_team = ?, away_team = ? WHERE matchup_id = ?", (correct_home, correct_away, matchup_id))

        conn.commit()

if __name__ == '__main__':
    db = '/Users/PV/PycharmProjects/FF DATA/data/espn_fantasy.db'
    teams_by_season = get_owner_teams(db)
    find_and_fix_matchups(db, teams_by_season)
    print("\nFinished fixing matchups.")
