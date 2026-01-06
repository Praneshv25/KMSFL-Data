<script lang="ts">
    import GlassCard from "$lib/components/GlassCard.svelte";

    // Get data from load function
    let { data } = $props();

    // Managers from API
    const managers = data.managers || [];
</script>

<svelte:head>
    <title>Managers | The Elemental League</title>
</svelte:head>

<div class="container mx-auto px-6 pt-6">
    <header class="text-center mb-8">
        <h1
            class="text-5xl md:text-6xl"
            style="font-family: 'Luckiest Guy', cursive;"
        >
            <span class="text-4xl mr-2">👥</span>
            <span class="text-gradient">Managers</span>
        </h1>
    </header>

    <div
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6"
    >
        {#each managers as manager}
            <a
                href="/manager/{encodeURIComponent(manager.name)}"
                class="block group"
            >
                <GlassCard
                    variant={manager.championships > 0 ? "gold" : "neutral"}
                >
                    <div class="text-center">
                        <!-- Avatar placeholder -->
                        <div
                            class="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br from-white/10 to-white/5 flex items-center justify-center text-4xl"
                        >
                            {manager.name.charAt(0)}
                        </div>

                        <h2 class="text-xl font-bold text-white mb-1">
                            {manager.name}
                        </h2>
                        <p class="text-white/50 text-sm mb-4">
                            {manager.seasons_played} seasons
                        </p>

                        <div class="grid grid-cols-2 gap-2 text-xs">
                            <div class="bg-white/5 rounded-lg p-2">
                                <div class="font-mono font-bold text-white">
                                    {manager.all_time_record}
                                </div>
                                <div class="text-white/40">Record</div>
                            </div>
                            <div class="bg-white/5 rounded-lg p-2">
                                <div class="font-bold text-yellow-400">
                                    {manager.championships} 🏆
                                </div>
                                <div class="text-white/40">Titles</div>
                            </div>
                        </div>
                    </div>
                </GlassCard>
            </a>
        {/each}
    </div>
</div>

<style>
    .text-gradient {
        background: linear-gradient(135deg, #ff5a00, #ffd200, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
</style>
