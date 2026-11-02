# Residential design delivery and acceptance

Use when a user supplies a professional drawing set as the expected work scope, asks for a complete residential design package, or asks what must be delivered and accepted. Read the supplied set before choosing deliverables. Preserve the existing project and the contractor-coordination readiness rules.

## Establish the brief and evidence first

Agree the actual rooms, work, requested purpose and language. Produce an input register: source file/revision, measured-plan basis, units, finished-floor datum, floor build-up, slab/beam/ceiling levels, opening sizes, existing services, retained items and proposed changes. Unknowns remain unknown. Without calibrated dimensions, deliver a concept and targeted survey list; hold setting-out, fabrication and demolition decisions that depend on them. Confirm wall-removal feasibility from responsible structural review, rather than deriving it from a photograph or line thickness.

Read each reference's title block, scale, date, legend and datum. A larger PDF or a later filename is not automatically the latest design. Compare the reference plan against the elevation key plan and room details. Register conflicting dimensions, equipment or dates before adopting them. A ceiling height measured before the new floor finish is not the finished clear height; record the conversion and its evidence. Interpret source units explicitly; export dimensions consistently, normally in mm.

References describe the expected information density and coordination, not a license to reuse another home's geometry, author marks, material choices, products, technical approval or private source files. Keep the original references in the private project; publish only generic methodology or cleared synthetic fixtures.

## Define the output scope

The machine-readable [delivery catalog](../assets/delivery-scope.json) is the category/checklist source for the full-residential profile. Use it to prepare a human-readable scope matrix before drawing. A limited furniture request can use a custom profile with its written scope; it does not inherit a whole-house services assignment.

For a full residential package, account for every catalog category. Mark out-of-scope work with a project-specific reason. For each included room, enumerate the actual wall directions and cabinet/feature elevations needed; a single generic elevation does not cover an apartment. Unchanged walls can share a documented typical detail where justified. Set the sheet count from coverage and readability, not from a fixed demo count or another project's page total.

Each requirement row needs: stable ID, category, room/element, required output, requested use, prerequisites, artifact/sheet/page references, revision, status, acceptance checks and open issues. Write the visible names in the user's language. Use these statuses:

- `delivered`: actual exported files exist, checks and their evidence are recorded; this alone does not establish construction approval.
- `held`: work is required but blocked; name the missing decision/evidence, consequence, proposed responsible role and required-before milestone.
- `not_applicable`: genuinely outside this project's scope, with a reason; missing inputs are held work instead.

Keep furniture arrangements, setting-out, ceilings, HVAC, floor finishes, power/data, fixture positions and lighting controls separately readable even if several fit in one file. A lighting-control relationship is not a panel circuit calculation, cable specification or concealed cable route. Separate cabinet outer elevations from internal arrangements/sections, and locate both through the elevation key plan. Detail tracks, curtain pockets, light recesses, access panels, support/backing and finish transitions where the actual design requires them.

## Acceptance evidence

Use actual files and actual sheet/page locators, not planned filenames. For each catalog check, record `pass`, `fail` or `pending` with a specific finding and an artifact reference. Include dimension closure, common datum, plan/elevation agreement, material/product status, operation/maintenance access and resolved callouts as relevant. Inspect the exported PDF at print scale and zoom; CAD, if agreed, needs verified units/layers and editable content. Inspect generated visuals against the same room revision; visual approval is separate from dimensional review.

Deliver a sheet register, scope/acceptance matrix and outstanding-decision register together with the drawings. Construction and quotation requirements remain in [contractor-coordination.md](contractor-coordination.md). Record critical holds by operation: a usable design discussion is not permission to order cabinets, break walls or install services.

## Run the file/coverage check

The agent prepares `acceptance.json` using the contract below and runs the single entry point:

```bash
python3 scripts/interior_design.py acceptance --scope /project/acceptance.json --root /project/delivery --out /project/acceptance-report.json
```

The checker uses the standard library. It checks declared category coverage, item/check records, safe existing files, SHA-256, revision and explicit holds. It does not parse CAD geometry, assess whether annotations are truthful, validate a technical design, or approve construction. Its best result is `ready_for_review`. A held or failed item yields `incomplete`, never a blanket acceptance. Keep the report outside the artifact directory so a report cannot become evidence for itself.

Contract (the agent writes this; the user need not author JSON):

```json
{
  "format": "interior-delivery-scope-v1",
  "profile": "full-residential",
  "revision": "R02",
  "rooms": ["Living room"],
  "requested_purpose": "coordination",
  "items": [
    {
      "id": "CEILING-LIVING",
      "category": "ceiling",
      "room": "Living room",
      "status": "held",
      "artifacts": [],
      "checks": [],
      "issues": [{
        "id": "RFI-01",
        "question": "Confirm floor finish build-up and the ceiling datum.",
        "owner_role": "Designer and surveyor",
        "required_before": "Ceiling setting-out",
        "consequence": "Finished clear height and equipment clearance remain unverified."
      }]
    }
  ]
}
```

This example is intentionally incomplete. Add all actual requirements. A delivered row has `artifacts: [{"path":"drawings.pdf","sha256":"actual lowercase SHA-256","revision":"R02","page":3,"sheet":"C101"}]` and `checks: [{"id":"levels_and_datum","result":"pass","finding":"Specific observed result","artifact":"drawings.pdf"}]` for every applicable catalog check. The checker requires positive PDF page locators and drawing sheet IDs; the reviewer must open those targets and confirm their content and actual page range. SVGs use sheet IDs without a PDF page. Each full-profile room needs elevation and visualization requirements, including justified exclusions. `not_applicable` rows need `reason`. A custom profile needs `scope_reason` and nonempty `required_categories`; custom requirements may add their own check IDs.

Test against real limitations: the bundled eight-sheet fictional demo proves the viewer/generator workflow. It lacks a full home's ceiling/HVAC/floor/control plans and room-by-room elevation set, so it must fail full-residential coverage. Never relabel that demo a complete professional package to satisfy a test.
