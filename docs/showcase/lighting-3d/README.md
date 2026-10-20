# Interactive 3D lighting comparison

These four images are screenshots of the actual public MCM model in the browser viewer. They use one loaded model, a stationary default camera and an integer-aligned **900 × 675 px** WebGL canvas. Time and artificial-light switches changed between captures; the camera, geometry and crop did not. No image-generation tool or photographic retouching was used.

| Time | Lights on | Lights off |
| --- | --- | --- |
| Day | [Actual 3D screenshot](day-on.jpg) | [Actual 3D screenshot](day-off.jpg) |
| Night | [Actual 3D screenshot](night-on.jpg) | [Actual 3D screenshot](night-off.jpg) |

The model opens with its interior visible. Daylight and artificial lighting are independent: turning the lamps off during the day retains window daylight, while the nighttime preview changes the exterior fill and reveals local artificial light. The download preserves the source model; the cutaway is a viewing operation.

[Provenance](provenance.json) records the source GLB hash, viewer-source hashes, image hashes, canvas dimensions, camera capture method and actual control states. The five-deliverable README preview uses the same final day/lights-on screenshot.

The lighting is a calibrated qualitative preview. Inferred helper sources, material response and screen exposure do not certify illuminance, luminaire photometry, circuit design or installed performance. The separate [image-gen studies](../lighting/README.md) develop photographic appearance from the approved MCM reference; they do not replace this interactive model or the dimensioned drawing sources.
