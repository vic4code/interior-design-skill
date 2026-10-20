import * as THREE from "three";

// This is a qualitative design preview. Source emitters anchor the warm light
// where available; it does not replace a lighting calculation or a fixture plan.
export function createLightingPreview(scene, model, renderer, bounds) {
  const size = bounds.getSize(new THREE.Vector3());
  const center = bounds.getCenter(new THREE.Vector3());
  const span = Math.max(size.x, size.z, size.y);
  const hemispheric = new THREE.HemisphereLight(0xe7efff, 0x675344, 0.5);
  const sun = new THREE.DirectionalLight(0xfff0d5, 2.1);
  sun.position
    .copy(center)
    .add(new THREE.Vector3(-0.7, 1.2, 0.55).multiplyScalar(span));
  sun.target.position.copy(center);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.left = sun.shadow.camera.bottom = -span * 0.7;
  sun.shadow.camera.right = sun.shadow.camera.top = span * 0.7;
  sun.shadow.camera.near = span * 0.01;
  sun.shadow.camera.far = span * 4;
  sun.shadow.normalBias = span * 0.0004;
  sun.shadow.bias = -0.00008;
  const indirect = new THREE.HemisphereLight(0xffd2a0, 0x70503b, 0.1);
  scene.add(hemispheric, sun, sun.target, indirect);

  const emitters = [];
  const namedFixtures = [];
  const emissiveMaterials = new Map();
  const nodeBounds = new THREE.Box3();
  model.traverse((node) => {
    if (node.isLight) {
      // A new preview rig consistently owns the four requested lighting states.
      node.visible = false;
    }
    if (!node.isMesh) return;
    const materials = Array.isArray(node.material)
      ? node.material
      : [node.material];
    node.castShadow = materials.some(
      (material) => !material.transparent || material.opacity > 0.9,
    );
    node.receiveShadow = true;
    nodeBounds.setFromObject(node);
    const position = nodeBounds.getCenter(new THREE.Vector3());
    let emits = false;
    for (const material of materials) {
      if (material.emissive?.getHex() && material.emissiveIntensity > 0) {
        emits = true;
        if (!emissiveMaterials.has(material)) {
          emissiveMaterials.set(material, material.emissiveIntensity);
        }
      }
    }
    if (emits) emitters.push(position);
    else if (
      /pendant|lamp|luminaire|downlight|light.?strip|吊燈|檯燈|燈具/i.test(node.name)
    ) {
      namedFixtures.push(position);
    }
  });

  const fixtureBasis = emitters.length
    ? "emissive-materials"
    : namedFixtures.length
      ? "fixture-geometry"
      : "spatial-preview";
  const candidates = emitters.length ? emitters : namedFixtures;
  // Spatial separation prevents a chandelier's many pieces consuming every
  // preview light and keeps a large dwelling within a small GPU light budget.
  const positions = [];
  const separation = Math.max(span * 0.13, 0.4);
  const remaining = candidates.map((position) => position.clone());
  while (remaining.length && positions.length < 8) {
    let index = 0;
    if (positions.length) {
      let furthest = -1;
      remaining.forEach((position, candidate) => {
        const distance = Math.min(
          ...positions.map((other) => position.distanceToSquared(other)),
        );
        if (distance > furthest) {
          furthest = distance;
          index = candidate;
        }
      });
    }
    const [position] = remaining.splice(index, 1);
    if (positions.some((other) => position.distanceTo(other) < separation)) {
      continue;
    }
    positions.push(position);
  }
  if (!positions.length) {
    // Models without fixture geometry receive an explicitly labelled preview
    // fill at the model center; it does not invent installed luminaire locations.
    positions.push(
      new THREE.Vector3(center.x, bounds.min.y + size.y * 0.68, center.z),
    );
  }
  const practicals = positions.map((position) => {
    // glTF uses metres. A larger dwelling needs more fixtures, rather than a
    // brighter bulb and a house-wide influence range at every emitter.
    const light = new THREE.PointLight(0xffd0a0, 0, 4, 2);
    light.position.copy(position);
    light.position.y = Math.max(light.position.y, bounds.min.y + size.y * 0.24);
    scene.add(light);
    return light;
  });
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.shadowMap.autoUpdate = false;
  let state = { time: "day", lights: true };
  const metadata = {
    fixtureCount: positions.length,
    fixtureBasis,
    previewOnly: true,
  };
  function setLighting(next = {}) {
    state = {
      time:
        next.time === undefined
          ? state.time
          : next.time === "night"
            ? "night"
            : "day",
      lights: next.lights === undefined ? state.lights : next.lights !== false,
    };
    const day = state.time === "day";
    scene.background.set(day ? "#e7e2d8" : "#171f2a");
    scene.environmentIntensity = day ? 0.3 : state.lights ? 0.085 : 0.018;
    hemispheric.intensity = day ? 0.65 : 0.055;
    hemispheric.color.set(day ? 0xe8f0ff : 0x8ba7dc);
    sun.color.set(day ? 0xfff0d5 : 0x9bb6e2);
    sun.intensity = day ? 2.1 : 0.035;
    indirect.intensity = state.lights ? (day ? 0.06 : 0.12) : 0;
    // A bounded per-fixture candela value keeps the qualitative preview useful
    // across room sizes. It is not a source fixture's measured photometry.
    const intensity = 12;
    practicals.forEach((light) => {
      light.intensity = state.lights ? intensity : 0;
    });
    emissiveMaterials.forEach((intensity, material) => {
      material.emissiveIntensity = state.lights ? intensity : 0;
    });
    renderer.toneMappingExposure = day ? 0.78 : 0.95;
    renderer.shadowMap.needsUpdate = true;
    renderer.domElement.dataset.lightingTime = state.time;
    renderer.domElement.dataset.lightingLights = String(state.lights);
    return { ...state, ...metadata };
  }
  setLighting(state);
  return {
    setLighting,
    getLighting: () => ({ ...state, ...metadata }),
    updateShadows: () => {
      renderer.shadowMap.needsUpdate = true;
    },
    dispose() {
      [hemispheric, sun, sun.target, indirect, ...practicals].forEach((light) =>
        scene.remove(light),
      );
      sun.shadow.dispose();
    },
  };
}
