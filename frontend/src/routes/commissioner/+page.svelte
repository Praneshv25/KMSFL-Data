<script lang="ts">
    import GlassCard from "$lib/components/GlassCard.svelte";

    // Mock commissioner blog posts
    const posts = [
        {
            id: 1,
            title: "State of the League 2024",
            date: "December 15, 2024",
            preview:
                "Another incredible season comes to a close. Dynasty Destroyers claim their second championship...",
            pinned: true,
        },
        {
            id: 2,
            title: "Rule Changes for 2025",
            date: "January 2, 2025",
            preview:
                "After much deliberation, we are implementing the following changes for the upcoming season...",
            pinned: false,
        },
        {
            id: 3,
            title: "Mid-Season Power Rankings",
            date: "October 20, 2024",
            preview:
                "With week 7 in the books, here are the official power rankings as determined by the commissioner...",
            pinned: false,
        },
    ];
</script>

<svelte:head>
    <title>Commissioner's Corner | The Elemental League</title>
</svelte:head>

<div class="container mx-auto px-6 pt-6 max-w-4xl">
    <header class="text-center mb-8">
        <h1
            class="text-5xl md:text-6xl"
            style="font-family: 'Luckiest Guy', cursive;"
        >
            <span class="text-4xl mr-2">👑</span>
            <span class="text-gradient-gold">Commissioner's Corner</span>
        </h1>
    </header>

    <!-- Welcome Banner -->
    <GlassCard variant="gold" class="mb-8">
        <div class="flex items-center gap-6">
            <div class="text-6xl">🏛️</div>
            <div>
                <h2 class="text-2xl font-bold text-white mb-2">
                    Welcome to Season 7
                </h2>
                <p class="text-white/70">
                    The Elemental League has grown from humble beginnings into a
                    fiercely competitive battleground. May the best manager win.
                </p>
            </div>
        </div>
    </GlassCard>

    <!-- Blog Posts -->
    <section class="space-y-6">
        {#each posts as post}
            <a href="/commissioner/{post.id}" class="block group">
                <GlassCard variant={post.pinned ? "gold" : "neutral"}>
                    <article>
                        <div class="flex items-start justify-between gap-4">
                            <div class="flex-1">
                                {#if post.pinned}
                                    <span
                                        class="inline-block px-2 py-1 bg-yellow-500/30 text-yellow-300 text-xs rounded-full mb-2"
                                    >
                                        📌 Pinned
                                    </span>
                                {/if}
                                <h3
                                    class="text-xl font-bold text-white mb-2 group-hover:text-yellow-400 transition-colors"
                                >
                                    {post.title}
                                </h3>
                                <p class="text-white/60 text-sm mb-3">
                                    {post.preview}
                                </p>
                                <time class="text-white/40 text-xs"
                                    >{post.date}</time
                                >
                            </div>
                            <div
                                class="text-2xl text-white/40 group-hover:text-white transition-colors"
                            >
                                →
                            </div>
                        </div>
                    </article>
                </GlassCard>
            </a>
        {/each}
    </section>
</div>

<style>
    .text-gradient-gold {
        background: linear-gradient(135deg, #ffd700, #ffa500, #ff8c00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
</style>
