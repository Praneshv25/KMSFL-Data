<script lang="ts">
  import './layout.css';
  import ElementCanvas from '$lib/components/ElementCanvas.svelte';
  import Navbar from '$lib/components/Navbar.svelte';
  import { fly, fade } from 'svelte/transition';
  import { page } from '$app/stores';
  
  let { children } = $props();
</script>

<svelte:head>
  <title>The Elemental League</title>
  <meta name="description" content="Fantasy Football History - Fire vs Water" />
</svelte:head>

<!-- Animated Background -->
<ElementCanvas />

<!-- Main Content with Page Transitions -->
<main class="min-h-screen pb-24">
  {#key $page.url.pathname}
    <div
      in:fade={{ duration: 200, delay: 150 }}
      out:fade={{ duration: 150 }}
    >
      {@render children()}
    </div>
  {/key}
</main>

<!-- Floating Navigation -->
<Navbar />
