"""
Extract 2019 playoff data from user-provided screenshots using Gemini Vision
"""
import json
import os
import sys
import time
from PIL import Image

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gemini_client import GeminiVisionClient
import config


def extract_box_score_from_image(image_path, gemini_client):
    """Extract detailed box score data from a single screenshot"""
    
    print(f"\nProcessing: {os.path.basename(image_path)}")
    
    # Open image
    image = Image.open(image_path)
    
    # Create detailed extraction prompt
    prompt = """
Analyze this ESPN Fantasy Football playoff box score screenshot and extract ALL data.

This is a TWO-WEEK playoff matchup. Extract data for BOTH weeks shown (check if it's Week 14 & 15, or Week 16 & 17).

Return JSON in this EXACT format:

```json
{
  "round_name": "Playoff Round 1 (NFL Week 14 - NFL Week 15)",
  "matchup_period_id": 14,
  "weeks": [14, 15],
  "home_team": "Team Name",
  "away_team": "Team Name",
  "home_total": 202.4,
  "away_total": 251.38,
  "week_14_data": {
    "home_score": 111.2,
    "away_score": 93.6,
    "home_starters": [
      {
        "slot": "QB",
        "player": "Ryan Tannehill",
        "team_pos": "Ten QB",
        "opp": "Oak",
        "status": "W 42-21",
        "proj": 18.7,
        "fpts": 27.54
      }
    ],
    "home_bench": [
      {
        "slot": "Bench",
        "player": "Le'Veon Bell",
        "team_pos": "NYJ RB",
        "opp": "Bal",
        "status": "L 21-42",
        "proj": 0.0,
        "fpts": 0.0
      }
    ],
    "away_starters": [...],
    "away_bench": [...]
  },
  "week_15_data": {
    "home_score": 97.06,
    "away_score": 137.98,
    "home_starters": [...],
    "home_bench": [...],
    "away_starters": [...],
    "away_bench": [...]
  }
}
```

**CRITICAL REQUIREMENTS:**
1. Extract data for BOTH weeks (14 & 15, or 16 & 17)
2. Include ALL starters (QB, RB, WR, TE, FLEX, D/ST, K)
3. Include ALL bench players
4. For each week, match the player stats to the correct week column
5. Return ONLY valid JSON, no markdown code blocks
"""
    
    # Get extraction from Gemini
    result = gemini_client.analyze_screenshot(image, prompt, temperature=0.1)
    
    # Clean up response
    cleaned = result.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    
    # Parse JSON
    try:
        data = json.loads(cleaned)
        print(f"✓ Successfully extracted: {data.get('home_team')} vs {data.get('away_team')}")
        return data
    except json.JSONDecodeError as e:
        print(f"✗ JSON parsing failed: {e}")
        print(f"Response preview: {cleaned[:300]}...")
        return None


def save_playoff_matchups(all_matchups, season=2019):
    """Save extracted matchups to the season JSON file"""
    
    json_file = os.path.join(config.DATA_DIR, f"espn_league_{config.LEAGUE_ID}_{season}_historical.json")
    
    # Load existing data
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Ensure matchups dict exists
    if "matchups" not in data:
        data["matchups"] = {}
    
    # Process each matchup
    for matchup in all_matchups:
        if not matchup:
            continue
            
        weeks = matchup.get("weeks", [])
        matchup_period = matchup.get("matchup_period_id")
        
        for week_num in weeks:
            week_key = f"week_{week_num}_data"
            if week_key not in matchup:
                print(f"⚠ Warning: No data for week {week_num}")
                continue
            
            week_data = matchup[week_key]
            
            # Initialize week in data structure if needed
            if str(week_num) not in data["matchups"]:
                data["matchups"][str(week_num)] = []
            
            # Create matchup entry
            matchup_entry = {
                "week": week_num,
                "season": season,
                "matchup_period_id": matchup_period,
                "round": matchup.get("round_name", f"Playoff Round"),
                "is_two_week_playoff": True,
                "home_team": matchup.get("home_team"),
                "away_team": matchup.get("away_team"),
                "home_score": week_data.get("home_score"),
                "away_score": week_data.get("away_score"),
                "home_total_score": matchup.get("home_total"),
                "away_total_score": matchup.get("away_total"),
                "home_roster": week_data.get("home_starters", []),
                "home_bench": week_data.get("home_bench", []),
                "away_roster": week_data.get("away_starters", []),
                "away_bench": week_data.get("away_bench", [])
            }
            
            data["matchups"][str(week_num)].append(matchup_entry)
            print(f"  Added: Week {week_num} - {matchup.get('home_team')} vs {matchup.get('away_team')}")
    
    # Save back to file
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Saved to {json_file}")


if __name__ == "__main__":
    print("="*80)
    print("2019 PLAYOFF DATA EXTRACTION FROM SCREENSHOTS")
    print("="*80)
    
    # Define screenshot directory
    screenshot_dir = os.path.join(config.DATA_DIR, "playoff_screenshots")
    
    print(f"\nLooking for screenshots in: {screenshot_dir}")
    
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
        print(f"\nCreated directory: {screenshot_dir}")
        print("\nPlease save your 9 playoff box score screenshots there:")
        print("  - Name them: matchup1.png, matchup2.png, etc.")
        print("  - Round 1 (Weeks 14-15): 3 matchups")
        print("  - Round 2 (Weeks 16-17): 3 matchups")
        print("\nRun this script again after adding the screenshots.")
        exit(0)
    
    # Get all image files
    image_files = sorted([
        os.path.join(screenshot_dir, f)
        for f in os.listdir(screenshot_dir)
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ])
    
    if not image_files:
        print(f"\n✗ No screenshots found in {screenshot_dir}")
        print("Please add your playoff box score screenshots and try again.")
        exit(1)
    
    print(f"\nFound {len(image_files)} screenshots:")
    for img in image_files:
        print(f"  - {os.path.basename(img)}")
    
    print("\nInitializing Gemini client...")
    gemini = GeminiVisionClient(config.GEMINI_API_KEY, config.GEMINI_MODEL)
    
    # Extract data from each screenshot
    all_matchups = []
    for img_path in image_files:
        try:
            matchup_data = extract_box_score_from_image(img_path, gemini)
            if matchup_data:
                all_matchups.append(matchup_data)
            
            # Rate limiting
            time.sleep(3)
            
        except Exception as e:
            print(f"✗ Error processing {os.path.basename(img_path)}: {e}")
            continue
    
    print(f"\n{'='*80}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*80}")
    print(f"Successfully extracted: {len(all_matchups)} matchups")
    
    # Save to JSON
    if all_matchups:
        save_playoff_matchups(all_matchups, season=2019)
        print("\n✓ 2019 playoff data has been added!")
    else:
        print("\n✗ No data extracted. Please check the screenshots.")

