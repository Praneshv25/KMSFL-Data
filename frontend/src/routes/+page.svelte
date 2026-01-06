<script lang="ts">
    import GlassCard from "$lib/components/GlassCard.svelte";
    import { ignite, float } from "$lib/actions";
</script>

<svelte:head>
    <title>The Elemental League | Fantasy Football History</title>
</svelte:head>

<div class="container mx-auto px-6 pt-6">
    <!-- Hero Section -->
    <header class="text-center mb-8">
        <h1
            class="text-5xl md:text-7xl"
            style="font-family: 'Luckiest Guy', cursive;"
            use:float={{ duration: 4000, amplitude: 8 }}
        >
            <span class="text-fire">The Elemental</span>
            <span class="text-water"> League</span>
        </h1>
    </header>

    <!-- Quick Stats Grid -->
    <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <GlassCard variant="fire">
            <div class="text-center">
                <div class="text-4xl font-bold text-fire mb-2" use:ignite>
                    7
                </div>
                <div class="text-white/60 text-sm uppercase tracking-wider">
                    Seasons
                </div>
            </div>
        </GlassCard>

        <GlassCard variant="water">
            <div class="text-center">
                <div class="text-4xl font-bold text-water mb-2">10</div>
                <div class="text-white/60 text-sm uppercase tracking-wider">
                    Managers
                </div>
            </div>
        </GlassCard>

        <GlassCard variant="fire">
            <div class="text-center">
                <div class="text-4xl font-bold text-fire mb-2" use:ignite>
                    500+
                </div>
                <div class="text-white/60 text-sm uppercase tracking-wider">
                    Matchups
                </div>
            </div>
        </GlassCard>

        <GlassCard variant="water">
            <div class="text-center">
                <div class="text-4xl font-bold text-water mb-2">∞</div>
                <div class="text-white/60 text-sm uppercase tracking-wider">
                    Glory
                </div>
            </div>
        </GlassCard>
    </section>

    <!-- Feature Cards -->
    <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <a href="/champions" class="block group">
            <GlassCard variant="gold" class="h-full">
                <div class="flex items-center gap-4 mb-4">
                    <span class="text-4xl">🏆</span>
                    <h2
                        class="text-2xl"
                        style="font-family: 'Luckiest Guy', cursive;"
                    >
                        Hall of Champions
                    </h2>
                </div>
                <p class="text-white/60">
                    The trophy wall. Every champion, every year, immortalized in
                    elemental glory.
                </p>
            </GlassCard>
        </a>

        <a href="/history" class="block group">
            <GlassCard variant="water" class="h-full">
                <div class="flex items-center gap-4 mb-4">
                    <span class="text-4xl">📜</span>
                    <h2
                        class="text-2xl"
                        style="font-family: 'Luckiest Guy', cursive;"
                    >
                        History Hub
                    </h2>
                </div>
                <p class="text-white/60">
                    Dive into the archives. Standings, matchups, and drafts from
                    every season.
                </p>
            </GlassCard>
        </a>

        <a href="/records" class="block group">
            <GlassCard variant="fire" class="h-full">
                <div class="flex items-center gap-4 mb-4">
                    <span class="text-4xl">📊</span>
                    <h2
                        class="text-2xl"
                        style="font-family: 'Luckiest Guy', cursive;"
                    >
                        Record Book
                    </h2>
                </div>
                <p class="text-white/60">
                    The definitive record of all-time highs, lows, and streaks
                    that define legends.
                </p>
            </GlassCard>
        </a>

        <a href="/managers" class="block group">
            <GlassCard variant="neutral" class="h-full">
                <div class="flex items-center gap-4 mb-4">
                    <span class="text-4xl">👥</span>
                    <h2
                        class="text-2xl"
                        style="font-family: 'Luckiest Guy', cursive;"
                    >
                        Manager Profiles
                    </h2>
                </div>
                <p class="text-white/60">
                    Character select. Every manager's journey through fire and
                    water.
                </p>
            </GlassCard>
        </a>

        <a href="/studio" class="block group">
            <GlassCard variant="mythic" class="h-full">
                <div class="flex items-center gap-4 mb-4">
                    <span class="text-4xl">✨</span>
                    <h2
                        class="text-2xl"
                        style="font-family: 'Luckiest Guy', cursive;"
                    >
                        Creator Studio
                    </h2>
                </div>
                <p class="text-white/60">
                    Ask the oracle anything. AI-powered insights from seven
                    years of data.
                </p>
            </GlassCard>
        </a>

        <a href="/commissioner" class="block group">
            <GlassCard variant="gold" class="h-full">
                <div class="flex items-center gap-4 mb-4">
                    <span class="text-4xl">👑</span>
                    <h2
                        class="text-2xl"
                        style="font-family: 'Luckiest Guy', cursive;"
                    >
                        Commissioner
                    </h2>
                </div>
                <p class="text-white/60">
                    The throne room. League announcements and state of the union
                    addresses.
                </p>
            </GlassCard>
        </a>
    </section>
</div>

<style>
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
