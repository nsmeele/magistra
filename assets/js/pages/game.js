// Game layer: profile page and the dashboard daily card. Called with body[data-page].
import { animate, inView, stagger, countUp, celebrate, pop, reducedMotion, ease } from '../core/motion.js';

export function initGame(page) {
    if (page === 'profile') {
        const root = document.querySelector('[data-profile]');
        if (!root) return;
        initRings(root);
        initCounts(root);
        initMedals(root);
        celebrateDailyGoal(root.querySelector('[data-daily-goal][data-daily-done]'));
    } else if (page === 'index') {
        const card = document.querySelector('[data-daily-card]');
        if (!card) return;
        initRings(card);
        if (card.hasAttribute('data-daily-done')) celebrateDailyGoal(card);
    }
}

/** Fill conic rings ([data-game-ring="pct"]) from 0 once they scroll into view. */
function initRings(root) {
    if (reducedMotion()) return;
    root.querySelectorAll('[data-game-ring]').forEach((ring) => {
        const to = parseFloat(ring.dataset.gameRing) || 0;
        ring.style.transition = 'none';
        ring.style.setProperty('--value', '0');
        inView(ring, () => {
            animate(0, to, {
                duration: 1.3,
                ease: ease.out,
                onUpdate: (v) => ring.style.setProperty('--value', String(v)),
            });
        }, { amount: 0.4 });
    });
}

/** Count numbers up from 0 ([data-game-count="n"]). */
function initCounts(root) {
    if (reducedMotion()) return;
    root.querySelectorAll('[data-game-count]').forEach((el) => {
        const to = parseInt(el.dataset.gameCount, 10) || 0;
        if (to === 0) return;
        el.textContent = '0';
        inView(el, () => { countUp(el, to, { duration: to > 50 ? 1.4 : 0.9 }); }, { amount: 0.5 });
    });
}

/** Unlocked medals pop in, staggered; the "Bijna!" tag gets a little nudge. */
function initMedals(root) {
    const grid = root.querySelector('[data-achievements]');
    if (!grid || reducedMotion()) return;
    const medals = Array.from(grid.querySelectorAll('[data-unlocked] .medal'));
    const tag = grid.querySelector('.achievement-bijna');
    medals.forEach((m) => (m.style.opacity = '0'));
    if (tag) tag.style.opacity = '0';

    inView(grid, () => {
        if (medals.length) {
            animate(
                medals,
                { opacity: [0, 1], scale: [0.4, 1], rotate: [-25, 0] },
                { ...ease.bouncy, delay: stagger(0.07) },
            );
        }
        if (tag) pop(tag, { delay: 0.25 + medals.length * 0.07 });
    }, { amount: 0.15 });
}

/** Confetti when today's goal is reached, at most once per day per browser. */
function celebrateDailyGoal(el) {
    if (!el) return;
    const key = `magistra-goal-${new Date().toISOString().slice(0, 10)}`;
    try {
        if (localStorage.getItem(key)) return;
        localStorage.setItem(key, '1');
    } catch (e) {
        // Storage blocked: still celebrate, just not remembered.
    }
    inView(el, () => { setTimeout(() => celebrate(), 300); }, { amount: 0.6 });
}
