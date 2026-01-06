<script lang="ts">
    import GlassCard from "$lib/components/GlassCard.svelte";
    import { ignite } from "$lib/actions";
    import { spring } from "svelte/motion";

    // Get data from load function
    let { data } = $props();

    // Champions from API
    const champions = data.champions || [];

    let selectedYear = $state<number | null>(null);

    // Spring physics for card expansion
    const cardScale = spring(1, { stiffness: 0.1, damping: 0.3 });

    function selectYear(year: number) {
        if (selectedYear === year) {
            selectedYear = null;
            cardScale.set(1);
        } else {
            selectedYear = year;
            cardScale.set(1.05);
        }
    }
</script>

<svelte:head>
    <title>Hall of Champions | The Elemental League</title>
    <meta
        name="description"
        content="Trophy wall - Every champion from 2019 to present"
    />
</svelte:head>

<div class="container mx-auto px-6 pt-6">
    <!-- Header -->
    <header class="text-center mb-8">
        <h1
            class="text-5xl md:text-6xl"
            style="font-family: 'Luckiest Guy', cursive;"
        >
            <span class="text-4xl mr-2">🏆</span>
            <span class="text-gradient-gold">Hall of Champions</span>
        </h1>
    </header>

    <!-- Trophy Grid -->
    <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
        {#each champions as champ}
            {@const isSelected = selectedYear === champ.year}
            <button
                onclick={() => selectYear(champ.year)}
                class="text-left w-full transition-transform duration-300 {isSelected
                    ? 'scale-105 z-10'
                    : ''}"
            >
                <GlassCard variant="gold" hover={true}>
                    <div class="relative">
                        <!-- Year Badge -->
                        <div
                            class="absolute -top-3 -left-3 bg-yellow-500 text-black rounded-full w-14 h-14 flex items-center justify-center font-bold shadow-lg"
                        >
                            {champ.year}
                        </div>

                        <div class="pt-6">
                            <!-- Team Name with Ember Effect -->
                            <h2
                                class="text-2xl font-bold text-white mb-2"
                                style="font-family: 'Luckiest Guy', cursive;"
                                use:ignite
                            >
                                {champ.team}
                            </h2>

                            <!-- Owner & Record -->
                            <div
                                class="flex items-center justify-between text-white/70"
                            >
                                <span class="flex items-center gap-2">
                                    <span class="text-xl">👑</span>
                                    {champ.owner}
                                </span>
                                <span
                                    class="font-mono text-sm bg-white/10 px-3 py-1 rounded-full"
                                >
                                    {champ.record}
                                </span>
                            </div>
                        </div>

                        <!-- Expanded Details -->
                        {#if isSelected}
                            <div class="mt-6 pt-4 border-t border-white/10">
                                <div class="grid grid-cols-2 gap-4 text-sm">
                                    <div class="text-center">
                                        <div
                                            class="text-2xl font-bold text-fire"
                                        >
                                            1st
                                        </div>
                                        <div class="text-white/50">
                                            Final Rank
                                        </div>
                                    </div>
                                    <div class="text-center">
                                        <div
                                            class="text-2xl font-bold text-water"
                                        >
                                            145
                                        </div>
                                        <div class="text-white/50">
                                            Avg Points
                                        </div>
                                    </div>
                                </div>
                                <p
                                    class="mt-4 text-white/50 text-sm text-center"
                                >
                                    Click to view playoff bracket →
                                </p>
                            </div>
                        {/if}
                    </div>
                </GlassCard>
            </button>
        {/each}
    </section>

    <!-- Playoff Bracket Section (Placeholder) -->
    <section class="mb-16">
        <h2
            class="text-3xl text-center mb-8"
            style="font-family: 'Luckiest Guy', cursive;"
        >
            {selectedYear ? `${selectedYear} Playoff Bracket` : "Select a Year"}
        </h2>

        <div class="max-w-4xl mx-auto">
            <GlassCard variant="neutral">
                <div class="text-center py-12 text-white/40">
                    {#if selectedYear}
                        <p class="text-lg">
                            Playoff bracket visualization coming soon...
                        </p>
                        <p class="text-sm mt-2">
                            Will show the journey to championship glory
                        </p>
                    {:else}
                        <p class="text-lg">
                            Click a championship card above to view the playoff
                            bracket
                        </p>
                    {/if}
                </div>
            </GlassCard>
        </div>
    </section>
</div>

<style>
    .text-gradient-gold {
        background: linear-gradient(135deg, #ffd700, #ffa500, #ff8c00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .text-fire {
        background: linear-gradient(135deg, #ff5a00, #ffd200);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .text-water {
        background: linear-gradient(135deg, #4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
</style>
