import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
const $ = (id) => document.getElementById(id);
const base = '/generated/';
export async function loadModel(isActive) {
  const host = $('model');
  let renderer;
  try { renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true }); }
  catch { throw new Error('瀏覽器目前不支援 WebGL'); }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#e9e4d9');
  scene.add(new THREE.HemisphereLight(0xffffff, 0x716b59, 3));
  const light = new THREE.DirectionalLight(0xffedcf, 4); light.position.set(4, 8, 5); scene.add(light);
  const camera = new THREE.PerspectiveCamera(40, 1, .01, 200);
  host.replaceChildren(renderer.domElement);
  renderer.domElement.tabIndex = 0; renderer.domElement.setAttribute('aria-label', '3D 空間：拖曳旋轉、滾輪縮放、方向鍵平移');
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true; controls.autoRotate = !matchMedia('(prefers-reduced-motion: reduce)').matches;
  controls.autoRotateSpeed = .35; controls.listenToKeyEvents(renderer.domElement);
  let gltf;
  try { gltf = await new GLTFLoader().loadAsync(base + 'scene.glb'); }
  catch (error) { controls.dispose(); renderer.dispose(); host.replaceChildren(); throw error; }
  scene.add(gltf.scene);
  const bounds = new THREE.Box3().setFromObject(gltf.scene); const center = bounds.getCenter(new THREE.Vector3());
  const size = bounds.getSize(new THREE.Vector3()); const span = Math.max(size.x, size.y, size.z);
  function reset() { camera.position.copy(center).add(new THREE.Vector3(span, span * .85, span * 1.15)); controls.target.copy(center); controls.update(); }
  reset(); controls.minDistance = span * .3; controls.maxDistance = span * 4;
  const cut = [];
  gltf.scene.traverse((node) => { if (/^wall_(south|east|corner)|^opening_(south|east)_/.test(node.name)) cut.push(node); });
  const toggleWalls = () => { cut.forEach((node) => { node.visible = $('walls').checked; }); }; toggleWalls();
  $('walls').onchange = toggleWalls; $('reset').onclick = reset;
  function rotateLabel() { $('rotate').textContent = controls.autoRotate ? '暫停旋轉' : '開始旋轉'; }
  rotateLabel(); $('rotate').onclick = () => { controls.autoRotate = !controls.autoRotate; rotateLabel(); };
  function resize() {
    if (!host.clientWidth || !host.clientHeight) return;
    camera.aspect = host.clientWidth / host.clientHeight; camera.updateProjectionMatrix();
    renderer.setSize(host.clientWidth, host.clientHeight, false);
  }
  const observer = new ResizeObserver(resize); observer.observe(host); resize();
  renderer.setAnimationLoop(() => { if (!isActive() || document.hidden) return; controls.update(); renderer.render(scene, camera); });
  window.addEventListener('pagehide', () => { observer.disconnect(); controls.dispose(); renderer.dispose(); }, { once: true });
}
