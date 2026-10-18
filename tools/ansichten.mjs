// Ansichten: baut die Welt einmal auf und fotografiert sie aus festen Blickwinkeln.
// Gut für Vorher/Nachher-Vergleiche bei Änderungen an Gelände, Licht, Himmel oder Pflanzen.
// Bilder landen in tools/out/ansichten/ (oder im Ordner aus dem dritten Argument).
//
// Aufruf:  node tools/ansichten.mjs [mittel|hoch|ultra] [Bildbreite] [Zielordner]
// Nur einzelne Ansichten:  ANSICHTEN=1,4 node tools/ansichten.mjs
// Voraussetzung wie beim Rauchtest: Playwright mit Chromium (PLAYWRIGHT_MODULE kann auf das Modul zeigen).
import { spawn } from 'node:child_process';
import { mkdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const quality = process.argv[2] || 'hoch';
const width = Number(process.argv[3]) || 1280;
const out = process.argv[4] ? resolve(process.argv[4]) : join(root, 'tools', 'out', 'ansichten');
mkdirSync(out, { recursive: true });
const port = 8700 + Math.floor(Math.random() * 90);

// Blickwinkel: Spielerposition (x, z), Kamera-Drehung (yaw), Neigung (pitch) und Abstand.
const VIEWS = [
  { name: '1-hof', x: -2, z: 18, yaw: 0.75, pitch: 0.2, dist: 11 },
  { name: '2-see', x: 40, z: -28, yaw: -0.85, pitch: 0.2, dist: 12 },
  { name: '3-weite', x: 4, z: -6, yaw: 2.5, pitch: 0.42, dist: 34 },
  { name: '4-gegenlicht', x: -2, z: 18, yaw: -2.27, pitch: 0.1, dist: 9 },
  { name: '5-ruinen', x: -47, z: 28, yaw: 2.1, pitch: 0.22, dist: 12 },
  { name: '6-wald', x: -30, z: -40, yaw: 0.9, pitch: 0.18, dist: 10 },
].filter(v => !process.env.ANSICHTEN || process.env.ANSICHTEN.split(',').includes(v.name[0]));

const pw = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const chromium = pw.chromium || pw.default.chromium;
const server = spawn('python3', ['-m', 'http.server', String(port)], { cwd: root, stdio: 'ignore' });
await new Promise(r => setTimeout(r, 1200));

let failed = false;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
try {
  const page = await browser.newPage({ viewport: { width, height: Math.round(width * 9 / 16) } });
  const problems = [];
  page.on('pageerror', e => problems.push('Seitenfehler: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/fonts\.g|ERR_INVALID_URL|net::ERR_/.test(m.text())) problems.push('Konsole: ' + m.text().slice(0, 300)); });
  // Kleiner Zugang zu Kamera und Spieler, nur für dieses Werkzeug (die Datei im Repository bleibt unverändert).
  await page.route('**/client/index.html', async route => {
    const res = await route.fetch(); let body = await res.text();
    body = body.replace('function frame(now){', 'window.__ansicht = { P, cam, getH, frames: 0 };\nfunction frame(now){ window.__ansicht.frames++;');
    route.fulfill({ response: res, body, headers: { ...res.headers(), 'content-type': 'text/html' } });
  });
  await page.addInitScript(q => { localStorage.setItem('sonnenhain-q', q); localStorage.setItem('sonnenhain-class', 'mage'); }, quality);
  await page.goto(`http://localhost:${port}/client/index.html`);
  await page.waitForTimeout(800);
  await page.evaluate(() => document.getElementById('startBtn').click());
  await page.waitForFunction(() => document.getElementById('start').hidden || /Erneut/.test(document.getElementById('startBtn').textContent), null, { timeout: 900000 });
  if (!(await page.evaluate(() => document.getElementById('start').hidden))) throw new Error('Weltaufbau fehlgeschlagen: ' + await page.textContent('#loadNote'));
  await page.evaluate(() => { document.getElementById('ui').hidden = true; });
  for (const v of VIEWS) {
    await page.evaluate(v => {
      const A = window.__ansicht;
      A.P.pos.set(v.x, A.getH(v.x, v.z), v.z); A.P.facing = v.yaw + Math.PI;
      A.cam.yaw = v.yaw; A.cam.pitch = v.pitch; A.cam.dist = A.cam.distT = v.dist;
      A.cam.look.set(v.x, A.P.pos.y + 1.6, v.z);
      A.frames = 0;
    }, v);
    await page.waitForFunction(() => window.__ansicht.frames >= 4, null, { timeout: 300000 });
    await page.screenshot({ path: join(out, v.name + '.png'), timeout: 300000 });
    console.log('Bild: ' + v.name);
  }
  if (problems.length) { failed = true; console.log('FEHLER:\n' + problems.join('\n')); }
  else console.log(`OK: ${VIEWS.length} Ansichten (${quality}) in ${out}`);
} finally {
  await browser.close();
  server.kill();
}
process.exit(failed ? 1 : 0);
