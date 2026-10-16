// Rauchtest: startet das Spiel in einem Browser ohne Grafikkarte, baut die Welt auf
// und meldet Fehler. Screenshots landen in tools/out/.
//
// Aufruf:  node tools/smoketest.mjs [mittel|hoch|ultra] [mage|warrior|ranger|rogue]
// Voraussetzung: Playwright mit Chromium (PLAYWRIGHT_MODULE kann auf das Modul zeigen).
import { spawn } from 'node:child_process';
import { mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const out = join(root, 'tools', 'out');
mkdirSync(out, { recursive: true });
const quality = process.argv[2] || 'mittel';
const cls = process.argv[3] || 'mage';
const port = 8700 + Math.floor(Math.random() * 90);

const pw = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const chromium = pw.chromium || pw.default.chromium;
const server = spawn('python3', ['-m', 'http.server', String(port)], { cwd: root, stdio: 'ignore' });
await new Promise(r => setTimeout(r, 1200));

let failed = false;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
try {
  const page = await browser.newPage({ viewport: { width: 960, height: 540 } });
  const problems = [];
  page.on('pageerror', e => problems.push('Seitenfehler: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/fonts\.g|ERR_INVALID_URL|net::ERR_/.test(m.text())) problems.push('Konsole: ' + m.text().slice(0, 300)); });
  await page.addInitScript(([q, c]) => { localStorage.setItem('sonnenhain-q', q); localStorage.setItem('sonnenhain-class', c); }, [quality, cls]);
  await page.goto(`http://localhost:${port}/client/`);
  await page.waitForTimeout(800);
  await page.evaluate(() => document.getElementById('startBtn').click());
  await page.waitForFunction(() => document.getElementById('start').hidden || /Erneut/.test(document.getElementById('startBtn').textContent), null, { timeout: 600000 });
  if (!(await page.evaluate(() => document.getElementById('start').hidden))) problems.push('Weltaufbau fehlgeschlagen: ' + await page.textContent('#loadNote'));
  await page.waitForTimeout(5000);
  await page.screenshot({ path: join(out, `start-${quality}-${cls}.png`), timeout: 180000 });
  if (problems.length) { failed = true; console.log('FEHLER:\n' + problems.join('\n')); }
  else console.log(`OK: Spiel startet (${quality}, ${cls}), Screenshot in tools/out/`);
} finally {
  await browser.close();
  server.kill();
}
process.exit(failed ? 1 : 0);
