// Flash messages as toasts that slide in and auto-dismiss.
import { animate, ease, reducedMotion } from './motion.js';

function dismiss(toast) {
    if (toast.dataset.leaving) return;
    toast.dataset.leaving = '1';
    const done = () => toast.remove();
    if (reducedMotion()) return done();
    animate(toast, { opacity: 0, y: -10, scale: 0.96 }, { duration: 0.25 }).then(done);
}

export function initToasts() {
    document.querySelectorAll('[data-toast]').forEach((toast, i) => {
        if (!reducedMotion()) {
            animate(toast, { opacity: [0, 1], y: [-16, 0], scale: [0.96, 1] }, { ...ease.spring, delay: i * 0.08 });
        }
        toast.querySelector('[data-toast-close]')?.addEventListener('click', () => dismiss(toast));
        let timer = setTimeout(() => dismiss(toast), 4500 + i * 600);
        toast.addEventListener('pointerenter', () => clearTimeout(timer));
        toast.addEventListener('pointerleave', () => { timer = setTimeout(() => dismiss(toast), 2000); });
    });
}
