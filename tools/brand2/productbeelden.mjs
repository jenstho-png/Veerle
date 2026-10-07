// Maakt van de html-pagina's in uit/productbeelden jpg's (1600x2000 en 800 breed) in theme/assets en docs/productbeelden.
import { chromium } from '../preview/node_modules/playwright-core/index.mjs';
import fs from 'fs';
const map = new URL('./uit/productbeelden/', import.meta.url).pathname;
const thema = new URL('../../theme/assets/', import.meta.url).pathname;
const docs = new URL('../../docs/productbeelden/', import.meta.url).pathname;
fs.mkdirSync(docs, { recursive: true });
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
for (const f of fs.readdirSync(map).filter((f) => f.endsWith('.html')).sort()) {
  const naam = f.replace('.html', '');
  for (const [schaal, achter, kwaliteit] of [[1, '', 74], [0.5, '-800', 74]]) {
    const p = await b.newPage({ viewport: { width: 1600, height: 2000 }, deviceScaleFactor: schaal });
    await p.goto('file://' + map + f); await p.waitForTimeout(500);
    await p.screenshot({ path: thema + naam + achter + '.png' });
    await p.close();
  }
}
await b.close();
console.log('klaar');
// daarna: python3 comprimeer.py (png naar jpg onder 190 kB)
