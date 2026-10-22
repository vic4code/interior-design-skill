# Lightweight interior walkthrough

Use the existing Three.js viewer and matching GLB for an interactive spatial review. Keep the five review modes, source geometry, drawings, image provenance and original overview available. A cinematic video reference is appearance inspiration; confirm what it actually demonstrates before attributing an implementation or promising free navigation.

## Browser behavior

Start in the existing cutaway overview. **走入空間** switches to an enclosed, eye-level view: 1.6 m above supported floor geometry, fixed 65° vertical field of view. Drag to look; click/tap **前進 / 後退** for a 0.35 m step. On the focused canvas, W/S or up/down move forward/back, A/D sidestep and left/right turn. Key movement is 1.1 m/s with capped frame deltas and subdivided steps. Do not capture keys from selectors or other inputs. Reset restores the entry position and orientation; **返回旋轉** restores the overview and its enclosure setting. Controls stay below the canvas, with 44 px minimum touch targets. No pointer lock, autoplay tour or device-motion permission is needed.

Movement changes camera position with fixed projection and eye height, so near and distant objects exhibit parallax. Entering the mode changes field of view once; movement itself never changes FOV or digitally enlarges an image. Reuse existing authored materials, environment lighting, warm fixtures, day/night choices and cached shadows. A standing perspective and full enclosure improve spatial presence without a new renderer or a claim of photographic quality.

## Conservative geometry support

The bundled implementation looks for named, thin floor meshes near the model's lowest level (glTF metres, Y up). It tests actual floor triangles under the center and four points of a 20 cm footprint, and uses expanded mesh bounding boxes overlapping the body height as obstacles, including enclosure faces hidden by the overview cutaway. Movement is checked in at most 8 cm substeps. This handles gaps and many irregular outlines more conservatively than clamping to the model's outer box.

This is **a single-level preview**, not a complete collision/physics or accessible-route system. Furniture boxes can block more space than their actual shapes; a mesh combining a whole room can prevent entry. Stairs, stacked floors, changing levels, animated furniture and unsuitably named/combined floor meshes need authored navigation data or a separately scoped solution. If no supported standing position is found, disable walking with an explanation and keep overview functional. Do not invent a rectangular floor or alter the source model to make walking available.

## Resource and acceptance budget

- Add no runtime dependencies, model downloads, paid calls or continuous simulation. Load Three.js and the GLB only on selecting 3D. Keep the existing DPR cap (1.75) and single cached 2048² sun shadow map; no extra shadowed lights or screen-space/path-tracing passes.
- Target at most 10 KB added raw production JS / 5 KB gzip across the existing viewer chunks. Compare actual build sizes and unchanged GLB hashes; measure gzip consistently. These are change budgets, not total model limits for every project.
- Render only on changes, damping/rotation, resize, lighting or navigation. A settled static view should issue **zero WebGL draws in a two-second window**; non-3D and hidden tabs should issue none. The browser animation callback remains available for input; no heavy work belongs in its idle path.
- Verify actual camera translation, constant projection during movement, near/far parallax, floor-edge/obstacle stops, reset and return-to-overview. Test keyboard blur/tab exit and rapid model switches, all lighting states and all five existing modes. Check 320 px mobile width, real touch input, adequate controls and failed requests.
- Report measurements with viewport, browser and GPU context. Do not infer phone FPS, battery savings or visual acceptance from software-rendered desktop tests. For a target phone, aim for a measured p95 frame time below 33 ms during a defined walk, and stop or reduce rendering cost if it misses; this is a future device acceptance target until measured.

Keep supplied projects and generated evidence outside the installed skill. For maintainer evidence, see the repository's dated review records; installed-skill instructions must remain useful without them.
