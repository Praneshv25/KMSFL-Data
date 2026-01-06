<script lang="ts">
    import GlassCard from "$lib/components/GlassCard.svelte";

    // Mock tidbits/insights data
    const tidbits = [
        {
            title: "Most Points in Week 1 History",
            value: "198.5",
            context: "Dynasty Destroyers (2023)",
            type: "fire",
        },
        {
            title: "Biggest Upset Ever",
            value: "45.3 pt margin",
            context: "Fumble Factory beat Gridiron Giants",
            type: "water",
        },
        {
            title: "Most Consistent Scorer",
            value: "±8.2 pts",
            context: "Touchdown Titans (2022)",
            type: "neutral",
        },
        {
            title: "Playoff Choker Award",
            value: "0-4 in playoffs",
            context: "Hail Mary Heroes",
            type: "water",
        },
    ];

    const chartData = [
        { year: 2019, avgPoints: 125 },
        { year: 2020, avgPoints: 132 },
        { year: 2021, avgPoints: 138 },
        { year: 2022, avgPoints: 145 },
        { year: 2023, avgPoints: 148 },
        { year: 2024, avgPoints: 152 },
    ];

    const maxPoints = Math.max(...chartData.map((d) => d.avgPoints));
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

    <!-- Tidbits Grid -->
    <section class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
        {#each tidbits as tidbit}
            <GlassCard variant={tidbit.type as "fire" | "water" | "neutral"}>
                <div class="flex items-start gap-4">
                    <div class="text-4xl">
                        {#if tidbit.type === "fire"}🔥
                        {:else if tidbit.type === "water"}💧
                        {:else}✨
                        {/if}
                    </div>
                    <div>
                        <h3 class="text-lg font-bold text-white mb-2">
                            {tidbit.title}
                        </h3>
                        <div class="text-3xl font-bold text-gradient mb-2">
                            {tidbit.value}
                        </div>
                        <p class="text-white/50 text-sm">{tidbit.context}</p>
                    </div>
                </div>
            </GlassCard>
        {/each}
    </section>

    <!-- Chart Section -->
    <section class="mb-12">
        <GlassCard variant="neutral">
            <h2
                class="text-2xl mb-6 text-center"
                style="font-family: 'Luckiest Guy', cursive;"
            >
                📈 League Scoring Trend
            </h2>

            <div class="h-64 flex items-end justify-around gap-4 px-4">
                {#each chartData as point}
                    <div class="flex-1 flex flex-col items-center gap-2">
                        <div
                            class="w-full rounded-t-lg bg-gradient-to-t from-orange-500 to-amber-400 transition-all duration-500 hover:opacity-80"
                            style="height: {(point.avgPoints / maxPoints) *
                                100}%;"
                        >
                            <div
                                class="text-center -mt-8 text-white font-bold text-sm"
                            >
                                {point.avgPoints}
                            </div>
                        </div>
                        <div class="text-white/60 text-sm">{point.year}</div>
                    </div>
                {/each}
            </div>

            <p class="text-center text-white/40 text-sm mt-4">
                Average points per game by season
            </p>
        </GlassCard>
    </section>

    <!-- Shareable Card Preview -->
    <section>
        <GlassCard variant="mythic">
            <div class="text-center">
                <h3
                    class="text-xl font-bold mb-4"
                    style="font-family: 'Luckiest Guy', cursive;"
                >
                    📸 Shareable Stat Cards
                </h3>
                <p class="text-white/60 mb-4">
                    Coming soon: Generate beautiful stat cards to share on
                    social media
                </p>
                <button
                    class="px-6 py-3 bg-orange-600/30 hover:bg-orange-600/50 rounded-full transition-colors text-white font-medium"
                >
                    Create Shareable Card →
                </button>
            </div>
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
