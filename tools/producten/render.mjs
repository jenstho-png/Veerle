// Rendert uit/*.html naar docs/producten/beelden/*.png (1600x2000). Daarna: python3 comprimeer.py
import { chromium } from '../preview/node_modules/playwright-core/index.mjs';
import fs from 'fs';
const map = new URL('./uit/', import.meta.url).pathname;
const doel = new URL('../../docs/producten/beelden/', import.meta.url).pathname;
const alleen = process.argv[2];
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const p = await b.newPage({ viewport: { width: 1600, height: 2000 } });
for (const f of fs.readdirSync(map).filter((f) => f.endsWith('.html') && (!alleen || f.startsWith(alleen))).sort()) {
  await p.goto('file://' + map + f); await p.waitForTimeout(250);
  await p.screenshot({ path: doel + f.replace('.html', '.png') });
}
await b.close();
console.log('klaar');
