// Page module: lists pages. Called with the current endpoint name (body[data-page]).
import { animate, countUp, ease, enter, pop, reducedMotion, shake } from '../core/motion.js';

const PAGES = new Set(['index', 'list_detail', 'new_list', 'edit_entry', 'edit_list', 'all_entries']);

const ADD_OPEN_KEY = 'magistra-add-entry-open';
const JUST_ADDED_KEY = 'magistra-just-added';

const storage = (store) => ({
    get(key) {
        try { return store.getItem(key); } catch { return null; }
    },
    set(key, value) {
        try { store.setItem(key, value); } catch { /* storage unavailable */ }
    },
    remove(key) {
        try { store.removeItem(key); } catch { /* storage unavailable */ }
    },
});
const local = storage(window.localStorage);
const session = storage(window.sessionStorage);

export function initLists(page) {
    if (!PAGES.has(page)) return;

    shakeFieldErrors();
    enterRows();

    if (page === 'index') initImportSamples();
    if (page === 'list_detail') initAddEntry();
    if (page === 'new_list') initLanguagePair();
    if (page === 'all_entries') initTotals();
}

/** Shake fields that came back from the server with a validation error, and focus the first one. */
function shakeFieldErrors() {
    const fields = document.querySelectorAll('.field.has-error');
    fields.forEach((field) => shake(field));
    fields[0]?.querySelector('input, select, textarea')?.focus({ preventScroll: false });
}

/** Animate the first rows of long entry lists in; the rest appear instantly. */
function enterRows() {
    document.querySelectorAll('[data-enter-rows]').forEach((list) => {
        const rows = Array.from(list.children).slice(0, 12);
        enter(rows, { y: 10, gap: 0.035, duration: 0.4 });
    });
}

/* ------------------------------------------------------------------ */
/* index: import sample lists                                          */
/* ------------------------------------------------------------------ */

function initImportSamples() {
    const form = document.querySelector('[data-import-samples]');
    if (!form) return;
    form.addEventListener('submit', (event) => {
        const button = event.submitter || form.querySelector('button[type="submit"]');
        if (!button || form.dataset.busy) {
            if (form.dataset.busy) event.preventDefault();
            return;
        }
        form.dataset.busy = '1';
        // Swap the label after the submit has been dispatched, then lock the button.
        setTimeout(() => {
            button.disabled = true;
            button.setAttribute('aria-busy', 'true');
            button.innerHTML = '<i class="fa-solid fa-spinner fa-spin" aria-hidden="true"></i> Bezig met importeren…';
        }, 0);
    });
}

/* ------------------------------------------------------------------ */
/* list_detail: collapsible "add entry" panel                          */
/* ------------------------------------------------------------------ */

function initAddEntry() {
    const panel = document.querySelector('[data-add-entry]');
    if (!panel) return;
    const form = panel.querySelector('[data-add-entry-form]');
    const source = form?.querySelector('#source_word');

    // Wide desktop (xl) shows the panel as an always-open aside; that state is never persisted.
    const desktop = window.matchMedia('(min-width: 80rem)');
    const defaultOpen = panel.hasAttribute('data-default-open');
    let silent = false; // skip focus/animation for programmatic toggles
    const setOpen = (open) => {
        if (panel.open === open) return;
        silent = true;
        panel.open = open;
    };
    const applyLayout = () => {
        // Restore the open state on mobile (an empty list is always open).
        setOpen(desktop.matches || defaultOpen || local.get(ADD_OPEN_KEY) === '1');
    };
    applyLayout();
    desktop.addEventListener('change', applyLayout);

    // As an aside the summary is a heading: clicking it must not collapse the panel.
    panel.querySelector('summary')?.addEventListener('click', (event) => {
        if (desktop.matches) event.preventDefault();
    });

    panel.addEventListener('toggle', () => {
        const quiet = silent;
        silent = false;
        if (quiet) return;
        if (!defaultOpen && !desktop.matches) local.set(ADD_OPEN_KEY, panel.open ? '1' : '0');
        if (panel.open) {
            enter(form ? Array.from(form.querySelectorAll('.field, :scope > div:last-child')) : [], { y: 8, gap: 0.04, duration: 0.35 });
            source?.focus({ preventScroll: true });
        }
    });

    if (form) {
        form.addEventListener('submit', (event) => {
            const empty = Array.from(form.querySelectorAll('[required]')).filter((el) => !el.value.trim());
            if (empty.length) {
                event.preventDefault();
                empty.forEach((el) => shake(el.closest('.field')));
                empty[0].focus();
                return;
            }
            session.set(JUST_ADDED_KEY, source?.value.trim() || '');
            const button = form.querySelector('button[type="submit"]');
            if (button) {
                // Disable after the submit has been dispatched, to avoid double posts.
                setTimeout(() => { button.disabled = true; }, 0);
            }
        });
    }

    // After a successful add: highlight the new row and get ready for the next word.
    const added = session.get(JUST_ADDED_KEY);
    session.remove(JUST_ADDED_KEY);
    if (added !== null && panel.open && document.querySelector('.toast-success')) {
        const row = Array.from(document.querySelectorAll('#entries .entry-row'))
            .reverse()
            .find((el) => el.querySelector('.entry-term')?.textContent.trim() === added);
        if (row) {
            row.classList.add('is-new');
            pop(row, { delay: 0.25 });
            setTimeout(() => row.classList.remove('is-new'), 2600);
        }
        source?.focus({ preventScroll: true });
    }
}

/* ------------------------------------------------------------------ */
/* new_list: source/target language selects                            */
/* ------------------------------------------------------------------ */

function initLanguagePair() {
    const sourceSelect = document.getElementById('source_language_id');
    const targetSelect = document.getElementById('target_language_id');
    const swap = document.querySelector('[data-swap-languages]');
    if (!sourceSelect || !targetSelect) return;

    const isEmpty = (value) => value === '' || value === '0';

    // A language picked on one side cannot be picked on the other.
    const sync = (changed) => {
        if (changed && sourceSelect.value === targetSelect.value && !isEmpty(sourceSelect.value)) {
            const other = changed === sourceSelect ? targetSelect : sourceSelect;
            other.value = other.options[0]?.value ?? '';
            shake(other.closest('.field'));
        }
        Array.from(targetSelect.options).forEach((option) => {
            option.disabled = option.value === sourceSelect.value && !isEmpty(option.value);
        });
        Array.from(sourceSelect.options).forEach((option) => {
            option.disabled = option.value === targetSelect.value && !isEmpty(option.value);
        });
        if (swap) swap.disabled = isEmpty(sourceSelect.value) && isEmpty(targetSelect.value);
    };

    sourceSelect.addEventListener('change', () => sync(sourceSelect));
    targetSelect.addEventListener('change', () => sync(targetSelect));
    sync(null);

    swap?.addEventListener('click', () => {
        const from = sourceSelect.value;
        const to = targetSelect.value;
        // Re-enable everything first so the swapped values can be selected.
        [...sourceSelect.options, ...targetSelect.options].forEach((option) => { option.disabled = false; });
        sourceSelect.value = to;
        targetSelect.value = from;
        sync(null);

        if (reducedMotion()) return;
        const icon = swap.querySelector('svg, i');
        if (icon) animate(icon, { rotate: [0, 180] }, { ...ease.spring });
        const wide = window.matchMedia('(width >= 40rem)').matches;
        const offset = wide ? 'x' : 'y';
        animate(sourceSelect, { [offset]: [16, 0], opacity: [0.4, 1] }, { duration: 0.35, ease: ease.out });
        animate(targetSelect, { [offset]: [-16, 0], opacity: [0.4, 1] }, { duration: 0.35, ease: ease.out });
    });
}

/* ------------------------------------------------------------------ */
/* all_entries: animated total                                          */
/* ------------------------------------------------------------------ */

function initTotals() {
    document.querySelectorAll('[data-count-up]').forEach((el) => {
        const to = Number(el.dataset.countUp);
        if (Number.isFinite(to)) countUp(el, to, { duration: 0.9 });
    });
}
