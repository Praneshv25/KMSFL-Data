<script lang="ts">
    import GlassCard from "$lib/components/GlassCard.svelte";
    import { ripple } from "$lib/actions";
    import { flip } from "svelte/animate";

    const API_BASE = "http://localhost:8000/api";

    // Get data from load function
    let { data } = $props();

    // Years from API (or default)
    const years = data.years || [2025, 2024, 2023, 2022, 2021, 2020, 2019];

    let selectedYear = $state(years[0] || 2025);
    let activeTab = $state<"standings" | "matchups" | "draft">("standings");

    // Standings from API (reactive fetch on year change)
    let standings = $state(data.standings || []);

    // Matchups
    let selectedWeek = $state(1);
    let maxWeek = $state(14);
    let matchups = $state<any[]>([]);

    // Draft picks
    let draftPicks = $state<any[]>([]);

    // Fetch standings when year changes
    async function fetchStandings(year: number) {
        try {
            const res = await fetch(`${API_BASE}/teams?year=${year}`);
            const data = await res.json();
            standings = data.teams || [];
        } catch (e) {
            console.error("Failed to fetch standings:", e);
        }
    }

    // Fetch matchups when year/week changes
    async function fetchMatchups(year: number, week: number) {
        try {
            const res = await fetch(
                `${API_BASE}/matchups?year=${year}&week=${week}`,
            );
            const data = await res.json();
            // Sort matchups by bracket type: Championship > Winner's Consolation > Consolation > Regular
            const bracketOrder = (b: string | null | undefined) => {
                if (!b) return 99;
                if (b === "Championship") return 1;
                if (b.includes("Winner") && b.includes("Consolation")) return 2;
                if (b === "Consolation") return 3;
                if (b === "Toilet Bowl") return 4;
                return 99;
            };
            matchups = (data.matchups || []).sort(
                (a: any, b: any) =>
                    bracketOrder(a.bracket_type) - bracketOrder(b.bracket_type),
            );
            maxWeek = data.max_week || 14;
        } catch (e) {
            console.error("Failed to fetch matchups:", e);
        }
    }

    // Fetch draft when year changes
    async function fetchDraft(year: number) {
        try {
            const res = await fetch(`${API_BASE}/draft?year=${year}`);
            const data = await res.json();
            draftPicks = data.picks || [];
        } catch (e) {
            console.error("Failed to fetch draft:", e);
        }
    }

    // Watch for data-fetching changes
    $effect(() => {
        if (activeTab === "standings") {
            fetchStandings(selectedYear);
        } else if (activeTab === "matchups") {
            fetchMatchups(selectedYear, selectedWeek);
        } else if (activeTab === "draft") {
            fetchDraft(selectedYear);
        }
    });

    // Generate weeks array based on maxWeek
    const weeks = $derived(Array.from({ length: maxWeek }, (_, i) => i + 1));

    // Draft filters
    let draftTeamFilter = $state("");
    let draftPosFilter = $state("");
    let draftNflFilter = $state("");

    // Get unique values for filter dropdowns
    const draftTeams = $derived(
        [...new Set(draftPicks.map((p) => p.team))].sort(),
    );
    const draftPositions = $derived(
        [...new Set(draftPicks.map((p) => p.position))].filter(Boolean).sort(),
    );
    const draftNflTeams = $derived(
        [...new Set(draftPicks.map((p) => p.nfl_team))].filter(Boolean).sort(),
    );

    // Filtered draft picks
    const filteredDraftPicks = $derived(
        draftPicks.filter((pick) => {
            if (draftTeamFilter && pick.team !== draftTeamFilter) return false;
            if (draftPosFilter && pick.position !== draftPosFilter)
                return false;
            if (draftNflFilter && pick.nfl_team !== draftNflFilter)
                return false;
            return true;
        }),
    );

    // Expanded matchup state
    let expandedMatchup = $state<{ home: string; away: string } | null>(null);
    let homeRoster = $state<any>({ starters: [], bench: [] });
    let awayRoster = $state<any>({ starters: [], bench: [] });
    let loadingRosters = $state(false);

    // Player modal state
    let selectedPlayer = $state<any>(null);
    let playerStats = $state<any>(null);
    let loadingPlayer = $state(false);
    let playerModalTab = $state<"season" | "career">("season");
    let expandedCareerSeason = $state<number | null>(null);

    // Expand/collapse matchup
    async function toggleMatchup(matchup: {
        home_team: string;
        away_team: string;
    }) {
        const key = { home: matchup.home_team, away: matchup.away_team };

        if (
            expandedMatchup?.home === key.home &&
            expandedMatchup?.away === key.away
        ) {
            expandedMatchup = null;
            return;
        }

        expandedMatchup = key;
        loadingRosters = true;

        try {
            const [homeRes, awayRes] = await Promise.all([
                fetch(
                    `${API_BASE}/matchup-roster?year=${selectedYear}&week=${selectedWeek}&team=${encodeURIComponent(matchup.home_team)}`,
                ),
                fetch(
                    `${API_BASE}/matchup-roster?year=${selectedYear}&week=${selectedWeek}&team=${encodeURIComponent(matchup.away_team)}`,
                ),
            ]);

            homeRoster = homeRes.ok
                ? await homeRes.json()
                : { starters: [], bench: [] };
            awayRoster = awayRes.ok
                ? await awayRes.json()
                : { starters: [], bench: [] };
        } catch (e) {
            console.error("Failed to fetch rosters:", e);
        } finally {
            loadingRosters = false;
        }
    }

    // Helper to calculate kicker fantasy points
    function calculateKickerPoints(week: any): number {
        let points = 0;
        points += (week.fg_made_0_19 || 0) * 3;
        points += (week.fg_made_20_29 || 0) * 3;
        points += (week.fg_made_30_39 || 0) * 3;
        points += (week.fg_made_40_49 || 0) * 4;
        points += (week.fg_made_50_59 || 0) * 5;
        points += (week.fg_made_60_ || 0) * 5;
        points += (week.pat_made || 0) * 1;
        return points;
    }

    // Open player modal
    async function openPlayerModal(player: {
        player_name: string;
        position?: string;
    }) {
        selectedPlayer = player;
        loadingPlayer = true;

        try {
            // Check if D/ST player
            const isDST =
                player.position === "D/ST" ||
                player.position === "DEF" ||
                player.player_name.includes("D/ST") ||
                player.player_name.includes("Defense");

            let endpoint = isDST
                ? `${API_BASE}/dst-stats/${encodeURIComponent(player.player_name)}?year=${selectedYear}`
                : `${API_BASE}/player-stats/${encodeURIComponent(player.player_name)}?year=${selectedYear}`;

            const res = await fetch(endpoint);
            playerStats = res.ok ? await res.json() : null;

            // Calculate kicker fantasy points if position is K
            if (playerStats && playerStats.position === "K") {
                for (const season of playerStats.seasons) {
                    let seasonKickerPts = 0;
                    for (const week of season.weeks || []) {
                        const kickerPts = calculateKickerPoints(week);
                        week.fantasy_points_ppr = kickerPts;
                        seasonKickerPts += kickerPts;
                    }
                    season.fantasy_points_ppr = seasonKickerPts;
                }
            }
        } catch (e) {
            console.error("Failed to fetch player stats:", e);
        } finally {
            loadingPlayer = false;
        }
    }

    // Close player modal
    function closePlayerModal() {
        selectedPlayer = null;
        playerStats = null;
    }

    // Sort starters by position order: QB, RB, WR, TE, FLEX, K, D/ST
    const positionOrder: Record<string, number> = {
        QB: 1,
        RB: 2,
        WR: 3,
        TE: 4,
        FLEX: 5,
        K: 6,
        "D/ST": 7,
        DEF: 7,
        DST: 7,
    };

    function sortByPosition(players: any[]): any[] {
        return [...players].sort((a, b) => {
            const orderA = positionOrder[a.position] || 99;
            const orderB = positionOrder[b.position] || 99;
            if (orderA !== orderB) return orderA - orderB;
            // Secondary sort by points for same position
            return (b.points || 0) - (a.points || 0);
        });
    }

    // Sorting
    type SortKey = "rank" | "wins" | "points_for" | "points_against";
    let sortKey = $state<SortKey>("rank");
    let sortAsc = $state(true);

    function sortBy(key: SortKey) {
        if (sortKey === key) {
            sortAsc = !sortAsc;
        } else {
            sortKey = key;
            sortAsc = key === "rank";
        }
    }

    const sortedStandings = $derived(
        [...standings].sort((a, b) => {
            const multiplier = sortAsc ? 1 : -1;
            return ((a[sortKey] ?? 0) - (b[sortKey] ?? 0)) * multiplier;
        }),
    );
</script>

<svelte:head>
    <title>History Hub | The Elemental League</title>
    <meta
        name="description"
        content="The archives - Standings, matchups, and drafts from every season"
    />
</svelte:head>

<div class="container mx-auto px-6 pt-6">
    <!-- Header -->
    <header class="text-center mb-6">
        <h1
            class="text-5xl md:text-6xl"
            style="font-family: 'Luckiest Guy', cursive;"
        >
            <span class="text-4xl mr-2">📜</span>
            <span class="text-water">History Hub</span>
        </h1>
    </header>

    <!-- Year Selector -->
    <div
        class="flex justify-center mb-8 px-4 overflow-x-auto -mx-4 scrollbar-hide"
    >
        <select
            bind:value={selectedYear}
            class="md:hidden bg-white/10 backdrop-blur-lg rounded-lg px-4 py-3 text-white border border-white/20 font-medium text-center appearance-none cursor-pointer min-w-[120px]"
        >
            {#each years as year}
                <option value={year} class="bg-gray-900 text-white"
                    >{year}</option
                >
            {/each}
        </select>
        <div
            class="hidden md:inline-flex bg-white/5 backdrop-blur-lg rounded-full p-1"
        >
            {#each years as year}
                <button
                    onclick={() => (selectedYear = year)}
                    use:ripple
                    class="px-5 py-2 rounded-full text-sm font-medium transition-all
            {selectedYear === year
                        ? 'bg-amber-600/30 text-white'
                        : 'text-white/60 hover:text-white hover:bg-white/5'}"
                >
                    {year}
                </button>
            {/each}
        </div>
    </div>

    <!-- Tab Navigation -->
    <div class="flex justify-center mb-8">
        <div class="inline-flex bg-white/5 backdrop-blur-lg rounded-lg p-1">
            {#each [["standings", "📊", "Standings"], ["matchups", "⚔️", "Matchups"], ["draft", "📋", "Draft"]] as [tab, icon, label]}
                <button
                    onclick={() =>
                        (activeTab = tab as "standings" | "matchups" | "draft")}
                    use:ripple
                    class="px-6 py-3 rounded-lg flex items-center gap-2 transition-all
            {activeTab === tab
                        ? 'bg-white/10 text-white'
                        : 'text-white/60 hover:text-white'}"
                >
                    <span>{icon}</span>
                    <span>{label}</span>
                </button>
            {/each}
        </div>
    </div>

    <!-- Content Area -->
    <div class="max-w-6xl mx-auto">
        {#if activeTab === "standings"}
            <!-- Standings Table -->
            <GlassCard variant="water">
                <div class="overflow-x-auto">
                    <table class="w-full">
                        <thead>
                            <tr
                                class="text-white/60 text-sm border-b border-white/10"
                            >
                                <th class="text-left py-4 px-4">
                                    <button
                                        onclick={() => sortBy("rank")}
                                        class="hover:text-white"
                                    >
                                        # {sortKey === "rank"
                                            ? sortAsc
                                                ? "↑"
                                                : "↓"
                                            : ""}
                                    </button>
                                </th>
                                <th class="text-left py-4 px-4">Team</th>
                                <th class="text-left py-4 px-4">Owner</th>
                                <th class="text-center py-4 px-4">
                                    <button
                                        onclick={() => sortBy("wins")}
                                        class="hover:text-white"
                                    >
                                        W-L {sortKey === "wins"
                                            ? sortAsc
                                                ? "↑"
                                                : "↓"
                                            : ""}
                                    </button>
                                </th>
                                <th class="text-right py-4 px-4">
                                    <button
                                        onclick={() => sortBy("points_for")}
                                        class="hover:text-white"
                                    >
                                        PF {sortKey === "points_for"
                                            ? sortAsc
                                                ? "↑"
                                                : "↓"
                                            : ""}
                                    </button>
                                </th>
                                <th class="text-right py-4 px-4">PF/G</th>
                                <th class="text-right py-4 px-4">
                                    <button
                                        onclick={() => sortBy("points_against")}
                                        class="hover:text-white"
                                    >
                                        PA {sortKey === "points_against"
                                            ? sortAsc
                                                ? "↑"
                                                : "↓"
                                            : ""}
                                    </button>
                                </th>
                                <th class="text-right py-4 px-4">PA/G</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each sortedStandings as team (team.team_name)}
                                <tr
                                    animate:flip={{ duration: 300 }}
                                    class="border-b border-white/5 hover:bg-white/5 transition-colors"
                                >
                                    <td class="py-4 px-4">
                                        <span
                                            class="
                      inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold
                      {team.rank <= 4
                                                ? 'bg-amber-600/30 text-amber-300'
                                                : team.rank <= 6
                                                  ? 'bg-blue-600/30 text-blue-300'
                                                  : 'bg-white/10 text-white/60'}
                    "
                                        >
                                            {team.rank}
                                        </span>
                                    </td>
                                    <td class="py-4 px-4 font-medium text-white"
                                        >{team.team_name}</td
                                    >
                                    <td class="py-4 px-4 text-white/60"
                                        >{team.owner}</td
                                    >
                                    <td class="py-4 px-4 text-center font-mono">
                                        <span class="text-green-400"
                                            >{team.wins}</span
                                        >
                                        <span class="text-white/30">-</span>
                                        <span class="text-red-400"
                                            >{team.losses}</span
                                        >
                                    </td>
                                    <td
                                        class="py-4 px-4 text-right font-mono text-amber-300"
                                        >{(team.points_for || 0).toFixed(1)}</td
                                    >
                                    <td
                                        class="py-4 px-4 text-right font-mono text-amber-200/70"
                                        >{(
                                            (team.points_for || 0) /
                                            Math.max(team.wins + team.losses, 1)
                                        ).toFixed(1)}</td
                                    >
                                    <td
                                        class="py-4 px-4 text-right font-mono text-white/50"
                                        >{(team.points_against || 0).toFixed(
                                            1,
                                        )}</td
                                    >
                                    <td
                                        class="py-4 px-4 text-right font-mono text-white/40"
                                        >{(
                                            (team.points_against || 0) /
                                            Math.max(team.wins + team.losses, 1)
                                        ).toFixed(1)}</td
                                    >
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            </GlassCard>
        {:else if activeTab === "matchups"}
            <!-- Week Selector -->
            <div class="flex justify-center mb-6 px-4">
                <!-- Mobile dropdown -->
                <select
                    bind:value={selectedWeek}
                    class="md:hidden bg-white/10 backdrop-blur-lg rounded-lg px-4 py-3 text-white border border-white/20 font-medium appearance-none cursor-pointer min-w-[120px]"
                >
                    {#each weeks as week}
                        <option value={week} class="bg-gray-900 text-white"
                            >Week {week}</option
                        >
                    {/each}
                </select>
                <!-- Desktop buttons -->
                <div
                    class="hidden md:inline-flex bg-white/5 backdrop-blur-lg rounded-lg p-1 gap-1 flex-wrap justify-center"
                >
                    {#each weeks as week}
                        <button
                            onclick={() => (selectedWeek = week)}
                            class="w-10 h-10 rounded-lg text-sm font-medium transition-all
                {selectedWeek === week
                                ? 'bg-amber-600/30 text-white'
                                : 'text-white/60 hover:text-white hover:bg-white/5'}"
                        >
                            {week}
                        </button>
                    {/each}
                </div>
            </div>

            <GlassCard variant="water">
                <h3 class="text-xl font-bold mb-4 text-center">
                    Week {selectedWeek} Matchups
                </h3>
                {#if matchups.length === 0}
                    <div class="text-center py-8 text-white/40">
                        <p>No matchups found for this week</p>
                    </div>
                {:else}
                    <div class="space-y-4">
                        {#each matchups as matchup}
                            {@const bracketColor =
                                matchup.bracket_type === "Championship"
                                    ? "border-amber-500"
                                    : matchup.bracket_type?.includes(
                                            "Consolation",
                                        ) &&
                                        matchup.bracket_type?.includes("Winner")
                                      ? "border-green-500"
                                      : matchup.bracket_type === "Consolation"
                                        ? "border-blue-500"
                                        : matchup.bracket_type === "Toilet Bowl"
                                          ? "border-purple-500"
                                          : "border-transparent"}
                            <div
                                class="bg-white/5 rounded-xl overflow-hidden {matchup.bracket_type
                                    ? `border-l-4 ${bracketColor}`
                                    : ''}"
                            >
                                <!-- Bracket Badge -->
                                {#if matchup.bracket_type}
                                    <div
                                        class="px-4 pt-2 flex items-center gap-2"
                                    >
                                        <span
                                            class="text-xs font-bold uppercase tracking-wide
                                            {matchup.bracket_type ===
                                            'Championship'
                                                ? 'text-amber-400'
                                                : matchup.bracket_type.includes(
                                                        'Consolation',
                                                    ) &&
                                                    matchup.bracket_type.includes(
                                                        'Winner',
                                                    )
                                                  ? 'text-green-400'
                                                  : matchup.bracket_type ===
                                                      'Consolation'
                                                    ? 'text-blue-400'
                                                    : matchup.bracket_type ===
                                                        'Toilet Bowl'
                                                      ? 'text-purple-400'
                                                      : 'text-white/60'}"
                                        >
                                            {matchup.bracket_type ===
                                            "Championship"
                                                ? "🏆"
                                                : matchup.bracket_type ===
                                                    "Toilet Bowl"
                                                  ? "🚽"
                                                  : ""}
                                            {matchup.bracket_type}
                                        </span>
                                        {#if matchup.round}
                                            <span class="text-xs text-white/40"
                                                >• {matchup.round}</span
                                            >
                                        {/if}
                                    </div>
                                {/if}
                                <!-- Matchup Header (clickable) -->
                                <button
                                    onclick={() => toggleMatchup(matchup)}
                                    class="w-full grid grid-cols-7 items-center gap-4 p-4 hover:bg-white/10 transition-colors cursor-pointer"
                                >
                                    <!-- Home Team -->
                                    <div class="col-span-3 text-right">
                                        <div
                                            class="font-medium text-white text-sm md:text-base"
                                        >
                                            {matchup.home_team}
                                        </div>
                                        <div
                                            class="text-xl md:text-2xl font-bold {matchup.home_score >
                                            matchup.away_score
                                                ? 'text-green-400'
                                                : 'text-white/60'}"
                                        >
                                            {matchup.home_score?.toFixed(1) ||
                                                "0.0"}
                                        </div>
                                    </div>

                                    <!-- VS / Expand indicator -->
                                    <div class="col-span-1 text-center">
                                        <span class="text-2xl">
                                            {expandedMatchup?.home ===
                                                matchup.home_team &&
                                            expandedMatchup?.away ===
                                                matchup.away_team
                                                ? "▼"
                                                : "▶"}
                                        </span>
                                    </div>

                                    <!-- Away Team -->
                                    <div class="col-span-3 text-left">
                                        <div
                                            class="font-medium text-white text-sm md:text-base"
                                        >
                                            {matchup.away_team}
                                        </div>
                                        <div
                                            class="text-xl md:text-2xl font-bold {matchup.away_score >
                                            matchup.home_score
                                                ? 'text-green-400'
                                                : 'text-white/60'}"
                                        >
                                            {matchup.away_score?.toFixed(1) ||
                                                "0.0"}
                                        </div>
                                    </div>
                                </button>

                                <!-- Expanded Rosters -->
                                {#if expandedMatchup?.home === matchup.home_team && expandedMatchup?.away === matchup.away_team}
                                    <div class="border-t border-white/10 p-4">
                                        {#if loadingRosters}
                                            <div
                                                class="text-center py-8 text-white/40"
                                            >
                                                <p>Loading rosters...</p>
                                            </div>
                                        {:else}
                                            <div
                                                class="grid grid-cols-1 lg:grid-cols-2 gap-4"
                                            >
                                                <!-- Home Roster -->
                                                <div>
                                                    <h4
                                                        class="font-bold text-center mb-3 text-amber-300"
                                                    >
                                                        {matchup.home_team}
                                                    </h4>
                                                    <div class="space-y-1">
                                                        {#each sortByPosition(homeRoster.starters) as player}
                                                            <button
                                                                onclick={() =>
                                                                    openPlayerModal(
                                                                        player,
                                                                    )}
                                                                class="w-full flex items-center justify-between p-2 bg-white/5 rounded hover:bg-white/10 transition-colors text-left"
                                                            >
                                                                <div
                                                                    class="flex items-center gap-2"
                                                                >
                                                                    <span
                                                                        class="text-xs px-1.5 py-0.5 rounded bg-white/10 text-white/60"
                                                                        >{player.position}</span
                                                                    >
                                                                    <span
                                                                        class="text-white text-sm"
                                                                        >{player.player_name}</span
                                                                    >
                                                                </div>
                                                                <div
                                                                    class="flex items-center gap-2"
                                                                >
                                                                    {#if player.projected > 0}
                                                                        <span
                                                                            class="text-xs text-white/30"
                                                                        >
                                                                            proj:
                                                                            {player.projected?.toFixed(
                                                                                1,
                                                                            )}
                                                                        </span>
                                                                    {/if}
                                                                    <span
                                                                        class="font-mono text-sm font-bold {player.points >
                                                                        15
                                                                            ? 'text-green-400'
                                                                            : player.points >
                                                                                10
                                                                              ? 'text-amber-300'
                                                                              : 'text-white/60'}"
                                                                    >
                                                                        {player.points?.toFixed(
                                                                            1,
                                                                        ) ||
                                                                            "0.0"}
                                                                    </span>
                                                                </div>
                                                            </button>
                                                        {/each}
                                                        {#if homeRoster.bench?.length > 0}
                                                            <div
                                                                class="text-xs text-white/40 mt-2 mb-1 uppercase"
                                                            >
                                                                Bench
                                                            </div>
                                                            {#each homeRoster.bench as player}
                                                                <button
                                                                    onclick={() =>
                                                                        openPlayerModal(
                                                                            player,
                                                                        )}
                                                                    class="w-full flex items-center justify-between p-2 bg-white/3 rounded hover:bg-white/5 transition-colors text-left opacity-60"
                                                                >
                                                                    <div
                                                                        class="flex items-center gap-2"
                                                                    >
                                                                        <span
                                                                            class="text-xs px-1.5 py-0.5 rounded bg-white/10 text-white/60"
                                                                            >{player.position}</span
                                                                        >
                                                                        <span
                                                                            class="text-white text-sm"
                                                                            >{player.player_name}</span
                                                                        >
                                                                    </div>
                                                                    <span
                                                                        class="font-mono text-sm text-white/40"
                                                                    >
                                                                        {player.points?.toFixed(
                                                                            1,
                                                                        ) ||
                                                                            "0.0"}
                                                                    </span>
                                                                </button>
                                                            {/each}
                                                        {/if}
                                                    </div>
                                                </div>

                                                <!-- Away Roster -->
                                                <div>
                                                    <h4
                                                        class="font-bold text-center mb-3 text-blue-300"
                                                    >
                                                        {matchup.away_team}
                                                    </h4>
                                                    <div class="space-y-1">
                                                        {#each sortByPosition(awayRoster.starters) as player}
                                                            <button
                                                                onclick={() =>
                                                                    openPlayerModal(
                                                                        player,
                                                                    )}
                                                                class="w-full flex items-center justify-between p-2 bg-white/5 rounded hover:bg-white/10 transition-colors text-left"
                                                            >
                                                                <div
                                                                    class="flex items-center gap-2"
                                                                >
                                                                    <span
                                                                        class="text-xs px-1.5 py-0.5 rounded bg-white/10 text-white/60"
                                                                        >{player.position}</span
                                                                    >
                                                                    <span
                                                                        class="text-white text-sm"
                                                                        >{player.player_name}</span
                                                                    >
                                                                </div>
                                                                <div
                                                                    class="flex items-center gap-2"
                                                                >
                                                                    {#if player.projected > 0}
                                                                        <span
                                                                            class="text-xs text-white/30"
                                                                        >
                                                                            proj:
                                                                            {player.projected?.toFixed(
                                                                                1,
                                                                            )}
                                                                        </span>
                                                                    {/if}
                                                                    <span
                                                                        class="font-mono text-sm font-bold {player.points >
                                                                        15
                                                                            ? 'text-green-400'
                                                                            : player.points >
                                                                                10
                                                                              ? 'text-amber-300'
                                                                              : 'text-white/60'}"
                                                                    >
                                                                        {player.points?.toFixed(
                                                                            1,
                                                                        ) ||
                                                                            "0.0"}
                                                                    </span>
                                                                </div>
                                                            </button>
                                                        {/each}
                                                        {#if awayRoster.bench?.length > 0}
                                                            <div
                                                                class="text-xs text-white/40 mt-2 mb-1 uppercase"
                                                            >
                                                                Bench
                                                            </div>
                                                            {#each awayRoster.bench as player}
                                                                <button
                                                                    onclick={() =>
                                                                        openPlayerModal(
                                                                            player,
                                                                        )}
                                                                    class="w-full flex items-center justify-between p-2 bg-white/3 rounded hover:bg-white/5 transition-colors text-left opacity-60"
                                                                >
                                                                    <div
                                                                        class="flex items-center gap-2"
                                                                    >
                                                                        <span
                                                                            class="text-xs px-1.5 py-0.5 rounded bg-white/10 text-white/60"
                                                                            >{player.position}</span
                                                                        >
                                                                        <span
                                                                            class="text-white text-sm"
                                                                            >{player.player_name}</span
                                                                        >
                                                                    </div>
                                                                    <span
                                                                        class="font-mono text-sm text-white/40"
                                                                    >
                                                                        {player.points?.toFixed(
                                                                            1,
                                                                        ) ||
                                                                            "0.0"}
                                                                    </span>
                                                                </button>
                                                            {/each}
                                                        {/if}
                                                    </div>
                                                </div>
                                            </div>
                                        {/if}
                                    </div>
                                {/if}
                            </div>
                        {/each}
                    </div>
                {/if}
            </GlassCard>
        {:else}
            <!-- Draft Board -->
            <GlassCard variant="water">
                <h3 class="text-xl font-bold mb-4 text-center">
                    {selectedYear} Draft Board
                </h3>
                {#if draftPicks.length === 0}
                    <div class="text-center py-8 text-white/40">
                        <p>No draft data available for this season</p>
                    </div>
                {:else}
                    <!-- Filters -->
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                        <div>
                            <label class="block text-white/60 text-sm mb-1"
                                >Team</label
                            >
                            <select
                                bind:value={draftTeamFilter}
                                class="w-full bg-white/10 backdrop-blur-lg rounded-lg px-3 py-2 text-white border border-white/20 text-sm"
                            >
                                <option value="" class="bg-gray-900"
                                    >All Teams</option
                                >
                                {#each draftTeams as team}
                                    <option value={team} class="bg-gray-900"
                                        >{team}</option
                                    >
                                {/each}
                            </select>
                        </div>
                        <div>
                            <label class="block text-white/60 text-sm mb-1"
                                >Position</label
                            >
                            <select
                                bind:value={draftPosFilter}
                                class="w-full bg-white/10 backdrop-blur-lg rounded-lg px-3 py-2 text-white border border-white/20 text-sm"
                            >
                                <option value="" class="bg-gray-900"
                                    >All Positions</option
                                >
                                {#each draftPositions as pos}
                                    <option value={pos} class="bg-gray-900"
                                        >{pos}</option
                                    >
                                {/each}
                            </select>
                        </div>
                        <div>
                            <label class="block text-white/60 text-sm mb-1"
                                >NFL Team</label
                            >
                            <select
                                bind:value={draftNflFilter}
                                class="w-full bg-white/10 backdrop-blur-lg rounded-lg px-3 py-2 text-white border border-white/20 text-sm"
                            >
                                <option value="" class="bg-gray-900"
                                    >All NFL Teams</option
                                >
                                {#each draftNflTeams as nfl}
                                    <option value={nfl} class="bg-gray-900"
                                        >{nfl}</option
                                    >
                                {/each}
                            </select>
                        </div>
                    </div>

                    <p class="text-center text-white/40 text-sm mb-4">
                        Showing {filteredDraftPicks.length} of {draftPicks.length}
                        picks
                    </p>

                    <div class="overflow-x-auto max-h-[600px] overflow-y-auto">
                        <table class="w-full">
                            <thead
                                class="sticky top-0 bg-gray-900/90 backdrop-blur-sm"
                            >
                                <tr
                                    class="text-white/60 text-sm border-b border-white/10"
                                >
                                    <th class="text-left py-3 px-4">Pick</th>
                                    <th class="text-left py-3 px-4">Team</th>
                                    <th class="text-left py-3 px-4">Player</th>
                                    <th class="text-center py-3 px-4">Pos</th>
                                    <th class="text-left py-3 px-4">NFL Team</th
                                    >
                                </tr>
                            </thead>
                            <tbody>
                                {#each filteredDraftPicks as pick}
                                    <tr
                                        class="border-b border-white/5 hover:bg-white/5 transition-colors"
                                    >
                                        <td class="py-3 px-4">
                                            <span
                                                class="font-mono text-amber-300"
                                            >
                                                {pick.round}.{pick.pick}
                                            </span>
                                            <span
                                                class="text-white/40 text-xs ml-2"
                                            >
                                                ({pick.overall_pick})
                                            </span>
                                        </td>
                                        <td
                                            class="py-3 px-4 text-white/60 text-sm"
                                            >{pick.team}</td
                                        >
                                        <td
                                            class="py-3 px-4 font-medium text-white cursor-pointer hover:text-amber-300 transition-colors"
                                            onclick={() =>
                                                openPlayerModal({
                                                    player_name:
                                                        pick.player_name,
                                                    position: pick.position,
                                                })}>{pick.player_name}</td
                                        >
                                        <td class="py-3 px-4 text-center">
                                            <span
                                                class="px-2 py-1 rounded text-xs font-bold
                                                {pick.position === 'QB'
                                                    ? 'bg-red-500/30 text-red-300'
                                                    : pick.position === 'RB'
                                                      ? 'bg-green-500/30 text-green-300'
                                                      : pick.position === 'WR'
                                                        ? 'bg-blue-500/30 text-blue-300'
                                                        : pick.position === 'TE'
                                                          ? 'bg-purple-500/30 text-purple-300'
                                                          : pick.position ===
                                                              'K'
                                                            ? 'bg-yellow-500/30 text-yellow-300'
                                                            : pick.position ===
                                                                'D/ST'
                                                              ? 'bg-orange-500/30 text-orange-300'
                                                              : 'bg-gray-500/30 text-gray-300'}"
                                            >
                                                {pick.position}
                                            </span>
                                        </td>
                                        <td class="py-3 px-4 text-white/50"
                                            >{pick.nfl_team || "-"}</td
                                        >
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                {/if}
            </GlassCard>
        {/if}
    </div>
</div>

<!-- Player Stats Modal (Legacy Dashboard Style) -->
{#if selectedPlayer}
    <div
        class="player-modal-overlay"
        onclick={(e) => {
            if (e.target === e.currentTarget) closePlayerModal();
        }}
        role="dialog"
    >
        <div class="player-modal">
            <!-- Gradient Header with Player Photo -->
            <div class="player-header">
                {#if playerStats?.headshot_url}
                    <img
                        src={playerStats.headshot_url}
                        alt={selectedPlayer.player_name}
                        class="player-photo"
                    />
                {:else}
                    <div class="player-photo-placeholder">👤</div>
                {/if}
                <div class="player-info">
                    <div class="player-name">{selectedPlayer.player_name}</div>
                    <div class="player-position">
                        {playerStats?.position || selectedPlayer.position} • {selectedPlayer.nfl_team ||
                            ""}
                    </div>
                </div>
                <button class="modal-close" onclick={closePlayerModal}>✕</button
                >
            </div>

            <!-- Tabs -->
            <div class="player-tabs">
                <button
                    class="player-tab {playerModalTab === 'season'
                        ? 'active'
                        : ''}"
                    onclick={() => (playerModalTab = "season")}
                >
                    {selectedYear} Season
                </button>
                <button
                    class="player-tab {playerModalTab === 'career'
                        ? 'active'
                        : ''}"
                    onclick={() => (playerModalTab = "career")}
                >
                    Career Stats
                </button>
            </div>

            <!-- Content -->
            <div class="player-content">
                {#if loadingPlayer}
                    <div class="player-loading">Loading player stats...</div>
                {:else if playerStats && playerStats.seasons?.length > 0}
                    {#if playerModalTab === "season"}
                        {@const currentSeason =
                            playerStats.seasons.find(
                                (s) => s.season === selectedYear,
                            ) || playerStats.seasons[0]}
                        <!-- Season Summary Stats -->
                        <div class="season-summary">
                            <div class="summary-stat">
                                <div class="summary-value">
                                    {currentSeason.games}
                                </div>
                                <div class="summary-label">GAMES</div>
                            </div>
                            {#if playerStats.position === "QB"}
                                <div class="summary-stat">
                                    <div class="summary-value">
                                        {currentSeason.passing_yards}
                                    </div>
                                    <div class="summary-label">PASS YDS</div>
                                </div>
                                <div class="summary-stat">
                                    <div class="summary-value">
                                        {currentSeason.passing_tds}
                                    </div>
                                    <div class="summary-label">PASS TDS</div>
                                </div>
                                <div class="summary-stat">
                                    <div class="summary-value">
                                        {currentSeason.interceptions}
                                    </div>
                                    <div class="summary-label">INTS</div>
                                </div>
                            {:else if playerStats.position === "RB"}
                                <div class="summary-stat">
                                    <div class="summary-value">
                                        {currentSeason.rushing_yards}
                                    </div>
                                    <div class="summary-label">RUSH YDS</div>
                                </div>
                                <div class="summary-stat">
                                    <div class="summary-value">
                                        {currentSeason.rushing_tds}
                                    </div>
                                    <div class="summary-label">RUSH TDS</div>
                                </div>
                                <div class="summary-stat">
                                    <div class="summary-value">
                                        {currentSeason.receptions}
                                    </div>
                                    <div class="summary-label">REC</div>
                                </div>
                            {:else if playerStats.position === "K"}
                                <div class="summary-stat">
                                    <div class="summary-value">
                                        {currentSeason.fg_made ||
                                            0}/{currentSeason.fg_att || 0}
                                    </div>
                                    <div class="summary-label">FG MADE/ATT</div>
                                </div>
                                <div class="summary-stat">
                                    <div class="summary-value">
                                        {currentSeason.fg_att > 0
                                            ? (
                                                  (currentSeason.fg_made /
                                                      currentSeason.fg_att) *
                                                  100
                                              ).toFixed(1)
                                            : 0}%
                                    </div>
                                    <div class="summary-label">FG %</div>
                                </div>
                                <div class="summary-stat">
                                    <div class="summary-value">
                                        {currentSeason.pat_made ||
                                            0}/{currentSeason.pat_att || 0}
                                    </div>
                                    <div class="summary-label">XP MADE/ATT</div>
                                </div>
                                <div class="summary-stat">
                                    <div class="summary-value">
                                        {currentSeason.fg_long || 0}
                                    </div>
                                    <div class="summary-label">LONGEST FG</div>
                                </div>
                            {:else if playerStats.position === "D/ST" || playerStats.position === "DEF"}
                                <div class="summary-stat">
                                    <div class="summary-value">
                                        {currentSeason.def_sacks || 0}
                                    </div>
                                    <div class="summary-label">SACKS</div>
                                </div>
                                <div class="summary-stat">
                                    <div class="summary-value">
                                        {currentSeason.def_interceptions || 0}
                                    </div>
                                    <div class="summary-label">INTS</div>
                                </div>
                                <div class="summary-stat">
                                    <div class="summary-value">
                                        {currentSeason.def_fumbles_recovered ||
                                            0}
                                    </div>
                                    <div class="summary-label">FUMBLES REC</div>
                                </div>
                                <div class="summary-stat">
                                    <div class="summary-value">
                                        {currentSeason.def_touchdowns || 0}
                                    </div>
                                    <div class="summary-label">DEF TDS</div>
                                </div>
                            {:else}
                                <div class="summary-stat">
                                    <div class="summary-value">
                                        {currentSeason.receptions}
                                    </div>
                                    <div class="summary-label">REC</div>
                                </div>
                                <div class="summary-stat">
                                    <div class="summary-value">
                                        {currentSeason.receiving_yards}
                                    </div>
                                    <div class="summary-label">REC YDS</div>
                                </div>
                                <div class="summary-stat">
                                    <div class="summary-value">
                                        {currentSeason.receiving_tds}
                                    </div>
                                    <div class="summary-label">REC TDS</div>
                                </div>
                            {/if}
                            <div class="summary-stat highlight">
                                <div class="summary-value">
                                    {currentSeason.fantasy_points_ppr}
                                </div>
                                <div class="summary-label">FANT PTS (PPR)</div>
                            </div>
                        </div>

                        <!-- Weekly Table -->
                        {#if currentSeason.weeks?.length > 0}
                            <div class="stats-table-container">
                                <table class="stats-table">
                                    <thead>
                                        <tr>
                                            <th>Week</th>
                                            <th>Opp</th>
                                            {#if playerStats.position === "QB"}
                                                <th>Cmp/Att</th>
                                                <th>Pass Yds</th>
                                                <th>Pass TD</th>
                                                <th>INT</th>
                                                <th>Rush Yds</th>
                                                <th>Rush TD</th>
                                            {:else if playerStats.position === "RB"}
                                                <th>Carries</th>
                                                <th>Rush Yds</th>
                                                <th>Rush TD</th>
                                                <th>Rec</th>
                                                <th>Rec Yds</th>
                                                <th>Rec TD</th>
                                            {:else if playerStats.position === "K"}
                                                <th>0-19</th>
                                                <th>20-29</th>
                                                <th>30-39</th>
                                                <th>40-49</th>
                                                <th>50+</th>
                                                <th>XP</th>
                                                <th>Long</th>
                                            {:else if playerStats.position === "D/ST" || playerStats.position === "DEF"}
                                                <th>Sacks</th>
                                                <th>INTs</th>
                                                <th>Fum Rec</th>
                                                <th>Def TDs</th>
                                                <th>ST TDs</th>
                                                <th>Pts Allow</th>
                                            {:else}
                                                <th>Tgt</th>
                                                <th>Rec</th>
                                                <th>Rec Yds</th>
                                                <th>Rec TD</th>
                                                <th>Rush Yds</th>
                                                <th>Rush TD</th>
                                            {/if}
                                            <th class="fant-pts">Fant Pts</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {#each currentSeason.weeks as week}
                                            <tr>
                                                <td>{week.week}</td>
                                                <td>{week.opponent || "-"}</td>
                                                {#if playerStats.position === "QB"}
                                                    <td
                                                        >{week.completions ||
                                                            0}/{week.attempts ||
                                                            0}</td
                                                    >
                                                    <td
                                                        >{week.passing_yards ||
                                                            0}</td
                                                    >
                                                    <td
                                                        >{week.passing_tds ||
                                                            0}</td
                                                    >
                                                    <td
                                                        >{week.interceptions ||
                                                            0}</td
                                                    >
                                                    <td
                                                        >{week.rushing_yards ||
                                                            0}</td
                                                    >
                                                    <td
                                                        >{week.rushing_tds ||
                                                            0}</td
                                                    >
                                                {:else if playerStats.position === "RB"}
                                                    <td>{week.carries || 0}</td>
                                                    <td
                                                        >{week.rushing_yards ||
                                                            0}</td
                                                    >
                                                    <td
                                                        >{week.rushing_tds ||
                                                            0}</td
                                                    >
                                                    <td
                                                        >{week.receptions ||
                                                            0}</td
                                                    >
                                                    <td
                                                        >{week.receiving_yards ||
                                                            0}</td
                                                    >
                                                    <td
                                                        >{week.receiving_tds ||
                                                            0}</td
                                                    >
                                                {:else if playerStats.position === "K"}
                                                    <td
                                                        >{week.fg_made_0_19 ||
                                                            0}/{(week.fg_made_0_19 ||
                                                            0) +
                                                            (week.fg_missed_0_19 ||
                                                                0)}</td
                                                    >
                                                    <td
                                                        >{week.fg_made_20_29 ||
                                                            0}/{(week.fg_made_20_29 ||
                                                            0) +
                                                            (week.fg_missed_20_29 ||
                                                                0)}</td
                                                    >
                                                    <td
                                                        >{week.fg_made_30_39 ||
                                                            0}/{(week.fg_made_30_39 ||
                                                            0) +
                                                            (week.fg_missed_30_39 ||
                                                                0)}</td
                                                    >
                                                    <td
                                                        >{week.fg_made_40_49 ||
                                                            0}/{(week.fg_made_40_49 ||
                                                            0) +
                                                            (week.fg_missed_40_49 ||
                                                                0)}</td
                                                    >
                                                    <td
                                                        >{(week.fg_made_50_59 ||
                                                            0) +
                                                            (week.fg_made_60_ ||
                                                                0)}/{(week.fg_made_50_59 ||
                                                            0) +
                                                            (week.fg_made_60_ ||
                                                                0) +
                                                            (week.fg_missed_50_59 ||
                                                                0) +
                                                            (week.fg_missed_60_ ||
                                                                0)}</td
                                                    >
                                                    <td
                                                        >{week.pat_made ||
                                                            0}/{week.pat_att ||
                                                            0}</td
                                                    >
                                                    <td>{week.fg_long || 0}</td>
                                                {:else if playerStats.position === "D/ST" || playerStats.position === "DEF"}
                                                    <td
                                                        >{week.def_sacks ||
                                                            0}</td
                                                    >
                                                    <td
                                                        >{week.def_interceptions ||
                                                            0}</td
                                                    >
                                                    <td
                                                        >{week.def_fumbles_recovered ||
                                                            0}</td
                                                    >
                                                    <td
                                                        >{week.def_touchdowns ||
                                                            0}</td
                                                    >
                                                    <td
                                                        >{week.special_teams_tds ||
                                                            0}</td
                                                    >
                                                    <td
                                                        >{week.points_allowed ||
                                                            0}</td
                                                    >
                                                {:else}
                                                    <td>{week.targets || 0}</td>
                                                    <td
                                                        >{week.receptions ||
                                                            0}</td
                                                    >
                                                    <td
                                                        >{week.receiving_yards ||
                                                            0}</td
                                                    >
                                                    <td
                                                        >{week.receiving_tds ||
                                                            0}</td
                                                    >
                                                    <td
                                                        >{week.rushing_yards ||
                                                            0}</td
                                                    >
                                                    <td
                                                        >{week.rushing_tds ||
                                                            0}</td
                                                    >
                                                {/if}
                                                <td class="fant-pts"
                                                    >{week.fantasy_points_ppr}</td
                                                >
                                            </tr>
                                        {/each}
                                    </tbody>
                                </table>
                            </div>
                        {/if}
                    {:else}
                        <!-- Career Stats -->
                        <div class="career-header">
                            Career Summary by Season (Click to expand)
                        </div>
                        <div class="stats-table-container">
                            <table class="stats-table">
                                <thead>
                                    <tr>
                                        <th></th>
                                        <th>Season</th>
                                        <th>Games</th>
                                        {#if playerStats.position === "QB"}
                                            <th>Pass Yds</th>
                                            <th>Pass TD</th>
                                            <th>INT</th>
                                            <th>Rush Yds</th>
                                            <th>Rush TD</th>
                                        {:else if playerStats.position === "RB"}
                                            <th>Rush Yds</th>
                                            <th>Rush TD</th>
                                            <th>Rec</th>
                                            <th>Rec Yds</th>
                                            <th>Rec TD</th>
                                        {:else if playerStats.position === "K"}
                                            <th>FG Made/Att</th>
                                            <th>FG %</th>
                                            <th>XP Made/Att</th>
                                            <th>Long</th>
                                        {:else if playerStats.position === "D/ST" || playerStats.position === "DEF"}
                                            <th>Sacks</th>
                                            <th>INTs</th>
                                            <th>Fum Rec</th>
                                            <th>Def TDs</th>
                                        {:else}
                                            <th>Rec</th>
                                            <th>Rec Yds</th>
                                            <th>Rec TD</th>
                                            <th>Rush Yds</th>
                                            <th>Rush TD</th>
                                        {/if}
                                        <th class="fant-pts">Fant Pts (PPR)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {#each playerStats.seasons as season}
                                        <tr
                                            class="season-row"
                                            onclick={() =>
                                                (expandedCareerSeason =
                                                    expandedCareerSeason ===
                                                    season.season
                                                        ? null
                                                        : season.season)}
                                        >
                                            <td
                                                >{expandedCareerSeason ===
                                                season.season
                                                    ? "▼"
                                                    : "▶"}</td
                                            >
                                            <td
                                                ><strong>{season.season}</strong
                                                ></td
                                            >
                                            <td>{season.games}</td>
                                            {#if playerStats.position === "QB"}
                                                <td>{season.passing_yards}</td>
                                                <td>{season.passing_tds}</td>
                                                <td>{season.interceptions}</td>
                                                <td>{season.rushing_yards}</td>
                                                <td>{season.rushing_tds}</td>
                                            {:else if playerStats.position === "RB"}
                                                <td>{season.rushing_yards}</td>
                                                <td>{season.rushing_tds}</td>
                                                <td>{season.receptions}</td>
                                                <td>{season.receiving_yards}</td
                                                >
                                                <td>{season.receiving_tds}</td>
                                            {:else if playerStats.position === "K"}
                                                <td
                                                    >{season.fg_made ||
                                                        0}/{season.fg_att ||
                                                        0}</td
                                                >
                                                <td
                                                    >{season.fg_att > 0
                                                        ? (
                                                              (season.fg_made /
                                                                  season.fg_att) *
                                                              100
                                                          ).toFixed(1)
                                                        : 0}%</td
                                                >
                                                <td
                                                    >{season.pat_made ||
                                                        0}/{season.pat_att ||
                                                        0}</td
                                                >
                                                <td>{season.fg_long || 0}</td>
                                            {:else if playerStats.position === "D/ST" || playerStats.position === "DEF"}
                                                <td>{season.def_sacks || 0}</td>
                                                <td
                                                    >{season.def_interceptions ||
                                                        0}</td
                                                >
                                                <td
                                                    >{season.def_fumbles_recovered ||
                                                        0}</td
                                                >
                                                <td
                                                    >{season.def_touchdowns ||
                                                        0}</td
                                                >
                                            {:else}
                                                <td>{season.receptions}</td>
                                                <td>{season.receiving_yards}</td
                                                >
                                                <td>{season.receiving_tds}</td>
                                                <td>{season.rushing_yards}</td>
                                                <td>{season.rushing_tds}</td>
                                            {/if}
                                            <td class="fant-pts"
                                                ><strong
                                                    >{season.fantasy_points_ppr}</strong
                                                ></td
                                            >
                                        </tr>
                                        {#if expandedCareerSeason === season.season && season.weeks?.length > 0}
                                            <tr class="expanded-weeks-header">
                                                <td colspan={99}
                                                    >Week-by-Week Stats for {season.season}</td
                                                >
                                            </tr>
                                            {#each season.weeks as week}
                                                <tr class="expanded-week">
                                                    <td></td>
                                                    <td>Week {week.week}</td>
                                                    <td
                                                        >{week.opponent ||
                                                            "-"}</td
                                                    >
                                                    {#if playerStats.position === "QB"}
                                                        <td
                                                            >{week.passing_yards ||
                                                                0}</td
                                                        >
                                                        <td
                                                            >{week.passing_tds ||
                                                                0}</td
                                                        >
                                                        <td
                                                            >{week.interceptions ||
                                                                0}</td
                                                        >
                                                        <td
                                                            >{week.rushing_yards ||
                                                                0}</td
                                                        >
                                                        <td
                                                            >{week.rushing_tds ||
                                                                0}</td
                                                        >
                                                    {:else if playerStats.position === "RB"}
                                                        <td
                                                            >{week.rushing_yards ||
                                                                0}</td
                                                        >
                                                        <td
                                                            >{week.rushing_tds ||
                                                                0}</td
                                                        >
                                                        <td
                                                            >{week.receptions ||
                                                                0}</td
                                                        >
                                                        <td
                                                            >{week.receiving_yards ||
                                                                0}</td
                                                        >
                                                        <td
                                                            >{week.receiving_tds ||
                                                                0}</td
                                                        >
                                                    {:else if playerStats.position === "K"}
                                                        <td
                                                            >{week.fg_made ||
                                                                0}/{week.fg_att ||
                                                                0}</td
                                                        >
                                                        <td
                                                            >{week.fg_att > 0
                                                                ? (
                                                                      ((week.fg_made ||
                                                                          0) /
                                                                          week.fg_att) *
                                                                      100
                                                                  ).toFixed(0)
                                                                : 0}%</td
                                                        >
                                                        <td
                                                            >{week.pat_made ||
                                                                0}/{week.pat_att ||
                                                                0}</td
                                                        >
                                                        <td
                                                            >{week.fg_long ||
                                                                0}</td
                                                        >
                                                    {:else if playerStats.position === "D/ST" || playerStats.position === "DEF"}
                                                        <td
                                                            >{week.def_sacks ||
                                                                0}</td
                                                        >
                                                        <td
                                                            >{week.def_interceptions ||
                                                                0}</td
                                                        >
                                                        <td
                                                            >{week.def_fumbles_recovered ||
                                                                0}</td
                                                        >
                                                        <td
                                                            >{week.def_touchdowns ||
                                                                0}</td
                                                        >
                                                    {:else}
                                                        <td
                                                            >{week.receptions ||
                                                                0}</td
                                                        >
                                                        <td
                                                            >{week.receiving_yards ||
                                                                0}</td
                                                        >
                                                        <td
                                                            >{week.receiving_tds ||
                                                                0}</td
                                                        >
                                                        <td
                                                            >{week.rushing_yards ||
                                                                0}</td
                                                        >
                                                        <td
                                                            >{week.rushing_tds ||
                                                                0}</td
                                                        >
                                                    {/if}
                                                    <td class="fant-pts"
                                                        >{week.fantasy_points_ppr}</td
                                                    >
                                                </tr>
                                            {/each}
                                        {/if}
                                    {/each}
                                </tbody>
                            </table>
                        </div>
                    {/if}
                {:else}
                    <div class="player-loading">
                        No stats available for this player
                    </div>
                {/if}
            </div>
        </div>
    </div>
{/if}

<style>
    .text-water {
        background: linear-gradient(135deg, #4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Modal Styles */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(4px);
        z-index: 100;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
    }

    .modal-container {
        background: #1a1a2e;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 1rem;
        width: 100%;
        max-width: 400px;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }

    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        position: sticky;
        top: 0;
        background: #1a1a2e;
    }

    .modal-title {
        font-size: 1.25rem;
        font-weight: bold;
        color: white;
    }

    .modal-subtitle {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-top: 0.25rem;
    }

    .position-badge {
        font-size: 0.75rem;
        padding: 0.125rem 0.5rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 0.25rem;
        color: rgba(255, 255, 255, 0.7);
    }

    .nfl-team {
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.4);
    }

    .close-btn {
        font-size: 1.5rem;
        color: rgba(255, 255, 255, 0.5);
        background: none;
        border: none;
        cursor: pointer;
        padding: 0.25rem 0.5rem;
        line-height: 1;
    }

    .close-btn:hover {
        color: white;
    }

    .modal-body {
        padding: 1rem;
    }

    .loading-state,
    .no-data {
        text-align: center;
        padding: 2rem;
        color: rgba(255, 255, 255, 0.4);
    }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }

    .stat-box {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 0.5rem;
        padding: 0.75rem;
        text-align: center;
    }

    .stat-value {
        font-size: 1.5rem;
        font-weight: bold;
    }

    .stat-value.amber {
        color: #fbbf24;
    }
    .stat-value.blue {
        color: #60a5fa;
    }
    .stat-value.green {
        color: #34d399;
    }

    .stat-label {
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.5);
    }

    .weekly-header {
        font-size: 0.875rem;
        font-weight: bold;
        color: rgba(255, 255, 255, 0.7);
        margin-bottom: 0.75rem;
    }

    .weekly-list {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        max-height: 250px;
        overflow-y: auto;
    }

    .weekly-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.5rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 0.25rem;
        font-size: 0.875rem;
    }

    .week-label {
        color: rgba(255, 255, 255, 0.6);
    }

    .start-status {
        font-size: 0.75rem;
    }

    .start-status.started {
        color: #34d399;
    }
    .start-status.bench {
        color: rgba(255, 255, 255, 0.3);
    }

    .week-points {
        font-family: monospace;
        color: rgba(255, 255, 255, 0.8);
    }

    /* Legacy-style Player Modal - Dark Glassmorphism */
    .player-modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.9);
        backdrop-filter: blur(12px);
        z-index: 200;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
    }

    .player-modal {
        background: linear-gradient(
            135deg,
            rgba(20, 20, 35, 0.98),
            rgba(30, 30, 50, 0.98)
        );
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 1.5rem;
        width: 100%;
        max-width: 900px;
        max-height: 90vh;
        overflow: hidden;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
        display: flex;
        flex-direction: column;
    }

    .player-header {
        background: linear-gradient(
            135deg,
            rgba(30, 41, 59, 0.95) 0%,
            rgba(51, 65, 85, 0.95) 100%
        );
        border-bottom: 1px solid rgba(96, 165, 250, 0.2);
        padding: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .player-photo {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid rgba(255, 255, 255, 0.3);
    }

    .player-photo-placeholder {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }

    .player-info {
        flex: 1;
    }

    .player-name {
        font-size: 1.5rem;
        font-weight: bold;
        color: white;
    }

    .player-position {
        font-size: 0.875rem;
        color: rgba(255, 255, 255, 0.8);
    }

    .modal-close {
        background: rgba(0, 0, 0, 0.2);
        border: none;
        color: white;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        font-size: 1.25rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .modal-close:hover {
        background: rgba(0, 0, 0, 0.4);
    }

    .player-tabs {
        display: flex;
        background: rgba(0, 0, 0, 0.3);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .player-tab {
        flex: 1;
        padding: 1rem;
        background: none;
        border: none;
        font-size: 0.9rem;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.5);
        cursor: pointer;
        border-bottom: 3px solid transparent;
        transition: all 0.2s;
    }

    .player-tab:hover {
        color: rgba(255, 255, 255, 0.8);
        background: rgba(255, 255, 255, 0.05);
    }

    .player-tab.active {
        color: #60a5fa;
        border-bottom-color: #60a5fa;
        background: rgba(255, 255, 255, 0.05);
    }

    .player-content {
        flex: 1;
        overflow-y: auto;
        padding: 1.5rem;
        background: transparent;
    }

    .player-loading {
        text-align: center;
        padding: 3rem;
        color: rgba(255, 255, 255, 0.5);
    }

    .season-summary {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 1rem;
        padding: 1.25rem;
        display: flex;
        flex-wrap: wrap;
        justify-content: space-around;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .summary-stat {
        text-align: center;
    }

    .summary-value {
        font-size: 1.75rem;
        font-weight: bold;
        color: #60a5fa;
    }

    .summary-label {
        font-size: 0.7rem;
        color: rgba(255, 255, 255, 0.5);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .summary-stat.highlight .summary-value {
        color: #fbbf24;
    }

    .stats-table-container {
        overflow-x: auto;
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 0.75rem;
    }

    .stats-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.875rem;
    }

    .stats-table thead {
        background: rgba(255, 255, 255, 0.05);
    }

    .stats-table th {
        padding: 0.75rem 0.5rem;
        text-align: left;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.7);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        font-size: 0.8rem;
    }

    .stats-table td {
        padding: 0.6rem 0.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        color: rgba(255, 255, 255, 0.85);
    }

    .stats-table tbody tr:hover {
        background: rgba(255, 255, 255, 0.05);
    }

    .stats-table .fant-pts {
        font-weight: bold;
        color: #fbbf24;
    }

    .season-row {
        cursor: pointer;
        transition: background 0.2s;
    }

    .season-row:hover {
        background: rgba(96, 165, 250, 0.1) !important;
    }

    .expanded-weeks-header td {
        background: rgba(96, 165, 250, 0.15);
        font-weight: 600;
        color: #60a5fa;
        padding: 0.75rem 1rem;
    }

    .expanded-week td {
        background: rgba(0, 0, 0, 0.1);
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.8rem;
    }

    .career-header {
        font-weight: 600;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 1rem;
        font-size: 1rem;
    }
</style>
