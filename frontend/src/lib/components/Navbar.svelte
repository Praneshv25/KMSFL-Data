<script lang="ts">
  import { page } from "$app/stores";
  import { ripple } from "$lib/actions";

  const navItems = [
    { href: "/", label: "Home", icon: "🏠" },
    { href: "/champions", label: "Champions", icon: "🏆" },
    { href: "/history", label: "History", icon: "📜" },
    { href: "/records", label: "Records", icon: "📊" },
    { href: "/managers", label: "Managers", icon: "👥" },
    { href: "/tidbits", label: "Tidbits", icon: "💡" },
    { href: "/commissioner", label: "Commish", icon: "👑" },
    { href: "/studio", label: "Studio", icon: "✨" },
  ];

  let currentPath = $derived($page.url.pathname);
</script>

<nav class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
  <div
    class="
    flex items-center gap-1 px-4 py-3
    bg-white/5 backdrop-blur-2xl
    border border-white/10
    rounded-full
    shadow-2xl shadow-black/20
  "
  >
    {#each navItems as item}
      {@const isActive =
        currentPath === item.href ||
        (item.href !== "/" && currentPath.startsWith(item.href))}
      <a
        href={item.href}
        use:ripple
        class="
          relative px-4 py-2 rounded-full
          text-sm font-medium
          transition-all duration-300
          hover:bg-white/10
          {isActive
          ? 'bg-white/15 text-white'
          : 'text-white/60 hover:text-white'}
        "
      >
        <!-- Active indicator glow -->
        {#if isActive}
          <div
            class="
            absolute inset-0 rounded-full
            bg-gradient-to-r from-orange-500/20 via-amber-600/20 to-yellow-500/20
            animate-pulse
          "
          ></div>
        {/if}

        <span class="relative flex items-center gap-2">
          <span class="text-base">{item.icon}</span>
          <span class="hidden md:inline">{item.label}</span>
        </span>
      </a>
    {/each}
  </div>
</nav>

<style>
  nav {
    /* Prevent nav from affecting page scroll */
    pointer-events: auto;
  }

  /* Subtle hover lift */
  nav > div:hover {
    transform: translateY(-2px);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4);
  }

  nav > div {
    transition:
      transform 0.3s ease,
      box-shadow 0.3s ease;
  }
</style>
