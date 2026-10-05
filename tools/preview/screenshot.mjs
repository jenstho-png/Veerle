import { chromium } from 'playwright-core';
const b = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium' });
const out = [];
for (const [name, w] of [320, 390, 768, 1024, 1440, 2560, 3840].map((w) => ['home', w]).concat([['over-ons', 1440], ['over-ons', 390], ['faq', 390]])) {
  const p = await b.newPage({ viewport: { width: w, height: 900 } });
  await p.goto(`file://${new URL('out/', import.meta.url).pathname}${name}.html`);
  await p.evaluate(() => document.querySelectorAll('.surf-reveal').forEach(e => e.classList.add('is-in')));
  await p.waitForTimeout(300);
  const ov = await p.evaluate(() => [document.documentElement.scrollWidth, innerWidth]);
  out.push(`${name}@${w}: scrollWidth=${ov[0]} innerWidth=${ov[1]}`);
  await p.screenshot({ path: new URL('out/', import.meta.url).pathname + `${name}-${w}.png`, fullPage: true });
  await p.close();
}
console.log(out.join('\n')); await b.close();
