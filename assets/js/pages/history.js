// Page module: quiz history pages. Called with the current endpoint name (body[data-page]).
import { animate, inView, enter, countUp, reducedMotion, ease } from '../core/motion.js';

export function initHistory(page) {
    if (page === 'quiz_history') {
        initStats();
        initProgressBars();
        initFilter(document.querySelector('[data-history-list]'), (el, filter) => el.dataset.type === filter);
        initTrendChart();
    } else if (page === 'quiz_history_detail') {
        initScoreRing();
        initFilter(document.querySelector('[data-answers]'), (el, filter) =>
            filter === 'correct' ? el.dataset.correct === 'true' : el.dataset.correct === 'false');
    }
}

/* ------------------------------------------------------------------ */
/* Shared                                                              */
/* ------------------------------------------------------------------ */

/** Chip filter: [data-filter] buttons toggle the children of [data-filter-items]. */
function initFilter(root, matches) {
    if (!root) return;
    const chips = Array.from(root.querySelectorAll('.chip[data-filter]'));
    const list = root.querySelector('[data-filter-items]');
    if (!chips.length || !list) return;

    const items = Array.from(list.children);
    const empty = root.querySelector('[data-filter-empty]');

    chips.forEach((chip) => {
        chip.addEventListener('click', () => {
            if (chip.getAttribute('aria-pressed') === 'true') return;
            chips.forEach((c) => c.setAttribute('aria-pressed', String(c === chip)));

            const filter = chip.dataset.filter;
            const visible = items.filter((el) => filter === 'all' || matches(el, filter));
            items.forEach((el) => { el.hidden = !visible.includes(el); });
            if (empty) empty.hidden = visible.length > 0;

            // Animate what is likely on screen; show the rest instantly.
            const head = visible.slice(0, 12);
            visible.slice(12).forEach((el) => { el.style.opacity = '1'; el.style.transform = 'none'; });
            enter(head, { y: 10, gap: 0.035, duration: 0.35 });
            if (empty && !empty.hidden) enter([empty], { y: 8, duration: 0.3 });
        });
    });
}

/* ------------------------------------------------------------------ */
/* Overview page                                                       */
/* ------------------------------------------------------------------ */

function initStats() {
    const values = document.querySelectorAll('.stat-value[data-count]');
    if (!values.length) return;
    inView(values[0].closest('section') || values[0], () => {
        values.forEach((el) => {
            countUp(el, parseFloat(el.dataset.count) || 0, {
                decimals: parseInt(el.dataset.decimals || '0', 10),
                suffix: el.dataset.suffix || '',
            });
        });
    }, { amount: 0.3 });
}

function initProgressBars() {
    document.querySelectorAll('.progress > span[data-progress]').forEach((bar) => {
        if (reducedMotion()) return;
        const to = `${parseFloat(bar.dataset.progress) || 0}%`;
        bar.style.transition = 'none';
        bar.style.width = '0%';
        inView(bar, () => {
            animate(bar, { width: ['0%', to] }, { duration: 0.9, ease: ease.out, delay: 0.2 });
        });
    });
}

/** Resolve any CSS colour to [r, g, b] so we can add alpha for the canvas. */
function rgb(color) {
    const ctx = rgb.ctx || (rgb.ctx = document.createElement('canvas').getContext('2d'));
    ctx.fillStyle = '#000';
    ctx.fillStyle = color;
    const v = ctx.fillStyle; // "#rrggbb" or "rgba(r, g, b, a)"
    if (v.startsWith('#')) {
        return [1, 3, 5].map((i) => parseInt(v.slice(i, i + 2), 16));
    }
    return (v.match(/[\d.]+/g) || [0, 0, 0]).slice(0, 3).map(Number);
}
const alpha = (color, a) => `rgba(${rgb(color).join(', ')}, ${a})`;

function readPalette() {
    const css = getComputedStyle(document.documentElement);
    const v = (name) => css.getPropertyValue(name).trim();
    return {
        primary: v('--primary'),
        text: v('--text'),
        muted: v('--text-muted'),
        subtle: v('--text-subtle'),
        grid: v('--chart-grid'),
        surface: v('--surface'),
        border: v('--border-strong'),
        success: v('--success'),
        warning: v('--warning'),
        danger: v('--danger'),
        font: getComputedStyle(document.body).fontFamily,
    };
}

function initTrendChart() {
    const canvas = document.getElementById('score-trend-chart');
    const dataEl = document.getElementById('score-trend-data');
    if (!canvas || !dataEl) return;

    let points;
    try { points = JSON.parse(dataEl.textContent); } catch { return; }
    if (!Array.isArray(points) || points.length < 2) return;

    const scores = points.map((p) => p.score);
    const average = scores.reduce((a, b) => a + b, 0) / scores.length;
    const fmt = (n) => n.toLocaleString('nl-NL', { maximumFractionDigits: 1 });

    // Load Chart.js only when the chart scrolls into view (separate chunk).
    inView(canvas, () => {
        import('chart.js/auto').then(({ default: Chart }) => {
            let pal = readPalette();
            const band = (score) => (score >= 80 ? pal.success : score >= 60 ? pal.warning : pal.danger);
            const narrow = () => window.matchMedia('(max-width: 639px)').matches;
            Chart.defaults.font.family = pal.font;

            const chart = new Chart(canvas, {
                type: 'line',
                data: {
                    labels: points.map((p) => p.date),
                    datasets: [
                        {
                            label: 'Score',
                            data: scores,
                            borderColor: () => pal.primary,
                            borderWidth: 2.5,
                            tension: 0.35,
                            fill: 'origin',
                            backgroundColor: ({ chart: c }) => {
                                const area = c.chartArea;
                                if (!area) return 'transparent';
                                const g = c.ctx.createLinearGradient(0, area.top, 0, area.bottom);
                                g.addColorStop(0, alpha(pal.primary, 0.28));
                                g.addColorStop(1, alpha(pal.primary, 0));
                                return g;
                            },
                            pointRadius: () => (points.length > 30 ? 0 : 4),
                            pointHoverRadius: 7,
                            pointBorderWidth: 2,
                            pointBackgroundColor: (ctx) => band(ctx.raw ?? 0),
                            pointBorderColor: () => pal.surface,
                            pointHoverBorderColor: () => pal.surface,
                        },
                        {
                            label: 'Gemiddelde',
                            data: scores.map(() => average),
                            borderColor: () => pal.subtle,
                            borderWidth: 1.5,
                            borderDash: [5, 5],
                            pointRadius: 0,
                            pointHoverRadius: 0,
                            fill: false,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: reducedMotion() ? false : { duration: 900, easing: 'easeOutQuart' },
                    interaction: { mode: 'index', intersect: false },
                    layout: { padding: { top: 6, right: 4 } },
                    scales: {
                        y: {
                            min: 0,
                            max: 100,
                            border: { display: false },
                            grid: { color: pal.grid, drawTicks: false },
                            ticks: { stepSize: 25, padding: 8, color: pal.muted, callback: (v) => `${v}%` },
                        },
                        x: {
                            border: { display: false },
                            grid: { display: false },
                            ticks: {
                                color: pal.muted,
                                maxRotation: 0,
                                autoSkip: true,
                                maxTicksLimit: narrow() ? 4 : 8,
                            },
                        },
                    },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            filter: (item) => item.datasetIndex === 0,
                            backgroundColor: pal.surface,
                            titleColor: pal.text,
                            bodyColor: pal.muted,
                            borderColor: pal.border,
                            borderWidth: 1,
                            padding: 12,
                            cornerRadius: 12,
                            displayColors: false,
                            callbacks: {
                                title: (items) => points[items[0].dataIndex].title,
                                label: (item) => {
                                    const p = points[item.dataIndex];
                                    return [`${fmt(p.score)}% · ${p.correct}/${p.total} goed`, p.date,
                                        `Gemiddeld: ${fmt(average)}%`];
                                },
                            },
                        },
                    },
                },
            });

            const applyPalette = () => {
                pal = readPalette();
                Chart.defaults.font.family = pal.font;
                const { scales, plugins } = chart.options;
                scales.y.grid.color = pal.grid;
                scales.y.ticks.color = pal.muted;
                scales.x.ticks.color = pal.muted;
                Object.assign(plugins.tooltip, {
                    backgroundColor: pal.surface,
                    titleColor: pal.text,
                    bodyColor: pal.muted,
                    borderColor: pal.border,
                });
            };

            window.addEventListener('themechange', () => {
                // Wait a frame so the new CSS variables are in effect.
                requestAnimationFrame(() => { applyPalette(); chart.update('none'); });
            });

            window.matchMedia('(max-width: 639px)').addEventListener('change', () => {
                chart.options.scales.x.ticks.maxTicksLimit = narrow() ? 4 : 8;
                chart.update('none');
            });
        });
    }, { amount: 0.2 });
}

/* ------------------------------------------------------------------ */
/* Detail page                                                         */
/* ------------------------------------------------------------------ */

function initScoreRing() {
    const ring = document.querySelector('[data-score-ring]');
    if (!ring || reducedMotion()) return;
    const to = parseFloat(ring.dataset.scoreRing) || 0;
    const label = ring.querySelector('[data-score-value]');

    ring.style.transition = 'none';
    ring.style.setProperty('--value', '0');
    if (label) label.textContent = '0%';

    inView(ring, () => {
        animate(0, to, {
            duration: 1.3,
            ease: ease.out,
            delay: 0.15,
            onUpdate: (v) => ring.style.setProperty('--value', v.toFixed(2)),
        });
        if (label) {
            countUp(label, to, { duration: 1.3, decimals: Number.isInteger(to) ? 0 : 1, suffix: '%' });
        }
    }, { amount: 0.4 });
}
