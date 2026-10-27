"""Genera el audio de la historia animada: música de fondo tranqui + un efecto en cada movimiento.

Uso:  python scripts/audio-historia.py [salida.wav] [segundos=12]
Todo es sintetizado acá (sin samples de terceros), así que no hay temas de derechos.
Los tiempos de CUES siguen los @keyframes de templates/historia-animada.html (loop de 12 s).
"""
import sys, wave
import numpy as np

SR = 44100
out = sys.argv[1] if len(sys.argv) > 1 else "assets/audio/historia-animada.wav"
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 12.0
N = int(SR * DUR)
rng = np.random.default_rng(7)

def env(n, a, r):
    """Envolvente con ataque y caída exponencial (en segundos)."""
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r)

def lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")

def note(f):
    return 440 * 2 ** ((f - 69) / 12)

# --- Fondo: pad suave (Cmaj7 · Am7 · Fmaj7 · G6, 3 s cada uno) + arpegio de campanitas muy bajo ---
chords = [[48, 55, 64, 71], [45, 52, 60, 67], [41, 48, 57, 64], [43, 50, 59, 64]]
bed = np.zeros(N)
seg = int(SR * 3)
t = np.arange(seg) / SR
for i, ch in enumerate(chords):
    s = np.zeros(seg)
    for m in ch:
        f = note(m)
        s += np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t + 0.3)
    fade = np.minimum(1, t / 0.6) * np.minimum(1, (3 - t) / 0.6)
    bed[i * seg:(i + 1) * seg] += s * fade * 0.05
bed = lowpass(bed, 9)
arp = [72, 76, 79, 83, 69, 72, 76, 79, 65, 69, 72, 76, 67, 71, 74, 76]
for k in range(int(DUR / 0.75)):
    m = arp[(k // 4 * 4 + k % 4) % len(arp)]
    st = int(k * 0.75 * SR)
    n = min(int(SR * 1.2), N - st)
    tt = np.arange(n) / SR
    bed[st:st + n] += np.sin(2 * np.pi * note(m) * tt) * env(n, 0.005, 0.35) * 0.035

# --- Efectos ---
def whoosh(dur=0.45, gain=0.35):
    n = int(SR * dur)
    x = rng.standard_normal(n)
    x = lowpass(x, 6) - lowpass(x, 60)          # banda media
    shape = np.sin(np.pi * np.arange(n) / n) ** 2
    return x * shape * gain

def pop(f0=700, f1=180, dur=0.12, gain=0.55):
    n = int(SR * dur)
    tt = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (tt / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(n, 0.002, 0.04) * gain

def tap(gain=0.5):
    n = int(SR * 0.18)
    tt = np.arange(n) / SR
    body = np.sin(2 * np.pi * 140 * tt) * env(n, 0.001, 0.05)
    paper = lowpass(rng.standard_normal(n), 3) * env(n, 0.001, 0.015) * 0.5
    return (body + paper) * gain

def chime(gain=0.3):
    n = int(SR * 1.2)
    tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1318.5 * tt) + 0.6 * np.sin(2 * np.pi * 1975.5 * tt)) * env(n, 0.002, 0.35) * gain

# (segundo, efecto) — 1 % del loop = 0,12 s
CUES = [
    (0.20, whoosh(0.4, 0.25)),   # entra "A 15 DÍAS DEL"
    (0.95, pop(900, 160, 0.14, 0.6)),  # explota el 20/11
    (1.20, whoosh(0.4, 0.25)),   # "vence el Monotributo"
    (2.85, whoosh(0.5, 0.35)),   # cambio de escena
    (3.25, whoosh(0.35, 0.2)),   # "un chequeo en 3 pasos"
    (4.10, tap()),               # cae la tarjeta 1
    (5.30, tap()),               # tarjeta 2
    (6.50, tap()),               # tarjeta 3
    (8.85, whoosh(0.5, 0.35)),   # cambio de escena
    (9.60, pop(700, 200, 0.12, 0.55)),  # "¿Dudas?"
    (10.10, whoosh(0.35, 0.2)),  # sube el WhatsApp
    (10.50, chime()),            # logo
]
fx = np.zeros(N)
for sec, s in CUES:
    st = int(sec * SR)
    n = min(len(s), N - st)
    fx[st:st + n] += s[:n]

mix = bed + fx
fade = int(SR * 0.4)
mix[:int(SR * 0.05)] *= np.linspace(0, 1, int(SR * 0.05))
mix[-fade:] *= np.linspace(1, 0, fade)
mix = mix / np.max(np.abs(mix)) * 0.89          # pico en -1 dB
pcm = (np.stack([mix, mix], axis=1) * 32767).astype(np.int16)
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("OK", out)
