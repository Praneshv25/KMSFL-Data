<script lang="ts">
    import GlassCard from "$lib/components/GlassCard.svelte";
    import { ignite, ripple } from "$lib/actions";
    import { flip } from "svelte/animate";

    // Get data from load function
    let { data } = $props();

    // Records from API
    const allTimeRecords = data.records || [];

    type SortKey = "category" | "holder";
    let sortKey = $state<SortKey>("category");
    let sortAsc = $state(true);

    function sortBy(key: SortKey) {
        if (sortKey === key) {
            sortAsc = !sortAsc;
        } else {
            sortKey = key;
            sortAsc = true;
        }
    }

    const sortedRecords = $derived(
        [...allTimeRecords].sort((a, b) => {
            const multiplier = sortAsc ? 1 : -1;
            const aVal = String(a[sortKey]);
            const bVal = String(b[sortKey]);
            return aVal.localeCompare(bVal) * multiplier;
        }),
    );
</script>

<svelte:head>
    <title>Record Book | The Elemental League</title>
</svelte:head>

<div class="container mx-auto px-6 pt-6">
    <header class="text-center mb-8">
        <h1
            class="text-5xl md:text-6xl"
            style="font-family: 'Luckiest Guy', cursive;"
        >
            <span class="text-4xl mr-2">📊</span>
            <span class="text-fire">Record Book</span>
        </h1>
    </header>

    <!-- Records Table -->
    <GlassCard variant="fire">
        <h2
            class="text-2xl mb-6 text-center"
            style="font-family: 'Luckiest Guy', cursive;"
        >
            All-Time Records
        </h2>
        <div class="overflow-x-auto">
            <table class="w-full">
                <thead>
                    <tr class="text-white/60 text-sm border-b border-white/10">
                        <th class="text-left py-4 px-4">
                            <button
                                onclick={() => sortBy("category")}
                                use:ripple
                                class="hover:text-white"
                            >
                                Record {sortKey === "category"
                                    ? sortAsc
                                        ? "↑"
                                        : "↓"
                                    : ""}
                            </button>
                        </th>
                        <th class="text-center py-4 px-4">Value</th>
                        <th class="text-left py-4 px-4">
                            <button
                                onclick={() => sortBy("holder")}
                                use:ripple
                                class="hover:text-white"
                            >
                                Holder {sortKey === "holder"
                                    ? sortAsc
                                        ? "↑"
                                        : "↓"
                                    : ""}
                            </button>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {#each sortedRecords as record (record.category)}
                        <tr
                            animate:flip={{ duration: 300 }}
                            class="border-b border-white/5 hover:bg-white/5 transition-colors"
                        >
                            <td class="py-4 px-4 font-medium text-white"
                                >{record.category}</td
                            >
                            <td class="py-4 px-4 text-center">
                                <span
                                    class="font-mono text-lg font-bold text-gradient"
                                    >{record.value}</span
                                >
                            </td>
                            <td class="py-4 px-4 text-white/80"
                                >{record.holder}</td
                            >
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>
    </GlassCard>
</div>

<style>
    .text-fire {
        background: linear-gradient(135deg, #ff5a00, #ffd200);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .text-gradient {
        background: linear-gradient(135deg, #ff5a00, #ffd200, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
</style>
