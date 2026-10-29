---
name: contenido-diario
description: Produce la placa (feed 1:1, estilo Papel crema) y la historia (9:16, estilo Papel oscuro) del día para @estudioierlip a partir de config/calendario-<mes>.json, las renderiza a PNG y prepara caption + checklist de verificación. Usar con /contenido-diario [YYYY-MM-DD] o cuando Seba pida "la placa de hoy", "las historias de la semana", etc.
---

# contenido-diario

Producís **una placa (carrusel o simple) y una historia** para el día pedido (por defecto hoy, ART). No publicás nada.

## 1. Contexto (leer siempre)
1. `CLAUDE.md`, `docs/linea-editorial.md` y `docs/estilos.md`.
2. `config/calendario-noviembre-2026.json` (o el del mes que corresponda): entrada de la fecha, `pilares`, `historias_por_dia` y `horarios`.
3. Si la fecha no está en el calendario, elegí un tema del pilar del día que no se haya usado en los últimos 60 días (mirá `output/*/meta.json`).

## 2. Verificar antes de escribir
- Por cada ítem de `verificar`, buscá en fuentes oficiales (arca.gob.ar, arba.gov.ar, agip.gob.ar, ca.gov.ar, boletinoficial.gob.ar) y anotá las URLs consultadas.
- Si un dato no se puede confirmar, reformulalo sin el dato o sacalo, y anotalo en `needs_review`.
- Para cada fecha que aparezca, comprobá el día de la semana con código.

## 3. Escribir las especificaciones
Creá `piezas/<fecha>/placa.json` y `piezas/<fecha>/historia.json` siguiendo el formato de `scripts/render.mjs`.

**Placa (template `placa-papel`), carrusel de 4 a 6 slides:**
- Slide 1, `portada`: eyebrow manuscrito, título de 2 o 3 líneas con la palabra clave entre `*asteriscos*` y bajada ("lo importante, sin vueltas").
- Slides 2 y 3, `items`: 2 a 4 ítems por slide (`t` máximo 6 palabras, `d` máximo 18 palabras). Usá `desde` para continuar la numeración.
- Opcional, `tip`: el error más común.
- Última, `cierre`.
- Placa simple: una sola slide `items` con título y hasta 3 ítems.

**Historia (template `historia-papel`, azul marino con tarjetas de papel):** según `historias_por_dia`. Eyebrow manuscrito en minúscula ("recordatorio · 05/11/2026"), título de máximo 3 líneas y hasta 4 tarjetas `{t, d}` (`t` máximo 5 palabras, `d` máximo 20). Llená la historia: nada de fondo vacío. Con sticker nativo, máximo 2 tarjetas. Si lleva un sticker nativo, poné `sticker_zone: true` y anotá en `meta.json` cuál pegar (encuesta, cuestionario, cuenta regresiva, preguntas o link a WhatsApp https://wa.me/541149922513).

**Debate (solo si Seba lo pide, o los martes como complemento del video):** template `placa-debate`, siguiendo la línea "debate con criterio".

**Fuentes:** nunca van en la pieza. Van en `meta.json → sources` y cada dato fiscal se verifica antes de escribirlo.

**Historia animada (opcional, si Seba la pide):** `templates/historia-animada.html` + `python scripts/audio-historia.py` + `node scripts/render-animada.mjs <html> <mp4> 12 30 assets/audio/historia-animada.wav`. Siempre con sonido (música de fondo tranqui y un efecto por movimiento); si cambian los tiempos de la animación, ajustá `CUES` en el script de audio.

## 4. Renderizar y revisar
```bash
node scripts/render.mjs piezas/<fecha>/placa.json piezas/<fecha>/historia.json
```
Mirá cada PNG con la herramienta Read como lo haría Seba. Revisá que se lea todo, que no haya texto cortado, que la palabra clave esté resaltada, que la historia respete las zonas libres y que el contador del carrusel esté bien. Si un texto no entra, **acortá el texto**: no cambies el tamaño ni el layout. Hacé como máximo 2 vueltas de corrección.

## 5. Entregar
En `output/<fecha>/`:
- PNGs: `placa-1.png`… y `historia.png`.
- `caption.txt`: gancho con emoji, 2 a 4 líneas de valor, "Guardalo 📌", "Escribinos por WhatsApp: +54 11 4992-2513", @estudioierlip y 5 a 8 hashtags (#EstudioIERLIP siempre).
- `meta.json`: `{fecha, pilar, titulo, publicar_placa, publicar_historia, sticker_nativo, sources[], needs_review[], notes}`. Los horarios de publicación salen de `config.horarios`, en ISO con -03:00.

Terminá con un resumen de 3 líneas: qué se hizo, qué hay que verificar y qué sticker pegar.

## 6. Paquete de carga (Zoho Social + TikTok Studio)
Cuando la semana esté aprobada, corré `python scripts/paquete-carga.py <desde> <hasta>` y mostrale a Seba `carga/<desde>_<hasta>/CARGA.md`. Si Seba pide que cargues vos, hacelo desde Chrome en Zoho Social (Instagram) y TikTok Studio, **pidiendo OK antes de cada tanda** y nunca con publicación inmediata. Las historias con sticker nativo se suben a mano desde el celular.
