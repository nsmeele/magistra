// Tiny synthesized sound effects (Web Audio API, no files). Off by default.
const KEY = 'magistra-sound';
let ctx = null;

export function isSoundOn() {
    try { return localStorage.getItem(KEY) === 'on'; } catch { return false; }
}

export function setSound(on) {
    try { localStorage.setItem(KEY, on ? 'on' : 'off'); } catch { /* storage blocked */ }
    if (on) unlock();
}

function context() {
    if (!ctx) {
        const AC = window.AudioContext || window.webkitAudioContext;
        if (!AC) return null;
        ctx = new AC();
    }
    return ctx;
}

/** Create/resume the audio context. Call from a user gesture (click, submit, keydown). */
export function unlock() {
    if (!isSoundOn()) return;
    const c = context();
    if (c && c.state === 'suspended') c.resume().catch(() => {});
}

function tone(c, out, { freq, start = 0, dur = 0.15, type = 'sine', gain = 0.5, slideTo = null }) {
    const t = c.currentTime + start;
    const osc = c.createOscillator();
    const g = c.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, t);
    if (slideTo) osc.frequency.exponentialRampToValueAtTime(slideTo, t + dur);
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(gain, t + 0.012);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    osc.connect(g).connect(out);
    osc.start(t);
    osc.stop(t + dur + 0.05);
}

const SOUNDS = {
    correct(c, out) {
        tone(c, out, { freq: 880, dur: 0.12, type: 'triangle' });
        tone(c, out, { freq: 1318.5, start: 0.08, dur: 0.28, type: 'triangle' });
    },
    wrong(c, out) {
        const lp = c.createBiquadFilter();
        lp.type = 'lowpass';
        lp.frequency.value = 900;
        lp.connect(out);
        tone(c, lp, { freq: 180, dur: 0.28, type: 'sawtooth', gain: 0.35, slideTo: 110 });
        tone(c, lp, { freq: 185, dur: 0.28, type: 'square', gain: 0.15, slideTo: 112 });
    },
    combo(c, out) {
        [1046.5, 1318.5, 1568, 2093].forEach((freq, i) =>
            tone(c, out, { freq, start: i * 0.06, dur: 0.18, type: 'triangle', gain: 0.4 }));
    },
    levelup(c, out) {
        const notes = [[784, 0, 0.14], [1046.5, 0.14, 0.14], [1318.5, 0.28, 0.14], [1568, 0.42, 0.6]];
        notes.forEach(([freq, start, dur]) => {
            tone(c, out, { freq, start, dur, type: 'triangle', gain: 0.45 });
            tone(c, out, { freq: freq / 2, start, dur, type: 'sine', gain: 0.25 });
        });
        tone(c, out, { freq: 1975.5, start: 0.42, dur: 0.6, type: 'sine', gain: 0.15 });
    },
};

/** Play a named effect: correct, wrong, combo, levelup. No-op when sound is off. */
export function play(name) {
    if (!isSoundOn() || !SOUNDS[name]) return;
    const c = context();
    if (!c) return;
    if (c.state === 'suspended') c.resume().catch(() => {});
    const master = c.createGain();
    master.gain.value = 0.18;
    master.connect(c.destination);
    SOUNDS[name](c, master);
}
