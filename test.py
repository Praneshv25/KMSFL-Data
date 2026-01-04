import nflreadpy as nfl

# Use 2024 season data
print("Fetching NFL player stats for 2024...")
player_stats = nfl.load_player_stats(seasons=[2024])

print("\n" + "="*60)
print("NFL PLAYER STATS (using nflreadpy)")
print("="*60)
print(f"\nTotal records: {len(player_stats)}")
print(f"\nFirst 5 rows:")
print(player_stats.head())
print(f"\n\nAll Columns ({len(player_stats.columns)}):")
for i, col in enumerate(player_stats.columns, 1):
    print(f"{i}. {col}")

# Example: Filter for a specific player
print("\n" + "="*60)
print("Example: Justin Herbert's 2024 stats")
print("="*60)
herbert_stats = player_stats.filter(
    player_stats['player_display_name'] == 'Justin Herbert'
)
if len(herbert_stats) > 0:
    print(herbert_stats.select(['player_display_name', 'week', 'completions', 'passing_yards', 'passing_tds', 'fantasy_points_ppr']))
else:
    print("No Herbert stats found")
