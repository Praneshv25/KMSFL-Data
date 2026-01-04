# NFL Player Stats Feature

## Overview
This feature integrates real NFL game statistics into the Fantasy Football dashboard using [nflreadpy](https://github.com/nflverse/nflreadpy), the official Python package from the nflverse project. When viewing matchups, you can click on any player name to see their detailed NFL stats including actual game performance data like receptions, passing touchdowns, rushing yards, etc.

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

This will install `nflreadpy` and `polars` along with other required packages.

### 2. Populate NFL Stats Database
Run the population script to fetch and store NFL statistics:

```bash
python populate_nfl_stats.py
```

This script will:
- Fetch NFL weekly stats for all relevant seasons (2019-2024+)
- Store statistics in the database (`data/espn_fantasy.db`)
- Create player name mappings between your fantasy league and NFL data
- This may take a few minutes on first run

**Note:** You can run this script multiple times. It will ask if you want to update existing data.

### 3. Start the Dashboard
```bash
python app.py
```

Navigate to the Matchups page and click on any player name to view their stats.

## Features

### Player Stats Modal
Click any player name in the matchups view to open a modal showing:

#### Current Season Tab
- Season summary with key totals
- Weekly game-by-game stats
- Opponent information
- Position-specific statistics:
  - **QB**: Completions, Passing Yards, Passing TDs, INTs, Rushing stats
  - **RB**: Carries, Rushing Yards, Rushing TDs, Receptions, Receiving Yards
  - **WR/TE**: Targets, Receptions, Receiving Yards, Receiving TDs
- Fantasy points (standard and PPR)

#### Career Stats Tab
- Career summary grouped by season
- Total games played per season
- Season totals for all major statistical categories
- Full career history from 2019-present

### Data Included
The NFL stats include:
- Passing: Completions, attempts, yards, TDs, interceptions, sacks
- Rushing: Carries, yards, TDs, fumbles
- Receiving: Targets, receptions, yards, TDs, fumbles
- Advanced: EPA, air yards, target share, etc.
- Fantasy points (both standard and PPR scoring)

## Database Schema

### New Tables

#### `nfl_weekly_stats`
Stores weekly NFL game statistics for all players from 2019-present.

Key columns:
- `player_id`, `player_name`, `player_display_name`
- `position`, `recent_team`, `season`, `week`
- All major statistical categories (passing, rushing, receiving)
- `fantasy_points`, `fantasy_points_ppr`

#### `nfl_player_mapping`
Maps fantasy player names to NFL player IDs to handle name variations.

Columns:
- `fantasy_player_name` - Name as it appears in your fantasy league
- `nfl_player_id` - Official NFL player ID
- `nfl_player_display_name` - Official NFL player name
- `confidence_score` - Match confidence (0.0-1.0)

## API Endpoint

### GET `/api/player-stats/<player_name>`
Returns NFL statistics for a specific player.

**Query Parameters:**
- `season` (optional) - Filter by specific season year

**Response:**
```json
{
  "player_info": {
    "player_id": "...",
    "player_display_name": "...",
    "position": "...",
    "team": "...",
    "headshot_url": "..."
  },
  "weekly_stats": [...],
  "seasons_data": {...},
  "season_totals": {...},
  "total_games": 123
}
```

## Troubleshooting

### Player Not Found
If a player's stats don't appear:
1. Check that the player name matches between your fantasy league and NFL data
2. Run `python populate_nfl_stats.py` again to update player mappings
3. The player might be a rookie or have limited NFL data

### Missing Data
- NFL data is available from **1999 onwards** through nflverse
- **Current Season**: Data is typically available within hours of games completing
- **Recent Weeks**: nflreadpy pulls from nflverse-data which updates regularly
- Only regular season games are included by default
- Some advanced stats may be null for certain positions

### Data Availability
Using [nflreadpy](https://github.com/nflverse/nflreadpy) from the nflverse project provides:
- **Historical Data**: 1999-present available
- **Current Season**: Updates within hours of game completion
- **Reliable Source**: Official nflverse data repository
- The populate script will automatically skip years that aren't available yet

### Performance
- First load may be slow as it fetches data
- Stats are cached in the database for fast subsequent access
- Browser caching improves repeated lookups

## Technical Details

### Files Modified/Created
- **requirements.txt** - Added `nflreadpy` and `polars`
- **data_manager.py** - Extended database schema
- **app.py** - Added `/api/player-stats/<player_name>` endpoint
- **templates/matchups.html** - Added modal UI and JavaScript
- **scrapers/nfl_stats_fetcher.py** - NFL data integration module using nflreadpy
- **populate_nfl_stats.py** - Database population script

### Data Flow
1. User clicks player name in matchups view
2. JavaScript makes AJAX request to `/api/player-stats/<player_name>`
3. API queries `nfl_weekly_stats` and `nfl_player_mapping` tables
4. Returns organized stats by season
5. Modal displays formatted data with tabs for current season and career

## Future Enhancements
Potential improvements:
- Add playoff stats
- Include defensive stats for D/ST positions
- Add charts/graphs for performance trends
- Export stats to CSV
- Compare multiple players side-by-side

## Data Source
NFL statistics are provided by [nflreadpy](https://github.com/nflverse/nflreadpy), the official Python port of nflreadr from the [nflverse project](https://github.com/nflverse). Data is sourced from the nflverse-data repository and updated regularly.

