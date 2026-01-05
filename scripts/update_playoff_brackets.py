#!/usr/bin/env python3
"""
Script to update playoff bracket types and rounds in the matchups table.
Uses team_ownership table to map owners to team names for each season.
"""

import sqlite3
import sys

# Database connection
DB_PATH = '../data/espn_fantasy.db'

# Playoff structure from docs/playoff_structure.md
PLAYOFF_STRUCTURE = {
    2019: {
        (14, 15): {  # Two-week Round 1
            'Championship': {
                'Round 1': [
                    ('Atul Iyengar', 'Pranesh Velmurugan'),
                    ('Vinay Subramanian', 'Varun Datta')
                ]
            },
            'Consolation': {
                'Round 1': [('Aditya Mishra', 'Saket Gaj')]
            }
        },
        (16, 17): {  # Two-week Round 2
            'Championship': {
                'Championship': [('Vinay Subramanian', 'Pranesh Velmurugan')]
            },
            "Winner's Consolation": {
                '3rd Place': [('Atul Iyengar', 'Varun Datta')]
            },
            'Consolation': {
                'Round 2': [('Aditya Mishra', 'Saket Gaj')]
            }
        }
    },
    2020: {
        14: {
            'Championship': {
                'Round 1': [
                    ('Pranesh Velmurugan', 'Atul Iyengar'),
                    ('Rohit Iyer', 'Saket Gaj'),  # Rohit, Ved
                    ('VED ANUMALA', 'Saket Gaj'),  # Rohit, Ved (co-owned)
                ]
            },
            'Consolation': {
                'Round 1': [('Varun Datta', 'Vinay Subramanian')]
            }
        },
        15: {
            'Championship': {
                'Round 2': [
                    ('Atul Iyengar', 'Kush Srivastava'),
                    ('Rohit Iyer', 'Aditya Mishra'),
                    ('VED ANUMALA', 'Aditya Mishra'),
                ]
            },
            "Winner's Consolation": {
                'Round 2': [('Pranesh Velmurugan', 'Saket Gaj')]
            },
            'Consolation': {
                'Round 2': [('Varun Datta', 'Vinay Subramanian')]
            }
        },
        16: {
            'Championship': {
                'Championship': [
                    ('Rohit Iyer', 'Atul Iyengar'),
                    ('VED ANUMALA', 'Atul Iyengar'),
                ]
            },
            "Winner's Consolation": {
                'Round 3': [
                    ('Pranesh Velmurugan', 'Saket Gaj'),
                    ('Aditya Mishra', 'Kush Srivastava')
                ]
            },
            'Consolation': {
                'Round 3': [('Varun Datta', 'Vinay Subramanian')]
            }
        }
    },
    2021: {
        15: {
            'Championship': {
                'Round 1': [
                    ('Mihir Kondapalli', 'Pranesh Velmurugan'),
                    ('Aditya Mishra', 'Varun Datta')
                ]
            },
            'Consolation': {
                'Round 1': [
                    ('Vinay Subramanian', 'Rohit Iyer'),
                    ('Vinay Subramanian', 'VED ANUMALA'),
                ]
            }
        },
        16: {
            'Championship': {
                'Round 2': [
                    ('Aditya Mishra', 'Kush Srivastava'),
                    ('Mihir Kondapalli', 'Atul Iyengar')
                ]
            },
            "Winner's Consolation": {
                'Round 2': [('Varun Datta', 'Pranesh Velmurugan')]
            },
            'Consolation': {
                'Round 2': [
                    ('Vinay Subramanian', 'Rohit Iyer'),
                    ('Vinay Subramanian', 'VED ANUMALA'),
                ]
            }
        },
        17: {
            'Championship': {
                'Championship': [('Aditya Mishra', 'Atul Iyengar')]
            },
            "Winner's Consolation": {
                '3rd Place': [('Varun Datta', 'Pranesh Velmurugan')],
                '5th Place': [('Mihir Kondapalli', 'Kush Srivastava')]
            },
            'Consolation': {
                'Round 3': [
                    ('Vinay Subramanian', 'Rohit Iyer'),
                    ('Vinay Subramanian', 'VED ANUMALA'),
                ]
            }
        }
    },
    2022: {
        15: {
            'Championship': {
                'Round 1': [
                    ('Saket Gaj', 'Pranesh Velmurugan'),
                    ('VED ANUMALA', 'Vinay Subramanian')
                ]
            },
            'Consolation': {
                'Round 1': [
                    ('Aditya Mishra', 'Mihir Kondapalli'),
                    ('Kush Srivastava', 'Rohit Iyer')
                ]
            }
        },
        16: {
            'Championship': {
                'Round 2': [
                    ('Saket Gaj', 'Varun Datta'),
                    ('Vinay Subramanian', 'Atul Iyengar')
                ]
            },
            "Winner's Consolation": {
                'Round 2': [('VED ANUMALA', 'Pranesh Velmurugan')]
            },
            'Consolation': {
                'Round 2': [
                    ('Rohit Iyer', 'Mihir Kondapalli'),
                    ('Kush Srivastava', 'Aditya Mishra')
                ]
            }
        },
        17: {
            'Championship': {
                'Championship': [('Saket Gaj', 'Vinay Subramanian')]
            },
            "Winner's Consolation": {
                '3rd Place': [('VED ANUMALA', 'Pranesh Velmurugan')],
                '5th Place': [('Atul Iyengar', 'Varun Datta')]
            },
            'Consolation': {
                '7th Place': [('Mihir Kondapalli', 'Kush Srivastava')],
                '8th Place': [('Rohit Iyer', 'Aditya Mishra')]
            }
        }
    },
    2023: {
        15: {
            'Championship': {
                'Round 1': [
                    ('Pranesh Velmurugan', 'Varun Datta'),
                    ('Aditya Mishra', 'Rohit Iyer')
                ]
            },
            'Consolation': {
                'Round 1': [
                    ('Vinay Subramanian', 'Atul Iyengar'),
                    ('Mihir Kondapalli', 'VED ANUMALA')
                ]
            }
        },
        16: {
            'Championship': {
                'Round 2': [
                    ('Pranesh Velmurugan', 'Saket Gaj'),
                    ('Aditya Mishra', 'Kush Srivastava')
                ]
            },
            "Winner's Consolation": {
                'Round 2': [('Rohit Iyer', 'Varun Datta')]
            },
            'Consolation': {
                'Round 2': [
                    ('Mihir Kondapalli', 'Atul Iyengar'),
                    ('VED ANUMALA', 'Vinay Subramanian')
                ]
            }
        },
        17: {
            'Championship': {
                'Championship': [('Pranesh Velmurugan', 'Kush Srivastava')]
            },
            "Winner's Consolation": {
                '3rd Place': [('Aditya Mishra', 'Saket Gaj')],
                '5th Place': [('Rohit Iyer', 'Varun Datta')]
            },
            'Consolation': {
                '7th Place': [('Vinay Subramanian', 'Atul Iyengar')],
                '8th Place': [('Mihir Kondapalli', 'VED ANUMALA')]
            }
        }
    },
    2024: {
        15: {
            'Championship': {
                'Round 1': [
                    ('Kush Srivastava', 'Saket Gaj'),
                    ('Mihir Kondapalli', 'Aditya Mishra')
                ]
            },
            'Consolation': {
                'Round 1': [
                    ('Varun Datta', 'Pranesh Velmurugan'),
                    ('Rohit Iyer', 'VED ANUMALA')
                ]
            }
        },
        16: {
            'Championship': {
                'Round 2': [
                    ('Saket Gaj', 'Atul Iyengar'),
                    ('Mihir Kondapalli', 'Vinay Subramanian')
                ]
            },
            "Winner's Consolation": {
                'Round 2': [('Kush Srivastava', 'Aditya Mishra')]
            },
            'Consolation': {
                'Round 2': [
                    ('Pranesh Velmurugan', 'VED ANUMALA'),
                    ('Varun Datta', 'Rohit Iyer')
                ]
            }
        },
        17: {
            'Championship': {
                'Championship': [('Vinay Subramanian', 'Atul Iyengar')]
            },
            "Winner's Consolation": {
                '3rd Place': [('Mihir Kondapalli', 'Saket Gaj')],
                '5th Place': [('Kush Srivastava', 'Aditya Mishra')]
            },
            'Consolation': {
                '7th Place': [('Varun Datta', 'Pranesh Velmurugan')],
                '8th Place': [('Rohit Iyer', 'VED ANUMALA')]
            }
        }
    },
    2025: {
        15: {
            'Championship': {
                'Round 1': [
                    ('Pranesh Velmurugan', 'Vinay Subramanian'),
                    ('Varun Datta', 'Atul Iyengar')
                ]
            },
            'Toilet Bowl': {
                'Round 1': [
                    ('Jacob Gino', 'Aditya Mishra'),
                    ('Rohit Iyer', 'Mihir Kondapalli')
                ]
            }
        },
        16: {
            'Championship': {
                'Round 2': [
                    ('George Gino', 'Pranesh Velmurugan'),
                    ('Kush Srivastava', 'Atul Iyengar')
                ]
            },
            "Winner's Consolation": {
                '5th Place': [('Vinay Subramanian', 'Varun Datta')]
            },
            'Consolation': {
                'Round 2': [
                    ('VED ANUMALA', 'Jacob Gino'),
                    ('Sohan', 'Mihir Kondapalli')
                ],
                '8th Place': [('Aditya Mishra', 'Rohit Iyer')]
            }
        },
        17: {
            'Championship': {
                'Championship': [('Kush Srivastava', 'Pranesh Velmurugan')]
            },
            "Winner's Consolation": {
                '3rd Place': [('Atul Iyengar', 'George Gino')]
            },
            'Consolation': {
                '7th Place': [('VED ANUMALA', 'Mihir Kondapalli')],
                '10th Place': [('Jacob Gino', 'Sohan')]
            }
        }
    }
}


def get_team_name(conn, owner_name, season_year):
    """Get team name for a given owner and season."""
    cursor = conn.cursor()
    query = """
        SELECT DISTINCT t.team_name 
        FROM team_ownership tow
        JOIN teams t ON t.id = tow.team_id
        WHERE tow.owner = ? AND t.season_year = ?
        LIMIT 1
    """
    result = cursor.execute(query, (owner_name, season_year)).fetchone()
    if result:
        return result[0]
    else:
        print(f"WARNING: No team found for owner '{owner_name}' in season {season_year}")
        return None


def update_playoffs(conn):
    """Update playoff matchups with bracket_type and round information."""
    cursor = conn.cursor()
    updates_made = 0
    
    for season_year, playoff_weeks in PLAYOFF_STRUCTURE.items():
        print(f"\nProcessing {season_year} season...")
        
        for weeks, brackets in playoff_weeks.items():
            # Handle both single week and tuple of weeks (for 2019)
            week_list = weeks if isinstance(weeks, tuple) else (weeks,)
            
            for bracket_type, rounds in brackets.items():
                for round_name, matchups in rounds.items():
                    for owner1, owner2 in matchups:
                        # Get actual team names
                        team1 = get_team_name(conn, owner1, season_year)
                        team2 = get_team_name(conn, owner2, season_year)
                        
                        if not team1 or not team2:
                            continue
                        
                        # Update matchup
                        for week in week_list:
                            update_query = """
                                UPDATE matchups 
                                SET bracket_type = ?, round = ?
                                WHERE season_year = ? AND week = ?
                                AND (
                                    (home_team = ? AND away_team = ?)
                                    OR (home_team = ? AND away_team = ?)
                                )
                            """
                            result = cursor.execute(
                                update_query,
                                (bracket_type, round_name, season_year, week, 
                                 team1, team2, team2, team1)
                            )
                            
                            if result.rowcount > 0:
                                updates_made += result.rowcount
                                print(f"  ✓ Updated: {team1} vs {team2} (Week {week}, {bracket_type}, {round_name})")
    
    conn.commit()
    return updates_made


def main():
    try:
        conn = sqlite3.connect(DB_PATH)
        print("Connected to database successfully")
        print("="*80)
        
        updates = update_playoffs(conn)
        
        print("="*80)
        print(f"\n✅ Successfully updated {updates} playoff matchups!")
        
        # Show summary statistics
        cursor = conn.cursor()
        summary = cursor.execute("""
            SELECT season_year, bracket_type, COUNT(*) as count
            FROM matchups
            WHERE bracket_type IS NOT NULL AND bracket_type != ''
            GROUP BY season_year, bracket_type
            ORDER BY season_year, bracket_type
        """).fetchall()
        
        print("\nSummary of labeled playoff matchups:")
        print("-" * 60)
        current_season = None
        for season, bracket, count in summary:
            if season != current_season:
                print(f"\n{season}:")
                current_season = season
            print(f"  {bracket}: {count} matchups")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
