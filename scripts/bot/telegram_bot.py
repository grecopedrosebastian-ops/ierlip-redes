#!/usr/bin/env python3
"""Bot de comandos de Telegram para @estudioierlip. Corre en GitHub Actions cada 5 minutos.

Comandos (solo se aceptan desde TELEGRAM_CHAT_ID):
  /placa <tema>       placa del feed (carrusel Papel), con datos verificados en la web
  /historia <tema>    historia informativa (Papel oscuro)
  /aviso <texto>      placa de aviso urgente + texto para WhatsApp
  /encuesta [tema]    historia para pegar el sticker de encuesta (o: pregunta | opción 1 | opción 2)
  /cambiar <pedido>   rehace la última pieza con ese cambio
  /video [formato] [tema]  pide un video al repo ierlip-video-diario (vencimientos, conversacion u oficina)
  /estado             si las tareas de hoy corrieron
  /ayuda              lista de comandos

Uso (lo llama .github/workflows/telegram-bot.yml):
  python scripts/bot/telegram_bot.py leer      # toma el próximo pedido y lo deja en bot/pedido.json
  python scripts/bot/telegram_bot.py enviar    # manda lo que quedó en bot/salida/
  python scripts/bot/telegram_bot.py error     # avisa que no se pudo generar
"""
import datetime as dt
import importlib.util
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOT = ROOT / "bot"
SALIDA = BOT / "salida"
ULTIMO = ROOT / "state" / "bot-ultimo.json"

# Reutiliza el cliente de Telegram del envío diario.
_spec = importlib.util.spec_from_file_location("tg", ROOT / "scripts" / "enviar-telegram.py")
tg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tg)

CON_IA = {"placa", "historia", "aviso", "encuesta", "cambiar"}
AYUDA = """🤖 COMANDOS

/aviso <texto> — placa de aviso urgente + texto para WhatsApp
/placa <tema> — placa del feed (verifica datos en la web)
/historia <tema> — historia informativa
/encuesta [tema] — historia de encuesta (o: pregunta | opción 1 | opción 2)
/cambiar <pedido> — rehace lo último con ese cambio
/video [formato] [tema] — pide un video (formato: vencimientos, conversacion u oficina; el tema es opcional)
/estado — si las tareas de hoy corrieron

Ejemplos: /placa fondo de asistencia laboral · /video vencimientos IVA de noviembre
Tarda entre 3 y 8 minutos. Todo llega como archivo para que lo revises y lo publiques vos."""


def telegram_get(method, **params):
    token = os.environ["TELEGRAM_BOT_TOKEN"].strip()
    q = "&".join(f"{k}={v}" for k, v in params.items())
    with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/{method}?{q}", timeout=60) as r:
        return json.loads(r.read())


def salida_gh(**kv):
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            for k, v in kv.items():
                f.write(f"{k}={v}\n")


def parsear(texto):
    """'/placa@Bot <tema>' → ('placa', 'tema'). Acepta el tema con o sin < >."""
    m = re.match(r"^/(\w+)(?:@\w+)?\s*(.*)$", texto.strip(), re.S)
    if not m:
        return None, ""
    arg = m.group(2).strip()
    if arg.startswith("<") and arg.endswith(">"):
        arg = arg[1:-1].strip()
    return m.group(1).lower(), arg


def estado():
    """Corridas de hoy de los workflows de este repo (el repo de videos es privado: no se puede leer desde acá)."""
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    hoy = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=3)).date().isoformat()
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/actions/runs?per_page=40",
                                 headers={"Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN', '')}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            runs = json.loads(r.read())["workflow_runs"]
    except Exception as e:
        return f"No pude consultar GitHub ({e})."
    lineas = []
    for run in runs:
        if run["name"].startswith("Telegram diario") and run["created_at"][:10] >= hoy:
            ok = {"success": "✅", "failure": "❌"}.get(run["conclusion"], "⏳")
            lineas.append(f"{ok} Historia del día ({run['created_at'][11:16]} UTC)")
    txt = "📋 ESTADO DE HOY\n" + ("\n".join(lineas) if lineas else "Todavía no corrió el envío de la historia (sale 07:30).")
    return txt + "\nVideos: si no te llegó el de hoy, mirá Actions en el repo ierlip-video-diario."


FORMATOS = {"vencimientos": "vencimientos", "vencimiento": "vencimientos",
            "conversacion": "situacion-graciosa", "conversación": "situacion-graciosa", "graciosa": "situacion-graciosa",
            "situacion-graciosa": "situacion-graciosa", "oficina": "personaje-oficina", "personaje-oficina": "personaje-oficina"}
VIDEOS_REPO = "grecopedrosebastian-ops/ierlip-video-diario"


def pedir_video(arg):
    """Lanza el workflow del repo de videos (necesita el secreto VIDEOS_TOKEN con permiso de Actions en ese repo)."""
    token = os.environ.get("VIDEOS_TOKEN", "").strip()
    if not token:
        return "Para pedir videos falta cargar el secreto VIDEOS_TOKEN en el repo ierlip-redes."
    palabras = arg.split(maxsplit=1)
    formato = "auto"
    if palabras and palabras[0].lower() in FORMATOS:
        formato = FORMATOS[palabras[0].lower()]
        arg = palabras[1] if len(palabras) > 1 else ""
    body = json.dumps({"ref": "main", "inputs": {"format": formato, "topic": arg.strip()}}).encode()
    req = urllib.request.Request(
        f"https://api.github.com/repos/{VIDEOS_REPO}/actions/workflows/daily-video.yml/dispatches", data=body, method="POST",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as e:
        return f"❌ No pude pedir el video (GitHub respondió {e.code}). Revisá el secreto VIDEOS_TOKEN."
    tema = f" sobre «{arg.strip()}»" if arg.strip() else ""
    return (f"🎬 Pedí un video ({formato}){tema}. Tarda entre 10 y 20 minutos y te llega por acá, "
            "como los diarios. Usa crédito de la IA igual que los videos automáticos.")


def leer():
    chat = os.environ["TELEGRAM_CHAT_ID"].strip()
    # Si otro sistema dejó un webhook en el bot, getUpdates no funciona: se saca.
    if telegram_get("getWebhookInfo").get("result", {}).get("url"):
        telegram_get("deleteWebhook")
    updates = telegram_get("getUpdates", timeout=0).get("result", [])
    pedido = None
    ultimo_id = None
    for u in updates:
        msg = u.get("message") or u.get("edited_message") or {}
        texto = msg.get("text", "")
        if str(msg.get("chat", {}).get("id")) != chat or not texto.startswith("/"):
            ultimo_id = u["update_id"]
            continue
        cmd, arg = parsear(texto)
        if cmd in CON_IA:
            if cmd in {"placa", "historia", "aviso"} and not arg:
                tg.texto(f"Falta el tema. Ejemplo: /{cmd} fondo de asistencia laboral")
            elif cmd == "cambiar" and not ULTIMO.exists():
                tg.texto("Todavía no hay ninguna pieza para cambiar. Pedí una con /placa, /historia, /aviso o /encuesta.")
            else:
                pedido = {"comando": cmd, "pedido": arg, "update_id": u["update_id"],
                          "fecha": (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=3)).isoformat(timespec="minutes")}
                ultimo_id = u["update_id"]
                break  # un pedido con IA por corrida; los demás quedan para la próxima
        elif cmd == "estado":
            tg.texto(estado())
        elif cmd == "video":
            tg.texto(pedir_video(arg))
        elif cmd in {"ayuda", "start", "help"}:
            tg.texto(AYUDA)
        else:
            tg.texto("No entendí ese comando.\n\n" + AYUDA)
        ultimo_id = u["update_id"]
    if ultimo_id is not None:
        telegram_get("getUpdates", offset=ultimo_id + 1, timeout=0)  # confirma lo leído
    if not pedido:
        salida_gh(hay_pedido="false")
        return
    BOT.mkdir(exist_ok=True)
    if pedido["comando"] == "cambiar":
        pedido["anterior"] = json.loads(ULTIMO.read_text(encoding="utf-8"))
    (BOT / "pedido.json").write_text(json.dumps(pedido, ensure_ascii=False, indent=2), encoding="utf-8")
    espera = {"placa": "la placa", "historia": "la historia", "aviso": "el aviso", "encuesta": "la encuesta", "cambiar": "el cambio"}
    tg.texto(f"⏳ Armando {espera[pedido['comando']]} (verifico datos en la web, tarda entre 3 y 8 minutos)…")
    salida_gh(hay_pedido="true")


def enviar():
    pngs = sorted(SALIDA.glob("pieza*.png"), key=lambda p: int(p.stem.split("-")[1]) if "-" in p.stem else 0)
    if not pngs:
        return error("no se generaron imágenes")
    meta = json.loads((SALIDA / "meta.json").read_text(encoding="utf-8")) if (SALIDA / "meta.json").exists() else {}
    tg.texto("✅ " + meta.get("resumen", "Listo") + "\nRevisala antes de publicar.")
    for i in range(0, len(pngs), 10):
        tg.documentos(pngs[i:i + 10])
    if (SALIDA / "texto.txt").exists():
        tg.texto((SALIDA / "texto.txt").read_text(encoding="utf-8").strip())
    if meta.get("needs_review"):
        tg.texto("🔎 VERIFICAR ANTES DE PUBLICAR\n" + "\n".join(f"• {n}" for n in meta["needs_review"]))
    # Guarda la pieza para que /cambiar pueda rehacerla.
    pedido = json.loads((BOT / "pedido.json").read_text(encoding="utf-8"))
    ULTIMO.parent.mkdir(exist_ok=True)
    ULTIMO.write_text(json.dumps({
        "comando": pedido["anterior"]["comando"] if pedido["comando"] == "cambiar" else pedido["comando"],
        "pedido": pedido["pedido"],
        "spec": json.loads((SALIDA / "spec.json").read_text(encoding="utf-8")),
        "texto": (SALIDA / "texto.txt").read_text(encoding="utf-8") if (SALIDA / "texto.txt").exists() else "",
        "meta": meta,
    }, ensure_ascii=False, indent=2), encoding="utf-8")


def error(motivo=""):
    detalle = f" ({motivo})" if motivo else ""
    tg.texto(f"❌ No pude generar el contenido{detalle}. Si se repite, puede ser falta de crédito de la IA: "
             "revisá Actions en el repo ierlip-redes. Probá de nuevo o reformulá el pedido.")


if __name__ == "__main__":
    if sys.argv[1] == "texto":  # manda un mensaje suelto (lo usa arca-diario)
        tg.texto(sys.argv[2])
    elif sys.argv[1] == "animada":  # manda la historia animada (lo usa historia-animada)
        meta = json.loads((SALIDA / "meta.json").read_text(encoding="utf-8")) if (SALIDA / "meta.json").exists() else {}
        tg.texto("🎬 " + meta.get("resumen", "Historia animada") + "
Revisala antes de subirla.")
        tg.documentos([SALIDA / "historia-animada.mp4"])
        if (SALIDA / "texto.txt").exists():
            tg.texto((SALIDA / "texto.txt").read_text(encoding="utf-8").strip())
        if meta.get("needs_review"):
            tg.texto("🔎 VERIFICAR ANTES DE SUBIR
" + "
".join(f"• {n}" for n in meta["needs_review"]))
    else:
        {"leer": leer, "enviar": enviar, "error": error}[sys.argv[1]]()
