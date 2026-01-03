"""
Extract 2019 playoff data directly from user-provided screenshots
"""
import json
import os
from PIL import Image
from gemini_client import GeminiVisionClient
import config

def extract_playoff_data_from_images(image_paths, season=2019):
    """Extract playoff matchup data from screenshot images"""
    
    # Initialize Gemini client
    gemini = GeminiVisionClient(config.GEMINI_API_KEY, config.GEMINI_MODEL)
    
    all_matchups = []
    
    for image_path in image_paths:
        print(f"\n{'='*80}")
        print(f"Processing: {image_path}")
        print(f"{'='*80}")
        
        # Open image
        image = Image.open(image_path)
        
        # Create detailed extraction prompt
        prompt = """
Analyze this ESPN Fantasy Football playoff box score screenshot and extract ALL matchup data.

This shows a two-week playoff matchup. Extract the following for BOTH weeks shown:

1. **Matchup Information:**
   - Round name (e.g., "Playoff Round 1", "Playoff Round 2")
   - NFL weeks covered (e.g., "NFL Week 14 - NFL Week 15")
   - Home team name and total score
   - Away team name and total score
   - matchupPeriodId (from the page structure)

2. **For EACH Week (Week 14 AND Week 15, or Week 16 AND Week 17):**
   - Week number
   - Each week has a separate column showing player performances

3. **For EACH team, extract ALL players (starters AND bench):**

**STARTERS:**
- Slot (QB, RB, WR, TE, FLEX, D/ST, K)
- Player name
- Team position (e.g., "Ten QB", "Mia RB")
- NFL team
- Opponent (OPP column)
- Game status (STATUS column, e.g., "W 42-21", "L 24-38")
- Projected points (PROJ column) for the specific week
- Actual fantasy points (FPTS column) for the specific week

**BENCH:**
- Same fields as starters
- Note that bench players have 0.0 projected and actual points unless they were moved

4. **Week Totals:**
   - Extract "Week 14 Total", "Week 15 Total" (or Week 16/17)
   - Extract overall "TOTALS"

Return the data as a JSON array with this structure:

```json
[
  {
    "round": "Playoff Round 1 (NFL Week 14 - NFL Week 15)",
    "matchup_period": 14,
    "home_team": "Team Name",
    "away_team": "Team Name",
    "home_total": 251.38,
    "away_total": 202.4,
    "weeks": [
      {
        "week": 14,
        "home_team_data": {
          "starters": [
            {
              "slot": "QB",
              "player_name": "Ryan Tannehill",
              "team_pos": "Ten QB",
              "nfl_team": "Ten",
              "opponent": "Oak",
              "status": "W 42-21",
              "projected": 18.7,
              "actual": 27.54
            }
          ],
          "bench": [
            {
              "slot": "Bench",
              "player_name": "Le'Veon Bell",
              "team_pos": "NYJ RB",
              "nfl_team": "NYJ",
              "opponent": "Bal",
              "status": "L 21-42",
              "projected": 0.0,
              "actual": 0.0
            }
          ],
          "week_total": 111.2,
          "team_total": 202.4
        },
        "away_team_data": {
          "starters": [...],
          "bench": [...],
          "week_total": 93.6,
          "team_total": 251.38
        }
      },
      {
        "week": 15,
        "home_team_data": {...},
        "away_team_data": {...}
      }
    ]
  }
]
```

**CRITICAL:**
- Extract data for BOTH weeks shown (14 AND 15, or 16 AND 17)
- Include ALL starters and ALL bench players for each week
- Make sure projected and actual points are correctly assigned to each week
- Pay attention to which column corresponds to which week
- Return ONLY valid JSON, no markdown formatting
"""
        
        # Get extraction from Gemini
        result = gemini.analyze_screenshot(image, prompt, temperature=0.1)
        
        print(f"\nRaw Gemini Response:\n{result}\n")
        
        # Try to parse JSON
        try:
            # Clean up response
            cleaned = result.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            matchups = json.loads(cleaned)
            if isinstance(matchups, list):
                all_matchups.extend(matchups)
            else:
                all_matchups.append(matchups)
                
            print(f"✓ Successfully extracted {len(matchups) if isinstance(matchups, list) else 1} matchup(s)")
            
        except json.JSONDecodeError as e:
            print(f"✗ JSON parsing failed: {e}")
            print(f"Response was: {result[:500]}...")
    
    return all_matchups


def save_playoff_data(matchups, season=2019):
    """Save extracted playoff data to the season JSON file"""
    
    json_file = os.path.join(config.DATA_DIR, f"espn_league_{config.LEAGUE_ID}_{season}_historical.json")
    
    # Load existing data
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)
    else:
        data = {
            "season": season,
            "league_id": config.LEAGUE_ID,
            "matchups": []
        }
    
    # Remove existing playoff weeks (14-17 for 2019)
    print(f"\nRemoving existing playoff data (weeks 14-17)...")
    original_count = len(data.get("matchups", []))
    data["matchups"] = [m for m in data.get("matchups", []) if m.get("week") not in [14, 15, 16, 17]]
    removed_count = original_count - len(data["matchups"])
    print(f"Removed {removed_count} existing playoff matchup entries")
    
    # Add new playoff matchups
    print(f"\nAdding {len(matchups)} new playoff matchups...")
    for matchup_group in matchups:
        for week_data in matchup_group.get("weeks", []):
            week_num = week_data.get("week")
            matchup_period = matchup_group.get("matchup_period")
            
            # Create matchup entry for each team perspective
            matchup_entry = {
                "week": week_num,
                "season": season,
                "matchup_period": matchup_period,
                "round": matchup_group.get("round", f"Playoff Round"),
                "home_team": matchup_group.get("home_team"),
                "away_team": matchup_group.get("away_team"),
                "home_score": week_data.get("home_team_data", {}).get("week_total"),
                "away_score": week_data.get("away_team_data", {}).get("week_total"),
                "home_total_score": matchup_group.get("home_total"),
                "away_total_score": matchup_group.get("away_total"),
                "is_two_week_playoff": True,
                "home_roster": week_data.get("home_team_data", {}).get("starters", []),
                "home_bench": week_data.get("home_team_data", {}).get("bench", []),
                "away_roster": week_data.get("away_team_data", {}).get("starters", []),
                "away_bench": week_data.get("away_team_data", {}).get("bench", [])
            }
            
            data["matchups"].append(matchup_entry)
            print(f"  Added: Week {week_num} - {matchup_group.get('home_team')} vs {matchup_group.get('away_team')}")
    
    # Save back to file
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Saved to {json_file}")
    print(f"Total matchups now: {len(data['matchups'])}")


if __name__ == "__main__":
    # Define the image paths (assuming user will save them in data/screenshots/)
    screenshot_dir = os.path.join(config.DATA_DIR, "user_screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)
    
    print("="*80)
    print("2019 PLAYOFF DATA EXTRACTION FROM SCREENSHOTS")
    print("="*80)
    print(f"\nPlease save your playoff screenshots to: {screenshot_dir}")
    print("Name them sequentially, e.g.:")
    print("  - playoff_round1_matchup1.png")
    print("  - playoff_round1_matchup2.png")
    print("  - playoff_round1_matchup3.png")
    print("  - playoff_round2_matchup1.png")
    print("  - etc.")
    print("\nPress Enter when ready...")
    input()
    
    # Get all image files
    image_files = sorted([
        os.path.join(screenshot_dir, f) 
        for f in os.listdir(screenshot_dir) 
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ])
    
    if not image_files:
        print(f"No images found in {screenshot_dir}")
        exit(1)
    
    print(f"\nFound {len(image_files)} screenshots:")
    for img in image_files:
        print(f"  - {os.path.basename(img)}")
    
    # Extract data
    playoff_data = extract_playoff_data_from_images(image_files, season=2019)
    
    print(f"\n{'='*80}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*80}")
    print(f"Total playoff matchups extracted: {len(playoff_data)}")
    
    # Save to JSON
    if playoff_data:
        save_playoff_data(playoff_data, season=2019)
    else:
        print("\n✗ No data extracted. Please check the screenshots and try again.")

