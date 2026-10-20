import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
const $ = (id) => document.getElementById(id);
export async function loadModel(
  isActive,
  url = "/generated/scene.glb",
  isCurrent = () => true,
) {
  const host = $("model");
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true });
  } catch {
    throw new Error("瀏覽器目前不支援 WebGL");
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.85;
  renderer.localClippingEnabled = true;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color("#e9e4d9");
  const pmrem = new THREE.PMREMGenerator(renderer);
  const room = new RoomEnvironment();
  const environment = pmrem.fromScene(room, 0.04);
  scene.environment = environment.texture;
  scene.environmentIntensity = 0.55;
  room.dispose();
  pmrem.dispose();
  scene.add(new THREE.HemisphereLight(0xfffbf3, 0x72756c, 0.65));
  const light = new THREE.DirectionalLight(0xfff5e7, 1.5);
  light.position.set(4, 8, 5);
  scene.add(light);
  const camera = new THREE.PerspectiveCamera(40, 1, 0.01, 200);
  host.replaceChildren(renderer.domElement);
  renderer.domElement.tabIndex = 0;
  renderer.domElement.setAttribute(
    "aria-label",
    "3D 空間：拖曳旋轉、滾輪縮放、方向鍵平移",
  );
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.autoRotate = false;
  controls.autoRotateSpeed = 0.35;
  controls.listenToKeyEvents(renderer.domElement);
  let gltf;
  try {
    gltf = await new GLTFLoader().loadAsync(url);
  } catch (error) {
    controls.dispose();
    environment.dispose();
    renderer.dispose();
    renderer.domElement.remove();
    throw error;
  }
  let disposed = false;
  function disposeModel() {
    if (disposed) return;
    disposed = true;
    renderer.setAnimationLoop(null);
    gltf.scene.traverse((node) => {
      node.geometry?.dispose();
      for (const material of Array.isArray(node.material)
        ? node.material
        : [node.material]) {
        if (!material) continue;
        Object.values(material).forEach((value) => {
          if (value?.isTexture) value.dispose();
        });
        material.dispose();
      }
    });
    controls.dispose();
    environment.dispose();
    renderer.dispose();
    renderer.domElement.remove();
  }
  if (!isCurrent()) {
    disposeModel();
    return { dispose: disposeModel };
  }
  scene.add(gltf.scene);
  const bounds = new THREE.Box3().setFromObject(gltf.scene);
  if (bounds.isEmpty()) {
    controls.dispose();
    environment.dispose();
    renderer.dispose();
    renderer.domElement.remove();
    throw new Error("模型沒有可檢視的幾何");
  }
  const center = bounds.getCenter(new THREE.Vector3());
  const size = bounds.getSize(new THREE.Vector3());
  const span = Math.max(size.x, size.y, size.z);
  const radius = bounds.getBoundingSphere(new THREE.Sphere()).radius;
  let userMoved = false;
  controls.addEventListener("start", () => {
    userMoved = true;
  });
  // A dollhouse view keeps the floor and furnishings readable on first open.
  // This is a display operation only: the downloaded model stays unchanged.
  const cutHeight = bounds.min.y + size.y * 0.42;
  const sectionPlane = new THREE.Plane(new THREE.Vector3(0, -1, 0), cutHeight);
  const cutCenter = center.clone();
  cutCenter.y = bounds.min.y + (cutHeight - bounds.min.y) / 2;
  function reset() {
    const vertical = THREE.MathUtils.degToRad(camera.fov / 2);
    const horizontal = Math.atan(Math.tan(vertical) * camera.aspect);
    const distance = (radius / Math.sin(Math.min(vertical, horizontal))) * 1.08;
    camera.position
      .copy($("walls").checked ? center : cutCenter)
      .add(
        new THREE.Vector3(1, 1.45, 1.15).normalize().multiplyScalar(distance),
      );
    camera.near = Math.max(span / 10000, 0.001);
    camera.far = Math.max(distance * 15, span * 20);
    camera.updateProjectionMatrix();
    controls.target.copy($("walls").checked ? center : cutCenter);
    controls.update();
    userMoved = false;
  }
  controls.minDistance = span * 0.15;
  controls.maxDistance = span * 15;
  const cut = [];
  const sectionMaterials = [];
  const nodeBounds = new THREE.Box3();
  const nodeSize = new THREE.Vector3();
  gltf.scene.traverse((node) => {
    if (!node.isMesh) return;
    if (
      /^wall_(south|east|corner)|^opening_(south|east)_|^(south|east)[ _]plaster[ _]wall|^Flush[ _]timber[ _]door/.test(
        node.name,
      )
    )
      cut.push({ node, visible: node.visible });
    nodeBounds.setFromObject(node);
    nodeBounds.getSize(nodeSize);
    const broad =
      Math.max(nodeSize.x, nodeSize.z) > Math.max(size.x, size.z) * 0.45;
    const tall = nodeSize.y > size.y * 0.65;
    const overhead = nodeBounds.min.y > cutHeight;
    const architectural = /wall|ceiling|roof|plaster|牆|天花|屋頂/i.test(node.name);
    // Imported ceilings are often split into small anonymous material meshes.
    // Their position identifies the obstruction even without semantic names.
    if (!architectural && !overhead && !(broad && tall)) return;
    // Clone per mesh so a shared wall/furniture material cannot clip furniture.
    const materials = (Array.isArray(node.material)
      ? node.material
      : [node.material]
    ).map((material) => {
      const clone = material.clone();
      sectionMaterials.push({ material: clone, original: clone.clippingPlanes });
      return clone;
    });
    node.material = Array.isArray(node.material) ? materials : materials[0];
  });
  $("walls").checked = false;
  $("walls").parentElement.hidden = !cut.length && !sectionMaterials.length;
  const toggleWalls = () => {
    const complete = $("walls").checked;
    cut.forEach(({ node, visible }) => {
      node.visible = complete ? visible : false;
    });
    sectionMaterials.forEach(({ material, original }) => {
      // Authored cutaway faces keep their remaining window/curtain context.
      // Anonymous imported envelopes use the generic horizontal section.
      material.clippingPlanes =
        complete || cut.length
          ? original
          : [...(original || []), sectionPlane];
      material.needsUpdate = true;
    });
    controls.target.copy(complete ? center : cutCenter);
    controls.update();
  };
  toggleWalls();
  $("walls").onchange = toggleWalls;
  $("reset").onclick = reset;
  function rotateLabel() {
    $("rotate").textContent = controls.autoRotate ? "暫停旋轉" : "開始旋轉";
  }
  rotateLabel();
  $("rotate").onclick = () => {
    controls.autoRotate = !controls.autoRotate;
    rotateLabel();
  };
  function resize() {
    if (!host.clientWidth || !host.clientHeight) return;
    camera.aspect = host.clientWidth / host.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(host.clientWidth, host.clientHeight, false);
    if (!userMoved) reset();
  }
  const observer = new ResizeObserver(resize);
  observer.observe(host);
  resize();
  renderer.setAnimationLoop(() => {
    if (!isActive() || document.hidden) return;
    controls.update();
    renderer.render(scene, camera);
  });
  return {
    dispose() {
      observer.disconnect();
      disposeModel();
    },
  };
}
