# Estilos visuales · placas e historias (aprobados el 27/10/2026)

Formatos:
- **Feed (placas y carruseles): 4:5, 1080×1350.** La grilla del perfil se ve en 3:4, así que 4:5 casi no se recorta. Margen seguro: 72 px a los lados y 90 px arriba y abajo.
- **Historias: 9:16, 1080×1920.** Zonas libres: 250 px arriba y 380 px abajo (interfaz de Instagram). Márgenes laterales: 72 px.
- Se exporta en PNG con `scripts/render.mjs`. **No se reescribe el layout:** se cambian los datos.

Paleta base IERLIP: Azul Profundo `#0A192F` · Azul marino de fondo `#0F1A30` · Azul Institucional `#0F2B5C` / `#1B2A5C` · Violeta `#892CA0` · Celeste `#60A5FA` · Blanco cálido `#F5F5F0` · Gris claro `#E2E8F0`.
Ampliación: Ámbar `#F5B335` · Crema `#F5F1E8` · Menta `#3FD0A5` · Mostaza `#E9B949` · Terracota `#C8643B`.

---

## B · Papel IERLIP → placas informativas del feed (`templates/placa-papel.html`)
Es el mismo lenguaje que los posts "resumen impositivo" y los videos de vencimientos.

- **Fondo:** crema `#F5F1E8` con textura de papel (ruido muy suave) y 2 o 3 **manchas orgánicas** en las esquinas, en violeta, mostaza, terracota o azul, con grano.
- **Eyebrow manuscrito** (Patrick Hand, 42 px, azul institucional) con **subrayado ondulado**: "tutorial ARCA · paso a paso", "resumen impositivo · 16/11/2026", "glosario".
- **Título serif grueso** (Source Serif 4, 800-900): 96-120 px en la portada y 60-68 px en el interior. Azul profundo sobre crema; blanco sobre azul marino.
- **Tarjeta de papel** `#FBF8F1` con sombra suave y **cinta adhesiva** mostaza translúcida arriba.
- **Ítems numerados:** número manuscrito dentro de un **círculo terracota** (solo trazo), título serif de 44-48 px y texto Inter 500 de 30-32 px. Entre ítems, una línea ondulada mostaza.
- **Logo:** pastilla blanca con el logo, centrada abajo.
- **Contador del carrusel:** "1/5", manuscrito, arriba a la derecha.

Estructura del carrusel (4 a 6 slides):
1. **Portada** (variante azul marino): eyebrow, título de 2 o 3 líneas, bajada manuscrita ("lo importante, sin vueltas") y logo.
2. **Pasos o ítems** (variante crema), 2 a 4 por slide, en una o dos slides.
3. **Ojo / tip** (opcional): un solo recuadro con el error más común.
4. **Cierre:** "¿Te sirvió? Guardalo 📌", tarjeta de WhatsApp +54 11 4992-2513 y @estudioierlip · estudioierlip.com.

Para una placa simple (no carrusel), usar la variante crema con título y hasta 3 ítems.

---

## B2 · Papel oscuro → historias (`templates/historia-papel.html`, aprobado el 27/10/2026)
Fondo azul marino `#0F1A30` con grano claro, banda azul y mostaza arriba a la derecha, banda violeta cruzando y arcos violeta/terracota abajo. Eyebrow manuscrito mostaza con subrayado ondulado, título Source Serif 4 900 blanco, hasta 4 tarjetas de papel `#F7F3EA` con cinta mostaza alternada (izquierda/derecha), título serif 800 con subrayado ondulado terracota y texto serif 700. Logo a color en pastilla blanca abajo. La historia va llena: sin fondo vacío.
Las historias animadas (`templates/historia-animada.html`) usan la misma base y se exportan a MP4 con sonido.
Las piezas nunca muestran la fuente: va en `meta.json`.

## C · Tipográfico → debate (las historias pasaron a B2) (`templates/historia-tipografica.html`, `templates/placa-debate.html`)
Es el mismo lenguaje que los videos POV y de chat.

- **Fondos** (un color por pieza): azul marino `#0F1A30` (por defecto), azul institucional `#1B2A5C` o crema `#F5F1E8`.
- **Marca de agua:** el globo del logo en trazo fino, al 7% de opacidad, grande y descentrado.
- **Eyebrow** Montserrat 800, 36-40 px, tracking 0.25em: ámbar sobre azul marino, celeste sobre azul institucional, violeta sobre crema. Ejemplos: "POV", "SPOILER", "QUIZ", "¿SABÍAS QUE?", "DEBATE".
- **Título** Montserrat 900, 110-130 px (historia) o 92-104 px (placa de debate), interlineado 0.98, máximo 4 palabras por línea. La **palabra clave en ámbar**: en el texto se marca entre `*asteriscos*`.
- **Tarjetas:** esquinas de 28 px, una crema rellena y otra solo con borde, con **tilde menta** en un círculo. Texto Inter 700 de 44-48 px.
- **Sticker:** rectángulo ámbar inclinado 3-4°, con texto Montserrat 900 en azul profundo ("¡HOY!", "VENCE EL 20", "YA ENVIADA ✓✓").
- **Pie:** @estudioierlip, Inter 600, 30 px, gris claro, apenas arriba de la zona libre de abajo.
- **Historias interactivas:** el template deja una **zona vacía** (`sticker_zone: true`) para pegar el sticker nativo de Instagram (encuesta, quiz, cuenta regresiva, caja de preguntas o link a WhatsApp). Nunca dibujar un sticker interactivo falso.

Placa de debate (4:5): fondo azul marino, eyebrow "DEBATE" en celeste, pregunta gigante con la palabra clave en ámbar, tarjeta crema con el **dato verificado** y la fuente en chico, y sticker ámbar "TE LEEMOS EN COMENTARIOS 👇".

---

## A · Institucional (skill `ierlip-placas-historias`, Python/PIL)
Ya no se usa para el feed. Queda como respaldo para piezas institucionales (anuncios, alianzas).

## Retirado
Violeta saturado con amarillo y lila pastel con fotos (estilo Canva viejo): no usar más, porque desordena la grilla.
