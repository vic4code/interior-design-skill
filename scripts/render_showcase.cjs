// Maintainer: rasterize the actual SVG sources on a shared, borderless 4:3 canvas.
// Requires Playwright and Chrome; set PLAYWRIGHT_MODULE for a local installation.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { execFileSync } = require('node:child_process');
const root = path.resolve(__dirname, '..');
const folder = path.join(root, 'docs/showcase/five-deliverables');
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');

(async () => {
  // Generate each language from the same geometry and source furniture names.
  execFileSync(process.env.INTERIOR_PYTHON || 'python3', ['-c', `
import copy, json, sys
from pathlib import Path
root = Path(sys.argv[1])
sys.path.insert(0, str(root/'skills/interior-design/scripts/_internal'))
from layout_preview import structured_layout
project = json.loads((root/'skills/interior-design/assets/style-studies/project.json').read_text())
for language, filename in [('en', 'layout.svg'), ('zh-TW', 'layout-zh-TW.svg')]:
    localized = copy.deepcopy(project)
    for item in localized['furniture']:
        names = item['name'].split(' / ', 1)
        item['name'] = names[-1] if language == 'en' else names[0]
    (root/'docs/showcase/five-deliverables'/filename).write_text(structured_layout(localized))
`, root]);
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 900, height: 675 }, deviceScaleFactor: 1 });
    const provenance = JSON.parse(fs.readFileSync(path.join(folder, 'provenance.json')));
    provenance.previews['01-layout.jpg'].language = 'en';
    provenance.previews['01-layout-zh-TW.jpg'] = {
      ...provenance.previews['01-layout.jpg'],
      svg: 'docs/showcase/five-deliverables/layout-zh-TW.svg',
      language: 'zh-TW',
    };
    for (const [name, source] of [
      ['01-layout.jpg', 'docs/showcase/five-deliverables/layout.svg'],
      ['01-layout-zh-TW.jpg', 'docs/showcase/five-deliverables/layout-zh-TW.svg'],
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
