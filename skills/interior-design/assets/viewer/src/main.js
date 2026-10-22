import "./style.css";
const $ = (id) => document.getElementById(id);
const rootBase = new URL("./generated/", document.baseURI);
const names = {
  "drawings.pdf": "完整工程圖冊",
  "native-coordination.pdf": "完整工程圖冊",
  "design-coordination.pdf": "完整工程圖冊",
  "plan.dxf": "可編輯平面 DXF",
  "scene.blend": "原始模型",
  "scene.glb": "3D 模型 GLB",
  "materials.csv": "材料明細",
  "openings.csv": "門窗明細",
  "furniture.csv": "家具明細",
  "joinery.csv": "櫃體內淨尺寸",
  "issues.csv": "施工前確認事項",
  "handoff.md": "交付說明",
};
const styleCopy = {
  mcm: [
    "Mid-century Modern",
    "溫潤木質、俐落的家具比例，讓日常留下時間的質感。",
  ],
  japandi: ["Japandi", "低彩度的自然材質與安靜留白，讓光線成為空間主角。"],
  contemporary: ["Contemporary", "柔和曲線與俐落量體，在細緻材質中找到平衡。"],
  bauhaus: ["Bauhaus", "以幾何線條、金屬與色彩，構築鮮明而有秩序的生活。"],
};
let base = rootBase,
  manifest,
  rootManifest,
  project = {},
  presentation,
  presentations = [],
  selectedViewId = "primary",
  selectedSpace = "all",
  layout,
  mep = [],
  selectedSheets = {},
  sheets = [],
  files = new Set(),
  modelFile,
  active = "render",
  lightingState = { time: "day", lights: true },
  modelController,
  modelPromise,
  packageVersion = 0,
  showingBase = false,
  zoom = 1,
  panX = 0,
  panY = 0,
  drag;
function status(message) {
  $("status").textContent = message;
}
function safePath(name) {
  return (
    typeof name === "string" &&
    name.length > 0 &&
    !/^(?:\/|\\|[a-z][a-z\d+.-]*:)/i.test(name) &&
    !name.split(/[\\/]/).some((s) => s === ".." || s === ".")
  );
}
function asset(name, from = base) {
  if (!safePath(name)) throw new Error("交付檔案路徑無效");
  const url = new URL(name.split("/").map(encodeURIComponent).join("/"), from);
  if (url.origin !== location.origin)
    throw new Error("交付檔案必須位於本機專案");
  return url.href;
}
function has(name) {
  return safePath(name) && files.has(name);
}
async function json(name, from = base) {
  const response = await fetch(asset(name, from));
  if (!response.ok) throw new Error(`無法讀取 ${name}（${response.status}）`);
  return response.json();
}
function link(name, label) {
  const a = document.createElement("a");
  a.href = asset(name);
  a.download = name.split("/").pop();
  const text = document.createElement("span");
  text.textContent = label;
  const arrow = document.createElement("span");
  arrow.textContent = "↗";
  arrow.setAttribute("aria-hidden", "true");
  a.append(text, arrow);
  return a;
}
function fact(label, value) {
  const group = document.createElement("div"),
    dt = document.createElement("dt"),
    dd = document.createElement("dd");
  dt.textContent = label;
  dd.textContent = value;
  group.append(dt, dd);
  $("facts").append(group);
}
function currentSheet() {
  const list = active === "mep" ? mep : sheets;
  return list.find((s) => s.file === $("sheet-select").value) || list[0];
}
function engineeringSheet() {
  return sheets.find((s) => /^(?:J301|N301)$/i.test(s.id)) ||
    sheets.find((s) => /detail|section|剖面|詳圖/i.test(`${s.kind || ""} ${s.title || ""}`)) || sheets[0];
}
function sheetOptions(list, preferred, previous) {
  $("sheet-select").replaceChildren();
  for (const sheet of list) {
    const option = document.createElement("option");
    option.value = sheet.file;
    option.textContent = `${sheet.id} · ${sheet.title || "尺寸圖面"}`;
    $("sheet-select").append(option);
  }
  $("sheet-select").value = list.some((s) => s.file === previous) ? previous : preferred?.file || list[0]?.file || "";
}
function updatePresentationInfo() {
  const labels = { "model-render": "模型基底 · 幾何檢查", concept: "IMAGE GEN · 風格概念" };
  $("presentation-badge").textContent = presentation ? labels[presentation.kind] || "IMAGE GEN · 空間完成模擬" : "尚無設計效果圖";
  const reviews = { pending: "生成圖像與模型配置待核對。", "accepted-for-visualization": "視覺呈現已核對；工程尺寸以圖面為準。", unavailable: "尚無設計效果圖。" };
  $("presentation-review").textContent = reviews[presentation?.review_status] || presentation?.review_status || "效果圖表達材質與光線，模型與圖面保存尺寸依據。";
  const provenance = typeof presentation?.provenance === "string" ? presentation.provenance : presentation?.provenance?.file;
  $("provenance").hidden = !has(provenance);
  if (has(provenance)) $("provenance").href = asset(provenance);
  $("base-toggle").hidden = !has(presentation?.base_image);
}
function galleryOptions() {
  const spaces = [...new Set(presentations.map((p) => p.space || "整體空間"))];
  if (!spaces.includes(selectedSpace)) selectedSpace = "all";
  $("space-select").replaceChildren();
  for (const [value, title] of [["all", "全部空間"], ...spaces.map((space) => [space, space])]) {
    const option = document.createElement("option"); option.value = value; option.textContent = title; $("space-select").append(option);
  }
  $("space-select").value = selectedSpace;
  const views = presentations.filter((p) => selectedSpace === "all" || (p.space || "整體空間") === selectedSpace);
  presentation = views.find((p) => p.id === selectedViewId) || views[0];
  selectedViewId = presentation?.id || "primary";
  $("view-select").replaceChildren(); $("view-thumbnails").replaceChildren();
  for (const view of views) {
    const option = document.createElement("option"); option.value = view.id; option.textContent = view.title || view.id; $("view-select").append(option);
    const button = document.createElement("button"); button.className = "view-thumbnail"; button.setAttribute("aria-pressed", String(view.id === selectedViewId));
    const img = document.createElement("img"); img.src = asset(view.image); img.alt = ""; img.loading = "lazy";
    const title = document.createElement("span"); title.textContent = view.title || view.id; button.append(img, title);
    button.onclick = () => { selectedViewId = view.id; showingBase = false; galleryOptions(); setMode("render"); };
    $("view-thumbnails").append(button);
  }
  $("view-select").value = selectedViewId;
  $("view-count").textContent = `${views.length} 個已完成視角`;
  updatePresentationInfo();
}
function imageFile() {
  return showingBase ? presentation?.base_image : presentation?.image;
}
function updateLighting() {
  lightingState = {
    time: $("lighting-time").value === "night" ? "night" : "day",
    lights: $("lighting-lights").value === "on",
  };
  $("lighting-summary").textContent = `${lightingState.time === "day" ? "白天" : "夜晚"} · ${lightingState.lights ? "開燈" : "關燈"} · 光線預覽`;
  modelController?.setLighting(lightingState);
}
function positionDrawing() {
  const image = $("plan");
  const limitX = image.clientWidth * (zoom - 1) / 2;
  const limitY = image.clientHeight * (zoom - 1) / 2;
  panX = Math.max(-limitX, Math.min(limitX, panX));
  panY = Math.max(-limitY, Math.min(limitY, panY));
  image.style.transform = `translate(${panX}px, ${panY}px) scale(${zoom})`;
}
function setZoom(value) {
  zoom = Math.max(1, Math.min(4, value));
  $("zoom-value").textContent = `${Math.round(zoom * 100)}%`;
  $("pan-controls").hidden = zoom === 1;
  $("drawing-viewport").dataset.zoomed = String(zoom > 1);
  if (zoom === 1) { panX = 0; panY = 0; }
  positionDrawing();
}
function panDrawing(direction) {
  if (zoom <= 1) return;
  const step = Math.max(40, $("drawing-viewport").clientWidth / 5);
  if (direction === "left") panX += step;
  if (direction === "right") panX -= step;
  if (direction === "up") panY += step;
  if (direction === "down") panY -= step;
  positionDrawing();
}
function updateImage() {
  const file = imageFile();
  if (has(file)) $("render").src = asset(file);
  $("render").alt = showingBase
    ? "同一空間與視角的幾何基底"
    : `${$("style-name").textContent} 空間設計效果；工程尺寸以圖面為準`;
  $("base-toggle").textContent = showingBase ? "查看設計效果" : "對照空間基底";
}
async function setMode(mode) {
  active = mode;
  const version = packageVersion;
  if (mode === "drawings") sheetOptions(sheets, engineeringSheet(), selectedSheets.drawings);
  if (mode === "mep") sheetOptions(mep, mep[0], selectedSheets.mep);
  document
    .querySelectorAll("[data-mode]")
    .forEach((b) =>
      b.setAttribute("aria-pressed", String(b.dataset.mode === mode)),
    );
  $("render").hidden = mode !== "render";
  $("model").hidden = mode !== "model";
  $("drawing-viewport").hidden = !["layout", "drawings", "mep"].includes(mode);
  $("sheet-controls").hidden = !["drawings", "mep"].includes(mode);
  $("gallery-controls").hidden = mode !== "render" || !presentations.length;
  $("view-thumbnails").hidden = mode !== "render" || presentations.length < 2;
  $("zoom-controls").hidden = !["layout", "drawings", "mep"].includes(mode);
  $("model-controls").hidden = mode !== "model";
  $("lighting-controls").hidden = mode !== "model";
  $("walk-tools").hidden = mode !== "model" || $("walk").getAttribute("aria-pressed") !== "true";
  $("presentation-controls").hidden = mode !== "render";
  const sheet = mode === "layout" ? layout : currentSheet();
  const file =
    mode === "render"
      ? imageFile()
      : mode === "model"
        ? modelFile
        : sheet?.file;
  const original = has(sheet?.original_file) && mode === "mep" ? sheet.original_file : file;
  const originalUrl = has(original) ? asset(original) + (sheet?.source_page && mode === "mep" ? `#page=${sheet.source_page}` : "") : "";
  $("current-download").hidden = !has(original);
  $("current-original").hidden = !has(original) || !["layout", "drawings", "mep"].includes(mode);
  if (has(original)) $("current-original").href = originalUrl;
  if (has(original)) {
    $("current-download").href = asset(original);
    $("current-download").download = original.split("/").pop();
  }
  const labels = {
    render: showingBase
      ? "空間幾何 · 視角參考"
      : presentation?.kind === "model-render"
        ? "模型基底 · 幾何檢查"
        : "IMAGE GEN · 空間設計效果",
    model: "3D 空間 · 旋轉檢視 / 走入空間",
    layout: "平面配置 · 家具位置與日常動線",
    mep: `${sheet?.id || ""} · 機電協調配置`,
    drawings: `${sheet?.id || ""} · ${sheet?.scale || "依圖面標註比例"}`,
  };
  $("view-label").textContent = labels[mode];
  $("mode-context").textContent = {
    layout: "先看空間怎麼使用：家具位置、門窗與動線。詳細定位、板厚與收口請切換工程圖面。",
    drawings: "給設計師與工班核對：尺寸定位、立面剖面、櫃體板厚與節點，依圖號查閱。",
    mep: sheet?.status ? `機電協調圖 · ${{ coordination_draft: "協調草案", concept: "概念配置", proposed: "設計提案", "coordination-only": "僅供協調" }[sheet.status] || sheet.status}；設備容量、回路與管線仍需依工程專業覆核。` : "燈具、開關、插座與設備定位。實際提供範圍以圖面為準。",
    render: "選擇已完成的空間與視角，查看 image gen 設計效果。",
    model: "旋轉或走入空間，核對家具配置與尺度；切換白天、夜晚及室內燈，預覽光線層次。",
  }[mode];
  if (mode === "mep" && sheet?.reference) $("mode-context").textContent += ` ${sheet.reference}`;
  $("hint").textContent =
    mode === "render"
      ? presentation?.kind === "model-render"
        ? "模型基底用於幾何檢查。"
        : presentation?.kind === "concept"
          ? "風格概念圖；尚未與實際空間幾何核對。"
          : "以空間輪廓與視角引導生成；材質與細節為設計模擬，尺寸仍以圖面為準。"
      : mode === "model"
        ? "旋轉模式可縮放與平移；走入空間後拖曳環視，按前進／後退或 W/S、上下鍵移動。單層地板與障礙檢查為保守預覽。光線為視覺預覽；燈位、回路與設備規格請見機電圖面。"
        : "整張圖面自動符合畫框；放大後可拖曳或用方向鍵平移，也可開啟原圖。施工前請覆核尺寸、五金與現場條件。";
  status("");
  if (["layout", "drawings", "mep"].includes(mode) && sheet) {
    $("plan").src = asset(sheet.file);
    $("plan").alt = `${sheet.id ? `${sheet.id} · ` : ""}${sheet.title || "工程尺寸圖"}`;
    $("sheet-original").href = originalUrl;
    $("sheet-count").textContent =
      `${(mode === "mep" ? mep : sheets).indexOf(sheet) + 1} / ${(mode === "mep" ? mep : sheets).length}`;
    setZoom(1);
  }
  if (mode === "render") updateImage();
  if (mode === "model") {
    if (!has(modelFile)) {
      status("此交付包尚未包含 3D 模型。");
      return;
    }
    if (modelController) return;
    status("載入空間模型…");
    const url = asset(modelFile);
    try {
      modelPromise ??= import("./model.js").then((m) =>
        m.loadModel(
          () => active === "model",
          url,
          () => version === packageVersion,
        ),
      );
      const controller = await modelPromise;
      if (version !== packageVersion) {
        controller?.dispose();
        return;
      }
      modelController = controller;
      modelController?.setLighting(lightingState);
      if (active === "model") status("");
    } catch (error) {
      if (version === packageVersion) {
        modelPromise = undefined;
        status(`模型載入失敗：${error.message}。仍可查看設計效果與圖面。`);
      }
    }
  }
}
async function loadPackage(data, from, variant) {
  const version = ++packageVersion;
  modelController?.dispose();
  modelController = undefined;
  modelPromise = undefined;
  base = from;
  manifest = data;
  files = new Set(
    (data.files || []).filter((f) => safePath(f.name)).map((f) => f.name),
  );
  showingBase = false;
  selectedSheets = {};
  if (
    !["1.0", "2.0"].includes(data.schema_version) ||
    !Array.isArray(data.files)
  )
    throw new Error("不支援的交付包格式");
  if (data.schema_version === "1.0") {
    const p = await json("project.json");
    if (version !== packageVersion) return;
    project = {
      ...p.project,
      area_m2: (p.room.width * p.room.depth) / 1e6,
      ceiling_height_mm: p.room.height,
    };
    presentation = has("render.png")
      ? { image: "render.png", kind: "model-render" }
      : undefined;
    modelFile = has("scene.glb") ? "scene.glb" : undefined;
    sheets = data.files
      .filter((f) => /\.svg$/i.test(f.name))
      .map((f) => ({
        id: f.name.replace(/\.svg$/i, ""),
        title: "尺寸圖面",
        file: f.name,
      }));
  } else {
    project = data.project || {};
    presentation = data.presentation;
    modelFile = typeof data.model === "string" ? data.model : data.model?.file;
    sheets = (data.sheets || []).filter((s) => has(s.file));
  }
  $("project-name").textContent =
    rootManifest.project?.name || project.name || "空間設計提案";
  document.title = `${$("project-name").textContent} · Interior`;
  $("brief").textContent = rootManifest.project?.brief || project.brief || "";
  $("facts").replaceChildren();
  if (Number.isFinite(project.area_m2) && project.area_m2 > 0)
    fact("室內面積", `${Number(project.area_m2.toFixed(2))} m²`);
  if (
    Number.isFinite(project.ceiling_height_mm) &&
    project.ceiling_height_mm > 0
  )
    fact("淨高", `${project.ceiling_height_mm} mm`);
  if (sheets.length) fact("圖面", `${sheets.length} 張`);
  if (project.revision || data.revision)
    fact("版本", project.revision || data.revision);
  const style = variant?.id || data.style_name || "";
  const copy = styleCopy[style];
  $("style-name").textContent =
    variant?.label || copy?.[0] || project.style || "空間提案";
  $("style-description").textContent =
    variant?.description ||
    project.design_note ||
    copy?.[1] ||
    "保留既有格局，整合空間配置、材質提案與工程細節。";
  presentations = (Array.isArray(data.presentations) && data.presentations.length ? data.presentations : presentation ? [{ id: "primary", title: "主要視角", ...presentation }] : []).filter((p) => has(p.image));
  const usedIds = new Set();
  presentations = presentations.filter((p) => { if (usedIds.has(p.id)) return false; usedIds.add(p.id); return true; });
  layout = typeof data.layout === "string" ? { file: data.layout, title: "家具配置" } : data.layout;
  if (!has(layout?.file)) layout = undefined;
  mep = (Array.isArray(data.mep) ? data.mep : []).filter((sheet) => has(sheet.file));
  galleryOptions();
  $("mep-availability").hidden = mep.length > 0;
  $("mep-availability").textContent = "此版本尚未提供機電配置。需要燈具／開關、插座弱電，以及適用空間的空調、給排水協調圖；完整電氣、空調與管徑設計須由相應工程專業確認。";
  $("package-status").textContent =
    data.status === "coordination_draft"
      ? "工程協調版本。施工前需完成圖面列示的現場尺寸、五金與固定方式覆核。"
      : data.status === "construction_ready"
        ? "圖面發行狀態與施工條件請見交付說明。"
        : "尺寸假設與施工前確認事項請見圖面。";
  sheetOptions(sheets, engineeringSheet());
  $("downloads").replaceChildren();
  const drawingPdfs = data.files.filter((f) => /\.pdf$/i.test(f.name) && !f.name.startsWith("mep/"));
  const primary = ["native-coordination.pdf", "design-coordination.pdf", "drawings.pdf"]
    .map((name) => drawingPdfs.find((f) => f.name.split("/").pop() === name))
    .find(Boolean) || drawingPdfs[0];
  $("primary-pdf").hidden = !primary;
  if (primary) $("primary-pdf").href = asset(primary.name);
  for (const file of data.files) {
    const name = file.name.split("/").pop();
    if (names[name] || /\.zip$/i.test(name))
      $("downloads").append(link(file.name, names[name] || "完整設計包 ZIP"));
  }
  $("reviews").replaceChildren();
  if (has("review.json")) {
    const review = await json("review.json");
    if (version !== packageVersion) return;
    for (const item of Array.isArray(review)
      ? review
      : review.items || review.issues || []) {
      const li = document.createElement("li");
      li.textContent =
        item.message ||
        item.topic ||
        item.description ||
        item.title ||
        String(item);
      $("reviews").append(li);
    }
  }
  $("review-section").hidden = !$("reviews").children.length;
  $("review-count").textContent = $("reviews").children.length
    ? `${$("reviews").children.length} 項待確認事項，詳見下方。`
    : "";
  const available = {
    render: has(presentation?.image),
    model: has(modelFile),
    layout: has(layout?.file),
    mep: mep.length > 0,
    drawings: sheets.length > 0,
  };
  document.querySelectorAll("[data-mode]").forEach((b) => {
    b.disabled = !available[b.dataset.mode];
    b.title = b.disabled ? (b.dataset.mode === "mep" ? "此交付包尚無機電圖；詳見下方說明。" : "此交付包尚未提供此內容。") : "";
    b.onclick = () => setMode(b.dataset.mode);
  });
  document
    .querySelectorAll("[data-variant]")
    .forEach((b) =>
      b.setAttribute("aria-pressed", String(b.dataset.variant === variant?.id)),
    );
  const first = available[active]
    ? active
    : ["render", "layout", "model", "drawings", "mep"].find((m) => available[m]);
  if (!first) throw new Error("此交付包尚無可檢視的內容");
  await setMode(first);
}
let selection = 0;
async function chooseVariant(variant) {
  const token = ++selection;
  status("切換設計風格…");
  try {
    if (!safePath(variant.manifest)) throw new Error("風格檔案路徑無效");
    const data = await json(variant.manifest, rootBase);
    if (token !== selection) return;
    await loadPackage(
      data,
      new URL("./", asset(variant.manifest, rootBase)),
      variant,
    );
  } catch (error) {
    if (token === selection) status(`無法切換風格：${error.message}`);
  }
}
async function init() {
  try {
    rootManifest = await json("manifest.json", rootBase);
    if (Array.isArray(rootManifest.variants) && rootManifest.variants.length) {
      $("variants-section").hidden = false;
      for (const variant of rootManifest.variants) {
        const button = document.createElement("button");
        button.className = "variant";
        button.dataset.variant = variant.id;
        button.setAttribute("aria-pressed", "false");
        if (safePath(variant.thumbnail)) {
          const img = document.createElement("img");
          img.src = asset(variant.thumbnail, rootBase);
          img.alt = "";
          img.loading = "lazy";
          button.append(img);
        } else {
          const swatch = document.createElement("span");
          swatch.className = "swatch";
          if (/^#[a-f\d]{3,8}$/i.test(variant.swatch || ""))
            swatch.style.setProperty("--swatch", variant.swatch);
          button.append(swatch);
        }
        const label = document.createElement("span");
        label.textContent = variant.label;
        button.append(label);
        button.onclick = () => chooseVariant(variant);
        $("variants").append(button);
      }
      await chooseVariant(
        rootManifest.variants.find(
          (v) => v.id === rootManifest.default_variant,
        ) || rootManifest.variants[0],
      );
    } else await loadPackage(rootManifest, rootBase);
  } catch (error) {
    status(`無法載入設計包：${error.message}`);
  }
}
$("sheet-select").onchange = () => { const mode = active === "mep" ? "mep" : "drawings"; selectedSheets[mode] = $("sheet-select").value; setMode(mode); };
$("space-select").onchange = () => { selectedSpace = $("space-select").value; showingBase = false; galleryOptions(); setMode("render"); };
$("view-select").onchange = () => { selectedViewId = $("view-select").value; showingBase = false; galleryOptions(); setMode("render"); };
$("lighting-time").onchange = updateLighting;
$("lighting-lights").onchange = updateLighting;
$("base-toggle").onclick = () => {
  showingBase = !showingBase;
  setMode("render");
};
$("zoom-in").onclick = () => setZoom(zoom + 0.5);
$("zoom-out").onclick = () => setZoom(zoom - 0.5);
$("zoom-fit").onclick = () => setZoom(1);
document.querySelectorAll("[data-pan]").forEach((button) => { button.onclick = () => panDrawing(button.dataset.pan); });
$("plan").ondragstart = (event) => event.preventDefault();
$("drawing-viewport").onpointerdown = (event) => {
  if (zoom <= 1 || (event.pointerType === "mouse" && event.button !== 0)) return;
  drag = { id: event.pointerId, x: event.clientX, y: event.clientY, panX, panY };
  $("drawing-viewport").setPointerCapture(event.pointerId);
  $("drawing-viewport").dataset.dragging = "true";
};
$("drawing-viewport").onpointermove = (event) => {
  if (!drag || drag.id !== event.pointerId) return;
  panX = drag.panX + event.clientX - drag.x; panY = drag.panY + event.clientY - drag.y;
  positionDrawing();
};
function endPan() { drag = undefined; $("drawing-viewport").dataset.dragging = "false"; }
$("drawing-viewport").onpointerup = endPan;
$("drawing-viewport").onpointercancel = endPan;
$("drawing-viewport").onlostpointercapture = endPan;
$("drawing-viewport").onkeydown = (event) => {
  const direction = { ArrowLeft: "left", ArrowRight: "right", ArrowUp: "up", ArrowDown: "down" }[event.key];
  if (zoom > 1 && direction) { event.preventDefault(); panDrawing(direction); }
};
window.addEventListener("resize", positionDrawing);
window.addEventListener("pagehide", () => {
  packageVersion++;
  modelController?.dispose();
});
document.querySelectorAll("[data-mode]").forEach((b) => (b.disabled = true));
init();
