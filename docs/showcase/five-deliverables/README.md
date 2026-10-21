# Five deliverables, one synthetic space

These previews show real outputs of the bundled S01 room example. Each JPEG uses the same 900 × 675 px canvas. The browser keeps the layout, interactive geometry, image-gen results, MEP references and engineering sheets in separate modes of one review page.

| Preview | Actual source | Meaning |
| --- | --- | --- |
| [1. Layout](layout.svg) | Room, opening and furniture coordinates in the shared structured project | Clean nominal furniture footprints for discussing arrangement; no invented measured dimensions |
| [2. 3D design](02-3d.jpg) | Screenshot of the actual MCM GLB in the interactive viewer | Real-time geometry and appearance preview with cutaway and lighting controls |
| [3. Image-gen visualization](../same-space/mcm/presentation.jpg) | Actual same-base-conditioned MCM generation | Photographic material/light proposal; geometry remains authoritative elsewhere |
| [4. MEP coordination](../drawings/A102.svg) | Actual A102 SVG from the drawing generator | Fixture/power placement and mounting-height proposal; not a complete circuit/HVAC/plumbing design |
| [5. Engineering drawings](../drawings/J301.svg) | Actual J301 cabinet arrangement SVG | Dimensioned front, plan and side views with assembly decisions; site/product/fixing review remains required |

Technical JPEGs are browser rasterizations of their linked SVGs on a white 900 × 675 canvas, without a colored mat or added frame. A3 sheets are contained without stretching or trimming; their original drawing borders remain. Click through to read every annotation. Regenerate with `node scripts/render_showcase.cjs` from the repository root. No image generation is used to fabricate technical sheet geometry or dimensions. See [preview hashes and source records](provenance.json), the [full A3 PDF](../drawings/design-coordination.pdf), and [image-generation records](../same-space/README.md).
