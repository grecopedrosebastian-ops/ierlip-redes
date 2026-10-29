---
name: arca-diario
description: Revisa las novedades oficiales de ARCA del día (lo mismo que ARCA publica en su Instagram) y arma una placa con el estilo de @estudioierlip, con la misma información, redacción propia y un juego de palabras. Lo llama el workflow arca-diario; no publica ni manda nada.
---

# arca-diario

Corrés sin supervisión dentro de GitHub Actions: **no hagas preguntas**, decidí con criterio y anotá lo dudoso. No uses git, no mandes mensajes y no busques tokens: el render y el envío los hace el workflow.

## 1. Contexto
1. `CLAUDE.md`, `docs/linea-editorial.md` y `docs/estilos.md`.
2. `state/arca-vistas.json`: lista de novedades que ya se usaron (`{"vistas": [{"id", "titulo", "fecha"}]}`). Si no existe, empezá vacía.
3. Ejemplos aprobados del estilo: `piezas/2026-11-09/placa.json` (carrusel) y `output/2026-11-09/caption.txt`.

## 2. Buscar las novedades
Con WebSearch/WebFetch, revisá lo publicado por ARCA en los **últimos 3 días** (hoy es la fecha del sistema, en Buenos Aires):
- Novedades de ARCA: `https://servicioscf.afip.gob.ar/publico/sitio/contenido/novedad/listado.aspx` y la portada de `https://www.arca.gob.ar/`.
- Boletín Oficial, primera sección: resoluciones generales de ARCA (`https://www.boletinoficial.gob.ar/seccion/primera`).
- El Instagram de ARCA no se puede leer de forma automática: no lo intentes.

Elegí **una sola novedad**: la que más le sirva a monotributistas, autónomos, empleadores o pymes (vencimientos, prórrogas, cambios de trámites, servicios nuevos, regímenes). Descartá las que ya estén en `arca-vistas.json`, las internas o aduaneras de nicho y las que no le cambian nada al contribuyente común.

Si no hay ninguna novedad útil y nueva, creá solo `bot/salida/sin-novedades.txt` con una línea explicando por qué, y terminá.

## 3. Verificar
- Todo dato (fechas, montos, alícuotas, a quién alcanza, desde cuándo rige) se confirma en la **fuente oficial** de la novedad (texto de la RG, página de ARCA). Comprobá con código el día de la semana de cada fecha.
- Lo que no puedas confirmar: reformulalo sin el dato o sacalo, y anotalo en `needs_review`.

## 4. Escribir con nuestro estilo
- **Misma información, redacción propia.** No copies frases ni el diseño de ARCA, y no uses sus imágenes ni su logo. Explicalo como lo explicaría el estudio: claro, cercano, con voseo rioplatense.
- **Juego de palabras:** el título de la portada lleva un juego de palabras o un giro ingenioso relacionado con el tema (por ejemplo: "*Factura* electrónica: se te terminó el talonario", "Ganancias: *simple* como debería ser"), sin perder claridad. Marcá la palabra clave entre `*asteriscos*`. Nada de chistes sobre ARCA, sus empleados o la política.
- Template `placa-papel`, carrusel de 4 slides, con `"out": "bot/salida/pieza"`:
  1. `portada`: eyebrow manuscrito en minúscula (por ejemplo "novedad ARCA · 29/10/2026"), título con el juego de palabras y bajada "lo importante, sin vueltas".
  2. `items`: 2 a 4 ítems con qué cambia, a quién le toca, desde cuándo y qué hacer (`t` máximo 6 palabras, `d` máximo 18).
  3. `tip`: el error más probable o el dato clave. El eyebrow no puede ser "ojo".
  4. `cierre`.
- Las fuentes **nunca** van en la pieza.

## 5. Entregar en `bot/salida/`
- `spec.json`: la especificación para `scripts/render.mjs`.
- `texto.txt`: el caption: gancho con emoji, 2 a 4 líneas de valor, "Guardalo para cuando lo necesites 📌", "Escribinos por WhatsApp: +54 11 4992-2513", "@estudioierlip · estudioierlip.com" y 5 a 8 hashtags con #EstudioIERLIP.
- `meta.json`: `{"resumen": "Novedad ARCA: <tema en una línea>", "sources": [urls oficiales], "needs_review": [...]}`.
- Agregá la novedad usada a `state/arca-vistas.json` (`id` = URL o número de la norma, `titulo`, `fecha` de hoy), conservando las anteriores.

Antes de terminar, revisá que `spec.json` sea JSON válido y que los textos respeten los largos.
