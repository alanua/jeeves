# Construction Takeoff / Aufmaß Runner Task Template

Status: TEMPLATE
Scope: private/local runner task template
Privacy: public-safe placeholders only

## Purpose

Run a private/local construction takeoff extraction using the Skeleton skill:

```text
Construction Takeoff / Aufmaß from Drawings
```

This template is generic. Replace placeholders only in private task packets or private Drive/local runner context. Do not commit real object data to public GitHub.

## Private placeholders

```text
<PRIVATE_PROJECT_FOLDER>
<WORKING_OUTPUT_FOLDER>
<GLOBAL_COORDINATION_DXF>
<MAIN_FLOOR_PLANS>
<SECTION_DXF_FILES>
<FACADE_DXF_FILES>
<PDF_CONTROL_FILES>
<SCAN_FOLDER>
<EXPECTED_WORKBOOK_NAME>
<OPTIONAL_GEMINI_PACKET_PATH>
<OPTIONAL_GEMINI_OUTPUT_PATH>
```

## Source priority

```text
1. DXF/DWG geometry first for vector geometry.
2. IFC if exported and trustworthy.
3. PDF for labels, legends, printed areas, annotations, and visual control.
4. Sections/façades for heights, slopes, openings, and façade areas.
5. Field scans/images as current-state evidence with datum.
6. PLN only through Archicad exports; no direct PLN parsing claim.
```

## Allowed local tools

Use only if installed locally and appropriate for the private runner environment:

```text
ezdxf
PyMuPDF
Shapely
pandas
openpyxl
Pillow
OpenCV
IfcOpenShell if available
```

Optional Gemini second-brain review may use only the existing Gemini Auditor adapter after explicit approval and after the bridge is verified for the Runner environment.

## Forbidden

```text
No private drawing upload to public GitHub.
No real object address/client data in public files.
No raw extracted real table data in public GitHub.
No private Drive URLs in public files.
No final billable quantity claims.
No live external model/API calls unless separately approved.
No merge/deploy/server/production changes.
No secrets, .env, credentials, or tokens.
No treating Gemini as a geometry source of record or final authority.
```

## Expected private output folder

```text
<WORKING_OUTPUT_FOLDER>/source_inventory.csv
<WORKING_OUTPUT_FOLDER>/global_coord_map.csv
<WORKING_OUTPUT_FOLDER>/scale_anchors.csv
<WORKING_OUTPUT_FOLDER>/rooms_prelim.csv
<WORKING_OUTPUT_FOLDER>/height_measurements_prelim.csv
<WORKING_OUTPUT_FOLDER>/openings_prelim.csv
<WORKING_OUTPUT_FOLDER>/walls_prelim.csv
<WORKING_OUTPUT_FOLDER>/facades_prelim.csv
<WORKING_OUTPUT_FOLDER>/crosscheck_matrix.csv
<WORKING_OUTPUT_FOLDER>/review_items.csv
<WORKING_OUTPUT_FOLDER>/assumptions.csv
<WORKING_OUTPUT_FOLDER>/<EXPECTED_WORKBOOK_NAME>.xlsx
<WORKING_OUTPUT_FOLDER>/runner_log.md
<WORKING_OUTPUT_FOLDER>/gemini_intake_packet.json optional, private/local only
<WORKING_OUTPUT_FOLDER>/gemini_auditor_output.json optional, private/local only
```

## Runner workflow

```text
1. Build INPUT_SOURCES from the private project folder.
2. Identify drawing roles: global coordination, floor plans, sections, façades, PDFs, scans.
3. Extract DXF/DWG candidate geometry locally with ezdxf.
4. Normalize geometry with Shapely where useful.
5. Extract PDF labels/printed areas/annotations with PyMuPDF where useful.
6. Register scan/image measurements only with explicit datum.
7. Build preliminary tables.
8. Run validation gates.
9. Write CSV/XLSX/log artifacts.
10. Optionally build a Gemini Intake Packet from summarized table/gate results.
11. Optionally run the Gemini Auditor adapter if explicitly approved and verified.
12. Validate Gemini output fail-closed.
13. Convert Gemini findings into review items/questions only after ChatGPT/Skeleton synthesis.
14. Report status and review items.
```

## Optional Gemini second-brain stage

Use this stage only when explicitly approved for the private pilot and only through the Runner-mediated Gemini Auditor adapter.

Allowed use:

```text
preliminary tables + validation-gate summaries
-> Gemini Intake Packet
-> stateless anomaly/consistency review
-> adapter output validation
-> ChatGPT/Skeleton synthesis
-> Oleksii review
```

Gemini review questions may include:

```text
Are source priorities applied consistently?
Are room, wall, opening, height, façade, and slope values internally consistent?
Which table rows look suspicious or need human review?
Which validation gates failed or need better evidence?
Are assumptions separated from extracted facts?
Are conflicts between DXF/DWG, IFC, PDF, sections, façades, and scans represented in CROSSCHECK_MATRIX or REVIEW_ITEMS?
```

Gemini must not:

```text
execute commands
access files outside the prepared packet
update canon
produce final billable quantities
merge or deploy
publish private project material
be treated as the geometry source of record
```

## Gemini packet privacy gate

Before any Gemini packet is created, choose one route:

```text
PUBLIC_SAFE = synthetic/redacted example only.
STRICT_REDACTION = real-derived summary after deterministic redaction.
INTERNAL_BHK = private/internal working packet only inside approved Runner/server environment.
```

The packet should include table and gate summaries, source-role labels, row identifiers, conflict categories, and exact review questions. It should not include raw drawings or unnecessary private context.

## Gemini output validation gate

The adapter output must fail closed if Gemini:

```text
sets canon_claim=true
returns commands
returns live access references
violates schema
claims final authority over quantities
contains private leakage in a public report path
```

Gemini results may become candidate REVIEW_ITEMS, ASSUMPTIONS, or cross-check notes only after ChatGPT/Skeleton synthesis.

## DXF/DWG parser expectations

The runner may implement local scripts for:

```text
layer inventory
entity inventory
text/dimension extraction
polyline/closed-boundary detection
block reference inventory
axis/grid extraction
room label association
opening candidate extraction
geometry-to-table normalization
```

The parser must produce preliminary candidates, not final unquestioned quantities.

## Required validation gates

```text
scale gate
axis/section-cut mapping gate
room area cross-check gate
height datum gate
opening subtraction gate
DG/sloped ceiling section gate
façade separation gate
privacy/publication gate
Gemini packet privacy gate, if second-brain review is used
Gemini output validation gate, if second-brain review is used
```

Every failed or uncertain gate must create a REVIEW_ITEMS row.

## Expected report format

```text
What changed:
What was extracted:
What was not extracted:
Validation gates:
Gemini review status, if used:
Conflicts:
Review items:
Private outputs created:
Remaining risk/noise:
Next safe step:
```

## Done condition

This runner task is done only when:

```text
- private source inventory exists;
- preliminary workbook exists;
- runner log exists;
- review items exist for unresolved gates;
- optional Gemini review, if used, produced only evidence/review output;
- no private files/data were committed to public GitHub;
- Oleksii has enough information to review one floor/object.
```

## Public report rule

A public GitHub report may say only:

```text
private pilot run completed / blocked / needs review
artifact types created
validation gates passed/failed by category
Gemini review used / not used / blocked by bridge status
next safe step
```

It must not include real project quantities, names, addresses, drawings, extracted tables, Drive links, or private assumptions.
