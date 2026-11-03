---
name: paquete-diario
description: Arma el paquete del día para @estudioierlip: 2 carruseles para el feed (1:1, estilo Papel con fondos y armados que van rotando) y 1 reel con cortes y música, todo verificado en fuentes oficiales. Lo llama el workflow paquete-diario todos los días; no publica ni manda nada.
---

# paquete-diario

Corrés sin supervisión dentro de GitHub Actions: **no hagas preguntas**, decidí con criterio y anotá lo dudoso. No uses git, no mandes mensajes y no busques tokens. El render y el envío por Telegram los hace el workflow.

Esto es **aparte** de lo que ya se carga solo (la placa del calendario en Metricool y la historia diaria): no repitas esos temas.

## 1. Contexto
1. `CLAUDE.md`, `docs/linea-editorial.md`, `docs/estilos.md` y `docs/referentes.md`.
2. `config/calendario-noviembre-2026.json` (o el del mes que corresponda): la entrada de hoy y de mañana (fecha del sistema, Buenos Aires). Esos temas **no** van en el paquete.
3. `state/paquete-vistas.json` (`{"dias": [...]}`, si existe): lo que salió los días anteriores (temas y diseño). Y `state/arca-vistas.json`: novedades de ARCA ya usadas.
4. Ejemplo del estilo de los carruseles: `piezas/2026-11-09/placa.json` y `output/2026-11-09/caption.txt`.

## 2. Elegir los 3 temas (distintos entre sí y a los de los últimos 30 días)
- **Placa 1, actualidad:** una novedad de ARCA de los últimos 3 días que no esté en `arca-vistas.json`. Buscala y elegila con los pasos 2 y 3 de `.claude/skills/arca-diario/SKILL.md`. Si no hay ninguna útil, usá una novedad de ARBA o AGIP, o el próximo vencimiento importante (de 3 a 10 días).
- **Placa 2, servicio:** algo que el contribuyente busca y guarda. Las ideas salen de `docs/referentes.md`: la pregunta frecuente al estilo de las guías de ARCA ("¿Pagaste dos veces…?", "¿Vas a inscribirte…?"), mito o realidad, cómo hacer un trámite paso a paso, el error típico, o un dato del mes (feriados, cierres bancarios). Rotá el público: monotributo, autónomos, empleadores, pymes e Ingresos Brutos.
- **Reel:** un chequeo o trámite práctico en 3 pasos (por ejemplo: "¿Cómo estás con ARCA?", "Antes de facturar", "Si contratás a alguien"). Tiene que ser distinto de las dos placas.

## 3. Verificar
Todo dato (fechas, montos, alícuotas, a quién alcanza, rutas de los servicios) se confirma con WebSearch/WebFetch en fuentes oficiales: arca.gob.ar o afip.gob.ar, boletinoficial.gob.ar, arba.gov.ar, agip.gob.ar o argentina.gob.ar. Comprobá con código el día de la semana de cada fecha. Lo que no puedas confirmar no va: reformulalo sin el dato o cambiá de tema, y anotalo en `needs_review`.

## 4. Diseño: que no salgan todas iguales
Se mantiene el estilo Papel (template `placa-papel`), pero cada día cambia.
- **`tema` de la spec:** "crema", "azul" o "violeta".
  - Las 2 placas del día van con temas distintos y al menos una no es crema, porque la placa de Metricool ya es crema.
  - No repitas la misma pareja del día anterior.
- **Portada:** "portada" (título con juego de palabras), "numero" (un número o fecha gigante: "20/11", "45 días", "3 errores") o "pregunta" (la duda del contribuyente con la respuesta corta en una nota pegada).
  - Las dos placas del día usan portadas distintas.
  - Ninguna repite la portada que tuvo la misma placa ayer.
- **Interior:** combiná "items", "versus" (mito o realidad), "tip" y siempre "cierre" al final.
  - Cada carrusel tiene de 3 a 5 slides.
  - Por día, al menos un carrusel lleva "versus" o una portada "numero".
- **Largos:**
  - `numero`: hasta 7 caracteres.
  - `titulo`: hasta 60 caracteres.
  - `respuesta`: hasta 45 caracteres.
  - Items: `t` máximo 6 palabras y `d` máximo 18; de 2 a 4 ítems.
  - `mito` y `realidad`: hasta 90 caracteres cada uno.
  - `tip`: `texto` hasta 150 caracteres. El eyebrow no puede ser "ojo", porque la tarjeta ya lo dice.
- **Eyebrows:** manuscritos y en minúscula. Marcá la palabra clave con `*asteriscos*`.
- **Nunca:** fuentes en la pieza, ni textos, imágenes o logo de ARCA.

## 5. Reel (`templates/reel-cortes.html`, 8 escenas de 2,4 s con música)
Es un objeto con estas claves:
- `gancho`: hasta 26 caracteres. Va en MAYÚSCULAS en el video y es una pregunta o frase corta, con la palabra clave entre `*asteriscos*`.
- `eyebrow`: hasta 26 caracteres (por ejemplo "MONOTRIBUTO · PYMES").
- `bajada`: hasta 34 caracteres, con una palabra entre `*asteriscos*`.
- `intro`: `{"arriba"`, hasta 18 caracteres (por ejemplo "UN CHEQUEO EN"); `"numero": "3"`; `"abajo"`, hasta 8 caracteres (por ejemplo "pasos")`}`.
- `pasos`: exactamente 3, cada uno `{"etiqueta"`, hasta 20 caracteres; `"texto"`, hasta 44, accionable y con voseo; `"nota"`, opcional, hasta 40, como mucho en uno de los pasos`}`.
- `variante`: 1, 2 o 3 (orden de colores y música). Rotá respecto del último reel de `paquete-vistas.json`.

## 6. Entregar en `bot/salida/`
- `placa1/spec.json` y `placa2/spec.json`: la spec para `scripts/render.mjs`, con `"template": "placa-papel"`, `"tema"` y `"out": "bot/salida/placa1/pieza"` (o `placa2`).
- `placa1/texto.txt` y `placa2/texto.txt`: el caption.
  - Primera línea: emoji + **Organismo · Tema**.
  - Después, de 2 a 4 líneas de valor, "Guardalo para cuando lo necesites 📌", "Escribinos por WhatsApp: +54 11 4992-2513", "@estudioierlip · estudioierlip.com" y de 5 a 8 hashtags con #EstudioIERLIP.
  - Al final, una línea con la hora sugerida: placa 1 a las 10:00 (11:00 los fines de semana) y placa 2 a las 15:00.
- `reel/reel.json` y `reel/texto.txt`: el caption del reel (gancho, 2 líneas, WhatsApp, hashtags).
  - Hora sugerida: 18:00.
  - Los lunes y jueves, a las 20:00, porque a las 18:00 sale el video de vencimientos.
- `meta.json`: `{"resumen": {"placa1": "...", "placa2": "...", "reel": "..."}, "sources": [urls oficiales], "needs_review": [...]}`.
- Agregá el día a `state/paquete-vistas.json`, conservando los anteriores, con este formato:
  ```json
  {"fecha": "...", "placa1": {"tema": "...", "fondo": "...", "portada": "..."}, "placa2": {"tema": "...", "fondo": "...", "portada": "..."}, "reel": {"tema": "...", "variante": 1}}
  ```
- Si la placa 1 es una novedad de ARCA, sumala también a `state/arca-vistas.json`.

Antes de terminar, revisá que todos los JSON sean válidos, que ningún texto supere su largo y que los dos carruseles se vean distintos entre sí.
