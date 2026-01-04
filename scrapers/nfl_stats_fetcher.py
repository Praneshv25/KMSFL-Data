"""
NFL Stats Fetcher
Fetches and processes NFL player statistics using nflreadpy
"""
import sqlite3
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re

try:
    import nflreadpy as nfl
    import polars as pl
except ImportError:
    print("⚠ nflreadpy not installed. Run: pip install nflreadpy polars")
    nfl = None
    pl = None

import config


class NFLStatsFetcher:
    """
    Fetches NFL player statistics and stores them in the database
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize NFL stats fetcher
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path or config.DB_FILE
        
        if nfl is None or pl is None:
            raise ImportError("nflreadpy and polars are not installed")
    
    def fetch_weekly_stats(self, seasons: List[int]) -> Optional[object]:
        """
        Fetch weekly NFL stats for given seasons using nflreadpy
        
        Args:
            seasons: List of seasons (years) to fetch
            
        Returns:
            Polars DataFrame with weekly stats or None if error
            
        Note:
            Data availability:
            - 1999-present: Available through nflverse
            - Recent weeks: Data typically available within hours
            - Uses nflreadpy which loads from nflverse-data repository
        """
        try:
            print(f"📊 Fetching NFL player stats for seasons: {seasons}")
            # nflreadpy uses load_player_stats() instead of import_weekly_data()
            # This returns game-level stats in a Polars DataFrame
            player_stats = nfl.load_player_stats(seasons=seasons)
            print(f"✓ Fetched {len(player_stats)} player-game records")
            return player_stats
        except Exception as e:
            print(f"✗ Error fetching NFL stats: {e}")
            if "404" in str(e) or "Not Found" in str(e):
                print(f"   (Data for {seasons} may not be published yet)")
            return None
    
    def normalize_player_name(self, name: str) -> str:
        """
        Normalize player name for better matching
        
        Args:
            name: Raw player name
            
        Returns:
            Normalized name
        """
        if not name:
            return ""
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Remove common suffixes for matching (but keep them in display)
        # We'll use this for fuzzy matching
        normalized = re.sub(r'\s+(Jr\.?|Sr\.?|III|II|IV|V)$', '', name, flags=re.IGNORECASE)
        
        return normalized.strip()
    
    def find_player_match(self, fantasy_name: str, weekly_stats) -> Optional[Dict]:
        """
        Find the best matching NFL player for a fantasy player name
        
        Args:
            fantasy_name: Name from fantasy league
            weekly_stats: Polars DataFrame with NFL weekly stats
            
        Returns:
            Dict with player info or None if no match
        """
        if weekly_stats is None or fantasy_name is None or len(weekly_stats) == 0:
            return None
        
        normalized_fantasy = self.normalize_player_name(fantasy_name)
        
        # Try exact match on player_display_name (case-insensitive)
        exact_match = weekly_stats.filter(
            pl.col('player_display_name').str.to_lowercase() == fantasy_name.lower()
        )
        
        if len(exact_match) > 0:
            player_row = exact_match[0].to_dicts()[0]
            return {
                'player_id': player_row['player_id'],
                'player_name': player_row['player_name'],
                'player_display_name': player_row['player_display_name'],
                'position': player_row['position'],
                'team': player_row.get('team') or player_row.get('recent_team') or '',
                'confidence': 1.0
            }
        
        # Try normalized match (without suffixes)
        for row in weekly_stats.to_dicts():
            if self.normalize_player_name(str(row['player_display_name'])).lower() == normalized_fantasy.lower():
                return {
                    'player_id': row['player_id'],
                    'player_name': row['player_name'],
                    'player_display_name': row['player_display_name'],
                    'position': row['position'],
                    'team': row.get('team') or row.get('recent_team') or '',
                    'confidence': 0.9
                }
        
        # Try partial match (for cases like "D. Smith" vs "DeVonta Smith")
        if ' ' in fantasy_name:
            parts = fantasy_name.split()
            last_name = parts[-1]
            
            # Look for players with same last name
            last_name_match = weekly_stats.filter(
                pl.col('player_display_name').str.to_lowercase().str.contains(last_name.lower())
            )
            
            if len(last_name_match) == 1:
                # Only one player with this last name - likely a match
                player_row = last_name_match[0].to_dicts()[0]
                return {
                    'player_id': player_row['player_id'],
                    'player_name': player_row['player_name'],
                    'player_display_name': player_row['player_display_name'],
                    'position': player_row['position'],
                    'team': player_row.get('team') or player_row.get('recent_team') or '',
                    'confidence': 0.7
                }
        
        return None
    
    def store_weekly_stats(self, weekly_stats) -> int:
        """
        Store weekly stats in database
        
        Args:
            weekly_stats: Polars DataFrame with weekly stats
            
        Returns:
            Number of records stored
        """
        if weekly_stats is None or len(weekly_stats) == 0:
            print("⚠ No weekly stats to store")
            return 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stored_count = 0
        
        # Convert Polars DataFrame to list of dicts for iteration
        for row in weekly_stats.to_dicts():
            try:
                # Build the values tuple
                values_tuple = (
                    str(row.get('player_id') or ''),
                    str(row.get('player_name') or ''),
                    str(row.get('player_display_name') or ''),
                    str(row.get('position') or ''),
                    str(row.get('position_group') or ''),
                    str(row.get('headshot_url') or ''),
                    str(row.get('team') or ''),
                    int(row.get('season') or 0),
                    int(row.get('week') or 0),
                    str(row.get('season_type') or 'REG'),
                    str(row.get('opponent_team') or ''),
                    int(row.get('completions') or 0),
                    int(row.get('attempts') or 0),
                    float(row.get('passing_yards') or 0.0),
                    int(row.get('passing_tds') or 0),
                    int(row.get('passing_interceptions') or 0),
                    int(row.get('sacks_suffered') or 0),
                    float(row.get('sack_yards_lost') or 0.0),
                    int(row.get('sack_fumbles') or 0),
                    int(row.get('sack_fumbles_lost') or 0),
                    float(row.get('passing_air_yards') or 0.0),
                    float(row.get('passing_yards_after_catch') or 0.0),
                    int(row.get('passing_first_downs') or 0),
                    float(row.get('passing_epa') or 0.0),
                    int(row.get('passing_2pt_conversions') or 0),
                    int(row.get('carries') or 0),
                    float(row.get('rushing_yards') or 0.0),
                    int(row.get('rushing_tds') or 0),
                    int(row.get('rushing_fumbles') or 0),
                    int(row.get('rushing_fumbles_lost') or 0),
                    int(row.get('rushing_first_downs') or 0),
                    float(row.get('rushing_epa') or 0.0),
                    int(row.get('rushing_2pt_conversions') or 0),
                    int(row.get('receptions') or 0),
                    int(row.get('targets') or 0),
                    float(row.get('receiving_yards') or 0.0),
                    int(row.get('receiving_tds') or 0),
                    int(row.get('receiving_fumbles') or 0),
                    int(row.get('receiving_fumbles_lost') or 0),
                    float(row.get('receiving_air_yards') or 0.0),
                    float(row.get('receiving_yards_after_catch') or 0.0),
                    int(row.get('receiving_first_downs') or 0),
                    float(row.get('receiving_epa') or 0.0),
                    int(row.get('receiving_2pt_conversions') or 0),
                    float(row.get('racr') or 0.0),
                    float(row.get('target_share') or 0.0),
                    float(row.get('air_yards_share') or 0.0),
                    float(row.get('wopr') or 0.0),
                    int(row.get('special_teams_tds') or 0),
                    float(row.get('fantasy_points') or 0.0),
                    float(row.get('fantasy_points_ppr') or 0.0)
                )
                
                # Debug: check tuple length
                if len(values_tuple) != 51:
                    print(f"⚠ DEBUG: Tuple length is {len(values_tuple)}, expected 51")
                    print(f"   Player: {row.get('player_display_name')}")
                    continue
                
                cursor.execute("""
                    INSERT OR REPLACE INTO nfl_weekly_stats (
                        player_id, player_name, player_display_name, position, position_group,
                        headshot_url, recent_team, season, week, season_type, opponent_team,
                        completions, attempts, passing_yards, passing_tds, interceptions,
                        sacks, sack_yards, sack_fumbles, sack_fumbles_lost,
                        passing_air_yards, passing_yards_after_catch, passing_first_downs,
                        passing_epa, passing_2pt_conversions,
                        carries, rushing_yards, rushing_tds, rushing_fumbles, rushing_fumbles_lost,
                        rushing_first_downs, rushing_epa, rushing_2pt_conversions,
                        receptions, targets, receiving_yards, receiving_tds,
                        receiving_fumbles, receiving_fumbles_lost, receiving_air_yards,
                        receiving_yards_after_catch, receiving_first_downs, receiving_epa,
                        receiving_2pt_conversions, racr, target_share, air_yards_share, wopr,
                        special_teams_tds, fantasy_points, fantasy_points_ppr
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, values_tuple)
                stored_count += 1
            except Exception as e:
                print(f"⚠ Error storing row for {row.get('player_display_name') or 'Unknown'}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        print(f"✓ Stored {stored_count} weekly stat records")
        return stored_count
    
    def create_player_mappings(self, fantasy_players: List[str], weekly_stats) -> int:
        """
        Create mappings between fantasy player names and NFL player IDs
        
        Args:
            fantasy_players: List of player names from fantasy leagues
            weekly_stats: Polars DataFrame with NFL weekly stats
            
        Returns:
            Number of mappings created
        """
        if not fantasy_players or weekly_stats is None or len(weekly_stats) == 0:
            return 0
        
        print(f"   Building player lookup table from {len(weekly_stats)} records...")
        
        # Create a unique players lookup for faster matching
        # Get unique players from the stats
        unique_players = weekly_stats.select([
            'player_id', 'player_name', 'player_display_name', 
            'position', 'team'
        ]).unique(subset=['player_id'])
        
        # Convert to dict for fast lookup
        player_lookup = {}
        for player in unique_players.to_dicts():
            name = player['player_display_name']
            name_lower = name.lower()
            player_lookup[name_lower] = player
            # Also add normalized version (without suffixes)
            normalized = self.normalize_player_name(name).lower()
            if normalized != name_lower and normalized not in player_lookup:
                player_lookup[normalized] = player
        
        print(f"   Lookup table created with {len(unique_players)} unique players")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        mapping_count = 0
        unique_fantasy_players = set(fantasy_players)
        
        print(f"   Mapping {len(unique_fantasy_players)} fantasy player names...")
        
        for i, fantasy_name in enumerate(unique_fantasy_players, 1):
            if i % 100 == 0:
                print(f"   Progress: {i}/{len(unique_fantasy_players)}...")
            
            if not fantasy_name or fantasy_name.lower() in ['unknown', 'n/a', '']:
                continue
            
            # Try exact match first
            match = None
            fantasy_lower = fantasy_name.lower()
            
            if fantasy_lower in player_lookup:
                match = player_lookup[fantasy_lower]
                confidence = 1.0
            else:
                # Try normalized match
                normalized = self.normalize_player_name(fantasy_name).lower()
                if normalized in player_lookup:
                    match = player_lookup[normalized]
                    confidence = 0.9
            
            if match:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO nfl_player_mapping (
                            fantasy_player_name, nfl_player_id, nfl_player_name,
                            nfl_player_display_name, position, team,
                            confidence_score, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        fantasy_name,
                        match['player_id'],
                        match['player_name'],
                        match['player_display_name'],
                        match['position'],
                        match.get('team') or '',
                        confidence,
                        datetime.now().isoformat()
                    ))
                    mapping_count += 1
                except Exception as e:
                    print(f"⚠ Error mapping {fantasy_name}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"✓ Created {mapping_count} player mappings")
        return mapping_count
    
    def get_player_stats(self, player_name: str, season: Optional[int] = None) -> Dict:
        """
        Get NFL stats for a specific player
        
        Args:
            player_name: Player name (fantasy or NFL format)
            season: Optional season to filter by
            
        Returns:
            Dict with player info and stats
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Try to find player mapping first
        cursor.execute("""
            SELECT nfl_player_id, nfl_player_display_name, position, team
            FROM nfl_player_mapping
            WHERE fantasy_player_name = ?
            ORDER BY confidence_score DESC
            LIMIT 1
        """, (player_name,))
        
        mapping = cursor.fetchone()
        
        if mapping:
            player_id = mapping['nfl_player_id']
            display_name = mapping['nfl_player_display_name']
        else:
            # Try direct match on display name (handle both column names for compatibility)
            cursor.execute("""
                SELECT DISTINCT player_id, player_display_name, position, 
                       COALESCE(recent_team, '') as recent_team
                FROM nfl_weekly_stats
                WHERE player_display_name = ?
                LIMIT 1
            """, (player_name,))
            
            direct_match = cursor.fetchone()
            
            if direct_match:
                player_id = direct_match['player_id']
                display_name = direct_match['player_display_name']
            else:
                conn.close()
                return {'error': 'Player not found', 'player_name': player_name}
        
        # Get weekly stats
        if season:
            cursor.execute("""
                SELECT * FROM nfl_weekly_stats
                WHERE player_id = ? AND season = ? AND season_type = 'REG'
                ORDER BY week
            """, (player_id, season))
        else:
            cursor.execute("""
                SELECT * FROM nfl_weekly_stats
                WHERE player_id = ? AND season_type = 'REG'
                ORDER BY season DESC, week
            """, (player_id,))
        
        weekly_stats = [dict(row) for row in cursor.fetchall()]
        
        # Get player info from most recent game
        if weekly_stats:
            latest = weekly_stats[0]
            player_info = {
                'player_id': player_id,
                'player_name': latest['player_name'],
                'player_display_name': latest['player_display_name'],
                'position': latest['position'],
                'team': latest.get('recent_team') or latest.get('team') or 'FA',
                'headshot_url': latest['headshot_url']
            }
        else:
            player_info = {
                'player_id': player_id,
                'player_display_name': display_name,
                'position': mapping['position'] if mapping else 'Unknown',
                'team': mapping['team'] if mapping else 'Unknown'
            }
        
        conn.close()
        
        return {
            'player_info': player_info,
            'weekly_stats': weekly_stats,
            'total_games': len(weekly_stats)
        }


if __name__ == "__main__":
    # Test the fetcher
    print("Testing NFL Stats Fetcher...")
    
    fetcher = NFLStatsFetcher()
    
    # Fetch a small sample (just 2024)
    weekly_stats = fetcher.fetch_weekly_stats([2024])
    
    if weekly_stats is not None and len(weekly_stats) > 0:
        print(f"Sample data: {len(weekly_stats)} records")
        print(weekly_stats.head())
    else:
        print("No data fetched")

