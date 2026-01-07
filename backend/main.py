"""
FastAPI Backend for The Elemental League
Serves fantasy football data from SQLite database
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from pydantic import BaseModel

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "espn_fantasy.db"

app = FastAPI(
    title="The Elemental League API",
    description="Fantasy Football History API",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Database utilities
# ============================================

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def rows_to_dicts(rows) -> List[dict]:
    """Convert sqlite3.Row objects to dictionaries"""
    return [dict(row) for row in rows]

# ============================================
# Pydantic Models
# ============================================

class Team(BaseModel):
    team_name: str
    owner: str
    rank: Optional[int] = None
    wins: int
    losses: int
    ties: int = 0
    points_for: float
    points_against: float
    season_year: int

class Champion(BaseModel):
    year: int
    team: str
    owner: str
    record: str
    points_for: float

class Matchup(BaseModel):
    week: int
    home_team: str
    home_score: float
    away_team: str
    away_score: float
    bracket_type: Optional[str] = None

class Manager(BaseModel):
    name: str
    all_time_record: str
    total_wins: int
    total_losses: int
    championships: int
    playoff_appearances: int
    avg_points_for: float
    seasons_played: int

class DraftPick(BaseModel):
    round: int
    pick: int
    overall_pick: int
    team: str
    player_name: str
    position: str

class Record(BaseModel):
    category: str
    value: str
    holder: str
    year: int

# ============================================
# API Endpoints
# ============================================

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "database": str(DB_PATH)}

@app.get("/api/seasons")
def get_seasons():
    """Get list of available seasons"""
    with get_db() as conn:
        cursor = conn.execute("SELECT DISTINCT season_year FROM teams ORDER BY season_year DESC")
        seasons = [row[0] for row in cursor.fetchall()]
    return {"seasons": seasons}

@app.get("/api/teams")
def get_teams(year: int = Query(..., description="Season year")):
    """Get team standings for a season"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT team_name, owner, rank, wins, losses, ties, points_for, points_against, season_year
            FROM teams 
            WHERE season_year = ?
            ORDER BY rank ASC
        """, (year,))
        teams = rows_to_dicts(cursor.fetchall())
    return {"year": year, "teams": teams}

@app.get("/api/champions")
def get_champions():
    """Get all champions by year"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT season_year, team_name, owner, wins, losses, points_for
            FROM teams 
            WHERE rank = 1
            ORDER BY season_year DESC
        """)
        rows = cursor.fetchall()
    
    champions = []
    for row in rows:
        champions.append({
            "year": row["season_year"],
            "team": row["team_name"],
            "owner": row["owner"],
            "record": f"{row['wins']}-{row['losses']}",
            "points_for": row["points_for"]
        })
    return {"champions": champions}

@app.get("/api/matchups")
def get_matchups(
    year: int = Query(..., description="Season year"),
    week: Optional[int] = Query(None, description="Week number (optional)")
):
    """Get matchups for a season, optionally filtered by week"""
    with get_db() as conn:
        if week:
            cursor = conn.execute("""
                SELECT week, home_team, home_score, away_team, away_score, bracket_type
                FROM matchups 
                WHERE season_year = ? AND week = ?
                ORDER BY matchup_id
            """, (year, week))
        else:
            cursor = conn.execute("""
                SELECT week, home_team, home_score, away_team, away_score, bracket_type
                FROM matchups 
                WHERE season_year = ?
                ORDER BY week, matchup_id
            """, (year,))
        matchups = rows_to_dicts(cursor.fetchall())
    
    # Get max week for this year
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT MAX(week) as max_week FROM matchups WHERE season_year = ?
        """, (year,))
        max_week = cursor.fetchone()["max_week"] or 0
    
    return {"year": year, "week": week, "max_week": max_week, "matchups": matchups}

@app.get("/api/managers")
def get_managers():
    """Get all manager profiles with aggregate stats"""
    with get_db() as conn:
        # Playoff cutoff: 4 teams in 2019, 6 teams in 2020+
        cursor = conn.execute("""
            SELECT 
                owner,
                SUM(wins) as total_wins,
                SUM(losses) as total_losses,
                ROUND(AVG(points_for), 1) as avg_points_for,
                COUNT(DISTINCT season_year) as seasons_played,
                SUM(CASE WHEN rank = 1 THEN 1 ELSE 0 END) as championships,
                SUM(CASE 
                    WHEN season_year = 2019 AND rank <= 4 THEN 1
                    WHEN season_year > 2019 AND rank <= 6 THEN 1
                    ELSE 0 
                END) as playoff_appearances
            FROM teams
            GROUP BY owner
            ORDER BY total_wins DESC
        """)
        rows = cursor.fetchall()
    
    managers = []
    for row in rows:
        wins = row["total_wins"]
        losses = row["total_losses"]
        managers.append({
            "name": row["owner"],
            "all_time_record": f"{wins}-{losses}",
            "total_wins": wins,
            "total_losses": losses,
            "championships": row["championships"],
            "playoff_appearances": row["playoff_appearances"],
            "avg_points_for": row["avg_points_for"],
            "seasons_played": row["seasons_played"]
        })
    return {"managers": managers}

@app.get("/api/manager/{name}")
def get_manager(name: str):
    """Get detailed stats for a specific manager"""
    with get_db() as conn:
        # Get season history
        cursor = conn.execute("""
            SELECT season_year, team_name, rank, wins, losses, points_for, points_against
            FROM teams
            WHERE owner = ?
            ORDER BY season_year DESC
        """, (name,))
        seasons = rows_to_dicts(cursor.fetchall())
        
        if not seasons:
            raise HTTPException(status_code=404, detail=f"Manager '{name}' not found")
        
        # Aggregate stats (playoff cutoff: 4 teams in 2019, 6 teams 2020+)
        total_wins = sum(s["wins"] for s in seasons)
        total_losses = sum(s["losses"] for s in seasons)
        championships = sum(1 for s in seasons if s["rank"] == 1)
        playoffs = sum(1 for s in seasons if (s["season_year"] == 2019 and s["rank"] <= 4) or (s["season_year"] > 2019 and s["rank"] <= 6))
        avg_pf = sum(s["points_for"] for s in seasons) / len(seasons)
        
    return {
        "name": name,
        "all_time_record": f"{total_wins}-{total_losses}",
        "total_wins": total_wins,
        "total_losses": total_losses,
        "championships": championships,
        "playoff_appearances": playoffs,
        "avg_points_for": round(avg_pf, 1),
        "seasons_played": len(seasons),
        "season_history": seasons
    }

@app.get("/api/draft")
def get_draft(year: int = Query(..., description="Season year")):
    """Get draft picks for a season"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT round, pick, overall_pick, team, player_name, position, nfl_team
            FROM draft_picks
            WHERE season_year = ?
            ORDER BY overall_pick
        """, (year,))
        picks = rows_to_dicts(cursor.fetchall())
    return {"year": year, "picks": picks}

@app.get("/api/records")
def get_records():
    """Get all-time records"""
    records = []
    
    with get_db() as conn:
        # Highest single game score - get all tied holders
        cursor = conn.execute("""
            WITH max_score AS (
                SELECT MAX(score) as max_val FROM (
                    SELECT home_score as score FROM matchups
                    UNION ALL
                    SELECT away_score FROM matchups
                )
            )
            SELECT DISTINCT t.owner, m.home_score as score, m.season_year
            FROM matchups m
            JOIN teams t ON m.home_team = t.team_name AND m.season_year = t.season_year
            WHERE m.home_score = (SELECT max_val FROM max_score)
            UNION
            SELECT DISTINCT t.owner, m.away_score, m.season_year
            FROM matchups m
            JOIN teams t ON m.away_team = t.team_name AND m.season_year = t.season_year
            WHERE m.away_score = (SELECT max_val FROM max_score)
        """)
        rows = cursor.fetchall()
        if rows:
            holders = list(set(row["owner"] for row in rows if row["owner"]))
            years = list(set(str(row["season_year"]) for row in rows))
            records.append({
                "category": "Highest Single Game Score",
                "value": str(rows[0]["score"]),
                "holder": ", ".join(holders),
                "year": ", ".join(years) if len(years) > 1 else years[0]
            })
        
        # Lowest single game score - get all tied holders
        cursor = conn.execute("""
            WITH min_score AS (
                SELECT MIN(score) as min_val FROM (
                    SELECT home_score as score FROM matchups WHERE home_score > 0
                    UNION ALL
                    SELECT away_score FROM matchups WHERE away_score > 0
                )
            )
            SELECT DISTINCT t.owner, m.home_score as score, m.season_year
            FROM matchups m
            JOIN teams t ON m.home_team = t.team_name AND m.season_year = t.season_year
            WHERE m.home_score = (SELECT min_val FROM min_score)
            UNION
            SELECT DISTINCT t.owner, m.away_score, m.season_year
            FROM matchups m
            JOIN teams t ON m.away_team = t.team_name AND m.season_year = t.season_year
            WHERE m.away_score = (SELECT min_val FROM min_score)
        """)
        rows = cursor.fetchall()
        if rows:
            holders = list(set(row["owner"] for row in rows if row["owner"]))
            years = list(set(str(row["season_year"]) for row in rows))
            records.append({
                "category": "Lowest Single Game Score",
                "value": str(rows[0]["score"]),
                "holder": ", ".join(holders),
                "year": ", ".join(years) if len(years) > 1 else years[0]
            })
        
        # Highest avg points per game in a season - get all tied holders
        cursor = conn.execute("""
            WITH season_ppg AS (
                SELECT owner, season_year, 
                       ROUND(points_for / (wins + losses), 2) as avg_ppg,
                       wins, losses
                FROM teams
                WHERE (wins + losses) > 0
            )
            SELECT owner, avg_ppg, season_year
            FROM season_ppg
            WHERE avg_ppg = (SELECT MAX(avg_ppg) FROM season_ppg)
        """)
        rows = cursor.fetchall()
        if rows:
            holders = list(set(row["owner"] for row in rows))
            years = list(set(str(row["season_year"]) for row in rows))
            records.append({
                "category": "Highest Avg PPG (Season)",
                "value": f"{rows[0]['avg_ppg']:.2f}",
                "holder": ", ".join(holders),
                "year": ", ".join(years) if len(years) > 1 else years[0]
            })
        
        # Best regular season record - get all tied holders
        cursor = conn.execute("""
            WITH best AS (
                SELECT MAX(wins) as max_wins FROM teams
            )
            SELECT owner, wins, losses, season_year
            FROM teams
            WHERE wins = (SELECT max_wins FROM best)
            AND losses = (SELECT MIN(losses) FROM teams WHERE wins = (SELECT max_wins FROM best))
        """)
        rows = cursor.fetchall()
        if rows:
            holders = list(set(row["owner"] for row in rows))
            years = list(set(str(row["season_year"]) for row in rows))
            records.append({
                "category": "Best Regular Season Record",
                "value": f"{rows[0]['wins']}-{rows[0]['losses']}",
                "holder": ", ".join(holders),
                "year": ", ".join(years) if len(years) > 1 else years[0]
            })
        
        # Most championships - get ALL tied owners
        cursor = conn.execute("""
            WITH champ_counts AS (
                SELECT owner, COUNT(*) as titles
                FROM teams WHERE rank = 1
                GROUP BY owner
            ),
            max_titles AS (
                SELECT MAX(titles) as max_val FROM champ_counts
            )
            SELECT owner, titles
            FROM champ_counts
            WHERE titles = (SELECT max_val FROM max_titles)
        """)
        rows = cursor.fetchall()
        if rows:
            holders = [row["owner"] for row in rows]
            records.append({
                "category": "Most Championships",
                "value": str(rows[0]["titles"]),
                "holder": ", ".join(holders),
                "year": "All-Time"
            })
        
        # Most playoff appearances - get ALL tied owners (4 teams in 2019, 6 teams 2020+)
        cursor = conn.execute("""
            WITH playoff_counts AS (
                SELECT owner, SUM(CASE 
                    WHEN season_year = 2019 AND rank <= 4 THEN 1
                    WHEN season_year > 2019 AND rank <= 6 THEN 1
                    ELSE 0 
                END) as appearances
                FROM teams
                GROUP BY owner
            ),
            max_appearances AS (
                SELECT MAX(appearances) as max_val FROM playoff_counts
            )
            SELECT owner, appearances
            FROM playoff_counts
            WHERE appearances = (SELECT max_val FROM max_appearances)
        """)
        rows = cursor.fetchall()
        if rows:
            holders = [row["owner"] for row in rows]
            records.append({
                "category": "Most Playoff Appearances",
                "value": str(rows[0]["appearances"]),
                "holder": ", ".join(holders),
                "year": "All-Time"
            })
    
    return {"records": records}

@app.get("/api/head-to-head")
def get_head_to_head(manager1: str = Query(...), manager2: str = Query(...)):
    """Get head-to-head record between two managers"""
    with get_db() as conn:
        # Find all matchups between these two managers
        cursor = conn.execute("""
            SELECT 
                m.season_year, m.week, m.home_team, m.away_team, m.home_score, m.away_score,
                t1.owner as home_owner, t2.owner as away_owner
            FROM matchups m
            JOIN teams t1 ON m.home_team = t1.team_name AND m.season_year = t1.season_year
            JOIN teams t2 ON m.away_team = t2.team_name AND m.season_year = t2.season_year
            WHERE (t1.owner = ? AND t2.owner = ?) OR (t1.owner = ? AND t2.owner = ?)
            ORDER BY m.season_year DESC, m.week DESC
        """, (manager1, manager2, manager2, manager1))
        matchups = cursor.fetchall()
    
    manager1_wins = 0
    manager2_wins = 0
    games = []
    
    for m in matchups:
        home_owner = m["home_owner"]
        away_owner = m["away_owner"]
        home_score = m["home_score"]
        away_score = m["away_score"]
        
        if home_score > away_score:
            winner = home_owner
        else:
            winner = away_owner
            
        if winner == manager1:
            manager1_wins += 1
        else:
            manager2_wins += 1
            
        games.append({
            "year": m["season_year"],
            "week": m["week"],
            "home_team": m["home_team"],
            "away_team": m["away_team"],
            "home_score": home_score,
            "away_score": away_score,
            "winner": winner
        })
    
    return {
        "manager1": manager1,
        "manager2": manager2,
        "manager1_wins": manager1_wins,
        "manager2_wins": manager2_wins,
        "total_games": len(games),
        "games": games
    }

@app.get("/api/rivalries/{manager_name}")
def get_rivalries(manager_name: str):
    """Get head-to-head records against all opponents for a manager"""
    with get_db() as conn:
        # Get all matchups involving this manager
        cursor = conn.execute("""
            SELECT 
                m.season_year, m.home_team, m.away_team, m.home_score, m.away_score,
                t1.owner as home_owner, t2.owner as away_owner
            FROM matchups m
            JOIN teams t1 ON m.home_team = t1.team_name AND m.season_year = t1.season_year
            JOIN teams t2 ON m.away_team = t2.team_name AND m.season_year = t2.season_year
            WHERE t1.owner = ? OR t2.owner = ?
        """, (manager_name, manager_name))
        matchups = cursor.fetchall()
    
    # Calculate record against each opponent
    opponents = {}
    for m in matchups:
        home_owner = m["home_owner"]
        away_owner = m["away_owner"]
        home_score = m["home_score"]
        away_score = m["away_score"]
        
        if home_owner == manager_name:
            opponent = away_owner
            won = home_score > away_score
        else:
            opponent = home_owner
            won = away_score > home_score
        
        if opponent not in opponents:
            opponents[opponent] = {"wins": 0, "losses": 0}
        
        if won:
            opponents[opponent]["wins"] += 1
        else:
            opponents[opponent]["losses"] += 1
    
    # Convert to list and sort by total games
    rivalries = []
    for opp, record in opponents.items():
        total = record["wins"] + record["losses"]
        rivalries.append({
            "opponent": opp,
            "wins": record["wins"],
            "losses": record["losses"],
            "total_games": total,
            "win_pct": round(record["wins"] / total * 100, 1) if total > 0 else 0
        })
    
    rivalries.sort(key=lambda x: x["total_games"], reverse=True)
    
    return {"manager": manager_name, "rivalries": rivalries}

@app.get("/api/weekly-results/{manager_name}")
def get_weekly_results(manager_name: str):
    """Get weekly win/loss results for a manager across all seasons"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT 
                m.season_year, m.week, m.home_team, m.away_team, 
                m.home_score, m.away_score,
                t1.owner as home_owner, t2.owner as away_owner
            FROM matchups m
            JOIN teams t1 ON m.home_team = t1.team_name AND m.season_year = t1.season_year
            JOIN teams t2 ON m.away_team = t2.team_name AND m.season_year = t2.season_year
            WHERE t1.owner = ? OR t2.owner = ?
            ORDER BY m.season_year DESC, m.week ASC
        """, (manager_name, manager_name))
        matchups = cursor.fetchall()
    
    results = []
    for m in matchups:
        home_owner = m["home_owner"]
        away_owner = m["away_owner"]
        home_score = m["home_score"]
        away_score = m["away_score"]
        
        if home_owner == manager_name:
            won = home_score > away_score
            score = home_score
            opponent_score = away_score
        else:
            won = away_score > home_score
            score = away_score
            opponent_score = home_score
        
        results.append({
            "season_year": m["season_year"],
            "week": m["week"],
            "result": "W" if won else "L",
            "score": score,
            "opponent_score": opponent_score
        })
    
    return {"manager": manager_name, "weekly_results": results}

@app.get("/api/luck")
def get_luck_rankings():
    """Get luck factor for all managers (expected wins vs actual wins)"""
    with get_db() as conn:
        # Get all matchups with owner info
        cursor = conn.execute("""
            SELECT 
                m.season_year, m.week, m.home_score, m.away_score,
                t1.owner as home_owner, t2.owner as away_owner
            FROM matchups m
            JOIN teams t1 ON m.home_team = t1.team_name AND m.season_year = t1.season_year
            JOIN teams t2 ON m.away_team = t2.team_name AND m.season_year = t2.season_year
        """)
        matchups = cursor.fetchall()
        
        # Get all scores for each week to calculate expected wins
        cursor2 = conn.execute("""
            SELECT 
                m.season_year, m.week, m.home_score as score, t.owner
            FROM matchups m
            JOIN teams t ON m.home_team = t.team_name AND m.season_year = t.season_year
            UNION ALL
            SELECT 
                m.season_year, m.week, m.away_score, t.owner
            FROM matchups m
            JOIN teams t ON m.away_team = t.team_name AND m.season_year = t.season_year
        """)
        all_scores = cursor2.fetchall()
    
    # Group scores by week
    weekly_scores = {}
    for s in all_scores:
        key = (s["season_year"], s["week"])
        if key not in weekly_scores:
            weekly_scores[key] = []
        weekly_scores[key].append({"owner": s["owner"], "score": s["score"]})
    
    # Calculate expected wins (how many teams each team would beat that week)
    expected_wins = {}
    actual_wins = {}
    
    for (year, week), scores in weekly_scores.items():
        scores_sorted = sorted(scores, key=lambda x: x["score"], reverse=True)
        n = len(scores_sorted)
        for i, s in enumerate(scores_sorted):
            owner = s["owner"]
            if owner not in expected_wins:
                expected_wins[owner] = 0
                actual_wins[owner] = 0
            # Expected win = (n_teams_beaten) / (n_teams - 1)
            teams_beaten = n - i - 1
            expected_wins[owner] += teams_beaten / (n - 1) if n > 1 else 0
    
    # Count actual wins
    for m in matchups:
        home_owner = m["home_owner"]
        away_owner = m["away_owner"]
        if m["home_score"] > m["away_score"]:
            if home_owner in actual_wins:
                actual_wins[home_owner] += 1
        else:
            if away_owner in actual_wins:
                actual_wins[away_owner] += 1
    
    # Calculate luck factor
    luck_rankings = []
    for owner in expected_wins:
        exp = expected_wins[owner]
        act = actual_wins.get(owner, 0)
        luck = act - exp
        luck_rankings.append({
            "owner": owner,
            "actual_wins": act,
            "expected_wins": round(exp, 1),
            "luck": round(luck, 1)
        })
    
    luck_rankings.sort(key=lambda x: x["luck"], reverse=True)
    
    return {"luck_rankings": luck_rankings}

@app.get("/api/weekly-scores")
def get_weekly_scores(year: int = Query(...), manager: Optional[str] = Query(None)):
    """Get weekly scores for a season, optionally filtered by manager"""
    with get_db() as conn:
        if manager:
            cursor = conn.execute("""
                SELECT m.week, m.home_score as score, m.home_team as team, t.owner
                FROM matchups m
                JOIN teams t ON m.home_team = t.team_name AND m.season_year = t.season_year
                WHERE m.season_year = ? AND t.owner = ?
                UNION ALL
                SELECT m.week, m.away_score, m.away_team, t.owner
                FROM matchups m
                JOIN teams t ON m.away_team = t.team_name AND m.season_year = t.season_year
                WHERE m.season_year = ? AND t.owner = ?
                ORDER BY week
            """, (year, manager, year, manager))
        else:
            cursor = conn.execute("""
                SELECT m.week, m.home_score as score, m.home_team as team, t.owner
                FROM matchups m
                JOIN teams t ON m.home_team = t.team_name AND m.season_year = t.season_year
                WHERE m.season_year = ?
                UNION ALL
                SELECT m.week, m.away_score, m.away_team, t.owner
                FROM matchups m
                JOIN teams t ON m.away_team = t.team_name AND m.season_year = t.season_year
                WHERE m.season_year = ?
                ORDER BY week, owner
            """, (year, year))
        scores = rows_to_dicts(cursor.fetchall())
    
    return {"year": year, "manager": manager, "scores": scores}

@app.get("/api/transactions")
def get_transactions(year: Optional[int] = Query(None), team: Optional[str] = Query(None)):
    """Get transactions, optionally filtered by year and/or team"""
    with get_db() as conn:
        if year and team:
            cursor = conn.execute("""
                SELECT * FROM transactions 
                WHERE season_year = ? AND team LIKE ?
                ORDER BY date DESC
            """, (year, f"%{team}%"))
        elif year:
            cursor = conn.execute("""
                SELECT * FROM transactions 
                WHERE season_year = ?
                ORDER BY date DESC
            """, (year,))
        elif team:
            cursor = conn.execute("""
                SELECT * FROM transactions 
                WHERE team LIKE ?
                ORDER BY date DESC
            """, (f"%{team}%",))
        else:
            cursor = conn.execute("""
                SELECT * FROM transactions 
                ORDER BY date DESC LIMIT 100
            """)
        transactions = rows_to_dicts(cursor.fetchall())
    
    return {"transactions": transactions}


@app.get("/api/matchup-roster")
def get_matchup_roster(
    year: int = Query(..., description="Season year"),
    week: int = Query(..., description="Week number"),
    team: str = Query(..., description="Team name")
):
    """Get roster for a specific team in a specific matchup"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT player_name, position, nfl_team, points, projected, started
            FROM matchup_rosters
            WHERE season_year = ? AND week = ? AND team_name = ?
            ORDER BY started DESC, points DESC
        """, (year, week, team))
        
        players = rows_to_dicts(cursor.fetchall())
        
        # Separate starters and bench
        starters = [p for p in players if p.get('started')]
        bench = [p for p in players if not p.get('started')]
        
        return {
            "team": team,
            "year": year,
            "week": week,
            "starters": starters,
            "bench": bench,
            "total_points": sum(p.get('points', 0) or 0 for p in starters)
        }


@app.get("/api/player-stats/{player_name}")
def get_player_stats(player_name: str, year: Optional[int] = Query(None)):
    """Get stats for a specific player, including career and season breakdown"""
    with get_db() as conn:
        # Get season-by-season stats from player_stats table
        if year:
            cursor = conn.execute("""
                SELECT season_year, position, nfl_team, owned_by, total_points, average_points
                FROM player_stats
                WHERE player_name = ? AND season_year = ?
                ORDER BY season_year DESC
            """, (player_name, year))
        else:
            cursor = conn.execute("""
                SELECT season_year, position, nfl_team, owned_by, total_points, average_points
                FROM player_stats
                WHERE player_name = ?
                ORDER BY season_year DESC
            """, (player_name,))
        
        seasons = rows_to_dicts(cursor.fetchall())
        
        # Get detailed NFL stats from nfl_weekly_stats table
        # Use LIKE to handle name variations (e.g., "Deebo Samuel" vs "Deebo Samuel Sr.")
        cursor = conn.execute("""
            SELECT 
                season, week, opponent_team, position, headshot_url,
                completions, attempts, passing_yards, passing_tds, interceptions,
                carries, rushing_yards, rushing_tds,
                receptions, targets, receiving_yards, receiving_tds,
                fantasy_points, fantasy_points_ppr,
                fg_made, fg_att, pat_made, pat_att, fg_long,
                fg_made_0_19, fg_made_20_29, fg_made_30_39, fg_made_40_49, fg_made_50_59, fg_made_60_,
                fg_missed_0_19, fg_missed_20_29, fg_missed_30_39, fg_missed_40_49, fg_missed_50_59, fg_missed_60_
            FROM nfl_weekly_stats
            WHERE player_display_name = ? 
               OR player_name = ?
               OR player_display_name LIKE ? || ' Sr.%'
               OR player_display_name LIKE ? || ' Jr.%'
               OR player_display_name LIKE ? || ' II%'
               OR player_display_name LIKE ? || ' III%'
               OR player_display_name LIKE ? || ' IV%'
            ORDER BY season DESC, week ASC
        """, (player_name, player_name, player_name, player_name, player_name, player_name, player_name))
        nfl_weekly = rows_to_dicts(cursor.fetchall())
        
        # Get player info from first result
        headshot = nfl_weekly[0].get('headshot_url') if nfl_weekly else None
        position = nfl_weekly[0].get('position') if nfl_weekly else None
        
        # Group by season for season summaries
        season_stats = {}
        for week in nfl_weekly:
            s = week['season']
            if s not in season_stats:
                season_stats[s] = {
                    'season': s,
                    'games': 0,
                    'passing_yards': 0,
                    'passing_tds': 0,
                    'interceptions': 0,
                    'rushing_yards': 0,
                    'rushing_tds': 0,
                    'receptions': 0,
                    'receiving_yards': 0,
                    'receiving_tds': 0,
                    'fantasy_points_ppr': 0,
                    # Kicker stats
                    'fg_made': 0,
                    'fg_att': 0,
                    'pat_made': 0,
                    'pat_att': 0,
                    'fg_long': 0,
                    'weeks': []
                }
            stats = season_stats[s]
            stats['games'] += 1
            stats['passing_yards'] += week.get('passing_yards') or 0
            stats['passing_tds'] += week.get('passing_tds') or 0
            stats['interceptions'] += week.get('interceptions') or 0
            stats['rushing_yards'] += week.get('rushing_yards') or 0
            stats['rushing_tds'] += week.get('rushing_tds') or 0
            stats['receptions'] += week.get('receptions') or 0
            stats['receiving_yards'] += week.get('receiving_yards') or 0
            stats['receiving_tds'] += week.get('receiving_tds') or 0
            stats['fantasy_points_ppr'] += week.get('fantasy_points_ppr') or 0
            # Kicker accumulation
            stats['fg_made'] += week.get('fg_made') or 0
            stats['fg_att'] += week.get('fg_att') or 0
            stats['pat_made'] += week.get('pat_made') or 0
            stats['pat_att'] += week.get('pat_att') or 0
            stats['fg_long'] = max(stats['fg_long'], week.get('fg_long') or 0)
            stats['weeks'].append({
                'week': week['week'],
                'opponent': week.get('opponent_team'),
                'completions': week.get('completions'),
                'attempts': week.get('attempts'),
                'passing_yards': week.get('passing_yards'),
                'passing_tds': week.get('passing_tds'),
                'interceptions': week.get('interceptions'),
                'carries': week.get('carries'),
                'rushing_yards': week.get('rushing_yards'),
                'rushing_tds': week.get('rushing_tds'),
                'receptions': week.get('receptions'),
                'targets': week.get('targets'),
                'receiving_yards': week.get('receiving_yards'),
                'receiving_tds': week.get('receiving_tds'),
                'fantasy_points_ppr': round(week.get('fantasy_points_ppr') or 0, 1),
                # Kicker stats
                'fg_made': week.get('fg_made'),
                'fg_att': week.get('fg_att'),
                'pat_made': week.get('pat_made'),
                'pat_att': week.get('pat_att'),
                'fg_long': week.get('fg_long'),
                'fg_made_0_19': week.get('fg_made_0_19'),
                'fg_made_20_29': week.get('fg_made_20_29'),
                'fg_made_30_39': week.get('fg_made_30_39'),
                'fg_made_40_49': week.get('fg_made_40_49'),
                'fg_made_50_59': week.get('fg_made_50_59'),
                'fg_made_60_': week.get('fg_made_60_'),
                'fg_missed_0_19': week.get('fg_missed_0_19'),
                'fg_missed_20_29': week.get('fg_missed_20_29'),
                'fg_missed_30_39': week.get('fg_missed_30_39'),
                'fg_missed_40_49': week.get('fg_missed_40_49'),
                'fg_missed_50_59': week.get('fg_missed_50_59'),
                'fg_missed_60_': week.get('fg_missed_60_')
            })
        
        # Round season totals
        for s in season_stats.values():
            s['passing_yards'] = round(s['passing_yards'])
            s['rushing_yards'] = round(s['rushing_yards'])
            s['receiving_yards'] = round(s['receiving_yards'])
            s['fantasy_points_ppr'] = round(s['fantasy_points_ppr'], 1)
        
        # Calculate career totals
        career_points = sum(s['fantasy_points_ppr'] for s in season_stats.values())
        total_games = sum(s['games'] for s in season_stats.values())
        
        return {
            "player_name": player_name,
            "position": position,
            "headshot_url": headshot,
            "seasons": list(season_stats.values()),
            "career_points": round(career_points, 1),
            "career_avg": round(career_points / total_games, 1) if total_games else 0,
            "total_games": total_games,
            "seasons_played": len(season_stats)
        }


def calculate_kicker_fantasy_points(week: dict) -> float:
    """Calculate kicker fantasy points based on standard scoring"""
    points = 0.0
    # Field goals by distance
    points += (week.get('fg_made_0_19') or 0) * 3
    points += (week.get('fg_made_20_29') or 0) * 3
    points += (week.get('fg_made_30_39') or 0) * 3
    points += (week.get('fg_made_40_49') or 0) * 4
    points += (week.get('fg_made_50_59') or 0) * 5
    points += (week.get('fg_made_60_') or 0) * 5
    # Extra points
    points += (week.get('pat_made') or 0) * 1
    # Missed field goals penalty (optional, common in some leagues)
    # points -= (week.get('fg_missed') or 0) * 1
    return points


def calculate_dst_fantasy_points(week: dict) -> float:
    """Calculate D/ST fantasy points based on standard ESPN scoring"""
    points = 0.0
    # Sacks: 1 pt each
    points += (week.get('def_sacks') or 0) * 1
    # Interceptions: 2 pts each
    points += (week.get('def_interceptions') or 0) * 2
    # Fumble recoveries: 2 pts each
    points += (week.get('def_fumbles_recovered') or 0) * 2
    # Defensive TDs: 6 pts each
    points += (week.get('def_touchdowns') or 0) * 6
    # Special teams TDs: 6 pts each
    points += (week.get('special_teams_tds') or 0) * 6
    # Safeties: 2 pts each
    points += (week.get('def_safeties') or 0) * 2
    # Points allowed scoring
    pts_allowed = week.get('points_allowed') or 0
    if pts_allowed == 0:
        points += 10
    elif pts_allowed <= 6:
        points += 7
    elif pts_allowed <= 13:
        points += 4
    elif pts_allowed <= 17:
        points += 1
    elif pts_allowed <= 27:
        points += 0
    elif pts_allowed <= 34:
        points += -1
    elif pts_allowed <= 45:
        points += -3
    else:
        points += -5
    return points


# Team abbreviation to full name mapping for D/ST
TEAM_ABBR_TO_NAME = {
    'ARI': 'Arizona Cardinals', 'ATL': 'Atlanta Falcons', 'BAL': 'Baltimore Ravens',
    'BUF': 'Buffalo Bills', 'CAR': 'Carolina Panthers', 'CHI': 'Chicago Bears',
    'CIN': 'Cincinnati Bengals', 'CLE': 'Cleveland Browns', 'DAL': 'Dallas Cowboys',
    'DEN': 'Denver Broncos', 'DET': 'Detroit Lions', 'GB': 'Green Bay Packers',
    'HOU': 'Houston Texans', 'IND': 'Indianapolis Colts', 'JAX': 'Jacksonville Jaguars',
    'KC': 'Kansas City Chiefs', 'LAC': 'Los Angeles Chargers', 'LAR': 'Los Angeles Rams',
    'LV': 'Las Vegas Raiders', 'MIA': 'Miami Dolphins', 'MIN': 'Minnesota Vikings',
    'NE': 'New England Patriots', 'NO': 'New Orleans Saints', 'NYG': 'New York Giants',
    'NYJ': 'New York Jets', 'PHI': 'Philadelphia Eagles', 'PIT': 'Pittsburgh Steelers',
    'SF': 'San Francisco 49ers', 'SEA': 'Seattle Seahawks', 'TB': 'Tampa Bay Buccaneers',
    'TEN': 'Tennessee Titans', 'WAS': 'Washington Commanders'
}


def extract_team_code(player_name: str) -> Optional[str]:
    """Extract team code from D/ST player name (matches abbreviations, full names, or nicknames)"""
    name_upper = player_name.upper().strip()
    
    # Team nickname to abbreviation mapping
    TEAM_NICKNAMES = {
        'CARDINALS': 'ARI', 'FALCONS': 'ATL', 'RAVENS': 'BAL', 'BILLS': 'BUF',
        'PANTHERS': 'CAR', 'BEARS': 'CHI', 'BENGALS': 'CIN', 'BROWNS': 'CLE',
        'COWBOYS': 'DAL', 'BRONCOS': 'DEN', 'LIONS': 'DET', 'PACKERS': 'GB',
        'TEXANS': 'HOU', 'COLTS': 'IND', 'JAGUARS': 'JAX', 'CHIEFS': 'KC',
        'CHARGERS': 'LAC', 'RAMS': 'LAR', 'RAIDERS': 'LV', 'DOLPHINS': 'MIA',
        'VIKINGS': 'MIN', 'PATRIOTS': 'NE', 'SAINTS': 'NO', 'GIANTS': 'NYG',
        'JETS': 'NYJ', 'EAGLES': 'PHI', 'STEELERS': 'PIT', '49ERS': 'SF',
        'NINERS': 'SF', 'SEAHAWKS': 'SEA', 'BUCCANEERS': 'TB', 'BUCS': 'TB',
        'TITANS': 'TEN', 'COMMANDERS': 'WAS', 'WASHINGTON': 'WAS'
    }
    
    # Check nickname first (most common case for D/ST like "Eagles")
    for nickname, abbr in TEAM_NICKNAMES.items():
        if nickname in name_upper:
            return abbr
    
    # Direct abbreviation match
    for abbr in TEAM_ABBR_TO_NAME.keys():
        if abbr in name_upper:
            return abbr
    
    # Check full names
    for abbr, full_name in TEAM_ABBR_TO_NAME.items():
        if full_name.upper() in name_upper:
            return abbr
    
    return None


@app.get("/api/dst-stats/{team_identifier:path}")
def get_dst_stats(team_identifier: str, year: Optional[int] = Query(None)):
    """Get D/ST stats for a specific team"""
    team_code = extract_team_code(team_identifier)
    
    if not team_code:
        raise HTTPException(status_code=404, detail=f"Could not identify team from: {team_identifier}")
    
    with get_db() as conn:
        # Check if table exists
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='nfl_team_defense_stats'")
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="D/ST stats table not found in database")
        
        # Get weekly D/ST stats
        if year:
            cursor = conn.execute("""
                SELECT * FROM nfl_team_defense_stats
                WHERE team_abbr = ? AND season = ? AND season_type = 'REG'
                ORDER BY week
            """, (team_code, year))
        else:
            cursor = conn.execute("""
                SELECT * FROM nfl_team_defense_stats
                WHERE team_abbr = ? AND season_type = 'REG'
                ORDER BY season DESC, week
            """, (team_code,))
        
        weekly_stats = rows_to_dicts(cursor.fetchall())
        
        if not weekly_stats:
            raise HTTPException(status_code=404, detail=f"No stats found for {team_code} defense")
        
        # Group by season
        seasons_data = {}
        for stat in weekly_stats:
            season_year = stat['season']
            if season_year not in seasons_data:
                seasons_data[season_year] = {
                    'season': season_year,
                    'games': 0,
                    'def_sacks': 0,
                    'def_interceptions': 0,
                    'def_fumbles_recovered': 0,
                    'def_touchdowns': 0,
                    'special_teams_tds': 0,
                    'points_allowed': 0,
                    'fantasy_points_ppr': 0,
                    'weeks': []
                }
            s = seasons_data[season_year]
            s['games'] += 1
            s['def_sacks'] += stat.get('def_sacks') or 0
            s['def_interceptions'] += stat.get('def_interceptions') or 0
            s['def_fumbles_recovered'] += stat.get('def_fumbles_recovered') or 0
            s['def_touchdowns'] += stat.get('def_touchdowns') or 0
            s['special_teams_tds'] += stat.get('special_teams_tds') or 0
            s['points_allowed'] += stat.get('points_allowed') or 0
            # Calculate fantasy points for this week
            week_pts = calculate_dst_fantasy_points(stat)
            s['fantasy_points_ppr'] += week_pts
            s['weeks'].append({
                'week': stat['week'],
                'opponent': stat.get('opponent_team'),
                'def_sacks': stat.get('def_sacks') or 0,
                'def_interceptions': stat.get('def_interceptions') or 0,
                'def_fumbles_recovered': stat.get('def_fumbles_recovered') or 0,
                'def_touchdowns': stat.get('def_touchdowns') or 0,
                'special_teams_tds': stat.get('special_teams_tds') or 0,
                'points_allowed': stat.get('points_allowed') or 0,
                'fantasy_points_ppr': round(week_pts, 1)
            })
        
        # Round totals
        for s in seasons_data.values():
            s['fantasy_points_ppr'] = round(s['fantasy_points_ppr'], 1)
        
        career_points = sum(s['fantasy_points_ppr'] for s in seasons_data.values())
        total_games = sum(s['games'] for s in seasons_data.values())
        
        return {
            "player_name": f"{TEAM_ABBR_TO_NAME.get(team_code, team_code)} D/ST",
            "position": "D/ST",
            "headshot_url": None,
            "team": team_code,
            "seasons": list(seasons_data.values()),
            "career_points": round(career_points, 1),
            "career_avg": round(career_points / total_games, 1) if total_games else 0,
            "total_games": total_games,
            "seasons_played": len(seasons_data),
            "is_dst": True
        }


# Run with: uvicorn main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

