// Client-side filtering.
// <input data-search="target-id"> filters children of #target-id that have [data-search-text].
// Optional: element [data-search-empty="target-id"] is shown when nothing matches,
// and [data-search-count="target-id"] gets the number of visible items.
const normalize = (s) => s.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().trim();

export function initSearch() {
    document.querySelectorAll('[data-search]').forEach((input) => {
        const id = input.dataset.search;
        const container = document.getElementById(id);
        if (!container) return;
        const items = Array.from(container.querySelectorAll('[data-search-text]'));
        const empty = document.querySelector(`[data-search-empty="${id}"]`);
        const counter = document.querySelector(`[data-search-count="${id}"]`);

        const run = () => {
            const q = normalize(input.value);
            let visible = 0;
            items.forEach((item) => {
                const match = !q || normalize(item.dataset.searchText).includes(q);
                item.hidden = !match;
                if (match) visible++;
            });
            if (empty) empty.hidden = visible > 0;
            if (counter) counter.textContent = visible;
        };
        input.addEventListener('input', run);
        input.addEventListener('keydown', (e) => { if (e.key === 'Escape') { input.value = ''; run(); } });
    });

    // Press "/" to focus the first search field.
    document.addEventListener('keydown', (e) => {
        if (e.key !== '/' || e.target.matches('input, textarea, select')) return;
        const field = document.querySelector('[data-search]');
        if (field) { e.preventDefault(); field.focus(); }
    });
}
