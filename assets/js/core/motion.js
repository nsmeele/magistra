// Shared animation helpers built on Motion (https://motion.dev).
// Every helper respects prefers-reduced-motion.
import { animate, inView, stagger } from 'motion';
import confetti from 'canvas-confetti';

export const reducedMotion = () =>
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

export const ease = {
    out: [0.2, 0.8, 0.2, 1],
    spring: { type: 'spring', stiffness: 420, damping: 26 },
    bouncy: { type: 'spring', stiffness: 500, damping: 18 },
};

/** Fade + slide elements in, staggered. */
export function enter(elements, { y = 14, delay = 0, gap = 0.05, duration = 0.5 } = {}) {
    if (!elements || (elements.length === 0)) return;
    if (reducedMotion()) {
        animate(elements, { opacity: 1, transform: 'none' }, { duration: 0 });
        return;
    }
    return animate(
        elements,
        { opacity: [0, 1], y: [y, 0] },
        { duration, ease: ease.out, delay: stagger(gap, { startDelay: delay }) },
    );
}

/** Springy scale-in, e.g. for feedback cards or badges. */
export function pop(element, { delay = 0 } = {}) {
    if (!element) return;
    if (reducedMotion()) return animate(element, { opacity: 1 }, { duration: 0 });
    return animate(element, { opacity: [0, 1], scale: [0.9, 1] }, { ...ease.bouncy, delay });
}

/** Horizontal shake for wrong answers / invalid input. */
export function shake(element) {
    if (!element || reducedMotion()) return;
    return animate(element, { x: [0, -10, 9, -6, 4, 0] }, { duration: 0.45, ease: 'easeInOut' });
}

/** Animate a number from 0 to its target. */
export function countUp(element, to, { duration = 1.2, decimals = 0, suffix = '' } = {}) {
    if (!element) return;
    const render = (v) => {
        element.textContent = v.toLocaleString('nl-NL', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals,
        }) + suffix;
    };
    if (reducedMotion()) return render(to);
    return animate(0, to, { duration, ease: ease.out, onUpdate: render });
}

/** Reveal [data-reveal] children once they scroll into view. */
export function initReveal(root = document) {
    root.querySelectorAll('[data-reveal]').forEach((group) => {
        const items = group.matches('[data-reveal="self"]')
            ? [group]
            : Array.from(group.children);
        if (reducedMotion()) return;
        items.forEach((el) => (el.style.opacity = '0'));

        // Watch each item, not the group: a long list can be many screens tall,
        // so a threshold on the whole group may never be reached. Items that
        // come into view in the same frame are staggered together.
        let batch = [];
        const flush = () => {
            enter(batch);
            batch = [];
        };
        inView(items, (el) => {
            if (batch.length === 0) requestAnimationFrame(flush);
            batch.push(el);
        }, { margin: '0px 0px -5% 0px' });
    });
}

/** Confetti burst in the brand colours. */
export function celebrate({ big = false } = {}) {
    if (reducedMotion()) return;
    const styles = getComputedStyle(document.documentElement);
    const colors = ['--primary', '--success', '--warning', '--info']
        .map((v) => styles.getPropertyValue(v).trim())
        .filter(Boolean);
    const base = { colors, disableForReducedMotion: true, zIndex: 60 };
    confetti({ ...base, particleCount: big ? 140 : 70, spread: 75, origin: { y: 0.65 } });
    if (big) {
        setTimeout(() => confetti({ ...base, particleCount: 60, angle: 60, spread: 60, origin: { x: 0, y: 0.7 } }), 200);
        setTimeout(() => confetti({ ...base, particleCount: 60, angle: 120, spread: 60, origin: { x: 1, y: 0.7 } }), 350);
    }
}

export { animate, inView, stagger };
