// Maintainer: rasterize the actual SVG sources on a shared, borderless 4:3 canvas.
// Requires Playwright and Chrome; set PLAYWRIGHT_MODULE for a local installation.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..');
const folder = path.join(root, 'docs/showcase/five-deliverables');
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 900, height: 675 }, deviceScaleFactor: 1 });
    const provenance = JSON.parse(fs.readFileSync(path.join(folder, 'provenance.json')));
    for (const [name, source] of [
      ['01-layout.jpg', 'docs/showcase/five-deliverables/layout.svg'],
      ['04-mep.jpg', 'docs/showcase/drawings/A102.svg'],
      ['05-engineering.jpg', 'docs/showcase/drawings/J301.svg'],
    ]) {
      const svg = fs.readFileSync(path.join(root, source)).toString('base64');
      await page.setContent(`<style>html,body{margin:0;width:100%;height:100%;background:#fff}img{display:block;width:100%;height:100%;object-fit:contain}</style><img src="data:image/svg+xml;base64,${svg}">`);
      await page.locator('img').evaluate(img => img.decode());
      await page.screenshot({ path: path.join(folder, name), type: 'jpeg', quality: 94 });
      const entry = provenance.previews[name];
      entry.image_sha256 = hash(path.join(folder, name));
      entry.width = 900;
      entry.height = 675;
      if (entry.svg) entry.svg_sha256 = hash(path.join(root, entry.svg));
      else entry.source_sha256 = hash(path.join(root, source));
      entry.method = 'Browser rasterization; white 900 × 675 canvas, contain without stretching, colored mat or added frame. Original drawing sheet borders retained.';
    }
    fs.writeFileSync(path.join(folder, 'provenance.json'), JSON.stringify(provenance, null, 2) + '\n');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
