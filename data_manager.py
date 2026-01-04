"""
Data Manager for ESPN Fantasy Data
Handles JSON export and SQLite database storage
"""
import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import config


class DataManager:
    """
    Manages data storage to both JSON and SQLite
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize data manager
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path or config.DB_FILE
        
        # Ensure data directory exists
        os.makedirs(config.DATA_DIR, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Teams table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_id INTEGER,
                season_year INTEGER,
                team_name TEXT,
                owner TEXT,
                rank INTEGER,
                wins INTEGER,
                losses INTEGER,
                ties INTEGER,
                points_for REAL,
                points_against REAL,
                streak TEXT,
                scraped_at TIMESTAMP,
                UNIQUE(league_id, season_year, team_name, scraped_at)
            )
        """)
        
        # Matchups table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matchups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_id INTEGER,
                season_year INTEGER,
                week INTEGER,
                matchup_id INTEGER,
                home_team TEXT,
                home_score REAL,
                home_projected REAL,
                away_team TEXT,
                away_score REAL,
                away_projected REAL,
                is_complete BOOLEAN,
                scraped_at TIMESTAMP,
                UNIQUE(league_id, season_year, week, matchup_id, scraped_at)
            )
        """)
        
        # Rosters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rosters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_id INTEGER,
                season_year INTEGER,
                team_name TEXT,
                player_name TEXT,
                position TEXT,
                nfl_team TEXT,
                is_starter BOOLEAN,
                points REAL,
                status TEXT,
                scraped_at TIMESTAMP
            )
        """)
        
        # Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_id INTEGER,
                season_year INTEGER,
                date TEXT,
                type TEXT,
                team TEXT,
                players_added TEXT,
                players_dropped TEXT,
                description TEXT,
                scraped_at TIMESTAMP
            )
        """)
        
        # Player stats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_id INTEGER,
                season_year INTEGER,
                player_name TEXT,
                position TEXT,
                nfl_team TEXT,
                owned_by TEXT,
                total_points REAL,
                average_points REAL,
                last_week_points REAL,
                scraped_at TIMESTAMP
            )
        """)
        
        # Scrape metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scrape_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_id INTEGER,
                season_year INTEGER,
                scraped_at TIMESTAMP,
                data_types TEXT,
                success BOOLEAN,
                notes TEXT
            )
        """)
        
        # NFL weekly stats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nfl_weekly_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT,
                player_name TEXT,
                player_display_name TEXT,
                position TEXT,
                position_group TEXT,
                headshot_url TEXT,
                recent_team TEXT,
                season INTEGER,
                week INTEGER,
                season_type TEXT,
                opponent_team TEXT,
                completions INTEGER,
                attempts INTEGER,
                passing_yards REAL,
                passing_tds INTEGER,
                interceptions INTEGER,
                sacks INTEGER,
                sack_yards REAL,
                sack_fumbles INTEGER,
                sack_fumbles_lost INTEGER,
                passing_air_yards REAL,
                passing_yards_after_catch REAL,
                passing_first_downs INTEGER,
                passing_epa REAL,
                passing_2pt_conversions INTEGER,
                carries INTEGER,
                rushing_yards REAL,
                rushing_tds INTEGER,
                rushing_fumbles INTEGER,
                rushing_fumbles_lost INTEGER,
                rushing_first_downs INTEGER,
                rushing_epa REAL,
                rushing_2pt_conversions INTEGER,
                receptions INTEGER,
                targets INTEGER,
                receiving_yards REAL,
                receiving_tds INTEGER,
                receiving_fumbles INTEGER,
                receiving_fumbles_lost INTEGER,
                receiving_air_yards REAL,
                receiving_yards_after_catch REAL,
                receiving_first_downs INTEGER,
                receiving_epa REAL,
                receiving_2pt_conversions INTEGER,
                racr REAL,
                target_share REAL,
                air_yards_share REAL,
                wopr REAL,
                special_teams_tds INTEGER,
                fantasy_points REAL,
                fantasy_points_ppr REAL,
                UNIQUE(player_id, season, week, season_type)
            )
        """)
        
        # NFL player mapping table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nfl_player_mapping (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fantasy_player_name TEXT,
                nfl_player_id TEXT,
                nfl_player_name TEXT,
                nfl_player_display_name TEXT,
                position TEXT,
                team TEXT,
                confidence_score REAL,
                created_at TIMESTAMP,
                UNIQUE(fantasy_player_name, nfl_player_id)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_nfl_weekly_stats_player 
            ON nfl_weekly_stats(player_id, season, week)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_nfl_weekly_stats_name 
            ON nfl_weekly_stats(player_display_name, season, week)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_nfl_player_mapping_fantasy_name 
            ON nfl_player_mapping(fantasy_player_name)
        """)
        
        conn.commit()
        conn.close()
        
        print(f"✓ Database initialized: {self.db_path}")
    
    def save_to_json(self, data: Dict[Any, Any], filename: Optional[str] = None) -> str:
        """
        Save data to JSON file
        
        Args:
            data: Data to save
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            league_id = data.get('league_id', config.LEAGUE_ID)
            season = data.get('season_year', config.SEASON_YEAR)
            filename = f"espn_league_{league_id}_{season}_{timestamp}.json"
        
        filepath = os.path.join(config.DATA_DIR, filename)
        
        # Add metadata
        data['saved_at'] = datetime.now().isoformat()
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Data saved to JSON: {filepath}")
        return filepath
    
    def save_to_database(self, data: Dict[Any, Any]) -> bool:
        """
        Save data to SQLite database
        
        Args:
            data: Complete league data
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            league_id = data.get('league_id', config.LEAGUE_ID)
            season_year = data.get('season_year', config.SEASON_YEAR)
            scraped_at = datetime.now().isoformat()
            
            # Save standings
            standings = data.get('standings', [])
            for team in standings:
                cursor.execute("""
                    INSERT OR REPLACE INTO teams 
                    (league_id, season_year, team_name, owner, rank, wins, losses, ties, 
                     points_for, points_against, streak, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    league_id, season_year,
                    team.get('team_name'),
                    team.get('owner'),
                    team.get('rank'),
                    team.get('wins'),
                    team.get('losses'),
                    team.get('ties', 0),
                    team.get('points_for'),
                    team.get('points_against'),
                    team.get('streak'),
                    scraped_at
                ))
            
            # Save matchups
            matchups = data.get('matchups', {})
            for week, week_matchups in matchups.items():
                for matchup in week_matchups:
                    cursor.execute("""
                        INSERT OR REPLACE INTO matchups
                        (league_id, season_year, week, matchup_id, home_team, home_score, 
                         home_projected, away_team, away_score, away_projected, is_complete, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        league_id, season_year,
                        week,
                        matchup.get('matchup_id'),
                        matchup.get('home_team'),
                        matchup.get('home_score'),
                        matchup.get('home_projected'),
                        matchup.get('away_team'),
                        matchup.get('away_score'),
                        matchup.get('away_projected'),
                        matchup.get('is_complete'),
                        scraped_at
                    ))
            
            # Save rosters
            rosters = data.get('rosters', [])
            for team in rosters:
                team_name = team.get('team_name')
                
                # Save starters
                for player in team.get('starters', []):
                    cursor.execute("""
                        INSERT INTO rosters
                        (league_id, season_year, team_name, player_name, position, 
                         nfl_team, is_starter, points, status, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        league_id, season_year, team_name,
                        player.get('player_name'),
                        player.get('position'),
                        player.get('nfl_team'),
                        True,
                        player.get('points'),
                        player.get('status'),
                        scraped_at
                    ))
                
                # Save bench
                for player in team.get('bench', []):
                    cursor.execute("""
                        INSERT INTO rosters
                        (league_id, season_year, team_name, player_name, position, 
                         nfl_team, is_starter, points, status, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        league_id, season_year, team_name,
                        player.get('player_name'),
                        player.get('position'),
                        player.get('nfl_team'),
                        False,
                        player.get('points'),
                        player.get('status'),
                        scraped_at
                    ))
            
            # Save transactions
            transactions = data.get('transactions', [])
            for txn in transactions:
                cursor.execute("""
                    INSERT INTO transactions
                    (league_id, season_year, date, type, team, players_added, 
                     players_dropped, description, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    league_id, season_year,
                    txn.get('date'),
                    txn.get('type'),
                    txn.get('team'),
                    json.dumps(txn.get('players_added', [])),
                    json.dumps(txn.get('players_dropped', [])),
                    txn.get('description'),
                    scraped_at
                ))
            
            # Save player stats
            player_stats = data.get('player_stats', [])
            for player in player_stats:
                cursor.execute("""
                    INSERT INTO player_stats
                    (league_id, season_year, player_name, position, nfl_team, 
                     owned_by, total_points, average_points, last_week_points, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    league_id, season_year,
                    player.get('player_name'),
                    player.get('position'),
                    player.get('nfl_team'),
                    player.get('owned_by'),
                    player.get('total_points'),
                    player.get('average_points'),
                    player.get('last_week_points'),
                    scraped_at
                ))
            
            # Save metadata
            data_types = json.dumps(list(data.keys()))
            cursor.execute("""
                INSERT INTO scrape_metadata
                (league_id, season_year, scraped_at, data_types, success, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                league_id, season_year, scraped_at, data_types, True,
                f"Scraped {len(standings)} teams, {len(matchups)} weeks, {len(transactions)} transactions"
            ))
            
            conn.commit()
            conn.close()
            
            print(f"✓ Data saved to database: {self.db_path}")
            return True
            
        except Exception as e:
            print(f"✗ Error saving to database: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_all(self, data: Dict[Any, Any]) -> bool:
        """
        Save data to both JSON and database
        
        Args:
            data: Complete league data
            
        Returns:
            True if both saves successful
        """
        print("\n" + "="*60)
        print("SAVING DATA")
        print("="*60)
        
        json_success = False
        db_success = False
        
        try:
            self.save_to_json(data)
            json_success = True
        except Exception as e:
            print(f"✗ JSON save failed: {e}")
        
        try:
            self.save_to_database(data)
            db_success = True
        except Exception as e:
            print(f"✗ Database save failed: {e}")
        
        if json_success and db_success:
            print("\n✓ All data saved successfully!")
            return True
        elif json_success or db_success:
            print("\n⚠ Partial save success")
            return True
        else:
            print("\n✗ Save failed")
            return False
    
    def get_latest_standings(self, league_id: Optional[int] = None) -> List[Dict]:
        """
        Get most recent standings from database
        
        Args:
            league_id: League ID (defaults to config)
            
        Returns:
            List of team standings
        """
        league_id = league_id or config.LEAGUE_ID
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM teams
            WHERE league_id = ?
            ORDER BY scraped_at DESC, rank ASC
            LIMIT 100
        """, (league_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]


if __name__ == "__main__":
    # Test data manager
    dm = DataManager()
    
    # Test with sample data
    test_data = {
        'league_id': config.LEAGUE_ID,
        'season_year': config.SEASON_YEAR,
        'standings': [
            {'rank': 1, 'team_name': 'Test Team', 'owner': 'Test Owner', 
             'wins': 10, 'losses': 3, 'ties': 0, 'points_for': 1234.56,
             'points_against': 1100.23, 'streak': 'W3'}
        ],
        'matchups': {},
        'rosters': [],
        'transactions': [],
        'player_stats': []
    }
    
    print("Testing data manager...")
    dm.save_all(test_data)

