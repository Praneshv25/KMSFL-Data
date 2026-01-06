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

# Run with: uvicorn main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
