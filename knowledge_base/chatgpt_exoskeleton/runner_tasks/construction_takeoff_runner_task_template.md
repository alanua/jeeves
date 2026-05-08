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
10. Report status and review items.
```

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
```

Every failed or uncertain gate must create a REVIEW_ITEMS row.

## Expected report format

```text
What changed:
What was extracted:
What was not extracted:
Validation gates:
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
- no private files/data were committed to public GitHub;
- Oleksii has enough information to review one floor/object.
```

## Public report rule

A public GitHub report may say only:

```text
private pilot run completed / blocked / needs review
artifact types created
validation gates passed/failed by category
next safe step
```

It must not include real project quantities, names, addresses, drawings, extracted tables, Drive links, or private assumptions.
