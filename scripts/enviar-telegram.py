#!/usr/bin/env python3
"""Manda a Telegram las piezas del día que NO están cargadas en Metricool, listas para subir desde el celular.

Por cada pieza manda los archivos sin comprimir (como documento, para que Instagram no pierda calidad),
y después el copy en un mensaje aparte para copiar y pegar, con la hora y el sticker a usar.
Solo librería estándar. Usa las mismas variables que el proyecto de videos:
  TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID y (opcional) TELEGRAM_THREAD_ID

Qué va por Telegram: en output/<fecha>/meta.json, "metricool": {"placa": true, "historia": false}
marca lo que ya está en Metricool. Lo que no figura como true se manda.

Uso:
  python scripts/enviar-telegram.py 2026-11-02          # una fecha
  python scripts/enviar-telegram.py hoy                 # la fecha de hoy (Buenos Aires)
  python scripts/enviar-telegram.py 2026-11-02 --probar # muestra qué mandaría, sin mandar
"""
import datetime as dt
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIMIT_TEXT = 4096


def api(method, fields, files=None):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat:
        sys.exit("Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID")
    fields = {"chat_id": chat, **fields}
    thread = os.environ.get("TELEGRAM_THREAD_ID", "").strip()
    if thread:
        fields["message_thread_id"] = thread
    boundary = uuid.uuid4().hex
    body = b""
    for k, v in fields.items():
        body += f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    for k, path in (files or {}).items():
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        body += (f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{Path(path).name}"\r\n'
                 f"Content-Type: {ctype}\r\n\r\n").encode() + Path(path).read_bytes() + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/{method}", data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        # no imprimir la URL: contiene el token
        sys.exit(f"Telegram respondió {e.code} en {method}: {e.read().decode('utf-8', 'replace')[:300]}")
    if not data.get("ok"):
        sys.exit(f"Telegram devolvió error en {method}: {str(data)[:300]}")
    return data


def texto(t):
    for i in range(0, len(t), LIMIT_TEXT):
        api("sendMessage", {"text": t[i:i + LIMIT_TEXT], "disable_web_page_preview": "true"})


def documentos(paths):
    """Hasta 10 archivos en un solo álbum, sin compresión."""
    if len(paths) == 1:
        api("sendDocument", {}, {"document": str(paths[0])})
        return
    media = [{"type": "document", "media": f"attach://f{i}"} for i in range(len(paths))]
    api("sendMediaGroup", {"media": json.dumps(media)}, {f"f{i}": str(p) for i, p in enumerate(paths)})


def main():
    args = sys.argv[1:]
    probar = "--probar" in args
    fecha = next((a for a in args if a != "--probar"), "hoy")
    if fecha == "hoy":
        fecha = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=3)).date().isoformat()
    d = ROOT / "output" / fecha
    if not (d / "meta.json").exists():
        msg = f"⚠️ IERLIP redes: no hay piezas generadas para {fecha}."
        print(msg)
        if not probar:
            texto(msg)
        return
    meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
    en_metricool = meta.get("metricool", {})
    envios = []

    if not en_metricool.get("historia"):
        archivos = [d / "historia.png"] + ([d / "historia-animada.mp4"] if (d / "historia-animada.mp4").exists() else [])
        st = meta.get("sticker_nativo")
        nota = (f"📲 HISTORIA · {fecha} · {meta['publicar_historia'][11:16]} h\n"
                + (f"Pegale el sticker: {st}" if st else "Sin sticker. Subila tal cual.")
                + ("\nDespués, la historia animada (con sonido) como segunda historia." if len(archivos) > 1 else ""))
        envios.append((archivos, nota))

    if not en_metricool.get("placa"):
        placas = sorted(d.glob("placa*.png"), key=lambda p: int(p.stem.split("-")[1]) if "-" in p.stem else 0)
        tipo = "CARRUSEL" if len(placas) > 1 else "PLACA"
        nota = (f"🖼️ {tipo} DEL FEED · {fecha} · {meta['publicar_placa'][11:16]} h · {len(placas)} imagen(es), en este orden.\n"
                "El copy va en el mensaje siguiente, listo para copiar.")
        envios.append((placas, nota, (d / "caption.txt").read_text(encoding="utf-8").strip()))

    if meta.get("needs_review"):
        envios.append(([], "🔎 VERIFICAR ANTES DE SUBIR\n" + "\n".join(f"• {n}" for n in meta["needs_review"])))

    if not envios:
        print(f"{fecha}: todo está en Metricool, no hay nada para mandar.")
        return
    for e in envios:
        archivos, nota, *copy = e
        print(nota.splitlines()[0], [p.name for p in archivos])
        if probar:
            continue
        texto(nota)
        if archivos:
            documentos(archivos)
        if copy:
            texto(copy[0])
    print("Enviado." if not probar else "Prueba: no se mandó nada.")


if __name__ == "__main__":
    main()
