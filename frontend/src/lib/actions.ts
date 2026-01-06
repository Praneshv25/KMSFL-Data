/**
 * Svelte Actions for The Elemental League
 * Interactive visual effects: ignite (fire sparks) and ripple (water effect)
 */

import { browser } from '$app/environment';

interface SparkParticle {
    x: number;
    y: number;
    vx: number;
    vy: number;
    life: number;
    maxLife: number;
    size: number;
    color: string;
}

const sparkColors = ['#FF5A00', '#FF8C00', '#FFD200', '#FFAA00'];

/**
 * Ignite action - creates spark particles on hover
 * Use on elements that should "burn" when interacted with (wins, high stats)
 */
export function ignite(node: HTMLElement) {
    let canvas: HTMLCanvasElement | null = null;
    let ctx: CanvasRenderingContext2D | null = null;
    let particles: SparkParticle[] = [];
    let animationId: number | null = null;
    let isActive = false;

    function createCanvas() {
        canvas = document.createElement('canvas');
        canvas.style.cssText = `
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 10;
    `;

        const rect = node.getBoundingClientRect();
        canvas.width = rect.width;
        canvas.height = rect.height;

        node.style.position = 'relative';
        node.appendChild(canvas);
        ctx = canvas.getContext('2d');
    }

    function createSpark(x: number, y: number): SparkParticle {
        return {
            x,
            y,
            vx: (Math.random() - 0.5) * 4,
            vy: -Math.random() * 3 - 1,
            life: 1,
            maxLife: 30 + Math.random() * 20,
            size: Math.random() * 3 + 1,
            color: sparkColors[Math.floor(Math.random() * sparkColors.length)]
        };
    }

    function spawnSparks() {
        if (!canvas) return;
        for (let i = 0; i < 3; i++) {
            const x = Math.random() * canvas.width;
            const y = canvas.height - 5;
            particles.push(createSpark(x, y));
        }
    }

    function animate() {
        if (!ctx || !canvas) return;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        particles = particles.filter(p => {
            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.05; // gravity
            p.life = Math.max(0, p.life - (1 / p.maxLife));

            // Draw spark
            ctx!.beginPath();
            ctx!.arc(p.x, p.y, p.size * p.life, 0, Math.PI * 2);
            ctx!.fillStyle = p.color;
            ctx!.globalAlpha = p.life * 0.8;
            ctx!.fill();
            ctx!.globalAlpha = 1;

            return p.life > 0;
        });

        if (isActive) {
            spawnSparks();
        }

        if (particles.length > 0 || isActive) {
            animationId = requestAnimationFrame(animate);
        }
    }

    function handleMouseEnter() {
        if (!canvas) createCanvas();
        isActive = true;
        if (!animationId) animate();
    }

    function handleMouseLeave() {
        isActive = false;
    }

    node.addEventListener('mouseenter', handleMouseEnter);
    node.addEventListener('mouseleave', handleMouseLeave);

    return {
        destroy() {
            node.removeEventListener('mouseenter', handleMouseEnter);
            node.removeEventListener('mouseleave', handleMouseLeave);
            if (animationId) cancelAnimationFrame(animationId);
            if (canvas) canvas.remove();
        }
    };
}

/**
 * Ripple action - creates water ripple effect on click
 * Use on navigation items, buttons, table rows
 */
export function ripple(node: HTMLElement) {
    function createRipple(event: MouseEvent) {
        const rect = node.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;

        const ripple = document.createElement('span');
        ripple.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      left: ${x}px;
      top: ${y}px;
      background: radial-gradient(circle, rgba(79, 172, 254, 0.4) 0%, transparent 70%);
      border-radius: 50%;
      transform: scale(0);
      animation: ripple-effect 0.6s ease-out forwards;
      pointer-events: none;
      z-index: 1;
    `;

        // Ensure parent has position for absolute positioning
        const computedStyle = getComputedStyle(node);
        if (computedStyle.position === 'static') {
            node.style.position = 'relative';
        }
        node.style.overflow = 'hidden';

        node.appendChild(ripple);

        ripple.addEventListener('animationend', () => {
            ripple.remove();
        });
    }

    // Inject keyframes if not already present (only in browser)
    if (browser && !document.getElementById('ripple-keyframes')) {
        const style = document.createElement('style');
        style.id = 'ripple-keyframes';
        style.textContent = `
      @keyframes ripple-effect {
        to {
          transform: scale(2);
          opacity: 0;
        }
      }
    `;
        document.head.appendChild(style);
    }

    node.addEventListener('click', createRipple);

    return {
        destroy() {
            node.removeEventListener('click', createRipple);
        }
    };
}

/**
 * Float action - adds subtle floating animation
 * Use on cards, badges, or highlighted items
 */
export function float(node: HTMLElement, { duration = 3000, amplitude = 10 } = {}) {
    node.style.animation = `float-effect ${duration}ms ease-in-out infinite`;

    // Inject keyframes if not already present (only in browser)
    if (browser && !document.getElementById('float-keyframes')) {
        const style = document.createElement('style');
        style.id = 'float-keyframes';
        style.textContent = `
      @keyframes float-effect {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-${amplitude}px); }
      }
    `;
        document.head.appendChild(style);
    }

    return {
        destroy() {
            node.style.animation = '';
        }
    };
}
