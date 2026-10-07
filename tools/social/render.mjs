// Rendert uit/*.html naar docs/social/*.png
import { chromium } from '../preview/node_modules/playwright-core/index.mjs';
import fs from 'fs';
const map = new URL('./uit/', import.meta.url).pathname;
const doel = new URL('../../docs/social/', import.meta.url).pathname;
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
for (const f of fs.readdirSync(map).filter((f) => f.endsWith('.html')).sort()) {
  const html = fs.readFileSync(map + f, 'utf8');
  const [w, h] = [+(html.match(/width: (\d+)px; height/)[1]), +(html.match(/height: (\d+)px; overflow/)[1])];
  const p = await b.newPage({ viewport: { width: w, height: h } });
  await p.goto('file://' + map + f); await p.waitForTimeout(250);
  await p.screenshot({ path: doel + f.replace('.html', '.png') });
  await p.close();
}
await b.close();
console.log('klaar');
