<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { browser } from "$app/environment";

  interface Particle {
    x: number;
    y: number;
    vx: number;
    vy: number;
    radius: number;
    color: string;
    alpha: number;
    type: "fire" | "water";
  }

  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D | null;
  let animationId: number;
  let particles: Particle[] = [];

  const PARTICLE_COUNT = 80;

  // Fire colors (warm oranges and reds)
  const fireColors = ["#FF5A00", "#FF8C00", "#FFD200", "#FF4500"];
  // Ember colors (warm ambers and bronze - replacing cold water)
  const waterColors = ["#D4A84B", "#B8860B", "#CD853F", "#8B4513"];

  function createParticle(type: "fire" | "water"): Particle {
    const colors = type === "fire" ? fireColors : waterColors;
    const isFire = type === "fire";

    return {
      x: isFire
        ? Math.random() * canvas.width * 0.5
        : canvas.width * 0.5 + Math.random() * canvas.width * 0.5,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 2 + (isFire ? 0.5 : -0.5),
      vy: (Math.random() - 0.5) * 1.5 + (isFire ? -0.5 : 0.5),
      radius: Math.random() * 3 + 2,
      color: colors[Math.floor(Math.random() * colors.length)],
      alpha: Math.random() * 0.5 + 0.3,
      type,
    };
  }

  function initParticles() {
    particles = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push(createParticle(i < PARTICLE_COUNT / 2 ? "fire" : "water"));
    }
  }

  function updateParticle(p: Particle) {
    p.x += p.vx;
    p.y += p.vy;

    // Add some turbulence near the center (collision zone)
    const centerX = canvas.width / 2;
    const distFromCenter = Math.abs(p.x - centerX);
    if (distFromCenter < 150) {
      p.vy += (Math.random() - 0.5) * 0.3;
      p.vx += (Math.random() - 0.5) * 0.3;
    }

    // Boundary handling with respawn
    if (
      p.x < -10 ||
      p.x > canvas.width + 10 ||
      p.y < -10 ||
      p.y > canvas.height + 10
    ) {
      Object.assign(p, createParticle(p.type));
    }

    // Subtle alpha flickering
    p.alpha = Math.max(
      0.2,
      Math.min(0.8, p.alpha + (Math.random() - 0.5) * 0.05),
    );
  }

  function drawParticle(p: Particle) {
    if (!ctx) return;

    // Create radial gradient for glow effect
    const gradient = ctx.createRadialGradient(
      p.x,
      p.y,
      0,
      p.x,
      p.y,
      p.radius * 3,
    );
    gradient.addColorStop(0, p.color);
    gradient.addColorStop(0.5, p.color + "80");
    gradient.addColorStop(1, "transparent");

    ctx.beginPath();
    ctx.arc(p.x, p.y, p.radius * 3, 0, Math.PI * 2);
    ctx.fillStyle = gradient;
    ctx.globalAlpha = p.alpha;
    ctx.fill();
    ctx.globalAlpha = 1;
  }

  function drawCollisionZone() {
    if (!ctx) return;

    const centerX = canvas.width / 2;
    const gradient = ctx.createLinearGradient(
      centerX - 100,
      0,
      centerX + 100,
      0,
    );
    gradient.addColorStop(0, "rgba(255, 90, 0, 0.1)");
    gradient.addColorStop(0.5, "rgba(155, 89, 182, 0.15)");
    gradient.addColorStop(1, "rgba(79, 172, 254, 0.1)");

    ctx.fillStyle = gradient;
    ctx.fillRect(centerX - 100, 0, 200, canvas.height);
  }

  function animate() {
    if (!ctx) return;

    // Clear with slight fade for trails (warm burgundy)
    ctx.fillStyle = "rgba(26, 15, 10, 0.15)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Removed collision zone visual - was too prominent

    for (const particle of particles) {
      updateParticle(particle);
      drawParticle(particle);
    }

    animationId = requestAnimationFrame(animate);
  }

  function handleResize() {
    if (!canvas || !browser) return;
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    initParticles();
  }

  onMount(() => {
    if (!browser) return;
    ctx = canvas.getContext("2d");
    handleResize();
    animate();

    window.addEventListener("resize", handleResize);
  });

  onDestroy(() => {
    if (!browser) return;
    if (animationId) {
      cancelAnimationFrame(animationId);
    }
    window.removeEventListener("resize", handleResize);
  });
</script>

<canvas
  bind:this={canvas}
  class="fixed inset-0 -z-10 pointer-events-none"
  aria-hidden="true"
></canvas>

<style>
  canvas {
    background: linear-gradient(180deg, #1a0f0a 0%, #2d1810 50%, #1a0f0a 100%);
  }
</style>
