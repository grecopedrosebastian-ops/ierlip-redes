"""Genera la música del reel con cortes (templates/reel-cortes.html): base rítmica a 100 BPM, un compás por escena.

Uso:  python scripts/audio-reel.py [salida.wav] [variante=1]
Cada corte de escena cae en el primer tiempo de un compás (2,4 s) y lleva un golpe con platillo; antes de cada corte
sube un "whoosh" corto, y los números que aparecen llevan un pop. La variante cambia la progresión de acordes y la melodía.
Todo es sintetizado acá (sin samples de terceros), así que no hay temas de derechos.
"""
import sys, wave
import numpy as np

SR = 44100
out = sys.argv[1] if len(sys.argv) > 1 else "assets/audio/reel-1.wav"
VAR = int(sys.argv[2]) if len(sys.argv) > 2 else 1
BPM = 100
BEAT = 60 / BPM            # 0,6 s
BAR = 4 * BEAT             # 2,4 s = una escena
ESCENAS = 8
DUR = ESCENAS * BAR        # 19,2 s
N = int(SR * DUR)
rng = np.random.default_rng(11 + VAR)

def env(n, a, r):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r)

def lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")

def note(m):
    return 440 * 2 ** ((m - 69) / 12)

def put(buf, sec, s, gain=1.0):
    st = int(sec * SR)
    if st >= len(buf):
        return
    n = min(len(s), len(buf) - st)
    buf[st:st + n] += s[:n] * gain

# --- Sonidos ---
def kick():
    n = int(SR * 0.32); t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t / 0.035)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.11)

def clap():
    n = int(SR * 0.18)
    x = rng.standard_normal(n)
    x = lowpass(x, 3) - lowpass(x, 25)
    e = env(n, 0.001, 0.05) + 0.6 * np.concatenate([np.zeros(int(SR * .012)), env(n - int(SR * .012), 0.001, 0.03)])
    return x * e * 0.9

def hat(largo=0.035):
    n = int(SR * 0.08)
    x = rng.standard_normal(n)
    return (x - lowpass(x, 4)) * env(n, 0.0005, largo) * 0.5

def crash():
    n = int(SR * 1.4)
    x = rng.standard_normal(n)
    return (x - lowpass(x, 3)) * env(n, 0.001, 0.45) * 0.35

def whoosh(dur=0.5):
    n = int(SR * dur)
    x = rng.standard_normal(n)
    x = lowpass(x, 5) - lowpass(x, 50)
    return x * (np.arange(n) / n) ** 2.2 * 0.5      # sube hasta el corte

def pop(f0=900, f1=170):
    n = int(SR * 0.14); t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / 0.14)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.045)

def chime():
    n = int(SR * 1.6); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1046.5 * t) + 0.6 * np.sin(2 * np.pi * 1568 * t) + 0.3 * np.sin(2 * np.pi * 2093 * t)) * env(n, 0.002, 0.5) * 0.35

# --- Armonía: un acorde por escena (raíz MIDI del bajo + notas del acorde) ---
PROG = {
    1: [(45, [57, 60, 64]), (41, [57, 60, 65]), (48, [55, 60, 64]), (43, [55, 59, 62])],   # Am F C G
    2: [(48, [55, 60, 64]), (43, [55, 59, 62]), (45, [57, 60, 64]), (41, [57, 60, 65])],   # C G Am F
    3: [(50, [57, 62, 65]), (46, [58, 62, 65]), (41, [57, 60, 65]), (48, [55, 60, 64])],   # Dm Bb F C
}[VAR if VAR in (1, 2, 3) else 1]

drums = np.zeros(N); bass = np.zeros(N); keys = np.zeros(N); fx = np.zeros(N)
side = np.ones(N)   # "bombeo": baja bajo y teclado cuando pega el bombo
for e in range(ESCENAS):
    t0 = e * BAR
    raiz, acorde = PROG[e % 4]
    final = e == ESCENAS - 1
    # Batería: bombo en 1 y 3 (+ el "y" del 3 desde la escena 3), aplausos en 2 y 4, hi-hat en corcheas (semicorcheas desde la 5).
    if not final:
        for b in (0, 2):
            put(drums, t0 + b * BEAT, kick())
            st = int((t0 + b * BEAT) * SR); n = min(int(SR * .25), N - st)
            side[st:st + n] *= 1 - 0.55 * np.exp(-np.arange(n) / SR / 0.06)
        if e >= 2:
            put(drums, t0 + 2.5 * BEAT, kick(), 0.7)
        for b in (1, 3):
            put(drums, t0 + b * BEAT, clap(), 0.55)
        paso = BEAT / 4 if e >= 4 else BEAT / 2
        k = 0
        while k * paso < BAR - 1e-6:
            put(drums, t0 + k * paso, hat(0.05 if k % 2 else 0.03), 0.35 if k % 2 else 0.5)
            k += 1
    # Golpe en cada corte (y en el arranque).
    put(drums, t0, crash(), 1.0 if e else 0.7)
    put(fx, t0, kick(), 0.6)
    # Whoosh que sube hasta el próximo corte.
    if e < ESCENAS - 1:
        put(fx, t0 + BAR - 0.5, whoosh(0.5), 0.55)
    # Bajo en corcheas con la raíz (octava arriba en los "y").
    if not final:
        for k in range(8):
            m = raiz + (12 if k % 2 else 0)
            n = int(SR * BEAT / 2 * 0.9); t = np.arange(n) / SR
            f = note(m)
            s = sum(np.sin(2 * np.pi * f * h * t) / h for h in (1, 2, 3, 4)) * env(n, 0.004, 0.16)
            put(bass, t0 + k * BEAT / 2, s, 0.32)
    # Teclado: acorde en golpes sincopados + arpegio corto.
    golpes = [0, 1.5, 2.5] if not final else [0]
    for g in golpes:
        n = int(SR * (BEAT * 0.9 if not final else 2.2)); t = np.arange(n) / SR
        s = sum(np.sin(2 * np.pi * note(m) * t) + 0.3 * np.sin(2 * np.pi * 2 * note(m) * t) for m in acorde)
        put(keys, t0 + g * BEAT, s * env(n, 0.005, 0.22 if not final else 0.8), 0.07)
    if not final:
        arp = acorde + [acorde[0] + 12]
        for k in range(8):
            if VAR == 2 and k % 4 == 3:
                continue
            m = arp[(k * (2 if VAR == 3 else 1)) % len(arp)] + 12
            n = int(SR * 0.3); t = np.arange(n) / SR
            put(keys, t0 + k * BEAT / 2, np.sin(2 * np.pi * note(m) * t) * env(n, 0.003, 0.09), 0.05)

# Pops cuando aparecen los números (intro y los 3 pasos) y campanita en el logo.
for e, d in ((2, 0.2), (3, 0.05), (4, 0.05), (5, 0.05)):
    put(fx, e * BAR + d + 0.12, pop(), 0.45)
put(fx, 6 * BAR + 0.3, chime(), 1.0)

drums = drums * 0.9
mix = drums + (bass + keys) * side + fx * 0.8
mix[:int(SR * 0.01)] *= np.linspace(0, 1, int(SR * 0.01))
fade = int(SR * 1.2)
mix[-fade:] *= np.linspace(1, 0, fade)
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.6) / np.tanh(1.6) * 0.89   # un poco de saturación, pico en -1 dB
pcm = (np.stack([mix, mix], axis=1) * 32767).astype(np.int16)
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("OK", out)
