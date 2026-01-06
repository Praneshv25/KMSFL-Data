<script lang="ts">
  import type { Snippet } from "svelte";

  interface Props {
    variant?: "fire" | "water" | "neutral" | "gold" | "mythic";
    hover?: boolean;
    children: Snippet;
    class?: string;
  }

  let {
    variant = "neutral",
    hover = true,
    children,
    class: className = "",
  }: Props = $props();

  const variantClasses = {
    fire: "border-orange-500/30 hover:border-orange-500/60 shadow-orange-500/20",
    water: "border-amber-600/30 hover:border-amber-600/60 shadow-amber-600/20",
    neutral: "border-white/10 hover:border-white/20",
    gold: "border-yellow-600/40 hover:border-yellow-600/70 shadow-yellow-600/20",
    mythic:
      "border-orange-700/30 hover:border-orange-700/60 shadow-orange-700/20",
  };

  const pulseClasses = {
    fire: "animate-pulse-fire",
    water: "animate-pulse-water",
    neutral: "",
    gold: "",
    mythic: "",
  };
</script>

<div
  class="
    relative rounded-2xl p-6
    bg-white/5 backdrop-blur-xl
    border transition-all duration-300
    {variantClasses[variant]}
    {hover ? 'hover:bg-white/10 hover:scale-[1.01]' : ''}
    {className}
  "
  class:shadow-lg={variant !== "neutral"}
>
  <!-- Gradient accent line for fire/water -->
  {#if variant === "fire"}
    <div
      class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-orange-500 to-transparent opacity-60"
    ></div>
  {:else if variant === "water"}
    <div
      class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-amber-500 to-transparent opacity-60"
    ></div>
  {:else if variant === "gold"}
    <div
      class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-yellow-500 to-transparent opacity-70"
    ></div>
  {:else if variant === "mythic"}
    <div
      class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-orange-600 to-transparent opacity-60"
    ></div>
  {/if}

  {@render children()}
</div>

<style>
  @keyframes pulse-fire {
    0%,
    100% {
      box-shadow: 0 0 20px rgba(255, 90, 0, 0.3);
    }
    50% {
      box-shadow: 0 0 35px rgba(255, 90, 0, 0.5);
    }
  }

  @keyframes pulse-water {
    0%,
    100% {
      box-shadow: 0 0 20px rgba(180, 120, 60, 0.3);
    }
    50% {
      box-shadow: 0 0 30px rgba(180, 120, 60, 0.5);
    }
  }

  .animate-pulse-fire {
    animation: pulse-fire 2s ease-in-out infinite;
  }

  .animate-pulse-water {
    animation: pulse-water 3s ease-in-out infinite;
  }
</style>
