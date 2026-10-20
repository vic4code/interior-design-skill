import './style.css';

const $ = (id) => document.getElementById(id);
const base = '/generated/';
let manifest, active = 'render', modelPromise;
const labels = { render: '1920 × 1440 / PNG', model: 'GLB / 可旋轉、縮放', plan: 'A101 / A3 · 1:50 · mm' };
const files = { render: 'render.png', model: 'scene.glb', plan: 'A101.svg' };
const hints = { render: '光線、材質與比例的第一輪對話。', model: '拖曳旋轉，滾輪縮放；鍵盤方向鍵可平移。', plan: '以標註尺寸為準。列印請使用 A3、100% 比例。' };
const names = { 'drawings.pdf': '平面＋四向牆面立面 / PDF', 'plan.dxf': '可編輯平面 / DXF', 'scene.blend': 'Blender 原始場景 / BLEND', 'scene.glb': '三維模型 / GLB', 'render.png': '高清渲染 / PNG', 'materials.csv': '淨面積與材質表 / CSV', 'openings.csv': '門窗尺寸表 / CSV', 'furniture.csv': '家具位置與尺寸 / CSV', 'project.json': '完整專案尺寸 / JSON', 'handoff.md': '交付說明與待確認事項 / MD' };

function status(text) { $('status').textContent = text; }
async function getJSON(name) {
  const response = await fetch(base + name);
  if (!response.ok) throw new Error(`無法讀取 ${name}（${response.status}）`);
  return response.json();
}
function has(name) { return manifest.files.some((f) => f.name === name); }
function download(name, label) {
  const link = document.createElement('a'); link.href = base + name; link.download = name;
  const text = document.createElement('span'); text.textContent = label;
  const arrow = document.createElement('span'); arrow.textContent = '↗'; arrow.setAttribute('aria-hidden', 'true');
  link.append(text, arrow); return link;
}
async function setMode(mode) {
  active = mode;
  document.querySelectorAll('[data-mode]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.mode === mode)));
  ['render', 'model', 'plan'].forEach((id) => { $(id).hidden = id !== mode; });
  $('view-label').textContent = labels[mode]; $('hint').textContent = hints[mode];
  $('model-controls').hidden = mode !== 'model' || !has('scene.glb');
  const link = $('current-download'); link.href = base + files[mode]; link.download = files[mode];
  link.hidden = !has(files[mode]);
  status('');
  if (!has(files[mode])) { status('此專案尚未產出這個檔案；請先執行完整 demo 建置。'); return; }
  if (mode === 'model') {
    status('載入三維空間…');
    try {
      modelPromise ??= import('./model.js').then((module) => module.loadModel(() => active === 'model')); await modelPromise;
      if (active === 'model') status('');
    } catch (error) { modelPromise = undefined; if (active === 'model') status(`3D 載入失敗：${error.message}。仍可下載模型或查看渲染圖。`); }
  }
}

async function init() {
  try {
    manifest = await getJSON('manifest.json');
    if (manifest.schema_version !== '1.0' || !Array.isArray(manifest.files)) throw new Error('不支援的交付包版本');
    const data = await getJSON('project.json');
    $('project-name').textContent = data.project.name; $('brief').textContent = data.project.brief;
    const facts = [['室內面積', `${(data.room.width * data.room.depth / 1e6).toFixed(1)} m²`], ['淨高', `${data.room.height} mm`], ['版本', data.project.revision]];
    facts.forEach(([key, value]) => { const div = document.createElement('div'); const dt = document.createElement('dt'); const dd = document.createElement('dd'); dt.textContent = key; dd.textContent = value; div.append(dt, dd); $('facts').append(div); });
    for (const [name, label] of Object.entries(names)) if (has(name)) $('downloads').append(download(name, label));
    const reviews = await getJSON('review.json');
    const translations = {R00:'尺寸尚未覆核：請先丈量現場，勿直接下單。',R01:'確認現場尺寸、牆體構造、地坪高程與門窗。',R02:'確認門扇、開啟方向、五金、通行淨寬及家具動線。',R03:'由專業人員補齊照明、插座、水電、空調與天花配置。',R04:'補齊木作接合、固定方式、基層、防火與防水節點。',R05:'確認當地法規、申請需求及各專業的覆核責任。',R06:'材料表是幾何淨面積，尚未加入損耗、收邊或施工層次。'};
    reviews.forEach((issue) => { const li = document.createElement('li'); li.textContent = translations[issue.id] ?? `${issue.topic}: ${issue.detail}`; $('reviews').append(li); });
    $('review-count').textContent = `${reviews.length} 項待確認 · 協調草圖，非施工核定版`;
    ['render', 'plan'].forEach((id) => { $(id).onerror = () => { if (active === id) status('圖片無法載入，請重新產出交付包。'); }; if (has(files[id])) $(id).src = base + files[id]; });
    document.querySelectorAll('[data-mode]').forEach((button) => { button.disabled = false; button.onclick = () => setMode(button.dataset.mode); });
    await setMode(has('render.png') ? 'render' : 'plan');
  } catch (error) {
    $('project-name').textContent = '尚未建立設計交付包';
    status(`${error.message}。請在 skill 目錄執行 .venv/bin/python scripts/project.py build assets/example-project.json --out assets/viewer/public/generated --blender，再重新整理。`);
    $('current-download').hidden = true;
  }
}
document.querySelectorAll('[data-mode]').forEach((button) => { button.disabled = true; });
init();
