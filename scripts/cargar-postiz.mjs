#!/usr/bin/env node
// Carga en Postiz (self-hosted) las piezas de output/<fecha>/ como BORRADORES de Instagram.
// Nunca programa ni publica: Seba revisa cada borrador en Postiz y recién ahí lo pasa a "programado".
//
// Uso:
//   node scripts/cargar-postiz.mjs 2026-11-01 2026-11-07            # simulación: muestra qué cargaría
//   node scripts/cargar-postiz.mjs 2026-11-01 2026-11-07 --crear    # crea los borradores
//
// Variables de entorno (no las escribas en archivos versionados):
//   POSTIZ_URL            https://redes.estudioierlip.com
//   POSTIZ_API_KEY        Settings > Developers > Public API, en Postiz
//   POSTIZ_INSTAGRAM_ID   id de la cuenta de Instagram en Postiz (la simulación lista las disponibles)
//
// Las historias con sticker nativo (encuesta, cuestionario, cuenta regresiva, preguntas, link)
// no se cargan: la API de Instagram no permite stickers, así que se suben a mano desde el celular.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const args = process.argv.slice(2);
const crear = args.includes("--crear");
const [desde, hasta = desde] = args.filter(a => /^\d{4}-\d{2}-\d{2}$/.test(a));
if (!desde) {
  console.error("Uso: node scripts/cargar-postiz.mjs <desde> [hasta] [--crear]");
  process.exit(1);
}
const BASE = (process.env.POSTIZ_URL || "").replace(/\/$/, "") + "/api/public/v1";
const KEY = process.env.POSTIZ_API_KEY;
const IG = process.env.POSTIZ_INSTAGRAM_ID;

async function api(method, ruta, body) {
  const headers = { Authorization: KEY };
  if (body && !(body instanceof FormData)) headers["Content-Type"] = "application/json";
  const res = await fetch(BASE + ruta, { method, headers, body: body instanceof FormData ? body : body && JSON.stringify(body) });
  const txt = await res.text();
  if (!res.ok) throw new Error(`${method} ${ruta} → ${res.status}: ${txt.slice(0, 300)}`);
  return txt ? JSON.parse(txt) : null;
}

async function subir(archivo) {
  const fd = new FormData();
  const tipo = archivo.endsWith(".mp4") ? "video/mp4" : "image/png";
  fd.append("file", new Blob([fs.readFileSync(archivo)], { type: tipo }), path.basename(archivo));
  const r = await api("POST", "/upload", fd);
  return { id: r.id, path: r.path };
}

function fechas() {
  const out = [];
  for (let d = new Date(desde + "T12:00:00Z"); d <= new Date(hasta + "T12:00:00Z"); d.setUTCDate(d.getUTCDate() + 1)) {
    out.push(d.toISOString().slice(0, 10));
  }
  return out;
}

// Arma la lista de borradores a partir de output/<fecha>/.
const plan = [];
const aMano = [];
for (const f of fechas()) {
  const dir = path.join(ROOT, "output", f);
  if (!fs.existsSync(path.join(dir, "meta.json"))) { console.warn(`(sin piezas para ${f})`); continue; }
  const meta = JSON.parse(fs.readFileSync(path.join(dir, "meta.json"), "utf-8"));
  const caption = fs.readFileSync(path.join(dir, "caption.txt"), "utf-8").trim();
  const placas = fs.readdirSync(dir).filter(n => /^placa(-\d+)?\.png$/.test(n))
    .sort((a, b) => (parseInt(a.split("-")[1]) || 0) - (parseInt(b.split("-")[1]) || 0));
  plan.push({ fecha: f, tipo: "post", cuando: meta.publicar_placa, caption, archivos: placas.map(n => path.join(dir, n)) });
  const historia = path.join(dir, "historia.png");
  if (meta.sticker_nativo) aMano.push(`${f} · ${path.relative(ROOT, historia)} · sticker: ${meta.sticker_nativo}`);
  else if (fs.existsSync(historia)) plan.push({ fecha: f, tipo: "story", cuando: meta.publicar_historia, caption: "", archivos: [historia] });
  const animada = path.join(dir, "historia-animada.mp4");
  if (fs.existsSync(animada)) {
    const t = new Date(meta.publicar_historia); t.setMinutes(t.getMinutes() + 30);
    plan.push({ fecha: f, tipo: "story", cuando: t.toISOString(), caption: "", archivos: [animada] });
  }
}

for (const p of plan) console.log(`${p.fecha}  ${p.tipo.padEnd(5)}  ${new Date(p.cuando).toISOString()}  ${p.archivos.map(a => path.basename(a)).join(", ")}`);
if (aMano.length) console.log("\nHistorias para subir a mano (llevan sticker nativo):\n  " + aMano.join("\n  "));

if (!KEY || !process.env.POSTIZ_URL) { console.log("\nFaltan POSTIZ_URL y POSTIZ_API_KEY: solo simulación."); process.exit(0); }
const integraciones = await api("GET", "/integrations");
if (!crear) {
  console.log("\nCuentas conectadas en Postiz:");
  for (const i of integraciones) console.log(`  ${i.id}  ${i.identifier}  ${i.name}`);
  console.log("\nSimulación: no se creó nada. Agregá --crear para cargar los borradores.");
  process.exit(0);
}
const ig = integraciones.find(i => i.id === IG);
if (!ig) throw new Error("POSTIZ_INSTAGRAM_ID no coincide con ninguna cuenta conectada.");
if (!/^instagram/.test(ig.identifier)) throw new Error(`La cuenta ${IG} es ${ig.identifier}, no Instagram.`);

for (const p of plan) {
  const media = [];
  for (const a of p.archivos) media.push(await subir(a));
  const r = await api("POST", "/posts", {
    type: "draft",                                   // siempre borrador: nunca programar ni publicar desde acá
    date: new Date(p.cuando).toISOString(),
    shortLink: false,
    tags: [],
    posts: [{
      integration: { id: ig.id },
      value: [{ content: p.caption, image: media }],
      settings: { __type: ig.identifier, post_type: p.tipo, collaborators: [] },
    }],
  });
  console.log(`OK borrador ${p.fecha} ${p.tipo} → ${JSON.stringify(r)}`);
}
