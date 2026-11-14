// Page module: quiz pages. Called with the current endpoint name (body[data-page]).
// quiz_complete.html is rendered by the `quiz` endpoint and mixed_quiz_complete.html by
// `mixed_quiz_question`, so the question/result views are detected by data attributes.
import { animate, enter, pop, shake, countUp, celebrate, reducedMotion, ease } from '../core/motion.js';
import { initReveal } from '../core/motion.js';
import { initToasts } from '../core/toasts.js';
import { play, isSoundOn, setSound, unlock } from '../core/sound.js';

const QUIZ_PAGES = new Set([
    'quiz_start', 'quiz', 'mixed_quiz', 'mixed_quiz_question', 'smart_practice', 'smart_practice_list',
]);

const COMBO_KEY = 'magistra-combo';

export function initQuiz(page) {
    if (!QUIZ_PAGES.has(page)) return;
    mount(document);

    const mixed = document.querySelector('[data-mixed-form]');
    if (mixed) initMixedSelection(mixed);

    if (page === 'smart_practice' || page === 'smart_practice_list') initSmartPractice();
}

/** Initialise question/result views inside `root` (also used after a soft navigation). */
function mount(root) {
    const question = root.querySelector('[data-quiz-question]');
    if (question) initQuestion(question);

    const result = root.querySelector('[data-quiz-result]');
    if (result) initResult(result);
}

const storage = {
    get(key) { try { return sessionStorage.getItem(key); } catch { return null; } },
    set(key, value) { try { sessionStorage.setItem(key, value); } catch { /* blocked */ } },
};

/* ------------------------------------------------------------------ */
/* Question                                                            */
/* ------------------------------------------------------------------ */

function initQuestion(root) {
    const card = root.querySelector('[data-quiz-card]');
    const word = root.querySelector('[data-quiz-word]');
    const feedback = root.querySelector('[data-feedback]');

    initSoundToggle(root.querySelector('[data-sound-toggle]'));

    // Feedback on the previous answer.
    if (feedback) {
        if (feedback.dataset.feedback === 'success') pop(feedback);
        else shake(feedback);
    }
    initCombo(root, feedback);

    // Progress bar grows from the previous step.
    const progress = root.querySelector('[data-progress]');
    const bar = progress?.querySelector('[data-progress-bar]');
    if (bar && !reducedMotion()) {
        const current = Number(progress.dataset.current);
        const total = Number(progress.dataset.total) || 1;
        const target = bar.style.width;
        const from = Math.max(0, ((current - 2) / total) * 100);
        bar.style.transition = 'none';
        bar.style.width = `${from}%`;
        requestAnimationFrame(() => requestAnimationFrame(() => {
            bar.style.transition = '';
            bar.style.width = target;
        }));
    }

    // Word entrance.
    if (card && !reducedMotion()) {
        animate(card, { opacity: [0, 1], y: [16, 0], scale: [0.98, 1] }, { ...ease.spring, delay: feedback ? 0.1 : 0 });
        if (word) animate(word, { opacity: [0, 1], y: [10, 0] }, { duration: 0.5, ease: ease.out, delay: 0.15 });
    }

    bindAnswerForm(root.querySelector('[data-answer-form]'));
    bindGlobalKeys();
}

/** Combo meter, combo break, XP float and sounds for the answer that was just given. */
function initCombo(root, feedback) {
    const meter = root.querySelector('[data-combo]');
    const combo = Number(meter?.dataset.combo) || 0;
    const previous = Number(storage.get(COMBO_KEY)) || 0;
    storage.set(COMBO_KEY, String(combo));

    if (!feedback) return;
    const motion = !reducedMotion();

    if (feedback.dataset.feedback === 'success') {
        const milestone = combo === 3 || combo === 5 || combo === 10 || (combo > 10 && combo % 5 === 0);
        play(milestone ? 'combo' : 'correct');

        const xp = feedback.querySelector('[data-xp-float]');
        if (xp && motion) {
            animate(xp, { opacity: [0, 1, 1, 0], y: [8, -10, -22, -44], scale: [0.8, 1.1, 1, 1] },
                { duration: 1.3, ease: 'easeOut', times: [0, 0.2, 0.6, 1], delay: 0.15 });
        }

        const bonus = feedback.querySelector('[data-combo-bonus]');
        if (bonus && motion) {
            animate(bonus, { opacity: [0, 1], scale: [0.4, 1.15, 1], rotate: [-8, 4, 0] }, { duration: 0.5, delay: 0.3 });
        }

        if (meter && combo >= 2 && combo > previous && motion) {
            animate(meter, { scale: milestone ? [1, 1.45, 1] : [1, 1.25, 1], rotate: milestone ? [0, -6, 6, 0] : 0 },
                { duration: milestone ? 0.55 : 0.4, ease: 'easeOut' });
        }
    } else {
        play('wrong');
        const broken = root.querySelector('[data-combo-break]');
        if (broken && previous >= 3) {
            broken.textContent = `Combo ×${previous}`;
            broken.hidden = false;
            if (motion) {
                animate(broken, { x: [0, -6, 6, -4, 0], opacity: [1, 1, 0], scale: [1, 1.05, 0.6], rotate: [0, 0, 12], filter: ['blur(0px)', 'blur(0px)', 'blur(3px)'] },
                    { duration: 0.9, ease: 'easeIn', times: [0, 0.4, 1] })
                    .then(() => { broken.hidden = true; });
            } else {
                setTimeout(() => { broken.hidden = true; }, 1500);
            }
        }
    }
}

function initSoundToggle(button) {
    if (!button) return;
    const sync = () => button.setAttribute('aria-pressed', String(isSoundOn()));
    sync();
    button.addEventListener('click', () => {
        setSound(!isSoundOn());
        sync();
        if (isSoundOn()) play('correct');
        if (!reducedMotion()) animate(button, { scale: [0.85, 1] }, ease.bouncy);
    });
}

let globalsBound = false;
function bindGlobalKeys() {
    if (globalsBound) return;
    globalsBound = true;

    // Esc jumps back to the answer field.
    document.addEventListener('keydown', (event) => {
        if (event.key !== 'Escape' || event.defaultPrevented) return;
        if (document.querySelector('dialog[open]')) return;
        const input = document.querySelector('[data-answer-input]');
        if (input) {
            input.focus();
            input.select();
        }
    });

    // Keep input and button visible above the on-screen keyboard.
    window.visualViewport?.addEventListener('resize', () => {
        const input = document.querySelector('[data-answer-input]');
        if (input && document.activeElement === input) keepVisible();
    });

    // Restore state when navigating back via bfcache.
    window.addEventListener('pageshow', (event) => {
        if (!event.persisted) return;
        const form = document.querySelector('[data-answer-form]');
        if (form) resetForm(form);
    });
}

function keepVisible() {
    if (window.matchMedia('(min-width: 768px)').matches) return;
    const submit = document.querySelector('[data-answer-submit]');
    setTimeout(() => submit?.scrollIntoView({ block: 'end', behavior: reducedMotion() ? 'auto' : 'smooth' }), 250);
}

const SUBMIT_LABEL = '<i class="fa-solid fa-check"></i> Controleer';

function resetForm(form) {
    const input = form.querySelector('[data-answer-input]');
    const submit = form.querySelector('[data-answer-submit]');
    delete form.dataset.submitting;
    input.readOnly = false;
    input.value = '';
    submit.innerHTML = SUBMIT_LABEL;
    submit.disabled = true;
}

function bindAnswerForm(form) {
    if (!form || form.dataset.bound) return;
    const input = form.querySelector('[data-answer-input]');
    const submit = form.querySelector('[data-answer-submit]');
    if (!input || !submit) return;
    form.dataset.bound = '1';

    const sync = () => { submit.disabled = input.value.trim() === '' || Boolean(form.dataset.submitting); };
    sync();
    input.addEventListener('input', sync);

    // Autofocus is unreliable after a redirect on some mobile browsers.
    if (document.activeElement !== input) input.focus({ preventScroll: true });
    input.addEventListener('focus', keepVisible);

    form.addEventListener('submit', (event) => {
        if (input.value.trim() === '') {
            event.preventDefault();
            shake(input);
            input.focus();
            return;
        }
        if (form.dataset.submitting) {
            event.preventDefault();
            return;
        }
        unlock(); // user gesture: lets the next feedback sound play
        form.dataset.submitting = '1';
        const data = new FormData(form);
        input.readOnly = true; // readonly, not disabled, so the value is still posted
        submit.disabled = true;
        submit.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Controleren...';

        if (!window.fetch || !window.DOMParser) return; // native submit
        event.preventDefault();
        softSubmit(form, data).catch(() => {
            // Network failure: fall back to a normal form post.
            HTMLFormElement.prototype.submit.call(form);
        });
    });
}

/**
 * Post the answer in the background and swap in the next question without a full
 * page load. This keeps the on-screen keyboard open on mobile (the answer field
 * itself is kept) and lets Web Audio play, since we stay inside the user gesture's page.
 */
async function softSubmit(form, data) {
    const response = await fetch(form.action, {
        method: 'POST',
        body: data,
        credentials: 'same-origin',
        headers: { Accept: 'text/html' },
    });

    const target = new URL(response.url, location.href);
    if (!response.ok || target.pathname !== location.pathname) {
        // Error page or redirect elsewhere (e.g. quiz could not load): follow it for real.
        location.assign(response.ok ? response.url : location.href);
        return;
    }

    const doc = new DOMParser().parseFromString(await response.text(), 'text/html');
    const nextMain = doc.querySelector('main');
    if (!nextMain) {
        location.assign(location.href);
        return;
    }
    document.title = doc.title;

    // Keep the topbar HUD (streak, level) in sync with the server.
    const nextHuds = doc.querySelectorAll('[data-hud]');
    document.querySelectorAll('[data-hud]').forEach((hud, i) => {
        if (nextHuds[i]) hud.replaceWith(document.adoptNode(nextHuds[i]));
    });

    // Toasts for non-answer messages.
    document.querySelector('[data-toasts]')?.remove();
    const toasts = doc.querySelector('[data-toasts]');
    if (toasts) {
        document.querySelector('main')?.before(document.adoptNode(toasts));
        initToasts();
    }

    const oldRoot = document.querySelector('[data-quiz-question]');
    const oldForm = oldRoot?.querySelector('[data-answer-form]');
    const newRoot = nextMain.querySelector('[data-quiz-question]');
    const newForm = newRoot?.querySelector('[data-answer-form]');

    if (oldRoot && oldForm && newRoot && newForm) {
        // Next question: replace everything except the form, then patch the form in place.
        Array.from(oldRoot.children).forEach((child) => { if (child !== oldForm) child.remove(); });
        let afterForm = false;
        Array.from(newRoot.children).forEach((child) => {
            if (child === newForm) { afterForm = true; return; }
            const node = document.adoptNode(child);
            if (afterForm) oldRoot.append(node);
            else oldForm.before(node);
        });
        newForm.querySelectorAll('input[type="hidden"]').forEach((hidden) => {
            const own = oldForm.querySelector(`input[type="hidden"][name="${CSS.escape(hidden.name)}"]`);
            if (own) own.value = hidden.value;
            else oldForm.prepend(document.adoptNode(hidden));
        });
        const oldInput = oldForm.querySelector('[data-answer-input]');
        const newInput = newForm.querySelector('[data-answer-input]');
        if (oldInput && newInput) oldInput.placeholder = newInput.placeholder;
        oldForm.action = newForm.action;
        resetForm(oldForm);
        initQuestion(oldRoot);
        oldInput?.focus({ preventScroll: true });
        return;
    }

    // Anything else (e.g. the results page): swap the whole main element.
    const main = document.querySelector('main');
    const adopted = document.adoptNode(nextMain);
    main.replaceWith(adopted);
    window.scrollTo({ top: 0 });
    initReveal(adopted);
    mount(adopted);
}

/* ------------------------------------------------------------------ */
/* Result + rewards                                                    */
/* ------------------------------------------------------------------ */

/** Runs a timed sequence that can be skipped: waits resolve at once and steps bail out. */
class Sequence {
    constructor() {
        this.skipped = reducedMotion();
        this.waiters = new Set();
        this.animations = new Set();
    }

    wait(ms) {
        if (this.skipped) return Promise.resolve();
        return new Promise((resolve) => {
            const done = () => { clearTimeout(timer); this.waiters.delete(done); resolve(); };
            const timer = setTimeout(done, ms);
            this.waiters.add(done);
        });
    }

    /** Track a Motion animation so skip() can finish it. Resolves when it ends. */
    track(animation) {
        if (!animation) return Promise.resolve();
        if (this.skipped) { animation.complete?.(); return Promise.resolve(); }
        this.animations.add(animation);
        return new Promise((resolve) => {
            const done = () => { this.animations.delete(animation); resolve(); };
            Promise.resolve(animation.finished ?? animation).then(done, done);
        });
    }

    skip() {
        if (this.skipped) return;
        this.skipped = true;
        this.animations.forEach((a) => { try { a.complete?.(); } catch { /* ignore */ } });
        this.animations.clear();
        this.waiters.forEach((done) => done());
    }
}

function initResult(root) {
    const seq = new Sequence();
    const percent = Number(root.dataset.percent) || 0;
    const band = root.dataset.band;
    const ring = root.querySelector('[data-ring]');
    const number = root.querySelector('[data-count-to]');
    const message = Array.from(root.children).slice(1);
    const panel = document.querySelector('[data-rewards]');
    const rewards = panel ? prepareRewards(panel) : null;

    const finishResult = () => {
        if (ring) ring.style.setProperty('--value', percent);
        if (number) number.textContent = `${percent}${number.dataset.countSuffix || ''}`;
        message.forEach((el) => { el.style.opacity = ''; el.style.transform = ''; });
    };

    const finishAll = () => {
        seq.skip();
        finishResult();
        rewards?.finish();
    };

    if (seq.skipped) {
        finishAll();
        return;
    }

    // Any click, tap or key finishes the sequence instantly.
    const onSkip = (event) => {
        if (event.type === 'keydown' && ['Tab', 'Shift', 'Alt', 'Control', 'Meta'].includes(event.key)) return;
        finishAll();
        cleanup();
    };
    const cleanup = () => {
        document.removeEventListener('pointerdown', onSkip, true);
        document.removeEventListener('keydown', onSkip, true);
    };
    document.addEventListener('pointerdown', onSkip, true);
    document.addEventListener('keydown', onSkip, true);

    (async () => {
        if (ring) {
            ring.style.transition = 'none';
            ring.style.setProperty('--value', 0);
            seq.track(animate(ring, { scale: [0.85, 1], opacity: [0, 1] }, ease.bouncy));
            seq.track(animate(0, percent, {
                duration: 1.4,
                ease: ease.out,
                onUpdate: (v) => ring.style.setProperty('--value', v),
            }));
        }
        message.forEach((el) => { el.style.opacity = '0'; });
        rewards?.rewind();
        if (number) seq.track(countUp(number, percent, { duration: 1.4, suffix: number.dataset.countSuffix || '' }));
        seq.track(enter(message, { delay: 0.5 }));

        await seq.wait(900);
        if (!seq.skipped) {
            if (band === 'perfect') { celebrate({ big: true }); play('levelup'); }
            else if (percent >= 80) { celebrate(); play('combo'); }
        }

        if (rewards) await rewards.play(seq);
        finishAll();
        cleanup();
    })();
}

/** Rewind the rewards panel to its start state and return play/finish controls. */
function prepareRewards(panel) {
    const d = panel.dataset;
    const xp = Number(d.xp) || 0;
    const level = Number(d.level) || 1;
    const levelBefore = Number(d.levelBefore) || level;
    const leveledUp = d.leveledUp === 'true';
    const levelPct = Number(d.levelPct) || 0;
    const dailyPct = Number(d.dailyPct) || 0;

    // Where the level bar stood before this quiz. Within a level that is simply the
    // XP gained taken back off; across a level-up the bar is drawn from 0.
    const into = Number(d.xpInto) || 0;
    const span = Number(d.xpFor) || 1;
    const beforePct = leveledUp ? 0 : Math.max(0, Math.min(100, ((into - xp) / span) * 100));

    const q = (sel) => panel.querySelector(sel);
    const xpCount = q('[data-xp-count]');
    const steps = Array.from(panel.querySelectorAll('[data-reward-step]'));
    const levelBar = q('[data-level-bar]');
    const levelNum = q('[data-level-num]');
    const levelLabel = q('[data-level-label]');
    const levelTitle = q('[data-level-title]');
    const levelup = q('[data-levelup]');
    const dailyBar = q('[data-daily-bar]');
    const streakPop = q('[data-streak-pop]');
    const achievements = Array.from(panel.querySelectorAll('[data-achievement]'));
    const skipButton = q('[data-rewards-skip]');
    const medal = levelNum?.parentElement;

    const setWidth = (bar, pct) => { if (bar) bar.style.width = `${pct}%`; };
    const hide = (el) => { if (el) { el.style.opacity = '0'; } };
    const show = (el) => { if (el) { el.style.opacity = ''; el.style.transform = ''; } };

    // Start state (only applied when the sequence will actually play).
    const rewind = () => {
        [levelBar, dailyBar].forEach((bar) => { if (bar) bar.style.transition = 'none'; });
        if (xpCount) xpCount.textContent = '0';
        steps.forEach(hide);
        achievements.forEach(hide);
        hide(streakPop);
        setWidth(levelBar, beforePct);
        setWidth(dailyBar, 0);
        if (leveledUp) {
            if (levelNum) levelNum.textContent = levelBefore;
            if (levelLabel) levelLabel.textContent = levelBefore;
            hide(levelTitle);
            if (levelup) levelup.hidden = true;
        }
        if (skipButton) skipButton.hidden = false;
        hide(panel);
    };

    const finish = () => {
        show(panel);
        if (xpCount) xpCount.textContent = String(xp);
        steps.forEach(show);
        achievements.forEach(show);
        show(streakPop);
        show(levelTitle);
        setWidth(levelBar, levelPct);
        setWidth(dailyBar, dailyPct);
        if (levelNum) levelNum.textContent = level;
        if (levelLabel) levelLabel.textContent = level;
        if (levelup) { levelup.hidden = false; show(levelup); }
        if (medal) medal.style.transform = '';
        if (skipButton) skipButton.hidden = true;
    };

    const fill = (seq, bar, from, to, duration = 0.9) => {
        if (!bar) return Promise.resolve();
        return seq.track(animate(bar, { width: [`${from}%`, `${to}%`] }, { duration, ease: ease.out }));
    };

    async function play(seq) {
        if (seq.skipped) return;
        skipButton?.addEventListener('click', () => seq.skip(), { once: true });
        seq.track(enter([panel], { y: 20 }));
        await seq.wait(250);

        // XP + level bar.
        const [levelStep, tilesStep, achievementsStep, ...rest] = steps;
        seq.track(enter([levelStep]));
        seq.track(countUp(xpCount, xp, { duration: 1 }));
        await fill(seq, levelBar, beforePct, leveledUp ? 100 : levelPct, leveledUp ? 1 : 0.9);
        if (seq.skipped) return;

        if (leveledUp) {
            await seq.wait(150);
            if (seq.skipped) return;
            if (levelNum) levelNum.textContent = level;
            if (levelLabel) levelLabel.textContent = level;
            if (medal) seq.track(animate(medal, { scale: [1, 1.35, 1], rotate: [0, -10, 0] }, { duration: 0.6 }));
            if (levelTitle) seq.track(animate(levelTitle, { opacity: [0, 1] }, { duration: 0.4 }));
            if (levelup) {
                levelup.hidden = false;
                seq.track(pop(levelup));
            }
            celebrate({ big: true });
            playSound('levelup');
            await seq.wait(700);
            if (seq.skipped) return;
            await fill(seq, levelBar, 0, levelPct, 0.8);
            if (seq.skipped) return;
        }

        // Streak + daily goal.
        await seq.wait(200);
        if (tilesStep && !seq.skipped) {
            seq.track(enter([tilesStep]));
            await seq.wait(200);
            if (streakPop && !seq.skipped) seq.track(animate(streakPop, { opacity: [0, 1], scale: [0.3, 1.25, 1], rotate: [-12, 6, 0] }, { duration: 0.55 }));
            await fill(seq, dailyBar, 0, dailyPct, 0.8);
        }
        if (seq.skipped) return;

        // New achievements, one by one.
        let after = rest;
        if (achievements.length && achievementsStep) {
            achievementsStep.style.opacity = '';
            for (const card of achievements) {
                await seq.wait(350);
                if (seq.skipped) return;
                seq.track(animate(card, { opacity: [0, 1], scale: [0.7, 1.04, 1], y: [12, 0] }, { duration: 0.55, ease: ease.out }));
                const icon = card.querySelector('.achievement-medal');
                if (icon) seq.track(animate(icon, { rotate: [-25, 10, 0], scale: [0.6, 1.15, 1] }, { duration: 0.7, delay: 0.1 }));
                playSound('combo');
            }
        } else if (achievementsStep) {
            after = [achievementsStep, ...rest];
        }

        await seq.wait(250);
        if (!seq.skipped) seq.track(enter(after));
        await seq.wait(400);
    }

    return { rewind, play, finish };
}

// Alias so the rewards closure's local `play` does not shadow the sound import.
const playSound = play;

/* ------------------------------------------------------------------ */
/* Mixed quiz: list selection                                          */
/* ------------------------------------------------------------------ */

function initMixedSelection(form) {
    const boxes = Array.from(form.querySelectorAll('[data-list-checkbox]'));
    const listsEl = form.querySelector('[data-selected-lists]');
    const listsLabel = form.querySelector('[data-selected-lists-label]');
    const itemsEl = form.querySelector('[data-selected-items]');
    const submit = form.querySelector('[data-mixed-submit]');
    const groups = Array.from(form.querySelectorAll('[data-list-group]'));

    let lastLists = null;
    const update = () => {
        const checked = boxes.filter((b) => b.checked);
        const items = checked.reduce((sum, b) => sum + (Number(b.dataset.count) || 0), 0);

        if (listsEl) listsEl.textContent = checked.length;
        if (listsLabel) listsLabel.textContent = checked.length === 1 ? 'lijst' : 'lijsten';
        if (itemsEl) itemsEl.textContent = items.toLocaleString('nl-NL');
        if (submit) {
            submit.disabled = checked.length === 0;
            submit.toggleAttribute('aria-disabled', checked.length === 0);
        }
        if (lastLists !== null && lastLists !== checked.length && listsEl && !reducedMotion()) {
            animate(listsEl, { scale: [1.35, 1] }, ease.bouncy);
        }
        lastLists = checked.length;

        groups.forEach((group) => {
            const btn = group.querySelector('[data-select-all]');
            if (!btn) return;
            const own = group.querySelectorAll('[data-list-checkbox]');
            const all = Array.from(own).every((b) => b.checked);
            btn.textContent = all ? 'Alles deselecteren' : 'Alles selecteren';
            btn.setAttribute('aria-pressed', String(all));
        });
    };

    groups.forEach((group) => {
        const btn = group.querySelector('[data-select-all]');
        btn?.addEventListener('click', () => {
            const own = Array.from(group.querySelectorAll('[data-list-checkbox]'));
            const all = own.every((b) => b.checked);
            own.forEach((b) => { b.checked = !all; });
            update();
        });
    });

    form.addEventListener('change', (event) => {
        if (event.target.matches('[data-list-checkbox]')) update();
    });

    form.addEventListener('submit', (event) => {
        if (!boxes.some((b) => b.checked)) {
            event.preventDefault();
            shake(form.querySelector('[data-mixed-bar]'));
        }
    });

    update();
}

/* ------------------------------------------------------------------ */
/* Smart practice                                                      */
/* ------------------------------------------------------------------ */

function initSmartPractice() {
    // Success-rate bars grow in once their card is revealed.
    const bars = Array.from(document.querySelectorAll('[data-rate-bar]'));
    if (reducedMotion()) return;
    bars.forEach((bar, i) => {
        const target = bar.style.width;
        bar.style.transition = 'none';
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.transition = '';
            bar.style.width = target;
        }, 300 + i * 50);
    });
}
