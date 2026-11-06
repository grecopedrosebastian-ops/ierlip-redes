"""Voz en off para los reels explicados (templates/reel-explicado.html), con voz neural gratis y sin clave (edge-tts).

Uso:  python scripts/voz-reel.py guion.json carpeta_salida [voz=es-AR-TomasNeural | eleven | eleven:<voice_id>] [velocidad=+6%]
Con "eleven" usa ElevenLabs (ELEVENLABS_API_KEY y ELEVENLABS_VOICE_ID en .env, que no se versiona).
guion.json: [[inicio_seg, duración_seg, "texto"], ...], una entrada por escena del template (texto "" = sin voz).
Cada escena dura lo que pide el template o lo que tarda la voz en decir su frase (+0,6 s), lo que sea mayor:
la voz va a ritmo natural y es el video el que se acomoda. Deja en la carpeta:
  voz.wav       la voz sola, ya ubicada en cada escena
  tiempos.json  {"TIEMPOS": [[inicio, duración], ...], "total": seg, "original": [[inicio, duración], ...]}
Después: scripts/audio-explicado.py arma la música con esos tiempos y scripts/mezcla-voz.sh junta todo.
Requiere: pip install edge-tts, y ffmpeg en el PATH.
"""
import asyncio, json, os, subprocess, sys, wave
import numpy as np
import edge_tts

SR = 44100
guion_f, carpeta = sys.argv[1:3]
VOZ = sys.argv[3] if len(sys.argv) > 3 else "es-AR-TomasNeural"
VEL = sys.argv[4] if len(sys.argv) > 4 else "+6%"
guion = json.load(open(guion_f, encoding="utf-8"))
os.makedirs(carpeta, exist_ok=True)

def leer(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768

def eleven(texto, path):
    """ElevenLabs: voz = "eleven" (usa ELEVENLABS_VOICE_ID) o "eleven:<voice_id>". La clave va en .env, nunca en el código."""
    import urllib.request
    clave = os.environ.get("ELEVENLABS_API_KEY")
    if not clave and os.path.exists(".env"):
        for linea in open(".env", encoding="utf-8"):
            k, _, v = linea.strip().partition("=")
            os.environ.setdefault(k, v.strip().strip('"'))
        clave = os.environ.get("ELEVENLABS_API_KEY")
    voz_id = VOZ.partition(":")[2] or os.environ.get("ELEVENLABS_VOICE_ID")
    if not clave or not voz_id:
        sys.exit("Falta ELEVENLABS_API_KEY o ELEVENLABS_VOICE_ID en .env")
    cuerpo = json.dumps({"text": texto, "model_id": "eleven_multilingual_v2",
                         "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "speed": 1.05}}).encode()
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voz_id}?output_format=mp3_44100_128",
                                 data=cuerpo, headers={"xi-api-key": clave, "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r, open(path, "wb") as f:
        f.write(r.read())

async def generar():
    frases = []
    for i, (_, _, texto) in enumerate(guion):
        if not texto.strip():
            frases.append(np.zeros(0, np.float32)); continue
        p = os.path.join(carpeta, f"frase-{i + 1}.mp3")
        if VOZ.startswith("eleven"):
            eleven(texto, p)
        else:
            await edge_tts.Communicate(texto, VOZ, rate=VEL).save(p)
        s = leer(p)
        nz = np.nonzero(np.abs(s) > 0.005)[0]          # recorta silencios del principio y del final
        frases.append(s[nz[0]:nz[-1] + 1] if len(nz) else s)
    return frases

frases = asyncio.run(generar())
tiempos, t = [], 0.0
for (_, dur, _), s in zip(guion, frases):
    d = max(dur, len(s) / SR + 0.6) if len(s) else dur
    tiempos.append([round(t, 2), round(d, 2)])
    t += d
total = round(t + 0.3, 2)

voz = np.zeros(int(total * SR) + SR, np.float32)
for (t0, d), s, (_, dur, texto) in zip(tiempos, frases, guion):
    st = int((t0 + 0.15) * SR)
    voz[st:st + len(s)] += s
    if len(s):
        print(f"{t0:5.1f} s  {len(s) / SR:4.1f} s de voz en {d:4.1f} s  | {texto[:50]}")
voz = voz / max(1e-6, np.max(np.abs(voz))) * 0.9
with wave.open(os.path.join(carpeta, "voz.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((voz * 32767).astype(np.int16).tobytes())
json.dump({"TIEMPOS": tiempos, "total": total, "original": [[g[0], g[1]] for g in guion]},
          open(os.path.join(carpeta, "tiempos.json"), "w"), indent=1)
print("total", total, "s ·", VOZ)
