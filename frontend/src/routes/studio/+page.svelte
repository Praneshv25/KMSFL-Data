<script lang="ts">
    import GlassCard from "$lib/components/GlassCard.svelte";
    import { ripple } from "$lib/actions";

    let query = $state("");
    let isLoading = $state(false);
    let result = $state<{ answer: string; data?: unknown } | null>(null);
    let error = $state<string | null>(null);

    // Example queries for inspiration
    const exampleQueries = [
        "Who has the best playoff record?",
        "What team scores the most on Monday Night Football?",
        "Who chokes the most in must-win games?",
        "Which draft position produces the most champions?",
    ];

    async function submitQuery() {
        if (!query.trim()) return;

        isLoading = true;
        error = null;
        result = null;

        try {
            // TODO: Replace with actual Gemini API call via backend
            // const response = await fetch('/api/studio/query', {
            //   method: 'POST',
            //   headers: { 'Content-Type': 'application/json' },
            //   body: JSON.stringify({ query })
            // });
            // const data = await response.json();

            // Simulated response for now
            await new Promise((resolve) => setTimeout(resolve, 1500));

            result = {
                answer: `Based on 7 seasons of data, here's what I found for: "${query}"\n\nThis is a placeholder response. Once connected to the Gemini API, you'll get AI-powered insights from your league's historical data.`,
                data: null,
            };
        } catch (e) {
            error = "Failed to process query. Please try again.";
        } finally {
            isLoading = false;
        }
    }

    function setExampleQuery(q: string) {
        query = q;
    }
</script>

<svelte:head>
    <title>Creator Studio | The Elemental League</title>
</svelte:head>

<div class="container mx-auto px-6 pt-6 max-w-4xl">
    <header class="text-center mb-8">
        <h1
            class="text-5xl md:text-6xl"
            style="font-family: 'Luckiest Guy', cursive;"
        >
            <span class="text-4xl mr-2">✨</span>
            <span class="text-gradient-mythic">Creator Studio</span>
        </h1>
    </header>

    <!-- Query Input -->
    <GlassCard variant="mythic" class="mb-8">
        <form
            onsubmit={(e) => {
                e.preventDefault();
                submitQuery();
            }}
        >
            <label for="query" class="block text-white/70 mb-2 text-sm"
                >Ask a question about your league:</label
            >
            <div class="flex gap-4">
                <input
                    id="query"
                    type="text"
                    bind:value={query}
                    placeholder="e.g., Who has the worst luck in fantasy football?"
                    class="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-xl
            text-white placeholder:text-white/30
            focus:outline-none focus:border-orange-500/50 focus:ring-2 focus:ring-orange-500/20
            transition-all"
                />
                <button
                    type="submit"
                    disabled={isLoading || !query.trim()}
                    use:ripple
                    class="px-6 py-3 bg-orange-600/40 hover:bg-orange-600/60 disabled:opacity-50
            disabled:cursor-not-allowed rounded-xl font-medium transition-all"
                >
                    {isLoading ? "🔮 Consulting..." : "🔮 Ask Oracle"}
                </button>
            </div>
        </form>

        <!-- Example Queries -->
        <div class="mt-4">
            <p class="text-white/40 text-xs mb-2">Try these:</p>
            <div class="flex flex-wrap gap-2">
                {#each exampleQueries as example}
                    <button
                        onclick={() => setExampleQuery(example)}
                        class="px-3 py-1 bg-white/5 hover:bg-white/10 rounded-full text-xs text-white/60 hover:text-white transition-all"
                    >
                        {example}
                    </button>
                {/each}
            </div>
        </div>
    </GlassCard>

    <!-- Results -->
    {#if isLoading}
        <GlassCard variant="neutral">
            <div class="text-center py-12">
                <div class="text-4xl mb-4 animate-bounce">🔮</div>
                <p class="text-white/60">
                    The oracle is consulting the ancient scrolls...
                </p>
            </div>
        </GlassCard>
    {:else if error}
        <GlassCard variant="fire">
            <div class="text-center py-8">
                <div class="text-4xl mb-4">❌</div>
                <p class="text-red-400">{error}</p>
            </div>
        </GlassCard>
    {:else if result}
        <GlassCard variant="mythic">
            <div class="flex items-start gap-4">
                <div class="text-4xl">🔮</div>
                <div class="flex-1">
                    <h3 class="text-lg font-bold text-orange-300 mb-3">
                        Oracle's Response
                    </h3>
                    <p class="text-white/80 whitespace-pre-line">
                        {result.answer}
                    </p>
                </div>
            </div>
        </GlassCard>
    {:else}
        <GlassCard variant="neutral">
            <div class="text-center py-12 text-white/40">
                <div class="text-4xl mb-4">🌟</div>
                <p>
                    Ask a question to unlock insights from seven years of
                    fantasy football history
                </p>
            </div>
        </GlassCard>
    {/if}

    <!-- API Notice -->
    <div class="mt-8 text-center">
        <p class="text-white/30 text-xs">
            Powered by Gemini AI. API key required for full functionality.
        </p>
    </div>
</div>

<style>
    .text-gradient-mythic {
        background: linear-gradient(135deg, #9b59b6, #e74c3c, #f39c12);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
</style>
