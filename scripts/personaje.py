"""Personaje 3D del reel: elige el gesto de cada escena, recorta los clips (fondo verde) y anota qué cuadro va en cada
momento. Uso:  python3 scripts/personaje.py <datos.json> <carpeta>
Lee el datos.json de scripts/voz-reel.py, deja los PNG recortados en <carpeta>/personaje/ y agrega PERSONAJE al JSON.
Los clips (assets/personaje/A-D.mp4, 1280x720 a 24 cps) no tienen audio: no se genera video nuevo para cada reel.
Requiere: numpy, scipy, pillow y ffmpeg.
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
FPS_CLIP = 24
# gesto: tramos (clip, desde, hasta) en segundos; si la escena dura más que un tramo, sigue con el siguiente.
GESTOS = {
    "serio":    [("B", 0.0, 1.9), ("B", 1.85, 5.5)],
    "advierte": [("B", 1.85, 5.5), ("B", 4.8, 8.0)],
    "señala":   [("B", 7.5, 10.0), ("B", 6.0, 8.0)],
    "sorpresa": [("D", 0.0, 2.4), ("C", 4.0, 6.6)],
    "explica":  [("A", 0.0, 6.5), ("C", 1.7, 5.9)],
    "pregunta": [("C", 4.0, 6.65), ("C", 0.0, 4.0)],
    "pulgar":   [("D", 6.5, 10.0), ("A", 8.0, 10.0)],
}
POR_TIPO = {"texto": "explica", "ticket": "explica", "cifra": "sorpresa", "lista": "advierte", "cierre": "pulgar", "barras": "explica"}

def recortar(src, dst):
    a = np.array(Image.open(src).convert("RGB")).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    al = np.clip((80 - (g - np.maximum(r, b))) / 55, 0, 1)
    lab, num = ndimage.label(al > .5)
    tam = ndimage.sum(al > .5, lab, range(1, num + 1))
    al *= ndimage.binary_dilation(np.isin(lab, np.where(tam > 1500)[0] + 1), iterations=3)
    mask = al > .5
    al = ndimage.gaussian_filter(ndimage.grey_erosion(al, size=(3, 3)), .6)
    rgb = np.dstack([r, np.minimum(g, np.maximum(r, b) + 4), b]).astype(np.uint8)
    im = Image.fromarray(np.dstack([rgb, (al * 255).astype(np.uint8)]), "RGBA")
    pad = 24                                   # borde blanco tipo sticker (no abajo)
    borde = np.clip(11 - ndimage.distance_transform_edt(np.pad(al, ((pad, 0), (pad, pad))) < .5), 0, 1)
    st = Image.new("RGBA", (im.width + 2 * pad, im.height + pad), (255, 255, 255, 0))
    st.putalpha(Image.fromarray((borde * 255).astype(np.uint8)))
    st.alpha_composite(im, (pad, pad))
    st.save(dst, compress_level=1)
    top = np.where(mask.any(1))[0][0]
    return float(np.where(mask[top:top + 70])[1].mean() + pad)   # centro de la cara

def main(datos_f, carpeta):
    datos = json.load(open(datos_f, encoding="utf-8"))
    salida = Path(carpeta).resolve() / "personaje"
    fuente = salida / "src"
    for c in "ABCD":
        (fuente / c).mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / "assets/personaje" / f"{c}.mp4"),
                        str(fuente / c / "%03d.png")], check=True)
    usados = {}                                # gesto -> próximo tramo, para no repetir el mismo arranque
    cache, cuadros, escenas = {}, [], []
    total = int(round(datos["total"] * 30))
    for i, (e, (t0, d)) in enumerate(zip(datos["escenas"], datos["TIEMPOS"])):
        gesto = e.get("gesto") or POR_TIPO.get(e.get("tipo"), "explica")
        if gesto not in GESTOS:
            sys.exit(f"Gesto desconocido: {gesto}. Opciones: {', '.join(GESTOS)}")
        if e.get("tipo") == "barras" and escenas:    # la transición sigue con el plano anterior
            gesto = escenas[-1]["gesto"]
        k = usados.get(gesto, 0); usados[gesto] = k + 1
        tramos = GESTOS[gesto][k % len(GESTOS[gesto]):] + GESTOS[gesto][:k % len(GESTOS[gesto])]
        lista = [(c, f) for c, a, b in tramos for f in range(int(a * FPS_CLIP) + 1, min(240, int(b * FPS_CLIP)) + 1)]
        fin = total if i == len(datos["escenas"]) - 1 else int(round((t0 + d) * 30))
        caras, ini = [], len(cuadros)
        for n in range(ini, fin):
            j = int((n - ini) / 30 * FPS_CLIP)
            if gesto == "pulgar":                    # termina quieto con el pulgar arriba
                j = min(j, len(lista) - 1)
            c, f = lista[j % len(lista)]
            nombre = f"{c}{f:03d}"
            if nombre not in cache:
                cache[nombre] = recortar(fuente / c / f"{f:03d}.png", salida / f"{nombre}.png")
            caras.append(cache[nombre]); cuadros.append([nombre, i])
        escenas.append({"gesto": gesto, "cara": float(np.median(caras)) if caras else 664.0, "desde": ini / 30})
    datos["PERSONAJE"] = {"base": salida.as_uri() + "/", "cuadros": cuadros, "escenas": escenas}
    json.dump(datos, open(datos_f, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"Personaje: {len(cache)} cuadros recortados, gestos: {[x['gesto'] for x in escenas]}")

if __name__ == "__main__":
    main(*sys.argv[1:3])
