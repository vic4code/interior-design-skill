import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { createWalkthrough } from '../src/walkthrough.js';

class Element extends EventTarget {
  attrs = {};
  setAttribute(k, v) { this.attrs[k] = v; }
  focus() {}
  setPointerCapture() {}
}
function fixture({floor = true, obstacle = false} = {}) {
  const elements = new Map(['walk', 'walk-status', 'walk-tools', 'walk-forward', 'walk-back', 'walk-availability'].map(id => [id, new Element()]));
  globalThis.document = Object.assign(new EventTarget(), {hidden: false, getElementById: id => elements.get(id)});
  globalThis.window = new EventTarget();
  const model = new THREE.Group();
  if (floor) {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(6, 0.1, 6), new THREE.MeshBasicMaterial());
    mesh.position.y = -0.05;
    mesh.name = 'Actual floor';
    model.add(mesh);
  }
  if (obstacle) {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(6, 1, 0.1), new THREE.MeshBasicMaterial());
    mesh.position.y = 0.5;
    model.add(mesh);
  }
  model.updateMatrixWorld(true);
  const camera = new THREE.PerspectiveCamera(65);
  const canvas = new Element();
  let active = true;
  const walk = createWalkthrough(model, new THREE.Box3(new THREE.Vector3(-3, -.1, -3), new THREE.Vector3(3, 2.8, 3)), camera, canvas, () => active, () => {});
  return {walk, camera, canvas, elements, pause() {active = false;}};
}
const click = (f, id) => f.elements.get(id).dispatchEvent(new Event('click'));
function key(canvas, type, value) { const event = new Event(type, {cancelable: true}); event.key = value; canvas.dispatchEvent(event); }

test('forward/back change position at fixed eye height and FOV, reset restores pose', () => {
  const f = fixture(); f.walk.setEnabled(true);
  const start = f.camera.position.clone(); const orientation = f.camera.quaternion.clone();
  click(f, 'walk-forward');
  assert.ok(Math.abs(f.camera.position.distanceTo(start) - .35) < 1e-8);
  assert.ok(Math.abs(f.camera.position.y - 1.6) < 1e-7); assert.equal(f.camera.fov, 65);
  click(f, 'walk-back'); assert.ok(f.camera.position.distanceTo(start) < 1e-8);
  click(f, 'walk-forward'); f.walk.reset();
  assert.ok(f.camera.position.equals(start)); assert.ok(f.camera.quaternion.equals(orientation));
  f.walk.dispose();
});
test('swept steps stop at a thin obstacle and model floor boundary', () => {
  const f = fixture({obstacle: true}); f.walk.setEnabled(true);
  for (let i=0;i<40;i++) click(f, 'walk-forward');
  assert.ok(f.camera.position.z >= .25); // wall half-depth + 20 cm clearance
  assert.match(f.elements.get('walk-status').textContent, /障礙/);
  for (let i=0;i<40;i++) click(f, 'walk-back');
  assert.ok(f.camera.position.z <= 2.8); // real floor support under footprint
  f.walk.dispose();
});
test('unsupported floor disables walk; overview remains available', () => {
  const f=fixture({floor:false}); assert.equal(f.elements.get('walk').disabled, true);
  assert.equal(f.elements.get('walk-availability').hidden, false);
  f.walk.setEnabled(true); assert.equal(f.walk.enabled, false); f.walk.dispose();
});
test('tab exit clears held keys, long frames are capped, blur stops, dispose removes buttons', () => {
  const f=fixture(); f.walk.setEnabled(true); const start=f.camera.position.clone();
  key(f.canvas,'keydown','w'); f.walk.update(10);
  assert.ok(f.camera.position.distanceTo(start) <= .05500001);
  f.canvas.dispatchEvent(new Event('blur')); const stopped=f.camera.position.clone(); f.walk.update(.05);
  assert.ok(f.camera.position.equals(stopped));
  key(f.canvas,'keydown','w'); f.pause(); f.walk.update(.05); click(f,'walk-forward');
  assert.ok(f.camera.position.equals(stopped));
  f.walk.dispose(); click(f,'walk-back'); assert.ok(f.camera.position.equals(stopped));
});
test('floor triangle support rejects missing portions inside an overall bounding box', () => {
  // Two separated floor slabs leave a real hole at z=0: the model bounds alone
  // would permit crossing it. The actual triangle support must stop at the gap.
  const f=fixture(); f.walk.dispose();
  const group=new THREE.Group();
  for (const z of [-2,2]) { const mesh=new THREE.Mesh(new THREE.BoxGeometry(6,.1,2),new THREE.MeshBasicMaterial());mesh.position.set(0,-.05,z);mesh.name='floor';group.add(mesh); }
  const walk=createWalkthrough(group,new THREE.Box3(new THREE.Vector3(-3,-.1,-3),new THREE.Vector3(3,2.8,3)),f.camera,f.canvas,()=>true,()=>{});
  walk.setEnabled(true); for(let i=0;i<30;i++)click(f,'walk-forward');
  assert.ok(f.camera.position.z >= 1.2); walk.dispose();
});
