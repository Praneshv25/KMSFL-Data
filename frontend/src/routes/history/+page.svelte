<script lang="ts">
    import GlassCard from "$lib/components/GlassCard.svelte";
    import { ripple } from "$lib/actions";
    import { flip } from "svelte/animate";

    // Available years (will come from API)
    const years = [2024, 2023, 2022, 2021, 2020, 2019];

    let selectedYear = $state(2024);
    let activeTab = $state<"standings" | "matchups" | "draft">("standings");

    // Mock standings data
    const standings = [
        {
            rank: 1,
            team: "Dynasty Destroyers",
            owner: "Mike",
            wins: 12,
            losses: 3,
            pf: 1890.5,
            pa: 1654.2,
        },
        {
            rank: 2,
            team: "Gridiron Giants",
            owner: "Sarah",
            wins: 11,
            losses: 4,
            pf: 1845.3,
            pa: 1702.1,
        },
        {
            rank: 3,
            team: "Touchdown Titans",
            owner: "Jason",
            wins: 10,
            losses: 5,
            pf: 1812.7,
            pa: 1689.4,
        },
        {
            rank: 4,
            team: "Fantasy Phenoms",
            owner: "Chris",
            wins: 9,
            losses: 6,
            pf: 1756.9,
            pa: 1734.8,
        },
        {
            rank: 5,
            team: "Endzone Elite",
            owner: "Alex",
            wins: 8,
            losses: 7,
            pf: 1698.4,
            pa: 1721.5,
        },
        {
            rank: 6,
            team: "Pigskin Prophets",
            owner: "Tyler",
            wins: 7,
            losses: 8,
            pf: 1645.2,
            pa: 1756.3,
        },
        {
            rank: 7,
            team: "Field Goal Fiends",
            owner: "Jordan",
            wins: 6,
            losses: 9,
            pf: 1589.6,
            pa: 1801.2,
        },
        {
            rank: 8,
            team: "Blitz Brigade",
            owner: "Morgan",
            wins: 5,
            losses: 10,
            pf: 1523.8,
            pa: 1834.7,
        },
        {
            rank: 9,
            team: "Hail Mary Heroes",
            owner: "Casey",
            wins: 4,
            losses: 11,
            pf: 1467.1,
            pa: 1889.0,
        },
        {
            rank: 10,
            team: "Fumble Factory",
            owner: "Pat",
            wins: 3,
            losses: 12,
            pf: 1412.0,
            pa: 1945.3,
        },
    ];

    // Mock matchups data
    const weeks = Array.from({ length: 14 }, (_, i) => i + 1);
    let selectedWeek = $state(1);

    const matchups = [
        {
            home: "Dynasty Destroyers",
            homeScore: 145.2,
            away: "Fumble Factory",
            awayScore: 98.7,
        },
        {
            home: "Gridiron Giants",
            homeScore: 132.1,
            away: "Hail Mary Heroes",
            awayScore: 115.4,
        },
        {
            home: "Touchdown Titans",
            homeScore: 128.9,
            away: "Blitz Brigade",
            awayScore: 121.3,
        },
        {
            home: "Fantasy Phenoms",
            homeScore: 142.5,
            away: "Field Goal Fiends",
            awayScore: 135.8,
        },
        {
            home: "Endzone Elite",
            homeScore: 118.7,
            away: "Pigskin Prophets",
            awayScore: 124.2,
        },
    ];

    // Sorting
    type SortKey = "rank" | "wins" | "pf" | "pa";
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
            return (a[sortKey] - b[sortKey]) * multiplier;
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
    <div class="flex justify-center mb-8">
        <div class="inline-flex bg-white/5 backdrop-blur-lg rounded-full p-1">
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
                                        onclick={() => sortBy("pf")}
                                        class="hover:text-white"
                                    >
                                        PF {sortKey === "pf"
                                            ? sortAsc
                                                ? "↑"
                                                : "↓"
                                            : ""}
                                    </button>
                                </th>
                                <th class="text-right py-4 px-4">
                                    <button
                                        onclick={() => sortBy("pa")}
                                        class="hover:text-white"
                                    >
                                        PA {sortKey === "pa"
                                            ? sortAsc
                                                ? "↑"
                                                : "↓"
                                            : ""}
                                    </button>
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each sortedStandings as team (team.rank)}
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
                                                : 'bg-white/10 text-white/60'}
                    "
                                        >
                                            {team.rank}
                                        </span>
                                    </td>
                                    <td class="py-4 px-4 font-medium text-white"
                                        >{team.team}</td
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
                                        >{team.pf.toFixed(1)}</td
                                    >
                                    <td
                                        class="py-4 px-4 text-right font-mono text-white/50"
                                        >{team.pa.toFixed(1)}</td
                                    >
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            </GlassCard>
        {:else if activeTab === "matchups"}
            <!-- Week Selector -->
            <div class="flex justify-center mb-6 overflow-x-auto pb-2">
                <div
                    class="inline-flex bg-white/5 backdrop-blur-lg rounded-lg p-1 gap-1"
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
                <div class="space-y-4">
                    {#each matchups as matchup}
                        <div
                            class="grid grid-cols-7 items-center gap-4 p-4 bg-white/5 rounded-xl hover:bg-white/10 transition-colors cursor-pointer"
                        >
                            <!-- Home Team -->
                            <div class="col-span-3 text-right">
                                <div class="font-medium text-white">
                                    {matchup.home}
                                </div>
                                <div
                                    class="text-2xl font-bold {matchup.homeScore >
                                    matchup.awayScore
                                        ? 'text-green-400'
                                        : 'text-white/60'}"
                                >
                                    {matchup.homeScore}
                                </div>
                            </div>

                            <!-- VS -->
                            <div class="col-span-1 text-center">
                                <span class="text-white/40 text-lg font-bold"
                                    >VS</span
                                >
                            </div>

                            <!-- Away Team -->
                            <div class="col-span-3 text-left">
                                <div class="font-medium text-white">
                                    {matchup.away}
                                </div>
                                <div
                                    class="text-2xl font-bold {matchup.awayScore >
                                    matchup.homeScore
                                        ? 'text-green-400'
                                        : 'text-white/60'}"
                                >
                                    {matchup.awayScore}
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>
            </GlassCard>
        {:else}
            <!-- Draft Board Placeholder -->
            <GlassCard variant="water">
                <div class="text-center py-16 text-white/40">
                    <p class="text-2xl mb-4">📋</p>
                    <p class="text-lg">Draft Board coming soon...</p>
                    <p class="text-sm mt-2">
                        Will show round-by-round picks with animate:flip
                        transitions
                    </p>
                </div>
            </GlassCard>
        {/if}
    </div>
</div>

<style>
    .text-water {
        background: linear-gradient(135deg, #4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
</style>
