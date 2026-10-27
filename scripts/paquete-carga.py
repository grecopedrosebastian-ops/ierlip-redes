"""Arma el paquete de carga semanal para Zoho Social (Instagram/Facebook) y TikTok Studio.

Uso:  python scripts/paquete-carga.py 2026-11-01 2026-11-07

Genera carga/<desde>_<hasta>/:
  <fecha>_<dia>/   archivos numerados en el orden en que se suben + caption.txt
  CARGA.md         planilla: qué programar, dónde, a qué hora, y qué verificar antes
No programa ni publica nada.
"""
import datetime as dt
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIDEOS = ROOT.parent / "ierlip-video-diario" / "ierlip-video-diario" / "config" / "topics.json"
DIAS = ["lun", "mar", "mie", "jue", "vie", "sab", "dom"]

desde, hasta = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else sys.argv[1]
d0, d1 = dt.date.fromisoformat(desde), dt.date.fromisoformat(hasta)
dest = ROOT / "carga" / f"{desde}_{hasta}"
if dest.exists():
    shutil.rmtree(dest)
dest.mkdir(parents=True)

videos = {}
if VIDEOS.exists():
    videos = json.loads(VIDEOS.read_text(encoding="utf-8")).get("calendario", {})


def hora(iso):
    return iso[11:16]


md = [f"# Paquete de carga · {desde} al {hasta}", "",
      "Nada de esto está programado todavía. Se programa recién con el OK de Seba.", "",
      "- **Zoho Social:** carruseles del feed (y historias sin sticker, si el plan gratis lo permite).",
      "- **Celular:** historias con sticker nativo, a la hora indicada.",
      "- **TikTok Studio** (desde la compu): videos del proyecto hermano, cuando llegan por Telegram.", ""]
pendientes = []

d = d0
while d <= d1:
    f = d.isoformat()
    dia = DIAS[d.weekday()]
    src = ROOT / "output" / f
    if not (src / "meta.json").exists():
        md += [f"## {f} ({dia})", "", "Sin piezas generadas.", ""]
        d += dt.timedelta(days=1)
        continue
    meta = json.loads((src / "meta.json").read_text(encoding="utf-8"))
    carpeta = dest / f"{f}_{dia}"
    carpeta.mkdir()
    placas = sorted(src.glob("placa*.png"), key=lambda p: int(p.stem.split("-")[1]) if "-" in p.stem else 0)
    for i, p in enumerate(placas, 1):
        shutil.copy(p, carpeta / f"1-feed-{i}.png")
    shutil.copy(src / "caption.txt", carpeta / "caption.txt")
    shutil.copy(src / "historia.png", carpeta / "2-historia.png")
    animada = src / "historia-animada.mp4"
    if animada.exists():
        shutil.copy(animada, carpeta / "3-historia-animada.mp4")

    md += [f"## {f} ({dia}) · {meta['pilar']}: {meta['titulo']}", "", f"Carpeta: `{carpeta.name}/`", "",
           "| ✓ | Hora | Dónde | Qué | Archivos |", "|---|---|---|---|---|"]
    st = meta.get("sticker_nativo")
    if st:
        md.append(f"| ☐ | {hora(meta['publicar_historia'])} | Celular (Instagram) | Historia con sticker: {st} | `2-historia.png` |")
    else:
        md.append(f"| ☐ | {hora(meta['publicar_historia'])} | Zoho Social (o celular) | Historia, sin sticker | `2-historia.png` |")
    if animada.exists():
        md.append(f"| ☐ | {hora(meta['publicar_historia'])} + 30 min | Zoho Social (o celular) | Historia animada con sonido | `3-historia-animada.mp4` |")
    tipo = "Carrusel" if len(placas) > 1 else "Placa"
    md.append(f"| ☐ | {hora(meta['publicar_placa'])} | Zoho Social → Instagram | {tipo} ({len(placas)} imágenes) + caption | `1-feed-*.png` + `caption.txt` |")
    v = videos.get(f)
    if v:
        redes = " y ".join({"tiktok": "TikTok", "instagram": "Instagram"}.get(r, r) for r in v.get("redes", []))
        md.append(f"| ☐ | {hora(v['publicar'])} | TikTok Studio + Zoho (Reel) | Video «{v['id']}» ({redes}), llega por Telegram | (del proyecto de videos) |")
    md += ["", "**Caption**", "", "```", (src / "caption.txt").read_text(encoding="utf-8").strip(), "```", ""]
    if meta.get("needs_review"):
        md += ["**Verificar antes de programar**", ""] + [f"- [ ] {n}" for n in meta["needs_review"]] + [""]
        pendientes += [f"{f}: {n}" for n in meta["needs_review"]]
    d += dt.timedelta(days=1)

md += ["## Resumen: verificar antes de programar", ""] + ([f"- [ ] {p}" for p in pendientes] or ["- Nada pendiente."]) + [""]
(dest / "CARGA.md").write_text("\n".join(md), encoding="utf-8")
print("OK", dest.relative_to(ROOT))
