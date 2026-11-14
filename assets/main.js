import { initIcons } from './js/core/icons.js';
import './style.css';

import { initTheme } from './js/core/theme.js';
import { initToasts } from './js/core/toasts.js';
import { initConfirm } from './js/core/confirm.js';
import { initSearch } from './js/core/search.js';
import { initReveal } from './js/core/motion.js';

import { initLists } from './js/pages/lists.js';
import { initQuiz } from './js/pages/quiz.js';
import { initHistory } from './js/pages/history.js';
import { initGame } from './js/pages/game.js';

const ready = (fn) =>
    document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', fn) : fn();

ready(() => {
    initIcons();
    initTheme();
    initToasts();
    initConfirm();
    initSearch();
    initReveal();

    // Page modules guard themselves on document.body.dataset.page.
    const page = document.body.dataset.page;
    initLists(page);
    initQuiz(page);
    initHistory(page);
    initGame(page);
});
