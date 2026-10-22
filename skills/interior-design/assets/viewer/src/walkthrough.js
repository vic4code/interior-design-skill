import * as THREE from "three";

// Conservative single-level preview, derived from actual floor meshes. No navmesh,
// physics engine, synthetic room rectangle or changes to the downloaded model.
export function createWalkthrough(model, bounds, camera, canvas, isActive, invalidate) {
  const floorMeshes = [];
  const boxes = [];
  model.updateMatrixWorld(true);
  model.traverse((node) => {
    if (!node.isMesh) return;
    const box = new THREE.Box3().setFromObject(node);
    const size = box.getSize(new THREE.Vector3());
    boxes.push(box);
    if (/floor|地板|地坪/i.test(node.name) && size.y < 0.2 &&
        Math.max(size.x, size.z) > 0.5 && box.max.y < bounds.min.y + 0.5) {
      floorMeshes.push(node);
    }
  });
  const ray = new THREE.Raycaster();
  const down = new THREE.Vector3(0, -1, 0);
  const margin = 0.2;
  const floorY = floorMeshes.length
    ? Math.max(...floorMeshes.map(node => new THREE.Box3().setFromObject(node).max.y))
    : bounds.min.y;
  const eyeY = floorY + 1.6; // glTF units are metres.
  const obstacles = boxes.filter(box => box.max.y > floorY + 0.16 && box.min.y < eyeY + 0.15);
  const origin = new THREE.Vector3();
  const footprint = [[0, 0], [margin, 0], [-margin, 0], [0, margin], [0, -margin]];
  function safe(x, z) {
    if (obstacles.some(box => x > box.min.x - margin && x < box.max.x + margin &&
        z > box.min.z - margin && z < box.max.z + margin)) return false;
    // Actual triangles keep holes, concave outlines and gaps out of the walk area.
    return footprint.every(([dx, dz]) => {
      origin.set(x + dx, floorY + 0.2, z + dz);
      ray.set(origin, down);
      ray.far = 0.4;
      return ray.intersectObjects(floorMeshes, false).some(hit => hit.face.normal.clone().transformDirection(hit.object.matrixWorld).y > 0.5 &&
        Math.abs(hit.point.y - floorY) < 0.15);
    });
  }
  const center = bounds.getCenter(new THREE.Vector3());
  const candidates = [];
  if (floorMeshes.length) {
    for (let ix = 1; ix < 20; ix++) for (let iz = 1; iz < 20; iz++) {
      const x = THREE.MathUtils.lerp(bounds.min.x, bounds.max.x, ix / 20);
      const z = THREE.MathUtils.lerp(bounds.min.z, bounds.max.z, iz / 20);
      candidates.push(new THREE.Vector3(x, eyeY, z));
    }
    const entry = new THREE.Vector3(center.x, eyeY, bounds.max.z - 0.8);
    candidates.sort((a, b) => a.distanceToSquared(entry) - b.distanceToSquared(entry));
  }
  const spawn = candidates.find(p => safe(p.x, p.z));
  let enabled = false;
  let yaw = 0;
  let pitch = 0;
  let drag;
  const keys = new Set();
  const abort = new AbortController();
  const on = (element, name, callback) => element.addEventListener(name, callback, {signal: abort.signal});
  const status = document.getElementById("walk-status");
  const button = document.getElementById("walk");
  button.disabled = !spawn;
  const availability = document.getElementById("walk-availability");
  availability.hidden = Boolean(spawn);
  availability.textContent = spawn ? "" : "此模型未找到可站立的單層地板，請使用旋轉檢視。";
  button.setAttribute("aria-describedby", "walk-availability");
  button.title = spawn ? "固定眼高 1.6 公尺，沿模型地板移動" : "未找到可安全站立的單層地板，請使用旋轉檢視";
  function orient() {
    camera.rotation.set(pitch, yaw, 0, "YXZ");
    invalidate();
  }
  function stop() { keys.clear(); drag = undefined; }
  function reset() {
    stop();
    if (!spawn) return;
    camera.position.copy(spawn);
    yaw = Math.atan2(spawn.x - center.x, spawn.z - center.z);
    pitch = -0.08;
    orient();
    status.textContent = "眼高 1.6 m · 拖曳環視，前進／後退；模型邊緣與障礙會停止移動。";
  }
  function move(forward, side = 0) {
    if (!enabled || !isActive() || document.hidden) return;
    const dx = -Math.sin(yaw) * forward + Math.cos(yaw) * side;
    const dz = -Math.cos(yaw) * forward - Math.sin(yaw) * side;
    const steps = Math.ceil(Math.hypot(dx, dz) / 0.08);
    let blocked = false;
    for (let i = 0; i < steps; i++) {
      const x = camera.position.x + dx / steps;
      const z = camera.position.z + dz / steps;
      if (!safe(x, z)) { blocked = true; break; }
      camera.position.set(x, eyeY, z);
    }
    const message = blocked ? "已到模型邊緣或障礙；可轉向或重設視角。" :
      "眼高 1.6 m · 拖曳環視，前進／後退。";
    if (status.textContent !== message) status.textContent = message;
    invalidate();
  }
  on(canvas, "pointerdown", event => {
    if (!enabled || drag || !event.isPrimary || event.button !== 0) return;
    canvas.focus({preventScroll: true});
    drag = {id: event.pointerId, x: event.clientX, y: event.clientY};
    canvas.setPointerCapture(event.pointerId);
  });
  on(canvas, "pointermove", event => {
    if (!enabled || drag?.id !== event.pointerId) return;
    yaw -= (event.clientX - drag.x) * 0.005;
    pitch = THREE.MathUtils.clamp(pitch - (event.clientY - drag.y) * 0.005, -0.65, 0.65);
    drag.x = event.clientX; drag.y = event.clientY;
    orient();
  });
  on(canvas, "pointerup", stop);
  on(canvas, "pointercancel", stop);
  on(canvas, "lostpointercapture", stop);
  const movementKeys = ["w", "s", "a", "d", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"];
  on(canvas, "keydown", event => {
    const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
    if (!enabled || !isActive() || !movementKeys.includes(key)) return;
    event.preventDefault(); keys.add(key);
  });
  on(canvas, "keyup", event => keys.delete(event.key.length === 1 ? event.key.toLowerCase() : event.key));
  on(canvas, "blur", stop);
  on(window, "blur", stop);
  on(document, "visibilitychange", stop);
  on(document.getElementById("walk-forward"), "click", () => move(0.35));
  on(document.getElementById("walk-back"), "click", () => move(-0.35));
  return {
    get enabled() { return enabled; },
    setEnabled(value) {
      enabled = Boolean(value && spawn);
      stop();
      button.setAttribute("aria-pressed", String(enabled));
      button.textContent = enabled ? "返回旋轉" : "走入空間";
      document.getElementById("walk-tools").hidden = !enabled;
      canvas.setAttribute("aria-label", enabled ? "室內步行：拖曳環視，W/S 或上下鍵前後移動，A/D 側移，左右鍵轉向" : "3D 空間：拖曳旋轉、滾輪縮放、方向鍵平移");
      if (enabled) { reset(); canvas.focus({preventScroll: true}); }
      invalidate();
    },
    reset,
    update(dt) {
      if (!enabled || !isActive() || document.hidden) { stop(); return; }
      if (!keys.size) return;
      const delta = Math.min(dt, 0.05);
      yaw += ((keys.has("ArrowLeft") ? 1 : 0) - (keys.has("ArrowRight") ? 1 : 0)) * delta;
      orient();
      const forward = Number(keys.has("w") || keys.has("ArrowUp")) - Number(keys.has("s") || keys.has("ArrowDown"));
      const side = Number(keys.has("d")) - Number(keys.has("a"));
      const scale = 1 / Math.max(1, Math.hypot(forward, side));
      move(forward * scale * delta * 1.1, side * scale * delta * 1.1);
    },
    dispose() { stop(); abort.abort(); },
  };
}
