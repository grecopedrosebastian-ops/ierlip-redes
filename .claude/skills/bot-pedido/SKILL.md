---
name: bot-pedido
description: Arma la pieza que Seba pidió por Telegram (/placa, /historia, /aviso, /encuesta o /cambiar) a partir de bot/pedido.json y deja la especificación, el texto y la verificación en bot/salida/. Lo llama el workflow telegram-bot; no publica ni manda nada.
---

# bot-pedido

Corrés sin supervisión dentro de GitHub Actions: **no hagas preguntas**, decidí con criterio y anotá lo dudoso. No uses git, no mandes mensajes y no busques tokens: el render y el envío los hace el workflow después.

## 1. Contexto (leer siempre)
1. `bot/pedido.json`: `comando`, `pedido` (el texto de Seba) y, si es `/cambiar`, `anterior` (la pieza previa: `comando`, `pedido`, `spec`, `texto`, `meta`).
2. `CLAUDE.md`, `docs/linea-editorial.md` y `docs/estilos.md`.
3. Un ejemplo aprobado del mismo tipo para copiar el tono y la estructura: `piezas/2026-11-09/placa.json` (carrusel), `piezas/2026-11-08/historia.json` (historia) y el `output/2026-11-09/caption.txt` correspondiente.

## 2. Verificar antes de escribir
- Todo dato fiscal (fechas, montos, alícuotas, procedimientos, nombres de servicios) se verifica con WebSearch/WebFetch en **fuentes oficiales**: arca.gob.ar o afip.gob.ar, arba.gov.ar, agip.gob.ar, boletinoficial.gob.ar, argentina.gob.ar. Los medios y blogs sirven solo como pista.
- Lo que no puedas confirmar: reformulalo sin el dato o sacalo, y anotalo en `needs_review`.
- Comprobá con código el día de la semana de cada fecha que menciones.
- Nunca inventes cifras ni estadísticas. Nada de partidos, políticos ni marcas o personas reales.
- Las fuentes **nunca** van en la pieza: solo en `meta.json → sources`.

## 3. Qué armar según el comando
Todas las especificaciones siguen el formato de `scripts/render.mjs`, con `"out": "bot/salida/pieza"`.

- **/placa**: template `placa-papel`, carrusel de 4 slides: `portada` (eyebrow manuscrito en minúscula, título con la palabra clave entre `*asteriscos*`, bajada "lo importante, sin vueltas"), `items` (2 a 4 ítems: `t` máximo 6 palabras, `d` máximo 18), `tip` (el error más común o el dato clave) y `cierre`. En los `tip`, el eyebrow no puede ser "ojo" (la tarjeta ya dice "ojo"). `texto.txt` = caption: gancho con emoji, 2 a 4 líneas de valor, "Guardalo para cuando lo necesites 📌", "Escribinos por WhatsApp: +54 11 4992-2513", "@estudioierlip · estudioierlip.com" y 5 a 8 hashtags con #EstudioIERLIP.
- **/historia**: template `historia-papel`, una slide: eyebrow manuscrito en minúscula, título de máximo 3 líneas con `*palabra clave*` y 3 o 4 tarjetas `{t, d}` (`t` máximo 5 palabras, `d` máximo 20). La historia tiene que verse llena. `texto.txt` = una línea con la hora sugerida (09:00) y, si corresponde, qué sticker nativo pegar.
- **/aviso**: template `placa-papel`, **una sola slide** `items` con eyebrow "aviso importante" o similar, título urgente con `*palabra clave*` y 2 o 3 ítems con lo esencial (qué pasa, desde cuándo, qué hacer). `texto.txt` = mensaje listo para WhatsApp a clientes: saludo corto, el aviso en 3 a 5 líneas claras, qué tienen que hacer y "Cualquier duda, escribinos. Estudio IERLIP".
- **/encuesta**: template `historia-papel` con `sticker_zone: true`, título = la pregunta (con `*palabra clave*`), `texto` "Votá acá abajo" y como máximo 1 tarjeta de contexto. Si el pedido trae `pregunta | opción 1 | opción 2`, usá exactamente eso; si trae solo un tema o viene vacío, proponé una pregunta sobre un tema de ARCA, ARBA o AGIP con 2 opciones cortas. `texto.txt` = "Pegá el sticker de ENCUESTA con: <opción 1> / <opción 2>".
- **/cambiar**: partí de `anterior.spec` y `anterior.texto`, aplicá **solo** el cambio pedido y mantené el mismo template y estructura salvo que el cambio diga lo contrario. Si el cambio agrega o modifica datos fiscales, verificalos igual que arriba.

## 4. Entregar (exactamente estos 3 archivos en `bot/salida/`)
- `spec.json`: la especificación para `scripts/render.mjs`.
- `texto.txt`: el texto según el comando.
- `meta.json`: `{"resumen": "<una línea: qué pieza es y sobre qué>", "sources": [urls oficiales], "needs_review": [lo que no se pudo confirmar]}`.

Antes de terminar, revisá que `spec.json` sea JSON válido, que use el template correcto y que los textos respeten los largos máximos (si no entran, acortá el texto, no cambies el layout).
