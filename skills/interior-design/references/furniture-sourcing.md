# From desired furniture to a trustworthy model

## Identify the exact product

Accept a product URL, brand/model, screenshot or reference photo. If only a photo exists, use image/web search to find candidates and compare distinctive geometry, feet, seams, materials and variants. Do not silently declare a lookalike an exact match. Ask for confirmation when identity materially changes size or price; continue with a visibly tentative placeholder.

## Search, then verify

Search `brand model dimensions`, `brand model technical sheet`, `brand model CAD download` and, for equipment, `brand model installation manual`. Open and read the authoritative page/PDF; a search snippet is only a lead. Prefer:

1. Manufacturer product page for the exact regional SKU and variant.
2. Official dimension drawing/technical sheet and installation manual.
3. Authorized distributor where the exact manufacturer information can be checked.
4. Other retailer or marketplace only as a labelled secondary lead.

Record the URL, document revision if present, access date, region, model/SKU, variant, units and the exact dimension labels. Confirm that values are assembled product dimensions rather than packaging, seat width or shipping size. Resolve conflicts explicitly; do not average measurements. Convert to mm without inventing extra precision.

## Store three different envelopes

| Envelope | Examples | Evidence |
| --- | --- | --- |
| Product | Overall W/D/H, seat height, local orientation | Manufacturer drawing |
| Operation | Swivel/pull-out/door swing, recline, person using it | Actual mechanism and reviewed use scenario |
| Installation/service | Cutout, ventilation, hose/cable bend, wall fixing, replacement access | Selected equipment installation manual and site confirmation |

One does not determine the others. A chair width alone cannot prove a comfortable passage. A refrigerator outside width cannot determine its enclosure width. A product box is sufficient for initial fit checks, not installation approval.

## Choose model fidelity

- **Manufacturer model:** preserve scale; inspect axes, materials, evaluated dimensions and exact variant. Record source/license and modifications.
- **Dimensioned approximation:** build original geometry to official dimensions; label it an approximation, not official CAD. Reference images may guide form; photo perspective does not supply concealed dimensions.
- **Placeholder:** use assumed W/D/H until verified. Keep its tentative status visible in UI, schedule and drawings.

Do not shrink real products to make a layout fit. Reject or change the layout instead. Keep product-local dimensions separate from its rotated world AABB. A legally downloadable asset may still lack redistribution rights; link it or let users obtain it themselves when a public bundle cannot include it.

## Product evidence record

For production, attach an optional product record to an object and extend the schedule exporter:

```json
{
  "brand": "Example manufacturer",
  "model": "Exact model",
  "sku": "REGIONAL-SKU",
  "variant": "Fabric and size option",
  "product_dimensions_mm": {"width": null, "depth": null, "height": null},
  "dimension_source_url": null,
  "installation_manual_url": null,
  "checked_at": null,
  "model_fidelity": "placeholder",
  "asset_source_url": null,
  "redistribution_license": null,
  "operation_envelope_status": "unverified",
  "installation_clearance_status": "unverified"
}
```

The starter currently exports only its core fields; do not assume these extended records automatically appear in CSV. Add fields and tests when introducing product workflows.

## Verified example, not a bundled asset

On 2026-10-20, [IKEA Taiwan's DYVLINGE green page, article 705.708.36](https://www.ikea.com.tw/en/products/armchairs-footstool-and-sofa-tables/armchairs/dyvlinge-art-70570836) listed overall width 63 cm, depth 75 cm and height 68 cm, separately from seat and package measurements. Normalize to W630 × D750 × H680 mm for that SKU. This verifies dimensions only; it does not establish swivel clearance, original CAD availability or redistribution rights. Recheck the actual selected variant for a live project. No product images or CAD are copied into this repository.
