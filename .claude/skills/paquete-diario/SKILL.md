---
name: paquete-diario
description: Arma la publicación del día para @estudioierlip, una sola por día y alternada: un reel "Lo que te diría tu contador" (lun, mié, vie y dom: un caso con números para emprendedores y pymes, con voz en off) o un carrusel para el feed (mar, jue y sáb: 1:1, estilo Papel). Los jueves suma un reel con voz solo para TikTok (Seba lo sube a mano). Todo verificado en fuentes oficiales. Lo llama el workflow paquete-diario todos los días; no publica ni manda nada.
---

# paquete-diario

**Fecha del paquete:** si te pasan una fecha (`/paquete-diario AAAA-MM-DD`), armás el paquete para ESA fecha (el
workflow corre la noche anterior): el día de la semana, la tabla de la sección 2, el calendario y la hora sugerida son
los de esa fecha. Sin argumento, es la fecha de hoy en Buenos Aires.

Corrés sin supervisión dentro de GitHub Actions: **no hagas preguntas**, decidí con criterio y anotá lo dudoso. No uses git, no mandes mensajes y no busques tokens. El render y el envío por Telegram los hace el workflow.

No repitas los temas del calendario del mes (la placa y la historia de `config/calendario-*.json`).

## 1. Contexto
1. `CLAUDE.md`, `docs/linea-editorial.md`, `docs/estilos.md` y `docs/referentes.md`.
2. `config/calendario-noviembre-2026.json` (o el del mes que corresponda): la entrada de la fecha del paquete y la del día siguiente. Esos temas **no** van en el paquete.
3. `state/paquete-vistas.json` (`{"dias": [...]}`, si existe): lo que salió los días anteriores (temas y diseño). Y `state/arca-vistas.json`: novedades de ARCA ya usadas.
4. Ejemplo del estilo de los carruseles: `piezas/2026-11-09/placa.json` y `output/2026-11-09/caption.txt`.

## 2. Qué toca (según la fecha del paquete) y elegir el tema
Desde el 19/11/2026 sale **una sola publicación por día**, alternando formato (decisión de Seba tras la auditoría: con
pocos seguidores, varias publicaciones por día se reparten el alcance; los reels son lo que más llega a gente nueva).

| Día | Qué armás | Línea |
|---|---|---|
| Lun | Reel | ¿Te conviene? |
| Mar | Carrusel (`placa1`) | actualidad o servicio |
| Mié | Reel | ¿Garpa? (un negocio, o un emprendimiento desde casa: alternan semana a semana) |
| Jue | Carrusel (`placa1`) + **reel solo para TikTok** | carrusel: actualidad o servicio · reel: Pagar tarde sale caro |
| Vie | Reel | Pyme: ¿cuánto cuesta de verdad? |
| Sáb | Carrusel (`placa1`) | actualidad o servicio |
| Dom | Reel | Consejo con números o Primeros pasos (alternan) |

Para saber qué toca en las líneas que alternan, mirá el último día igual en `state/paquete-vistas.json`.
El tema no puede repetir los de los últimos 30 días.

- **Carrusel:** si hay una novedad fuerte (opción "actualidad", abajo), va esa; si no, uno de "servicio". Va en `placa1/`.
- **Actualidad:** una novedad de ARCA de los últimos 3 días que no esté en `arca-vistas.json`. Buscala y elegila con los pasos 2 y 3 de `.claude/skills/arca-diario/SKILL.md`. Si no hay ninguna útil, usá una novedad de ARBA o AGIP, o el próximo vencimiento importante (de 3 a 10 días).
- **Servicio:** algo que el contribuyente busca y guarda. Las ideas salen de `docs/referentes.md`: la pregunta frecuente al estilo de las guías de ARCA ("¿Pagaste dos veces…?", "¿Vas a inscribirte…?"), mito o realidad, cómo hacer un trámite paso a paso, el error típico, o un dato del mes (feriados, cierres bancarios). Rotá el público: monotributo, autónomos, empleadores, pymes e Ingresos Brutos.
- **Reel "Lo que te diría tu contador":** el caso con números de la línea del día (tabla de arriba). Todo el detalle está
  en `reel-explicado.md`, en esta misma carpeta: leelo entero (su tabla de líneas quedó como lista de ideas).
- **Reel solo para TikTok (los jueves):** ver la sección 7.

## 3. Verificar
Todo dato (fechas, montos, alícuotas, a quién alcanza, rutas de los servicios) se confirma con WebSearch/WebFetch en fuentes oficiales: arca.gob.ar o afip.gob.ar, boletinoficial.gob.ar, arba.gov.ar, agip.gob.ar o argentina.gob.ar. Comprobá con código el día de la semana de cada fecha. Lo que no puedas confirmar no va: reformulalo sin el dato o cambiá de tema, y anotalo en `needs_review`.

## 4. Diseño: que no salgan todas iguales
Se mantiene el estilo Papel (template `placa-papel`), pero cada día cambia.
- **`tema` de la spec:** "crema", "azul" o "violeta".
  - No repitas el `tema` ni la portada del último carrusel, y al menos 1 de cada 3 carruseles no es crema.
- **Portada:** "portada" (título con juego de palabras), "numero" (un número o fecha gigante: "20/11", "45 días", "3 errores") o "pregunta" (la duda del contribuyente con la respuesta corta en una nota pegada).
- **Interior:** combiná "items", "versus" (mito o realidad), "tip" y siempre "cierre" al final.
  - Cada carrusel tiene de 3 a 5 slides.
  - Alterná: si el último carrusel no llevó "versus" ni portada "numero", este lleva uno de los dos.
- **Largos:**
  - `numero`: hasta 7 caracteres.
  - `titulo`: hasta 60 caracteres.
  - `respuesta`: hasta 45 caracteres.
  - Items: `t` máximo 6 palabras y `d` máximo 18; de 2 a 4 ítems.
  - `mito` y `realidad`: hasta 90 caracteres cada uno.
  - `tip`: `texto` hasta 150 caracteres. El eyebrow no puede ser "ojo", porque la tarjeta ya lo dice.
- **Eyebrows:** manuscritos y en minúscula. Marcá la palabra clave con `*asteriscos*`.
- **Nunca:** fuentes en la pieza, ni textos, imágenes o logo de ARCA.

## 5. Reel "Lo que te diría tu contador"
Seguí `reel-explicado.md` (líneas por día, reglas de los números, estructura, voz y formato del JSON). El workflow genera
la voz, la música y el video a partir de tu JSON.

## 6. Entregar en `bot/salida/`
Solo lo que toca hoy (no dejes carpetas con archivos a medias):
- **Días de carrusel:** `placa1/spec.json` (spec para `scripts/render.mjs`, con `"template": "placa-papel"`, `"tema"` y `"out": "bot/salida/placa1/pieza"`) y `placa1/texto.txt` (el caption):
  - Primera línea: emoji + **Organismo · Tema**.
  - Después, de 2 a 4 líneas de valor.
  - **Una pregunta para comentar**, concreta, fácil de contestar y del tema: "¿Ya te pasó? Contanos 👇", "¿Vos lo pagás
    por débito o a mano? 👇", "¿Cuál de las 3 no sabías?". Nunca un "¿Qué opinás?" a secas.
  - "Guardalo y mandáselo a quien lo necesite 📌", "Escribinos por WhatsApp: +54 11 4992-2513", "@estudioierlip · estudioierlip.com" y de 5 a 8 hashtags con #EstudioIERLIP.
  - Al final, una línea con la hora sugerida: 12:00 (11:00 los sábados).
- **Días de reel:** `reel/explicado.json` y `reel/texto.txt`, con el formato de `reel-explicado.md` (también con la
  pregunta para comentar). Hora sugerida: 18:00; los lunes, 20:00, porque a las 18:00 sale el video de vencimientos.
- **Jueves:** además, el reel para TikTok en `reel/` (sección 7).
- `meta.json`: `{"resumen": {"placa1": "...", "reel": "..."}, "reel_solo_tiktok": true|false, "sources": [urls oficiales], "needs_review": [...]}` (solo las claves de lo que armaste).
- Agregá el día a `state/paquete-vistas.json`, conservando los anteriores, con este formato:
  ```json
  {"fecha": "...", "placa1": {"tema": "...", "fondo": "...", "portada": "..."}, "reel": {"tema": "...", "linea": "¿Garpa?"}}
  ```
- Si la placa 1 es una novedad de ARCA, sumala también a `state/arca-vistas.json`.

## 7. Reel solo para TikTok (los jueves)
Desde el 19/11 (Seba no graba videos a cámara por ahora): los jueves, además del carrusel, armás un reel "Lo que te
diría tu contador" de la línea **Pagar tarde sale caro**, igual que cualquier reel (`reel/explicado.json` y
`reel/texto.txt`, formato de `reel-explicado.md`). Diferencias:
- En `meta.json` poné `"reel_solo_tiktok": true`: así no entra a la cola de Instagram (ese día en Instagram va solo el
  carrusel) y llega por Telegram para que Seba lo suba a mano a TikTok.
- `texto.txt` al estilo TikTok: gancho, resultado, la pregunta para comentar y 3 a 5 hashtags (#EstudioIERLIP y
  #Emprendedores siempre). Sin la línea del sitio web. Última línea: la hora sugerida (18:00).
- Los demás días `"reel_solo_tiktok"` va en false o no va.

Antes de terminar, revisá que todos los JSON sean válidos, que ningún texto supere su largo, que armaste solo lo que toca hoy y que las cuentas del reel coincidan entre la voz y la pantalla.
