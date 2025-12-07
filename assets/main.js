// Import FontAwesome
import '@fortawesome/fontawesome-free/js/all.js';

// Import our custom styles
import './style.css';

const entryInputs = [
    document.getElementById("source_word"),
    document.getElementById("target_word"),
].filter(Boolean);

entryInputs.forEach(entry => {
    // skip dot at the end.
    entry.addEventListener("input", (event) => {
        const value = event.target.value;
        if (value.endsWith('.')) {
            event.target.value = value.slice(0, -1);
        }
    });
});