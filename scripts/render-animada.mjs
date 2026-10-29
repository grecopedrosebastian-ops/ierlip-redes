#!/usr/bin/env node
// Exporta una historia animada (CSS) a MP4 1080x1920, cuadro por cuadro.
//
// Uso:  node scripts/render-animada.mjs [--datos datos.json] [templates/historia-animada.html] [output/historia-animada.mp4] [segundos=12] [fps=30] [assets/audio/historia-animada.wav]
// El audio es opcional (se genera con scripts/audio-historia.py). Requiere ffmpeg en el PATH.
import { chromium } from "playwright";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
// --datos <archivo.json> carga los textos de la historia (window.PIEZA); sin él, queda el ejemplo.
const argv = process.argv.slice(2);
const iDatos = argv.indexOf("--datos");
const datos = iDatos >= 0 ? fs.readFileSync(path.resolve(argv.splice(iDatos, 2)[1]), "utf-8") : null;
const [tplArg = "templates/historia-animada.html", outArg = "output/historia-animada.mp4", secs = "12", fpsArg = "30", audioArg] = argv;
const fps = Number(fpsArg), frames = Math.round(Number(secs) * fps);
const out = path.resolve(ROOT, outArg);
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "ierlip-anim-"));
fs.mkdirSync(path.dirname(out), { recursive: true });

const browser = await chromium.launch();
try {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  if (datos) await page.addInitScript(`window.PIEZA = ${datos};`);
  await page.goto(pathToFileURL(path.resolve(ROOT, tplArg)).href);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  await page.evaluate(() => document.getAnimations().forEach(a => a.pause()));
  for (let i = 0; i < frames; i++) {
    const ms = (i * 1000) / fps;
    await page.evaluate(t => document.getAnimations().forEach(a => { a.currentTime = t; }), ms);
    await page.screenshot({ path: path.join(tmp, `f${String(i).padStart(5, "0")}.png`) });
  }
} finally {
  await browser.close();
}
const audio = audioArg ? ["-i", path.resolve(ROOT, audioArg), "-c:a", "aac", "-b:a", "192k", "-shortest"] : [];
execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-framerate", String(fps), "-i", path.join(tmp, "f%05d.png"), ...audio,
  "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow", "-movflags", "+faststart", out], { stdio: "inherit" });
fs.rmSync(tmp, { recursive: true, force: true });
console.log("OK", path.relative(ROOT, out));
