<script lang="ts">
    import GlassCard from "$lib/components/GlassCard.svelte";

    // Get data from load function
    let { data } = $props();

    // Luck rankings from API
    const luckRankings = data.luck || [];

    // Get luckiest and unluckiest
    const luckiest = luckRankings.slice(0, 3);
    const unluckiest = luckRankings.slice(-3).reverse();
</script>

<svelte:head>
    <title>Tidbits | The Elemental League</title>
</svelte:head>

<div class="container mx-auto px-6 pt-6">
    <header class="text-center mb-8">
        <h1
            class="text-5xl md:text-6xl"
            style="font-family: 'Luckiest Guy', cursive;"
        >
            <span class="text-4xl mr-2">💡</span>
            <span class="text-gradient">Tidbits</span>
        </h1>
    </header>

    <!-- Luck Rankings Section -->
    <section class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
        <!-- Luckiest -->
        <GlassCard variant="fire">
            <h2
                class="text-2xl mb-6 text-center"
                style="font-family: 'Luckiest Guy', cursive;"
            >
                🍀 Luckiest Managers
            </h2>
            <div class="space-y-4">
                {#each luckiest as manager, i}
                    <div
                        class="flex items-center gap-4 p-3 bg-white/5 rounded-lg"
                    >
                        <div class="text-2xl font-bold text-yellow-400">
                            {#if i === 0}🥇
                            {:else if i === 1}🥈
                            {:else}🥉
                            {/if}
                        </div>
                        <div class="flex-1">
                            <div class="font-medium text-white">
                                {manager.owner}
                            </div>
                            <div class="text-xs text-white/50">
                                {manager.actual_wins} wins (expected: {manager.expected_wins})
                            </div>
                        </div>
                        <div class="text-right">
                            <div
                                class="font-mono text-lg font-bold text-green-400"
                            >
                                +{manager.luck}
                            </div>
                            <div class="text-xs text-white/50">luck</div>
                        </div>
                    </div>
                {/each}
            </div>
        </GlassCard>

        <!-- Unluckiest -->
        <GlassCard variant="water">
            <h2
                class="text-2xl mb-6 text-center"
                style="font-family: 'Luckiest Guy', cursive;"
            >
                😢 Unluckiest Managers
            </h2>
            <div class="space-y-4">
                {#each unluckiest as manager, i}
                    <div
                        class="flex items-center gap-4 p-3 bg-white/5 rounded-lg"
                    >
                        <div class="text-2xl">
                            {#if i === 0}💀
                            {:else if i === 1}😭
                            {:else}😔
                            {/if}
                        </div>
                        <div class="flex-1">
                            <div class="font-medium text-white">
                                {manager.owner}
                            </div>
                            <div class="text-xs text-white/50">
                                {manager.actual_wins} wins (expected: {manager.expected_wins})
                            </div>
                        </div>
                        <div class="text-right">
                            <div
                                class="font-mono text-lg font-bold text-red-400"
                            >
                                {manager.luck}
                            </div>
                            <div class="text-xs text-white/50">luck</div>
                        </div>
                    </div>
                {/each}
            </div>
        </GlassCard>
    </section>

    <!-- Full Luck Rankings -->
    <section class="mb-12">
        <GlassCard variant="neutral">
            <h2
                class="text-2xl mb-6 text-center"
                style="font-family: 'Luckiest Guy', cursive;"
            >
                📊 Full Luck Rankings
            </h2>
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead>
                        <tr
                            class="text-white/60 text-sm border-b border-white/10"
                        >
                            <th class="text-left py-3 px-4">#</th>
                            <th class="text-left py-3 px-4">Manager</th>
                            <th class="text-center py-3 px-4">Actual Wins</th>
                            <th class="text-center py-3 px-4">Expected Wins</th>
                            <th class="text-right py-3 px-4">Luck Factor</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each luckRankings as manager, i}
                            <tr
                                class="border-b border-white/5 hover:bg-white/5 transition-colors"
                            >
                                <td class="py-3 px-4 font-medium text-white/60"
                                    >{i + 1}</td
                                >
                                <td class="py-3 px-4 font-medium"
                                    >{manager.owner}</td
                                >
                                <td class="py-3 px-4 text-center"
                                    >{manager.actual_wins}</td
                                >
                                <td class="py-3 px-4 text-center"
                                    >{manager.expected_wins}</td
                                >
                                <td
                                    class="py-3 px-4 text-right font-mono font-bold {manager.luck >=
                                    0
                                        ? 'text-green-400'
                                        : 'text-red-400'}"
                                >
                                    {manager.luck >= 0 ? "+" : ""}{manager.luck}
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
            <p class="text-center text-white/40 text-sm mt-4">
                Luck = Actual Wins - Expected Wins (based on weekly score
                rankings)
            </p>
        </GlassCard>
    </section>
</div>

<style>
    .text-gradient {
        background: linear-gradient(135deg, #ff5a00, #ffd200, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
</style>
