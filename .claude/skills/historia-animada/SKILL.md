---
name: historia-animada
description: Elige el tema del día y escribe los textos de la historia animada de 12 segundos (con sonido) de @estudioierlip, verificados en fuentes oficiales. Lo llama el workflow historia-animada los martes, viernes y domingos; no publica ni manda nada.
---

# historia-animada

Corrés sin supervisión dentro de GitHub Actions: **no hagas preguntas**, decidí con criterio y anotá lo dudoso. No uses git, no mandes mensajes y no busques tokens. El render del video (`templates/historia-animada.html`), el sonido y el envío los hace el workflow.

## 1. Contexto
1. `CLAUDE.md` y `docs/linea-editorial.md`.
2. `config/calendario-noviembre-2026.json` (o el del mes que corresponda): la entrada de hoy (fecha del sistema, Buenos Aires).
3. `state/animadas-vistas.json` (si existe): temas ya usados, para no repetir.
4. Ejemplo aprobado: `templates/historia-animada.html` con sus textos por defecto (vence el monotributo el 20/11).

## 2. Elegir el tema
En este orden:
1. Un **vencimiento o cambio importante de los próximos 7 días** (monotributo, IVA, F.931, Ganancias, una norma que entra en vigencia).
2. Si no hay, el tema de la placa o la historia del día en el calendario.
3. Si tampoco hay, un dato útil y verificable sobre ARCA, ARBA o AGIP que no esté en `animadas-vistas.json`.

## 3. Verificar
Todo dato (fechas, montos, porcentajes, a quién alcanza) se confirma con WebSearch/WebFetch en fuentes oficiales: arca.gob.ar o afip.gob.ar, arba.gov.ar, agip.gob.ar, boletinoficial.gob.ar, argentina.gob.ar. Comprobá con código el día de la semana de cada fecha. Lo que no puedas confirmar no va: reformulalo o elegí otro tema, y anotalo en `needs_review`.

## 4. Escribir los textos
La historia tiene 3 escenas fijas; vos escribís sus textos. Respetá los largos, porque el diseño no se cambia:
- **Escena 1**:
  - `eyebrow`: hasta 20 caracteres, en MAYÚSCULAS (por ejemplo "A 15 DÍAS DEL", "DESDE EL 1/12", "¿SABÍAS QUE?").
  - `grande`: hasta 6 caracteres, va gigante (una fecha como "20/11", una sigla como "FAL" o "IVA", un número como "2,5%").
  - `sub`: hasta 30 caracteres, completa la frase (por ejemplo "vence el Monotributo").
- **Escena 2**:
  - `titulo_pasos`: hasta 28 caracteres, en minúscula (por ejemplo "un chequeo en 3 pasos").
  - `pasos`: exactamente 3 textos de hasta 32 caracteres cada uno, accionables y con voseo.
- **Escena 3**:
  - `cierre`: hasta 16 caracteres, una pregunta corta que invite a escribir (por ejemplo "¿Dudas?", "¿Tenés empleados?"). El WhatsApp y el logo ya están en el diseño.

Tono: claro, cercano, rioplatense. Sin chistes sobre ARCA ni política. Nunca pongas la fuente en la historia.

## 5. Entregar en `bot/salida/`
- `animada.json`: `{"eyebrow", "grande", "sub", "titulo_pasos", "pasos": [3], "cierre"}`.
- `texto.txt`: una línea para Seba con la hora sugerida para subirla (09:00 o 18:00) y, si suma, qué sticker nativo agregar (link a WhatsApp, cuenta regresiva o encuesta).
- `meta.json`: `{"resumen": "Historia animada: <tema en una línea>", "sources": [urls oficiales], "needs_review": [...]}`.
- Agregá el tema a `state/animadas-vistas.json` (`{"vistas": [{"fecha", "tema"}]}`), conservando los anteriores.

Antes de terminar, revisá que `animada.json` sea JSON válido y que ningún texto supere su largo.
