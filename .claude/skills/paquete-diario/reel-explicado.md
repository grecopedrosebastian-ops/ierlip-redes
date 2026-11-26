# Reel "Lo que te diría tu contador" (con personaje y voz en off)

Formato vigente desde el 26/11/2026 (aprobado por Seba): **estilo cómic** (azul, violeta, rojo y lima) con el
**personaje 3D** del estudio que gesticula, letras gigantes, voz de **Franco** (ElevenLabs), **30 a 40 segundos** y un tono
**polémico con criterio**, pensado para generar comentarios. Vale para todos los reels, incluido el de TikTok de los jueves.
Se mantiene la base: un **caso con números** y **"lo que te diría tu contador"** (lo que la cuenta no muestra).
Template: `templates/reel-personaje.html`. El anterior (`reel-explicado.html`, papel crema) quedó archivado.

Público: **emprendedores, gente que quiere arrancar un negocio, principiantes y pymes**. Lenguaje simple, con voseo.

## Líneas (qué día va cada una: tabla de la sección 2 de `SKILL.md`; acá, las ideas)
| Día | Línea | Qué es | Ejemplos |
|---|---|---|---|
| Lun | **¿Te conviene?** | Una decisión A contra B, con los dos números | ¿Monotributo o responsable inscripto? · ¿En blanco o facturando? · ¿Local a la calle o vender online? · ¿Monotributo o SAS? |
| Mar | **¿Garpa?** | Una idea de negocio con la cuenta: inversión, ventas, costos, impuestos, cuándo recuperás | Café al paso · peluquería · viandas · food truck · lavadero · estética · tienda online de ropa |
| Mié | **Primeros pasos** | Para el que arranca: qué necesita y cuánto le cuesta estar en regla | Arrancás a vender por Instagram · tu primer cliente del exterior · te inscribís de monotributista: cuánto pagás el primer año |
| Jue | **Pagar tarde sale caro** | Lo que cuesta un vencimiento salteado, con intereses y multas reales | Monotributo 2 meses tarde · IVA fuera de término · la DDJJ que no presentaste |
| Vie | **Pyme: ¿cuánto cuesta de verdad?** | El costo completo de algo que parece simple | Un empleado de $1.000.000 · cobrar con tarjeta o con QR · emitir factura A · vender en cuotas |
| Sáb | **¿Garpa? (desde casa)** | Emprendimientos chicos o desde casa, con la cuenta | Tortas por encargo · clases particulares · reventa online · alquiler temporario · servicio técnico |
| Dom | **Consejo con números** | Un consejo práctico para emprendedores, con la cuenta que lo demuestra | Cómo poner precio con los impuestos adentro · separar la plata del negocio · el mito "si no facturo no se enteran" · cuánto ahorrar para impuestos |

Rotá rubros, públicos y montos. No repitas un caso de los últimos 60 días (`state/paquete-vistas.json`, campo `reel`).

## Los números
- **Datos fiscales** (cuotas y topes de monotributo, alícuotas, aportes, intereses, multas): siempre verificados en fuentes
  oficiales (arca.gob.ar, boletinoficial.gob.ar, arba.gov.ar, agip.gob.ar, argentina.gob.ar). Anotá la fuente en `meta.json`.
- **Datos del caso** (cuánto sale el local, cuánto vende, cuánto cobra un corte): son un **ejemplo**. Usá montos redondos y
  razonables, decilo en la voz ("supongamos que…", "un ejemplo:") y ponelo en la `nota` del ticket ("Ejemplo con valores
  redondos"). Nunca los presentes como estadística ni como "el promedio del mercado".
- Hacé las cuentas con código y revisalas dos veces: lo que dice la voz y lo que dice la pantalla tienen que coincidir.
- Lo que no puedas confirmar no va: cambiá el caso. Los supuestos van en `needs_review`.

## Tono polémico con criterio
- **Gancho que divide:** una afirmación incómoda o una pregunta con dos bandos, en la primera escena y en menos de 10
  palabras ("¿Perdiste plata? Pagás impuestos igual.", "Facturar todo te sale caro. ¿O no?").
- El tema sale de la **experiencia del contribuyente**: impuestos sobre la venta, burocracia, costo de estar en regla,
  en blanco contra facturando, efectivo contra QR. La línea del día de la tabla se mantiene; cambia el ángulo.
- La incomodidad sale de un **dato verificado** mostrado sin vueltas, nunca de exagerarlo. El "pero" va siempre en el mismo reel.
- **Cierre de debate:** una pregunta de dos opciones que se responda con una palabra ("¿Justo o injusto?", "¿Team blanco o
  team factura?"). La misma va primera en el texto del reel, para fijarla como comentario.
- El estudio no toma partido sobre si la norma está bien: plantea, muestra la cuenta y ayuda a pagar lo que corresponde.
- **Límites (sin excepción):** nada de partidos, políticos, funcionarios o ideología; nada de sugerir no pagar, evadir o
  "zafar"; sin cifras sin fuente, alarmas falsas ni títulos que el video no cumpla; sin burlas a empleados de organismos,
  clientes o seguidores. Si el gancho solo funciona rompiendo una de estas reglas, cambiá de tema.
- Anotá en `needs_review` toda afirmación discutible, para que Seba la mire antes de aprobar.

## Estructura (de 6 a 8 escenas, 30 a 40 segundos)
1. **Gancho** polémico. Tipo `texto`, gesto `serio` o `sorpresa`.
2. **La regla** que incomoda, en una frase. Tipo `texto`, gesto `explica`.
3. **La cuenta**: un solo `ticket`.
4. **La cifra** que resume: tipo `cifra`, gesto `sorpresa`.
5. **"Pero…"** lo que conviene revisar: tipo `lista`, gesto `advierte`.
6. **La pregunta de debate**: tipo `texto`, gesto `señala`.
7. **Cierre** con WhatsApp: tipo `cierre`, gesto `pulgar`.

## El personaje (`gesto`, opcional en cada escena)
`serio` (dedo en alto) · `advierte` (señala serio) · `señala` (a cámara) · `sorpresa` (manos arriba) · `explica` ·
`pregunta` · `pulgar`. Sin `gesto`, sale según el tipo de escena. No repitas el mismo en dos escenas seguidas.
La boca se mueve pero no está sincronizada con la voz; los gestos salen de clips fijos (`assets/personaje/`).

## La voz (`voz` de cada escena)
- Una o dos oraciones cortas por escena, como se habla, con voseo. **Se lee en voz alta**: escribí los números como se dicen
  ("un millón y medio", "diecisiete por ciento", "sesenta y seis mil") y redondeá ("unos sesenta y seis mil").
- Nada de siglas raras sin explicar. "ART" e "IVA" sí; "SIPA" no.
- Evitá comas en medio de las preguntas (la voz se traba): "¿Qué te conviene: en blanco o facturando?".
- La escena dura lo que tarde la voz; no hace falta medir. Total: **75 a 95 palabras** (con más, pasa de 40 segundos).

## Formato del JSON (`bot/salida/reel/explicado.json`)
```json
{
  "pie": "lo que te diría tu contador",
  "escenas": [
    {"tipo": "texto", "gesto": "serio", "lineas": [{"t": "¿Garpa abrir"}, {"t": "un café", "color": "vio"}, {"t": "con $20 M?", "tam": "xl", "hl": true}], "mano": "— un ejemplo con números", "voz": "..."},
    {"tipo": "texto", "centro": true, "lineas": [{"t": "Hagamos la cuenta", "peso": 3, "tam": "md"}, {"t": "como tu contador", "hl": true}], "voz": "..."},
    {"tipo": "barras"},
    {"tipo": "ticket", "arriba": "Por mes · *el local*", "titulo": "Lo que entra y lo que sale",
     "filas": [["Ventas", "$6.000.000"], ["Mercadería", "−$2.100.000", "menos"], ["Alquiler y sueldos", "−$2.800.000", "menos"], ["Te queda", "$1.100.000", "sub"]],
     "total": ["Recuperás en", "18 meses"], "nota": "Ejemplo con valores redondos.", "voz": "..."},
    {"tipo": "cifra", "numero": "18 meses", "texto": "para recuperar la *inversión*", "mano": "¿garpa?", "voz": "..."},
    {"tipo": "lista", "titulo": "Pero…", "bajada": "la cuenta no muestra:", "items": ["Ingresos Brutos", "Meses flojos"], "marca": "x", "voz": "..."},
    {"tipo": "texto", "lineas": [{"t": "Antes de abrir,", "peso": 3, "tam": "md"}, {"t": "ojo:", "hl": true}, {"t": "hacé la cuenta *con IVA.*", "tam": "md"}], "voz": "..."},
    {"tipo": "cierre", "arriba": "La cuenta no es", "abajo": "solo el número.", "boton": "La hacemos con tus datos", "voz": "..."}
  ]
}
```
- `texto.lineas[]`: `t` (hasta 22 caracteres; `*palabra*` en violeta), `peso` 9 (gruesa, por defecto) o 3 (fina),
  `tam` "xl" | "lg" (por defecto) | "md" | "sm", `hl: true` (resaltado mostaza, una sola línea por escena), `color: "vio"`.
  De 2 a 4 líneas. `centro: true` las centra. `mano`: nota manuscrita opcional, hasta 32 caracteres.
- `ticket`: `arriba` (hasta 30), `titulo` (hasta 28), `filas` de 2 a 5: `[concepto (hasta 18), valor (hasta 13), clase?]`,
  clase "menos" (resta, terracota), "mas" (suma, verde), "sub" (subtotal con línea) o "por" (multiplicador manuscrito).
  `total`: `[etiqueta (hasta 14), valor (hasta 12)]`. `nota`: hasta 70.
- `cifra`: `numero` hasta 11 caracteres, `texto` hasta 40, `mano` opcional.
- `lista`: `titulo` (hasta 10), `bajada` (hasta 28), `items` de 2 a 4 (hasta 18 cada uno), `marca` "x" o "check".
- `cierre`: `arriba` y `abajo` (hasta 20 cada uno), `boton` (hasta 28).
- `barras` no lleva voz. Todas las demás escenas llevan `voz`.

## Texto del reel (`bot/salida/reel/texto.txt`)
Primera línea: emoji + la pregunta de debate (la de dos opciones). Después, 2 o 3 líneas con el resultado y el "pero", **una pregunta para
comentar** ("¿Vos cuánto separás de cada cobro? Contanos 👇", "¿Lo harías? 👇"), "Guardalo y mandáselo a quien lo
necesite 📌", "Escribinos por WhatsApp: +54 11 4992-2513", "@estudioierlip · estudioierlip.com" y de 5 a 8 hashtags con
#EstudioIERLIP y #Emprendedores. Última línea: la hora sugerida (18:00; los lunes, 20:00).
