# One room, three lighting conditions

These are actual host image-generation results edited from the **same approved MCM image**, not independent text-to-image rooms. The input is the [shared MCM presentation](../same-space/mcm/presentation.jpg), SHA-256 `524300f24693994628c9a9ccd99f5bd30c475f98c774611bc53053abc42b2f90`.

| Condition | Image | Actual prompt and review |
| --- | --- | --- |
| Day · lights off / 白天關燈 | [Full image](day-off/presentation.jpg) | [Provenance](day-off/image-provenance.json) |
| Day · lights on / 白天開燈 | [Full image](day-on/presentation.jpg) | [Provenance](day-on/image-provenance.json) |
| Night · lights on / 夜晚開燈 | [Full image](night-on/presentation.jpg) | [Provenance](night-on/image-provenance.json) |

Every generation prompt requests the same 4:3 landscape canvas, camera position, lens, field of view, horizon, vanishing points, object positions and crop. It explicitly forbids camera roll, tilt, zoom, reframing and additional furniture or lights. Only illumination changes: existing daylight with both fixtures off; the same daylight with the existing pendant and desk lamp on; or those two warm 3000 K fixtures after dark.

The three original generated frames are **1448 × 1086 px**. Full-image JPEGs retain that frame; every lightweight preview is **900 × 675 px**, with no stretching, cropping or unequal aspect ratios. README columns have fixed equal widths and shared title/image rows so different text lengths cannot move an image's top edge.

Side-by-side visual review found the two openings, curtain edges, pendant, artwork, sofa and desk positions consistent across the series. Fine texture, shadow and small surface details can differ. Prompt constraints and visual comparison do not certify exact geometry, product performance, illuminance or construction dimensions. The source model and engineering drawings remain authoritative for those dimensions.

The interactive 3D page provides separate day/night and lights-on/off controls for fast appearance review. The gallery contains these real generated images; moving a 3D light control does not call an image API or silently regenerate an image. The host tool did not expose its model identifier or per-image cost; the provenance records that rather than inventing metadata.
