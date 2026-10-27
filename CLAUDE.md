# IERLIP · Redes (proyecto para Claude Code)

Contenido de Instagram y TikTok para **Estudio Integral IERLIP** (@estudioierlip), estudio contable e impositivo argentino. Responsable: Seba (Hook Studio). Idioma de trabajo: español rioplatense, con voseo.

## Objetivo
Noviembre 2026 con contenido todos los días, **sin publicar nada sin el OK de Seba**:
- **20 videos** (Reels y TikTok) del proyecto hermano `../ierlip-video-diario/ierlip-video-diario`. Llegan por Telegram y se programan en **TikTok Studio** (TikTok) y **Zoho Social** (Reels de Instagram), con el OK de Seba.
- **1 placa por día** (feed 4:5) y **1 historia por día** (9:16), informativas y de aprendizaje sobre ARCA, ARBA y AGIP. Las produce **este** proyecto.
- **1 video de "debate con criterio" por semana** (los martes), con @elpyme como referencia de energía.

## Decisiones aprobadas (27/10/2026)
1. Línea "debate con criterio", 1 por semana. Reglas en `docs/linea-editorial.md`.
2. Formatos: feed **4:5 (1080×1350)** e historias **9:16 (1080×1920)**.
3. Estilos: **B · Papel** para las placas y **C · Tipográfico** para las historias y el debate. Detalle en `docs/estilos.md`.
4. **Carga (decidido el 27/10): Zoho Social Free** para Instagram y Facebook (1 marca, publicaciones sin límite) + **TikTok Studio** para TikTok (programador nativo, hasta ~10 días antes). Todo gratis. Metricool gratis (20 por mes) y Postiz en servidor propio quedaron descartados; la instalación de Postiz queda archivada en `infra/postiz/`. Nada se programa sin el OK de Seba.

## Estructura
```
CLAUDE.md                          este archivo
docs/linea-editorial.md            tono, pilares, reglas del debate
docs/estilos.md                    especificación visual B y C (colores, tipografías, medidas)
config/calendario-noviembre-2026.json  30 días: placa + historia por día (tema, puntos, qué verificar)
templates/placa-papel.html         estilo B (portada / items / tip / cierre)
templates/historia-tipografica.html estilo C, historia
templates/placa-debate.html        estilo C, placa de debate
scripts/render.mjs                 JSON → PNG con Playwright
piezas/<fecha>/*.json              especificaciones de cada pieza (las escribe Claude)
output/<fecha>/                    PNG + caption.txt + meta.json (no se versiona)
claude-skills/contenido-diario/    skill del día (mover a .claude/skills, ver abajo)
assets/logo/ierlip-logo.png        logo (lo sube Seba)
```

## Primera vez (hacelo vos, Claude Code, al abrir el proyecto)
1. `npm run setup` (instala Playwright, Chromium y las fuentes de @fontsource).
2. Mové la skill a su lugar: `mkdir -p .claude/skills && cp -r claude-skills/contenido-diario .claude/skills/`. No se pudo crear directo desde Cowork porque `.claude/` estaba protegida.
3. Pedile a Seba el logo y guardalo en `assets/logo/ierlip-logo.png` (PNG con fondo transparente). Sin logo, las placas muestran el texto "ESTUDIO IERLIP".
4. Probá el render: `node scripts/render.mjs piezas/ejemplo/placa.json piezas/ejemplo/historia.json piezas/ejemplo/debate.json` y mostrale los PNG a Seba con Read. **Los templates nunca se renderizaron:** es esperable tener que ajustar espaciados en esta primera prueba.
5. Inicializá git si Seba quiere versionarlo (`git init`, repo privado).

## Uso diario
- `/contenido-diario 2026-11-02` produce la placa y la historia de esa fecha (ver la skill).
- Para hacer una semana por adelantado, corré la skill por cada fecha y mostrá los PNG antes de cargar nada.

## Estado del proyecto de videos (`../ierlip-video-diario/ierlip-video-diario`)
Cambios hechos el 22 y el 27/10, **solo en la copia local, sin push**:
- `config/topics.json → calendario`: 20 videos con fecha. Los martes 3, 10, 17 y 24 son de **debate** (`"linea": "debate"`).
- `scripts/pick_format.py`: usa el calendario si la fecha figura y pasa `slot` y `topic.linea` a `state/today.json`.
- `scripts/publish_queue.py` (nuevo) y un paso nuevo en `.github/workflows/daily-video.yml`: sube el video a R2 (bucket S3 compatible), anota fecha, link y caption en `state/queue.json` y manda el link por Telegram. Si faltan los secretos `S3_*`, no hace nada.
- `README.md`: sección "Calendario con fecha fija y cola de publicación".
- **Falta aplicar a mano** (Cowork no pudo editar `.claude/`): agregar a `.claude/skills/daily-video/SKILL.md`, sección 2, esta viñeta:
  > **Línea "debate con criterio"** (`topic.linea == "debate"`, aprobada por Seba, 1 por semana): se permite plantear un tema que genere opinión (burocracia, presión fiscal, trámites) desde la experiencia del contribuyente, con un dato verificado y una pregunta abierta en pantalla y en el caption. Sigue prohibido: partidos, políticos o funcionarios con nombre, burlas a empleados de ARCA/ARBA/AGIP, sugerir no pagar o evadir, cifras sin fuente y parodias de marcas, películas o personas reales. Estilo: POV tipográfico azul marino con la palabra clave en ámbar.
- **Antes del push:** la copia local tiene un solo commit ("inicio") y GitHub va adelantado, porque el pipeline ya usa personajes realistas. Hacer `git pull`, resolver conflictos y mostrarle el diff a Seba antes de `git push`.

## Pendientes
- [ ] Seba: `git pull` y push del repo de videos (después de revisar el diff).
- [ ] Seba: crear el bucket público en Cloudflare R2 y cargar los secretos `S3_ENDPOINT_URL`, `S3_BUCKET`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY` y `S3_PUBLIC_BASE_URL`.
- [ ] Con la URL pública de `ierlip/queue.json`: programar cada video en su fecha en TikTok Studio y en Zoho (Reel), con el OK de Seba.
- [x] Primera prueba de render y estilo nuevo aprobado en Design (27/10).
- [ ] Seba: crear la cuenta de Zoho Social Free, conectar Instagram (cuenta business) y la página de Facebook, y confirmar si el plan gratis programa historias.
- [ ] Seba: pasar TikTok a cuenta Business o Creator (TikTok Studio solo programa desde la compu y en esas cuentas).
- [ ] Opcional: conectar LinkedIn (página de la empresa) en Zoho; entra en los 6 canales del plan gratis.

## Carga en redes (Zoho Social + TikTok Studio)
- Cada semana: `python scripts/paquete-carga.py <desde> <hasta>` arma `carga/<desde>_<hasta>/` con una carpeta por día (archivos numerados en el orden de carga, caption y horario) y `CARGA.md`, la planilla con todo lo que hay que programar y lo que hay que verificar antes.
- **Zoho Social Free** (Instagram y Facebook): carruseles, Reels y, si el plan lo permite, historias sin sticker. No tiene API: la carga la hace Seba o Claude desde Chrome **con el OK de Seba antes de cada tanda**.
- **TikTok Studio** (tiktok.com/tiktokstudio, desde la compu): videos del proyecto hermano, hasta ~10 días antes.
- **Historias con sticker nativo** (encuesta, cuestionario, cuenta regresiva, preguntas, link): siempre a mano desde el celular a las 09:00.
- Horarios (datos de la cuenta): Instagram a las 10 h los días hábiles y a las 18 h como segundo pico; TikTok a las 10, 12 y 18 h. Videos a las 10:00 o 18:00 según el calendario. Placas: 12:00 en días hábiles y 11:00 los fines de semana. Historias: 09:00. Zona horaria America/Buenos_Aires.
- Metricool (blogId 6874988) queda conectado pero sin uso.

## Reglas no negociables
- No publicar, no programar con publicación automática y no hacer push sin el OK de Seba. Mostrar los cambios antes.
- Verificar todo dato fiscal en fuentes oficiales. Lo dudoso va a "VERIFICAR ANTES DE PUBLICAR".
- No tocar `state/history.json` del repo de videos a mano.
- No inventar estadísticas. No usar marcas ni personas reales.

## Fuentes usadas en la planificación
- Vencimientos de noviembre 2026: https://yo-facturo.com/vencimientos/noviembre-2026/ (referencial, confirmar en arca.gob.ar)
- Feriados del 9, 10 y 11/11 (Decreto 1103/2026): https://chequeado.com/el-explicador/visita-del-papa-leon-xiv-cuales-son-los-feriados-del-9-10-y-11-de-noviembre-y-donde-rigen/ · https://www.forbesargentina.com/today/visita-papa-leon-xiv-argentina-gobierno-decreto-9-noviembre-sera-feriado-nacional-n98511
- Feriado del 23/11: https://www.lanacion.com.ar/feriados/2026/noviembre/
- Referencia de debate: https://www.instagram.com/elpyme/ · Perfil propio: https://www.instagram.com/estudioierlip/
- Plan de videos completo: `../IERLIP_plan_videos_noviembre_2026.html`
