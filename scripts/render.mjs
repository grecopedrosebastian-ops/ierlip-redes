#!/usr/bin/env node
// Renderiza placas e historias a PNG desde una especificación JSON.
//
// Uso:  node scripts/render.mjs piezas/2026-11-02/placa.json [piezas/2026-11-02/historia.json ...]
//
// Formato del JSON:
// {
//   "template": "placa-papel" | "placa-debate" | "historia-tipografica",
//   "slides": [ { ...datos de window.PIEZA... }, ... ],   // 1 = pieza simple, 2+ = carrusel
//   "out": "output/2026-11-02/placa"                      // genera placa-1.png, placa-2.png, ...
// }
import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SIZES = {
  "placa-papel": [1080, 1350],
  "placa-debate": [1080, 1350],
  "historia-tipografica": [1080, 1920],
  "historia-papel": [1080, 1920],
};

const specs = process.argv.slice(2);
if (!specs.length) {
  console.error("Uso: node scripts/render.mjs <spec.json> [...]");
  process.exit(1);
}

const browser = await chromium.launch();
try {
  for (const specPath of specs) {
    const spec = JSON.parse(fs.readFileSync(path.resolve(specPath), "utf-8"));
    const size = SIZES[spec.template];
    if (!size) throw new Error(`Template desconocido: ${spec.template}`);
    const tpl = pathToFileURL(path.join(ROOT, "templates", `${spec.template}.html`)).href;
    const total = spec.slides.length;
    const outBase = path.resolve(ROOT, spec.out);
    fs.mkdirSync(path.dirname(outBase), { recursive: true });

    for (let i = 0; i < total; i++) {
      const page = await browser.newPage({ viewport: { width: size[0], height: size[1] }, deviceScaleFactor: 1 });
      const data = JSON.stringify(spec.slides[i]);
      const meta = JSON.stringify({ n: i + 1, total });
      await page.addInitScript(`window.PIEZA = ${data}; window.META = ${meta};`);
      await page.goto(tpl);
      await page.waitForFunction(() => window.__READY === true);
      await page.evaluate(() => document.fonts.ready);
      await page.waitForTimeout(150);
      const file = total > 1 ? `${outBase}-${i + 1}.png` : `${outBase}.png`;
      await page.screenshot({ path: file, clip: { x: 0, y: 0, width: size[0], height: size[1] } });
      console.log("OK", path.relative(ROOT, file));
      await page.close();
    }
  }
} finally {
  await browser.close();
}
