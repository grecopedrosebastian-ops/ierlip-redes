#!/usr/bin/env python3
"""Publicación automática en Instagram y Facebook (API de Meta), siempre con el OK de Seba por Telegram.

Flujo:
  1. paquete-diario arma el paquete y corre `armar`: deja las piezas en la rama `publicar` del repo
     (cola/<fecha>/: JPG, MP4 y manifiesto.json) y manda por Telegram los botones Publicar / No publicar.
  2. Seba toca un botón. Lo lee `correr` (que queda esperando) o el bot de comandos (`aprobar-desde`).
  3. `correr` publica cada pieza aprobada a su hora (si la hora ya pasó, enseguida) y avisa el link.
     Lo que no se aprueba antes de las 23:00 no se publica.

Sin el OK no se publica nada. El manifiesto guarda qué se publicó, así una corrida repetida no duplica.

Secretos (GitHub): META_ACCESS_TOKEN (token de página que no vence), IG_USER_ID y FB_PAGE_ID (opcional).
Prueba sin publicar: PUBLICAR_PRUEBA=1. Prueba local sin git: COLA_DIR=<carpeta>.

Uso:
  python scripts/publicar.py armar [fecha]              # desde bot/salida/ (lo usa paquete-diario)
  python scripts/publicar.py correr [fecha]             # espera el OK y publica (lo usa publicar.yml)
  python scripts/publicar.py aprobar <fecha> <alcance>  # todo | placas | reel | nada
  python scripts/publicar.py aprobar-desde bot/aprobacion.json   # lo usa el bot de comandos
"""
import datetime as dt
import importlib.util
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SALIDA = ROOT / "bot" / "salida"
RAMA = "publicar"
VERSION = os.environ.get("GRAPH_VERSION", "").strip() or "v27.0"
# Los tokens del inicio de sesión con Instagram empiezan con "IG" y van por graph.instagram.com;
# los de Facebook (EAA…) por graph.facebook.com.
_TOKEN = os.environ.get("META_ACCESS_TOKEN", "").strip()
GRAPH = ("https://graph.instagram.com/" if _TOKEN.startswith("IG") else "https://graph.facebook.com/") + VERSION
ART = dt.timezone(dt.timedelta(hours=-3))
CIERRE = dt.time(23, 0)          # lo que no se aprueba hasta esta hora, no sale
PEDIDO = dt.time(9, 0)           # a esta hora llegan los botones para autorizar (antes de las 11:30)
RECORDATORIO = dt.time(15, 0)    # si sigue sin OK, se vuelven a mandar los botones
ESPACIO = dt.timedelta(minutes=3)  # entre una publicación y otra
PRUEBA = os.environ.get("PUBLICAR_PRUEBA", "").strip() not in ("", "0")
NOMBRES = {"placa1": "Carrusel", "placa2": "Carrusel 2", "reel": "Reel"}
ALCANCES = {"todo": {"placa1", "placa2", "reel"}, "placas": {"placa1", "placa2"}, "reel": {"reel"}, "nada": set()}

_spec = importlib.util.spec_from_file_location("tg", ROOT / "scripts" / "enviar-telegram.py")
tg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tg)


def ahora():
    return dt.datetime.now(ART)


def hoy():
    return ahora().date().isoformat()


def log(*a):
    print(*a, flush=True)


# ---------------------------------------------------------------- rama `publicar` (la cola)

def git(*args, cwd=None, check=True):
    return subprocess.run(["git", *args], cwd=cwd or ROOT, check=check, text=True, capture_output=True)


def cola_dir():
    """Carpeta de trabajo de la rama `publicar` (un worktree aparte, sin tocar la rama principal)."""
    if os.environ.get("COLA_DIR"):
        d = Path(os.environ["COLA_DIR"])
        d.mkdir(parents=True, exist_ok=True)
        return d
    d = Path(os.environ.get("RUNNER_TEMP", ROOT / ".tmp")) / "cola-publicar"
    if (d / ".git").exists():
        return d
    hay = git("ls-remote", "--heads", "origin", RAMA).stdout.strip()
    if hay:
        git("fetch", "-q", "origin", f"+refs/heads/{RAMA}:refs/remotes/origin/{RAMA}")
        git("worktree", "add", "-q", "-B", RAMA, str(d), f"origin/{RAMA}")
    else:
        git("worktree", "add", "-q", "--detach", str(d))
        git("checkout", "-q", "--orphan", RAMA, cwd=d)
        git("rm", "-rq", "--cached", ".", cwd=d, check=False)
        for p in d.iterdir():
            if p.name != ".git":
                shutil.rmtree(p) if p.is_dir() else p.unlink()
        (d / "README.md").write_text("Cola de publicación de @estudioierlip (la maneja scripts/publicar.py).\n",
                                     encoding="utf-8")
    return d


def actualizar(d):
    if os.environ.get("COLA_DIR"):
        return
    git("fetch", "-q", "origin", f"+refs/heads/{RAMA}:refs/remotes/origin/{RAMA}", cwd=d, check=False)
    git("reset", "-q", "--hard", f"origin/{RAMA}", cwd=d, check=False)


def guardar(d, mensaje):
    if os.environ.get("COLA_DIR"):
        return
    git("config", "user.name", "ierlip-redes-bot", cwd=d)
    git("config", "user.email", "actions@users.noreply.github.com", cwd=d)
    git("add", "-A", cwd=d)
    if not git("status", "--porcelain", cwd=d).stdout.strip():
        return
    git("commit", "-q", "-m", mensaje, cwd=d)
    for _ in range(5):
        if git("push", "-q", "origin", f"HEAD:{RAMA}", cwd=d, check=False).returncode == 0:
            return
        git("pull", "-q", "--rebase", "origin", RAMA, cwd=d, check=False)
        time.sleep(3)
    sys.exit("No pude guardar la cola en la rama publicar")


def leer_manifiesto(d, fecha):
    f = d / "cola" / fecha / "manifiesto.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def escribir_manifiesto(d, m):
    f = d / "cola" / m["fecha"] / "manifiesto.json"
    f.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------- armar

def separar_hora(texto, defecto):
    """El caption termina con la hora sugerida: se saca del texto y se usa como horario."""
    lineas = texto.strip().splitlines()
    while lineas and not lineas[-1].strip():
        lineas.pop()
    if lineas:
        m = re.search(r"\b([01]?\d|2[0-3])[:.]([0-5]\d)\b", lineas[-1])
        if m and len(lineas[-1]) < 90 and "#" not in lineas[-1]:
            lineas.pop()
            return "\n".join(lineas).strip(), f"{int(m.group(1)):02d}:{m.group(2)}"
    return "\n".join(lineas).strip(), defecto


def horas_defecto(fecha):
    dia = dt.date.fromisoformat(fecha).weekday()  # 0 = lunes
    return {"placa1": "11:00" if dia >= 5 else "12:00", "placa2": "15:00", "reel": "20:00" if dia == 0 else "18:00"}


def a_jpg(png, jpg):
    """Instagram solo acepta JPEG."""
    try:
        from PIL import Image
        Image.open(png).convert("RGB").save(jpg, "JPEG", quality=93)
    except ImportError:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(png), "-q:v", "2", str(jpg)], check=True)


def armar(fecha):
    d = cola_dir()
    actualizar(d)
    base = d / "cola" / fecha
    if base.exists():
        shutil.rmtree(base)
    base.mkdir(parents=True)
    defecto = horas_defecto(fecha)
    piezas = []
    for p in ("placa1", "placa2"):
        pngs = sorted((SALIDA / p).glob("pieza*.png"), key=lambda f: int(f.stem.split("-")[1]) if "-" in f.stem else 0)
        if not pngs or not (SALIDA / p / "texto.txt").exists():
            continue
        (base / p).mkdir()
        archivos = []
        for i, png in enumerate(pngs[:10], 1):
            a_jpg(png, base / p / f"{i}.jpg")
            archivos.append(f"{p}/{i}.jpg")
        caption, hora = separar_hora((SALIDA / p / "texto.txt").read_text(encoding="utf-8"), defecto[p])
        piezas.append({"id": p, "tipo": "carrusel" if len(archivos) > 1 else "imagen", "archivos": archivos,
                       "caption": caption, "hora": hora, "estado": "pendiente", "redes": {}})
    reel = SALIDA / "reel" / "reel.mp4"
    meta = json.loads((SALIDA / "meta.json").read_text(encoding="utf-8")) if (SALIDA / "meta.json").exists() else {}
    solo_tiktok = bool(meta.get("reel_solo_tiktok"))  # los jueves: el reel va a mano a TikTok, no a Instagram
    if reel.exists() and (SALIDA / "reel" / "texto.txt").exists() and not solo_tiktok:
        (base / "reel").mkdir()
        shutil.copy(reel, base / "reel" / "reel.mp4")
        caption, hora = separar_hora((SALIDA / "reel" / "texto.txt").read_text(encoding="utf-8"), defecto["reel"])
        piezas.append({"id": "reel", "tipo": "reel", "archivos": ["reel/reel.mp4"], "caption": caption, "hora": hora,
                       "estado": "pendiente", "redes": {}})
    if not piezas:
        sys.exit("No hay piezas para la cola")
    m = {"fecha": fecha, "aprobacion": None, "piezas": piezas, "mensaje_id": None}
    # Se borran las carpetas de más de 10 días para que la rama no crezca.
    limite = (dt.date.fromisoformat(fecha) - dt.timedelta(days=10)).isoformat()
    for vieja in (d / "cola").iterdir():
        if vieja.is_dir() and vieja.name < limite:
            shutil.rmtree(vieja)
    escribir_manifiesto(d, m)
    guardar(d, f"cola: paquete del {fecha}")
    # El paquete se arma la noche anterior: los botones salen a las 9:00 del día (los manda `correr`).
    # Si se arma de día (a mano), salen enseguida.
    if ahora() >= dt.datetime.combine(dt.date.fromisoformat(fecha), PEDIDO, ART):
        m["mensaje_id"] = mandar_botones(m)
        m["recordatorio"] = ahora() >= dt.datetime.combine(dt.date.fromisoformat(fecha), RECORDATORIO, ART)
        escribir_manifiesto(d, m)
        guardar(d, f"cola: botones del {fecha}")
    log(f"Cola del {fecha}: " + ", ".join(f"{p['id']} {p['hora']}" for p in piezas))


DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def mandar_botones(m, recordatorio=False):
    lineas = [f"• {NOMBRES[p['id']]}: {p['hora']}" for p in m["piezas"] if p["estado"] == "pendiente"]
    redes = "Instagram y Facebook" if os.environ.get("FB_PAGE_ID", "").strip() else "Instagram"
    dia = dt.date.fromisoformat(m["fecha"])
    cuando = f"{DIAS[dia.weekday()]} {dia.day}/{dia.month}"
    titulo = (f"⏰ RECORDATORIO: todavía no autorizaste lo del {cuando}" if recordatorio
              else f"📤 ¿PUBLICO LO DEL {cuando.upper()}?")
    texto = (titulo + "\n(lo que te llegó con el paquete)\n" + "\n".join(lineas) +
             f"\n\nSale solo en {redes} a esa hora (si ya pasó, enseguida). Sin tu OK no se publica nada; "
             "lo que no apruebes antes de las 23:00 queda sin publicar.")
    f = m["fecha"]
    filas = [[{"text": "✅ Publicar", "callback_data": f"pub:{f}:todo"}]]
    if len(m["piezas"]) > 1:
        filas.append([{"text": "🗞️ Solo carrusel", "callback_data": f"pub:{f}:placas"},
                      {"text": "🎬 Solo reel", "callback_data": f"pub:{f}:reel"}])
    filas.append([{"text": "❌ No publicar", "callback_data": f"pub:{f}:nada"}])
    teclado = {"inline_keyboard": filas}
    r = tg.api("sendMessage", {"text": texto, "reply_markup": json.dumps(teclado)})
    return r["result"]["message_id"]


# ---------------------------------------------------------------- aprobación

def leer_callbacks(fecha):
    """Busca en Telegram un botón tocado para esta fecha, sin marcar los mensajes como leídos
    (los comandos de texto los sigue leyendo el bot de comandos)."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    try:
        with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/getUpdates?timeout=0", timeout=60) as r:
            updates = json.loads(r.read()).get("result", [])
    except Exception as e:
        log("No pude leer Telegram:", e)
        return None
    elegido = None
    for u in updates:
        cb = u.get("callback_query") or {}
        datos = cb.get("data", "")
        if str(cb.get("message", {}).get("chat", {}).get("id")) != chat or not datos.startswith(f"pub:{fecha}:"):
            continue
        elegido = {"fecha": fecha, "alcance": datos.split(":")[2], "callback_id": cb.get("id"),
                   "mensaje_id": cb.get("message", {}).get("message_id")}
    return elegido


def registrar(d, m, alcance, callback_id=None):
    """Guarda la decisión (la primera vale) y responde en Telegram."""
    if alcance not in ALCANCES:
        return False
    if ahora() >= dt.datetime.combine(dt.date.fromisoformat(m["fecha"]), CIERRE, ART):
        if callback_id:
            responder_callback(callback_id, "Ese paquete ya venció.")
        tg.texto(f"⌛ El paquete del {m['fecha']} ya venció (después de las 23:00 no se publica).")
        return False
    if m.get("aprobacion"):
        if callback_id:
            responder_callback(callback_id, "Ya estaba decidido.")
        return False
    m["aprobacion"] = {"alcance": alcance, "hora": ahora().isoformat(timespec="minutes")}
    for p in m["piezas"]:
        if p["estado"] == "pendiente":
            p["estado"] = "aprobada" if p["id"] in ALCANCES[alcance] else "descartada"
    escribir_manifiesto(d, m)
    guardar(d, f"cola: {alcance} el {m['fecha']}")
    if callback_id:
        responder_callback(callback_id, "Listo, anotado.")
    if m.get("mensaje_id"):
        try:
            tg.api("editMessageReplyMarkup", {"message_id": m["mensaje_id"], "reply_markup": json.dumps({"inline_keyboard": []})})
        except SystemExit:
            pass
    aprobadas = [f"{NOMBRES[p['id']]} a las {p['hora']}" for p in m["piezas"] if p["estado"] == "aprobada"]
    if aprobadas:
        tg.texto("👍 Anotado. Publico: " + ", ".join(aprobadas) + ". Te aviso con el link de cada una.")
    else:
        tg.texto("👌 Anotado: hoy no se publica nada del paquete.")
    return True


def responder_callback(callback_id, texto):
    try:
        tg.api("answerCallbackQuery", {"callback_query_id": callback_id, "text": texto})
    except SystemExit:
        pass  # el botón ya era viejo: no importa


def aprobar(fecha, alcance, callback_id=None):
    d = cola_dir()
    actualizar(d)
    m = leer_manifiesto(d, fecha)
    if not m:
        tg.texto(f"No encontré el paquete del {fecha} para publicar.")
        return
    if registrar(d, m, alcance, callback_id) and alcance != "nada" and not PRUEBA:
        despachar(fecha)


def despachar(fecha):
    """Lanza publicar.yml (si ya hay una corrida esperando, queda en cola y no duplica nada)."""
    repo, token = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_TOKEN", "").strip()
    if not repo or not token:
        return
    body = json.dumps({"ref": os.environ.get("GITHUB_REF_NAME", "main"), "inputs": {"fecha": fecha}}).encode()
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/actions/workflows/publicar.yml/dispatches",
                                 data=body, method="POST",
                                 headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
    try:
        urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as e:
        log("No pude lanzar publicar.yml:", e.code)


# ---------------------------------------------------------------- API de Meta

def meta_token():
    return os.environ.get("META_ACCESS_TOKEN", "").strip()


def graph(metodo, ruta, campos=None, base=GRAPH):
    datos = dict(campos or {})
    datos["access_token"] = meta_token()
    url = f"{base}/{ruta}"
    if metodo == "GET":
        req = urllib.request.Request(url + "?" + urllib.parse.urlencode(datos))
    else:
        req = urllib.request.Request(url, data=urllib.parse.urlencode(datos).encode(), method="POST")
    return _pedir(req, ruta)


def _pedir(req, ruta):
    for intento in range(4):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            cuerpo = e.read().decode("utf-8", "replace")
            if e.code >= 500 and intento < 3:
                time.sleep(15 * (intento + 1))
                continue
            try:
                err = json.loads(cuerpo).get("error", {})
                detalle = f"{err.get('message')} (código {err.get('code')})"
            except ValueError:
                detalle = cuerpo[:200]
            raise RuntimeError(f"Meta respondió {e.code} en {ruta.split('?')[0]}: {detalle}") from None
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            if intento == 3:
                raise RuntimeError(f"No pude conectar con Meta: {e}") from None
            time.sleep(15 * (intento + 1))


def esperar_contenedor(cid, minutos=10):
    for _ in range(minutos * 6):
        st = graph("GET", cid, {"fields": "status_code,status"})
        if st.get("status_code") == "FINISHED":
            return
        if st.get("status_code") in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram no pudo procesar el archivo: {st.get('status')}")
        time.sleep(10)
    raise RuntimeError("Instagram tardó demasiado en procesar el archivo")


def url_publica(fecha, archivo):
    repo = os.environ.get("GITHUB_REPOSITORY", "grecopedrosebastian-ops/ierlip-redes")
    return f"https://raw.githubusercontent.com/{repo}/{RAMA}/cola/{fecha}/{archivo}"


def instagram(pieza, fecha, d):
    ig = os.environ["IG_USER_ID"].strip()
    cap = pieza["caption"]
    if pieza["tipo"] == "reel":
        # Igual que las imágenes: Instagram baja el video desde la URL pública de la rama `publicar`.
        # (La subida "resumable" a rupload.facebook.com respondía 400 con el token de Instagram.)
        c = graph("POST", f"{ig}/media", {"media_type": "REELS", "video_url": url_publica(fecha, pieza["archivos"][0]),
                                          "caption": cap, "share_to_feed": "true"})
        esperar_contenedor(c["id"], 15)
        cid = c["id"]
    elif pieza["tipo"] == "carrusel":
        hijos = []
        for a in pieza["archivos"]:
            h = graph("POST", f"{ig}/media", {"image_url": url_publica(fecha, a), "is_carousel_item": "true"})
            hijos.append(h["id"])
        for h in hijos:
            esperar_contenedor(h)
        cid = graph("POST", f"{ig}/media", {"media_type": "CAROUSEL", "children": ",".join(hijos), "caption": cap})["id"]
        esperar_contenedor(cid)
    else:
        cid = graph("POST", f"{ig}/media", {"image_url": url_publica(fecha, pieza["archivos"][0]), "caption": cap})["id"]
        esperar_contenedor(cid)
    mid = graph("POST", f"{ig}/media_publish", {"creation_id": cid})["id"]
    try:
        link = graph("GET", mid, {"fields": "permalink"}).get("permalink", "")
    except RuntimeError:
        link = ""
    return {"id": mid, "link": link}


def facebook(pieza, fecha, d):
    page = os.environ["FB_PAGE_ID"].strip()
    cap = pieza["caption"]
    if pieza["tipo"] == "reel":
        video = d / "cola" / fecha / pieza["archivos"][0]
        boundary = uuid.uuid4().hex
        partes = {"description": cap, "access_token": meta_token()}
        body = b"".join(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
                        for k, v in partes.items())
        body += (f'--{boundary}\r\nContent-Disposition: form-data; name="source"; filename="reel.mp4"\r\n'
                 f"Content-Type: video/mp4\r\n\r\n").encode() + video.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
        req = urllib.request.Request(f"{GRAPH.replace('graph.', 'graph-video.')}/{page}/videos", data=body, method="POST",
                                     headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        r = _pedir(req, "video de Facebook")
        return {"id": r.get("id"), "link": f"https://www.facebook.com/{r.get('id')}"}
    fotos = []
    for a in pieza["archivos"]:
        f = graph("POST", f"{page}/photos", {"url": url_publica(fecha, a), "published": "false"})
        fotos.append(f["id"])
    campos = {"message": cap}
    for i, fid in enumerate(fotos):
        campos[f"attached_media[{i}]"] = json.dumps({"media_fbid": fid})
    r = graph("POST", f"{page}/feed", campos)
    return {"id": r.get("id"), "link": f"https://www.facebook.com/{r.get('id')}"}


def publicar_pieza(d, m, pieza):
    redes = [("instagram", instagram)]
    if os.environ.get("FB_PAGE_ID", "").strip():
        redes.append(("facebook", facebook))
    errores = []
    for nombre, fn in redes:
        if pieza["redes"].get(nombre, {}).get("id"):
            continue  # ya salió en esa red
        try:
            if PRUEBA:
                log(f"[prueba] publicaría {pieza['id']} en {nombre}: {pieza['archivos']}")
                pieza["redes"][nombre] = {"id": "prueba", "link": ""}
            else:
                pieza["redes"][nombre] = fn(pieza, m["fecha"], d)
        except Exception as e:
            errores.append(f"{nombre}: {e}")
        escribir_manifiesto(d, m)
        guardar(d, f"cola: {pieza['id']} en {nombre} ({m['fecha']})")
    pieza["intentos"] = pieza.get("intentos", 0) + 1
    hechas = [n for n, _ in redes if pieza["redes"].get(n, {}).get("id")]
    if len(hechas) == len(redes):
        pieza["estado"] = "publicada"
    elif pieza["intentos"] >= 3:
        pieza["estado"] = "error"
    escribir_manifiesto(d, m)
    guardar(d, f"cola: {pieza['id']} {pieza['estado']} ({m['fecha']})")
    links = " · ".join(f"{n.capitalize()}: {pieza['redes'][n].get('link') or 'publicado'}" for n in hechas)
    if hechas and (pieza["estado"] == "publicada" or not errores):
        tg.texto(f"✅ Publicado{' (prueba)' if PRUEBA else ''}: {NOMBRES[pieza['id']]}. {links}")
    if errores:
        if pieza["estado"] == "error":
            tg.texto(f"❌ No pude publicar {NOMBRES[pieza['id']]} ({'; '.join(errores)}). "
                     "Subila a mano desde el archivo que te mandé.")
        else:
            log("Error, se reintenta:", errores)
    return not errores


# ---------------------------------------------------------------- correr

def correr(fecha, presupuesto_min=330):
    inicio = time.monotonic()
    d = cola_dir()
    ultima = None
    falta_meta = not PRUEBA and not (meta_token() and os.environ.get("IG_USER_ID", "").strip())
    while True:
        actualizar(d)
        m = leer_manifiesto(d, fecha)
        if not m:
            sys.exit(f"No hay cola para el {fecha}")
        if not m.get("aprobacion"):
            cb = leer_callbacks(fecha)
            if cb:
                registrar(d, m, cb["alcance"], cb["callback_id"])
        if not m.get("aprobacion"):
            dia = dt.date.fromisoformat(fecha)
            t0 = ahora()
            if not m.get("mensaje_id") and t0 >= dt.datetime.combine(dia, PEDIDO, ART):
                m["mensaje_id"] = mandar_botones(m)
                m["recordatorio"] = t0 >= dt.datetime.combine(dia, RECORDATORIO, ART)  # ya es tarde: sin recordatorio
                escribir_manifiesto(d, m)
                guardar(d, f"cola: botones del {fecha}")
            elif (m.get("mensaje_id") and not m.get("recordatorio")
                  and dt.datetime.combine(dia, RECORDATORIO, ART) <= t0 < dt.datetime.combine(dia, CIERRE, ART)):
                m["recordatorio"] = True
                m["mensaje_id"] = mandar_botones(m, recordatorio=True)
                escribir_manifiesto(d, m)
                guardar(d, f"cola: recordatorio del {fecha}")
        if m.get("aprobacion") and falta_meta and any(p["estado"] == "aprobada" for p in m["piezas"]):
            tg.texto("⚠️ Aprobaste, pero faltan los secretos de Meta (META_ACCESS_TOKEN e IG_USER_ID) en GitHub: "
                     "no publiqué nada. Subilo a mano.")
            for p in m["piezas"]:
                if p["estado"] == "aprobada":
                    p["estado"] = "error"
            escribir_manifiesto(d, m)
            guardar(d, f"cola: sin secretos ({fecha})")
            return
        t = ahora()
        cierre = dt.datetime.combine(dt.date.fromisoformat(fecha), CIERRE, ART)
        if not m.get("aprobacion") and t >= cierre:
            for p in m["piezas"]:
                p["estado"] = "vencida" if p["estado"] == "pendiente" else p["estado"]
            escribir_manifiesto(d, m)
            guardar(d, f"cola: sin OK ({fecha})")
            tg.texto(f"⌛ No hubo OK para el paquete del {fecha}: no se publicó nada.")
            return
        for p in sorted(m["piezas"], key=lambda x: x["hora"]):
            if p["estado"] != "aprobada":
                continue
            hora = dt.datetime.combine(dt.date.fromisoformat(fecha), dt.time.fromisoformat(p["hora"]), ART)
            if t >= hora and (ultima is None or t - ultima >= ESPACIO):
                publicar_pieza(d, m, p)
                ultima = t = ahora()
        pendientes = [p for p in m["piezas"] if p["estado"] in ("pendiente", "aprobada")]
        if not pendientes:
            log("Nada más para publicar.")
            return
        if (time.monotonic() - inicio) / 60 > presupuesto_min:
            log("Se termina el tiempo de esta corrida: lanzo otra para seguir esperando.")
            despachar(fecha)
            return
        time.sleep(15 if PRUEBA else 60)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    cmd = args[0]
    if cmd == "armar":
        armar(args[1] if len(args) > 1 else hoy())
    elif cmd == "correr":
        correr(args[1] if len(args) > 1 and args[1] else hoy(),
               float(os.environ.get("PUBLICAR_PRESUPUESTO_MIN", "330")))
    elif cmd == "verificar":  # solo lee la cuenta: confirma que el token y el ID andan, sin publicar nada
        try:
            r = graph("GET", os.environ["IG_USER_ID"].strip(), {"fields": "username,media_count"})
            msg = f"🔌 Conexión con Instagram OK: @{r.get('username')} ({r.get('media_count')} publicaciones). Ya puedo publicar con tu OK."
        except Exception as e:
            msg = f"❌ La conexión con Instagram falló: {e}"
        log(msg)
        tg.texto(msg)
    elif cmd == "informe":  # solo lectura: métricas de las últimas publicaciones (para la auditoría)
        ig = os.environ["IG_USER_ID"].strip()
        cuenta = graph("GET", ig, {"fields": "username,followers_count,follows_count,media_count,biography"})
        campos = "id,caption,media_type,media_product_type,timestamp,like_count,comments_count,permalink"
        items, r = [], graph("GET", f"{ig}/media", {"fields": campos, "limit": "60"})
        items += r.get("data", [])
        for it in items:
            it["caption"] = (it.get("caption") or "").splitlines()[0][:90] if it.get("caption") else ""
            met = "reach,saved,shares,views,total_interactions"
            try:
                ins = graph("GET", f"{it['id']}/insights", {"metric": met})
                it["insights"] = {d["name"]: d["values"][0]["value"] for d in ins.get("data", [])}
            except Exception as e:
                it["insights"] = {"error": str(e)[:120]}
        print("INFORME_JSON " + json.dumps({"cuenta": cuenta, "media": items}, ensure_ascii=False))
    elif cmd == "aprobar":
        aprobar(args[1], args[2])
    elif cmd == "aprobar-desde":
        a = json.loads(Path(args[1]).read_text(encoding="utf-8"))
        aprobar(a["fecha"], a["alcance"], a.get("callback_id"))
    else:
        sys.exit(__doc__)
