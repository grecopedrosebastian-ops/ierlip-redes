"""Música del reel explicado (templates/reel-explicado.html): base suave a 92 BPM para ir debajo de la voz en off.

Uso:  python scripts/audio-explicado.py [salida.wav] [duración=43 | tiempos.json]
Con el tiempos.json de scripts/voz-reel.py, los golpes y pops se corren a donde quedó cada escena.
Cada cambio de escena (CORTES) lleva un golpe suave y un "whoosh" que sube hasta el corte; los números que aparecen
(POPS) llevan un pop. Va bajita a propósito: la voz manda. Todo sintetizado acá, sin samples de terceros.
"""
import json, sys, wave
import numpy as np

SR = 44100
out = sys.argv[1] if len(sys.argv) > 1 else "assets/audio/reel-explicado.wav"
arg = sys.argv[2] if len(sys.argv) > 2 else "43"
BEAT = 60 / 92
CORTES = [3.4, 6.6, 8.2, 9.0, 16.0, 23.0, 27.0, 33.5, 38.5]
POPS = [1.15, 13.6, 20.6, 23.15, 39.9]
if arg.endswith(".json"):
    T = json.load(open(arg))
    def mover(t):   # misma cuenta que hace el template: cada escena se estira en proporción
        for (o0, od), (n0, nd) in zip(T["original"], T["TIEMPOS"]):
            if o0 <= t < o0 + od:
                return n0 + (t - o0) * nd / od
        return t
    CORTES = [n0 for n0, _ in T["TIEMPOS"][1:]]
    POPS = [mover(p) for p in POPS]
    DUR = T["total"]
else:
    DUR = float(arg)
N = int(SR * DUR)
rng = np.random.default_rng(7)

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

def kick():
    n = int(SR * 0.3); t = np.arange(n) / SR
    f = 48 + 70 * np.exp(-t / 0.04)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.12)

def hat():
    n = int(SR * 0.06); x = rng.standard_normal(n)
    return (x - lowpass(x, 4)) * env(n, 0.0005, 0.02) * 0.4

def snap():
    n = int(SR * 0.12); x = rng.standard_normal(n)
    return (lowpass(x, 3) - lowpass(x, 30)) * env(n, 0.001, 0.035)

def whoosh(dur=0.45):
    n = int(SR * dur); x = rng.standard_normal(n)
    return (lowpass(x, 6) - lowpass(x, 60)) * (np.arange(n) / n) ** 2.4 * 0.5

def pop():
    n = int(SR * 0.14); t = np.arange(n) / SR
    f = 880 * (180 / 880) ** (t / 0.14)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.045)

def pad(ms, dur):
    n = int(SR * dur); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * note(m) * t) + 0.25 * np.sin(2 * np.pi * note(m) * 2.003 * t) for m in ms)
    e = np.minimum(1, t / 0.25) * np.minimum(1, (dur - t) / 0.4)
    return s * e

# Fa mayor 7 · La menor 7 · Re menor 9 · Si bemol mayor 7 (cálido, sin tensión)
ACORDES = [(41, [60, 64, 65, 69]), (45, [60, 64, 67, 69]), (38, [57, 60, 64, 65]), (46, [57, 58, 62, 65])]
music = np.zeros(N); drums = np.zeros(N); fx = np.zeros(N)
compas = 4 * BEAT
k = 0
while k * compas < DUR:
    t0 = k * compas
    raiz, acorde = ACORDES[k % 4]
    put(music, t0, pad(acorde, compas + 0.3), 0.045)
    nb = int(SR * compas); tb = np.arange(nb) / SR
    put(music, t0, np.sin(2 * np.pi * note(raiz) * tb) * env(nb, 0.01, 1.2), 0.22)
    for b in range(4):
        tb0 = t0 + b * BEAT
        if b in (0, 2): put(drums, tb0, kick(), 0.55)
        if b in (1, 3): put(drums, tb0, snap(), 0.22)
        put(drums, tb0 + BEAT / 2, hat(), 0.7)
        # arpegio suave en corcheas
        for h in range(2):
            m = acorde[(b * 2 + h) % 4] + 12
            n = int(SR * 0.35); tt = np.arange(n) / SR
            put(music, tb0 + h * BEAT / 2, np.sin(2 * np.pi * note(m) * tt) * env(n, 0.004, 0.12), 0.035)
    k += 1

for c in CORTES:
    put(fx, c - 0.45, whoosh(), 0.35)
    put(fx, c, kick(), 0.35)
for p in POPS:
    put(fx, p, pop(), 0.35)

mix = drums + music + fx
mix[:int(SR * 0.3)] *= np.linspace(0, 1, int(SR * 0.3))
fade = int(SR * 2.0)
mix[-fade:] *= np.linspace(1, 0, fade)
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.3) / np.tanh(1.3) * 0.7   # pico en -3 dB: queda lugar para la voz
pcm = (np.stack([mix, mix], axis=1) * 32767).astype(np.int16)
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("OK", out)
