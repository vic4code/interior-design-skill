# Contractor coordination and quotation delivery

Load for requests such as「專業一點」「跟師傅討論」「工程圖」「發包」「估價」or fabrication/construction detail. Develop the actual requested scope; use the existing geometry and decisions. Professional delivery resolves build questions through linked evidence, specifications and responsibilities. More symbols or photorealism alone do not establish readiness.

## Select purpose and report readiness

These are local workflow labels, not statutory certifications or substitutes for the project agreement.

| Purpose | Useful deliverable | Condition to claim readiness |
| --- | --- | --- |
| Concept / 概念 | Layout, visual studies, stated assumptions | Adequate to compare the requested design alternatives |
| Coordination / 工程協調 | Relevant dimensioned sheets, specs, point schedules, interface and issue registers | Every in-scope item has evidence or an explicit unresolved decision, with its consequence and proposed owner |
| Quotation / 詢價發包 | Coordinated drawings/specs and comparable work items, units, quantity bases, inclusions/exclusions | Pricing uncertainties are individually declared as held work, identified alternatives or explicit allowances; no hidden assumptions in a fixed scope |
| Construction or fabrication issue / 施工或製作發行 | Applicable coordinated details and recorded site/product/trade reviews | Evidence and responsible review support the issued work; critical decisions for that work are resolved and excluded/held work is identified |

A contractor discussion can proceed with open issues. Unresolved dimensions, fixing substrates or equipment connections may hold procurement or fabrication even when the package is useful for discussion. Issue readiness per scope: a reviewed cabinet does not release unreviewed electrical work. Write the requested purpose, achieved purpose and remaining conditions on the handoff.

## Establish the technical basis

Record the actual source revision and hash, units, coordinate origin, wall orientation, and finished-floor datum. Retain the producer's measurement status on each critical dimension: assumed, manufacturer, site measured/unreviewed, or site measured/reviewed. A manufacturer dimension is not evidence that its installation envelope fits on site. Record known fabrication and installation tolerances with their source; unresolved tolerances stay open.

For the next iteration, ask only for information that changes a consequential decision: wall/beam geometry, floor/ceiling build-up, openings, retained equipment, existing service points, selected products or scope/budget constraints. Continue independent work while a response is pending. Keep unknown numeric values null rather than zero. A phone screenshot can inform the desired interaction, but cannot establish hidden routes, site dimensions or technical specifications.

## Cover the requested work

Build a coverage matrix with `scope_id, room, trade, required_output, artifact_reference, status, gap_issue_ids`. Select relevant rows rather than generating a fixed sheet count. Explicitly mark irrelevant disciplines with a reason; absent evidence is a gap, not an exemption.

- Existing/demolition/proposed work: retained elements, removals and new work, setting-out faces, openings and critical clearances.
- Floor/wall finishes: material boundaries, build-ups, direction/joints and transitions, skirtings and interfaces.
- Ceiling/lighting: finished heights, beams/soffits, fixture/control intent and access conflicts.
- Power/data/equipment: point setting-out, mounting datum, equipment schedule, service/operation access and electrical design inputs.
- Plumbing/wet areas, when in scope: equipment connections, routes and levels from available evidence, waterproofing/drain/threshold interfaces and inspection requirements determined for the actual system.
- HVAC, when in scope: equipment/duct/drain/grille routes, ceiling/beam coordination and service access from selected equipment and trade input.
- Joinery: plans/elevations/sections, clear dimensions, panel build-up, edges, gaps, hardware, joints and fixing details.
- Details and schedules: located section/detail callouts, selected product/material schedules, quantity scope and unresolved interfaces.

Use the graphic requirements in [construction-documents.md](construction-documents.md). Local electrical, structural, fire, waterproofing or other regulated requirements must be checked against current applicable primary sources and responsible technical input when relevant to the requested work. Do not turn generic examples into mandatory pipe sizes, cable sections, slopes, waterproofing heights, anchor spacing or acceptance tolerances.

## Produce linked records

Use stable IDs across plans, models, sections and tables. Native project data remains authoritative. The following are delivery field contracts: the agent prepares project-specific CSV/JSON/Markdown records; these are not new CLI commands or built-in viewer schemas. Preserve existing fields where possible and document adapters. Keep private output outside the installed skill.

| Record | Required fields for included items |
| --- | --- |
| Sheet register | sheet ID, title, revision, issue purpose, scale, source revision, current/superseded state |
| Element/specification | element ID, room/trade, location/datum, drawing/detail refs, dimensions and basis, material/finish/build-up, product/hardware selection status, installation/maintenance requirements, source refs, open issue IDs |
| Service point | ID, system, existing/retained/removed/proposed state, room, XYZ/unit/datum, setting-out face and reference, equipment/spec ref, control intent where relevant, source/revision, evidence/review state, issue IDs |
| Service route | ID, system, endpoint IDs, known geometry/levels, size/material and their evidence, entry direction, access/crossings, proposed/reviewed state, technical owner, detail/source refs, issue IDs |
| Trade interface | ID, affected elements/sheets, interface location, supplying/installing/connecting/making-good roles, predecessor work, inspection or access point, decision needed, status and issue IDs |
| Open decision / RFI | ID, precise question, location/element, evidence and options, consequence, affected scope/sheets, proposed responsible role, actual assignee if known, due date or required-before milestone, status and closure evidence |
| Quotation item | ID, location/trade, scope/spec/sheet refs, unit, quantity, measurement basis/revision, net quantity vs waste/allowance, inclusions/exclusions, alternative/held status, source of any rate and estimate confidence |
| Readiness/revision record | requested purpose, achieved purpose by scope, checks performed and results, critical holds, actual reviewer/date/evidence if present, changed IDs, affected drawings/specs/quantities, next decisions |

Supply only relevant records, with readable column headings in the user's language and stable technical IDs. A single workbook or Markdown document may hold several tables. JSON field names are implementation choices, not a demand that users author data. Keep product selection, dimensional evidence and review status separate. A proposed role is not an appointed contractor or a completed approval. A deadline is unknown until supplied; use a milestone such as「櫃體下單前」when appropriate.

Preserve the question and its answer when closing an issue. Closure requires a recorded decision with source, revision/date, responsible reviewer where applicable and affected outputs updated. Blank reviewer fields stay blank. A checked box does not establish professional review.

## Resolve the interfaces, not just the isolated items

For each relevant intersection, identify the actual boundary and missing evidence:

| Interface | Questions the delivery must resolve or track |
| --- | --- |
| Cabinet × outlet/appliance | Is the point usable with installed panels/doors and plugs? Where does the service enter, how is it maintained, who opens/seals/makes good, and what equipment envelope applies? |
| Ceiling × HVAC × light | Are levels and equipment depths compatible with beams? Where are access openings, controls and removal paths? Who coordinates final setting-out? |
| Wet area × drain × threshold | What system build-up and levels establish the interface, who provides/inspects each layer, and what recorded method defines acceptance? |
| Joinery × wall/floor | What substrate/load and hardware govern fixing? How are leveling, restraint, service gaps and edge finishing resolved? |
| Finish × opening | What are the frame, structural opening and finished clear dimensions? Who supplies liners, sealants and transitions? |

A visible 2D gap is a geometric observation, not a passed installation check. Verify the complete build-up, operation/service envelope, selected products and site evidence before closing the relevant question.

## Make quotations comparable

On quotation requests, separate loose furniture, fabricated work, installation and services where the scope requires it. Link each item to a spec and drawing. State measurement rules (net/gross, opening deductions, layers/faces, length vs area vs count), unit and source revision. Show waste, allowances and alternatives separately. Unknown prices stay blank; label budget estimates and their dated source. Avoid double counting shared substrates, making-good or materials included in an assembly.

Group unanswered technical matters into clearly priced alternatives, explicit allowances or held work only when the project scope supports that treatment. Do not invent amounts or silently select a contractor's method. Flag provisional quantities separately from verified site takeoffs. State who is proposed to supply/install/connect each item, pending confirmation.

## Check before handoff

Inspect the actual exported sheets/tables and record findings:

1. All in-scope items have locations and traceable drawing/spec refs or named gaps. IDs resolve without collisions; detail/section targets exist. Existing and proposed work are visually distinct.
2. Dimension chains close against source geometry; datum and reference face are consistent. Check openings, wall build-ups, cabinet clear sizes, equipment and service access. Record actual conflicts rather than declaring blanket clearance.
3. Plans, elevations, sections, schedules and quantities share the current revision. Changes propagate across dependent artifacts. Retain superseded issues separately from the current package.
4. Print-scale drawings have readable glyphs, distinct linework, useful legends/scales, non-overlapping annotations and consistent references. Open actual PDFs/SVGs; inspect CAD units/layers when CAD is included.
5. Relevant cross-trade questions have a location, consequence, proposed owner and required-before milestone. Critical unresolved work remains held for the affected operation.
6. Downloads contain actual deliverables. If the browser provides technical point/route selection, verify it displays the correct record and related drawing. Static tables are a valid delivery when richer interaction is unavailable; identify the actual UI capability.

Conclude with a compact handoff: what can be discussed/priced/issued now, specific outstanding decisions, who should answer, and which drawings change next. Do not ask the user to approve a vague plan before producing the work already possible within scope. Send to contractors only when separately authorized.

## Example: turn a generic question into a useful record

Given only the bundled fictional F05 cabinet, an 18 mm door and an unspecified concealed hinge, record a question such as:「F05：選用鉸鏈型號、覆蓋量及開啟角度後，覆核門縫、門片尺寸與鑽孔圖；由木作／五金供應方提出，櫃體下單前完成，關聯 J301/J401。」Keep proposed ownership distinct from actual assignment. Track wall substrate/anchorage separately. Existing numerical door sizes remain design dimensions pending hardware review; do not replace the missing hinge model with a popular brand and declare fabrication ready.

## Method reference

[AIA: Defining the architect's basic services](https://www.aia.org/resource-center/defining-the-architects-basic-services) describes increasing detail from design development through construction documents and the information used for pricing/building. This skill adapts that distinction into project-level evidence and issue tracking. Its tables and labels are local workflow conventions; local contracts, responsibilities and applicable requirements determine actual delivery and release conditions.
