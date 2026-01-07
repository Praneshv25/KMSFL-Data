<script lang="ts">
    import GlassCard from "$lib/components/GlassCard.svelte";
    import { ignite } from "$lib/actions";

    // Get data from load function
    let { data } = $props();

    // Manager from API
    const manager = data.manager || {
        name: "Loading...",
        all_time_record: "0-0",
        total_wins: 0,
        total_losses: 0,
        championships: 0,
        playoff_appearances: 0,
        avg_points_for: 0,
        seasons_played: 0,
        season_history: [],
    };

    // Rivalries from API
    const rivalries = data.rivalries || [];

    // Weekly results from API
    const weeklyResults = data.weeklyResults || [];

    // Calculate win percentage
    const totalGames = manager.total_wins + manager.total_losses;
    const winPct = totalGames > 0 ? manager.total_wins / totalGames : 0;

    // Group weekly results by season for heatmap display
    interface WeekResult {
        week: number;
        result: string;
        score: number;
        opponent_score: number;
    }
    const seasonGroups: Record<number, WeekResult[]> = {};
    for (const r of weeklyResults) {
        if (!seasonGroups[r.season_year]) {
            seasonGroups[r.season_year] = [];
        }
        seasonGroups[r.season_year].push(r);
    }
    // Get sorted seasons (most recent first)
    const seasons = Object.keys(seasonGroups)
        .map(Number)
        .sort((a, b) => b - a);
</script>

<svelte:head>
    <title>{manager.name} | The Elemental League</title>
</svelte:head>

<div class="container mx-auto px-6 pt-12">
    <!-- Profile Header -->
    <header class="mb-12">
        <div class="flex flex-col lg:flex-row items-center gap-8">
            <!-- Avatar -->
            <div class="relative">
                <div
                    class="w-32 h-32 rounded-full bg-gradient-to-br from-orange-500/30 to-amber-500/30 flex items-center justify-center text-6xl font-bold border-4 border-white/20"
                >
                    {manager.name.charAt(0)}
                </div>
                {#if manager.championships > 0}
                    <div
                        class="absolute -bottom-2 -right-2 bg-yellow-500 rounded-full w-10 h-10 flex items-center justify-center text-xl"
                    >
                        🏆
                    </div>
                {/if}
            </div>

            <!-- Info -->
            <div class="text-center lg:text-left">
                <h1
                    class="text-4xl md:text-5xl mb-2"
                    style="font-family: 'Luckiest Guy', cursive;"
                >
                    {manager.name}
                </h1>
                <p class="text-xl text-white/60 mb-4">
                    {manager.seasons_played} seasons played
                </p>

                <div
                    class="flex flex-wrap justify-center lg:justify-start gap-3"
                >
                    <span class="px-4 py-2 bg-white/10 rounded-full text-sm">
                        {manager.seasons_played > 0
                            ? `Since ${2025 - manager.seasons_played + 1}`
                            : ""}
                    </span>
                    <span
                        class="px-4 py-2 bg-green-500/20 rounded-full text-sm text-green-400"
                    >
                        {manager.all_time_record} ({(winPct * 100).toFixed(0)}%)
                    </span>
                    <span
                        class="px-4 py-2 bg-yellow-500/20 rounded-full text-sm text-yellow-400"
                    >
                        {manager.championships}× Champion
                    </span>
                </div>
            </div>
        </div>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-12">
        <!-- Stats -->
        <GlassCard variant="fire">
            <h3
                class="text-lg font-bold mb-4"
                style="font-family: 'Luckiest Guy', cursive;"
            >
                Career Stats
            </h3>
            <div class="space-y-4">
                <div class="flex justify-between items-center">
                    <span class="text-white/60">Playoff Appearances</span>
                    <span class="font-bold text-xl"
                        >{manager.playoff_appearances}</span
                    >
                </div>
                <div class="flex justify-between items-center">
                    <span class="text-white/60">Avg Points/Game</span>
                    <span class="font-bold text-xl" use:ignite
                        >{manager.avg_points_for}</span
                    >
                </div>
                <div class="flex justify-between items-center">
                    <span class="text-white/60">Championships</span>
                    <span class="font-bold text-xl text-yellow-400"
                        >{manager.championships} 🏆</span
                    >
                </div>
            </div>
        </GlassCard>

        <!-- Heatmap -->
        <GlassCard variant="water">
            <h3
                class="text-lg font-bold mb-4"
                style="font-family: 'Luckiest Guy', cursive;"
            >
                Win/Loss Heatmap
            </h3>
            <div class="max-h-64 overflow-y-auto space-y-3">
                {#each seasons as season}
                    <div>
                        <div class="text-xs text-white/50 mb-1">{season}</div>
                        <div class="flex flex-wrap gap-1">
                            {#each seasonGroups[season] as week}
                                <div
                                    class="w-6 h-6 rounded flex items-center justify-center text-xs font-bold cursor-default
                                    {week.result === 'W'
                                        ? 'bg-green-500/40 text-green-300'
                                        : 'bg-red-500/40 text-red-300'}"
                                    title="Week {week.week}: {week.score} - {week.opponent_score}"
                                >
                                    {week.week}
                                </div>
                            {/each}
                        </div>
                    </div>
                {/each}
            </div>
        </GlassCard>

        <!-- Rivalries -->
        <GlassCard variant="mythic">
            <h3
                class="text-lg font-bold mb-4"
                style="font-family: 'Luckiest Guy', cursive;"
            >
                Rivalries
            </h3>
            {#if rivalries.length > 0}
                <div class="space-y-3 max-h-64 overflow-y-auto">
                    {#each rivalries as rival}
                        <div
                            class="flex items-center gap-4 p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
                        >
                            <span class="text-2xl"
                                >{rival.win_pct >= 50 ? "🔥" : "⚔️"}</span
                            >
                            <div class="flex-1">
                                <div class="font-medium text-white">
                                    {rival.opponent}
                                </div>
                                <div class="text-xs text-white/50">
                                    {rival.total_games} games played
                                </div>
                            </div>
                            <div class="text-right">
                                <div
                                    class="font-mono text-sm {rival.wins >
                                    rival.losses
                                        ? 'text-green-400'
                                        : rival.wins < rival.losses
                                          ? 'text-red-400'
                                          : 'text-white/60'}"
                                >
                                    {rival.wins}-{rival.losses}
                                </div>
                                <div class="text-xs text-white/50">
                                    {rival.win_pct}%
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>
            {:else}
                <div class="text-center py-8 text-white/40">
                    <p>No rivalry data available</p>
                </div>
            {/if}
        </GlassCard>
    </div>

    <!-- Season History -->
    <GlassCard variant="neutral">
        <h3
            class="text-lg font-bold mb-4"
            style="font-family: 'Luckiest Guy', cursive;"
        >
            Season History
        </h3>
        <div class="overflow-x-auto">
            <table class="w-full">
                <thead>
                    <tr class="text-white/60 text-sm border-b border-white/10">
                        <th class="text-left py-3 px-4">Year</th>
                        <th class="text-center py-3 px-4">Finish</th>
                        <th class="text-center py-3 px-4">Record</th>
                        <th class="text-right py-3 px-4">Points For</th>
                    </tr>
                </thead>
                <tbody>
                    {#each manager.season_history || [] as season}
                        <tr
                            class="border-b border-white/5 hover:bg-white/5 transition-colors"
                        >
                            <td class="py-3 px-4 font-medium"
                                >{season.season_year}</td
                            >
                            <td class="py-3 px-4 text-center">
                                <span
                                    class="inline-flex items-center justify-center w-8 h-8 rounded-full
                  {season.rank === 1
                                        ? 'bg-yellow-500/30 text-yellow-300'
                                        : season.rank <= 4
                                          ? 'bg-amber-600/30 text-amber-300'
                                          : 'bg-white/10 text-white/60'}"
                                >
                                    {season.rank}
                                </span>
                            </td>
                            <td class="py-3 px-4 text-center font-mono"
                                >{season.wins}-{season.losses}</td
                            >
                            <td
                                class="py-3 px-4 text-right font-mono text-amber-300"
                                >{season.points_for}</td
                            >
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>
    </GlassCard>
</div>
