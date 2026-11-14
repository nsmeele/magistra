// Replace window.confirm with a styled <dialog>.
// Usage: <form data-confirm="Deze lijst verwijderen?"> or <button data-confirm="...">
export function initConfirm() {
    const dialog = document.querySelector('[data-confirm-dialog]');
    if (!dialog) return;
    const message = dialog.querySelector('[data-confirm-message]');

    const ask = (text) => new Promise((resolve) => {
        message.textContent = text;
        dialog.returnValue = '';
        dialog.showModal();
        dialog.querySelector('[data-confirm-ok]')?.focus();
        dialog.addEventListener('close', () => resolve(dialog.returnValue === 'confirm'), { once: true });
    });

    document.addEventListener('submit', async (event) => {
        const form = event.target;
        const submitter = event.submitter;
        const text = submitter?.dataset.confirm || form.dataset.confirm;
        if (!text || form.dataset.confirmed) return;
        event.preventDefault();
        if (await ask(text)) {
            form.dataset.confirmed = '1';
            form.requestSubmit(submitter);
        }
    });

    // Close when clicking the backdrop.
    dialog.addEventListener('click', (e) => { if (e.target === dialog) dialog.close('cancel'); });
}
