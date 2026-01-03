"""
Use Gemini to extract playoff data from the images provided in the conversation
"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gemini_client import GeminiVisionClient
import config
from PIL import Image
import time

# Initialize Gemini
gemini = GeminiVisionClient(config.GEMINI_API_KEY)

# I'll process the screenshots that were provided
# The user sent 9 screenshots showing:
# Round 1 (Weeks 14-15): 3 matchups  
# Round 2 (Weeks 16-17): 3 matchups

print("Processing screenshots from conversation...")
print("I need you to save the 9 screenshots you sent to:")
print("  data/playoff_screenshots/")
print("\nName them: round1_matchup1.png, round1_matchup2.png, round1_matchup3.png")
print("           round2_matchup1.png, round2_matchup2.png, round2_matchup3.png")
print("\nPress Enter when ready...")
input()

screenshot_dir = "data/playoff_screenshots"
image_files = sorted([
    os.path.join(screenshot_dir, f)
    for f in os.listdir(screenshot_dir)
    if f.lower().endswith(('.png', '.jpg', '.jpeg'))
])

if not image_files:
    print("No images found!")
    exit(1)

print(f"\nFound {len(image_files)} images")

all_data = {"14": [], "15": [], "16": [], "17": []}

for img_path in image_files:
    print(f"\nProcessing: {os.path.basename(img_path)}")
    
    # Read image as bytes
    with open(img_path, 'rb') as f:
        image_bytes = f.read()
    
    prompt = """
Extract ALL data from this ESPN Fantasy Football playoff box score screenshot.

This shows ONE specific week of a two-week playoff matchup. Look at the page title to determine which weeks and which specific week is shown.

Return JSON with this EXACT structure:

{
  "round": "Playoff Round 1 (NFL Week 14 - NFL Week 15)" or "Playoff Round 2 (NFL Week 16 - NFL Week 17)",
  "matchup_period": 14 or 15,
  "current_week": 14, 15, 16, or 17,
  "home_team": "Team Name",
  "away_team": "Team Name",
  "home_total": 202.4,
  "away_total": 251.38,
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
}

**CRITICAL:**
1. Extract "current_week" from the active week tab or column header
2. Include ALL starters (QB, RB, RB, WR, WR, TE, FLEX, D/ST, K)
3. Include ALL bench players
4. Get the correct week's stats (not the other week's stats)
5. Return ONLY valid JSON, no markdown
"""
    
    result = gemini.analyze_screenshot(image_bytes, prompt, temperature=0.05)
    
    # Clean and parse
    cleaned = result.strip()
    for prefix in ["```json", "```"]:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    
    try:
        matchup_data = json.loads(cleaned)
        print(f"✓ Extracted: {matchup_data.get('home_team')} vs {matchup_data.get('away_team')}")
        
        # Get the week this screenshot is for
        week_num = matchup_data.get("current_week")
        matchup_period = matchup_data.get("matchup_period")
        
        if not week_num:
            print(f"✗ Could not determine week number")
            continue
        
        entry = {
            "week": week_num,
            "season": 2019,
            "matchup_period_id": matchup_period,
            "round": matchup_data.get("round"),
            "is_two_week_playoff": True,
            "home_team": matchup_data.get("home_team"),
            "away_team": matchup_data.get("away_team"),
            "home_score": matchup_data.get("home_score"),
            "away_score": matchup_data.get("away_score"),
            "home_total_score": matchup_data.get("home_total"),
            "away_total_score": matchup_data.get("away_total"),
            "home_roster": matchup_data.get("home_starters", []),
            "home_bench": matchup_data.get("home_bench", []),
            "away_roster": matchup_data.get("away_starters", []),
            "away_bench": matchup_data.get("away_bench", [])
        }
        
        all_data[str(week_num)].append(entry)
        print(f"  Added week {week_num} data")
        
        time.sleep(3)  # Rate limit
        
    except json.JSONDecodeError as e:
        print(f"✗ Failed to parse JSON: {e}")
        print(f"Response: {cleaned[:500]}")
        continue

# Save to file
print("\n" + "="*80)
print("Updating 2019 data file...")

json_file = "data/espn_league_31288798_2019_historical.json"
with open(json_file, 'r') as f:
    data = json.load(f)

# Add playoff data
for week_str, matchups in all_data.items():
    if matchups:  # Only add if we have data
        if week_str not in data["matchups"]:
            data["matchups"][week_str] = []
        data["matchups"][week_str].extend(matchups)
        print(f"✓ Added {len(matchups)} matchups for week {week_str}")

# Save
with open(json_file, 'w') as f:
    json.dump(data, f, indent=2)

print(f"\n✓ DONE! Updated {json_file}")

