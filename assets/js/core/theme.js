// Light/dark theme toggle with a circular reveal (View Transitions API when available).
const KEY = 'magistra-theme';
const root = document.documentElement;

export const currentTheme = () => root.dataset.theme === 'dark' ? 'dark' : 'light';

function apply(theme) {
    root.dataset.theme = theme;
    try { localStorage.setItem(KEY, theme); } catch { /* storage unavailable */ }
    window.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
}

export function initTheme() {
    // Follow the OS setting until the user picks a theme themselves.
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        let stored = null;
        try { stored = localStorage.getItem(KEY); } catch { /* ignore */ }
        if (!stored) {
            root.dataset.theme = e.matches ? 'dark' : 'light';
            window.dispatchEvent(new CustomEvent('themechange', { detail: { theme: currentTheme() } }));
        }
    });

    document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
        btn.addEventListener('click', (event) => {
            const next = currentTheme() === 'dark' ? 'light' : 'dark';
            const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            if (!document.startViewTransition || reduce) return apply(next);

            const x = event.clientX || window.innerWidth / 2;
            const y = event.clientY || 0;
            const r = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
            const transition = document.startViewTransition(() => apply(next));
            transition.ready.then(() => {
                document.documentElement.animate(
                    { clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${r}px at ${x}px ${y}px)`] },
                    { duration: 550, easing: 'cubic-bezier(.2,.8,.2,1)', pseudoElement: '::view-transition-new(root)' },
                );
            });
        });
    });
}
