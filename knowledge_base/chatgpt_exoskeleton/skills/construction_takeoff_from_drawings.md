# Construction Takeoff / Aufmaß from Drawings

Status: LIKELY_NEEDS_REVIEW
Priority: HIGH
Scope: reusable public-safe Skeleton skill
Private pilot route: real project files and pilot outputs stay in private Drive only

## Purpose

Convert repeated construction drawing analysis into a controlled preliminary Aufmaß workflow:

```text
mixed construction drawings -> preliminary quantity tables with source confidence and review items
```

This skill supports floors, ceilings, walls, openings, façades, heights, slopes, volumes, and source cross-checks. It must not produce unsupported final billable quantities.

## Activation rule

Activate when the user provides or mentions:

```text
DXF / DWG / PDF / PLN / IFC / scans / sections / façades / room plans / Aufmaß / Aufmass / Massenberechnung / quantities / walls / floors / ceilings / openings / volumes
```

## Public/private routing

Public GitHub may contain only:

```text
generic workflow
generic schemas
generic statuses
generic synthetic examples
runner task template
safe acceptance criteria
```

Private Drive/local runner may contain:

```text
real drawing files
real source inventory
real extracted CSV/JSON/XLSX
real run logs
real review items
object-specific assumptions
```

Do not put real object addresses, client data, raw project drawings, extracted real quantities, private Drive URLs, or private file names in public GitHub.

## Source priority

Use source priority as a control rule, not as blind trust:

```text
1. DXF/DWG geometry first for vector room outlines, walls, axes, dimensions, layers.
2. IFC if exported from BIM and trustworthy for rooms, walls, openings, heights, metadata.
3. PDF for labels, printed areas, legends, annotations, visual control, signed/issued drawing checks.
4. Sections/façades for heights, roof slopes, openings, façade areas, datum relationships.
5. Field scans/images as current-state measurement evidence with datum.
6. PLN only as master upstream source through Archicad exports; do not claim direct PLN parsing in v1.
```

## Standard workflow

```text
source inventory
-> legend dictionary
-> global coordination / axes map
-> DXF/PDF/IFC/scans extraction
-> scale/calibration gate
-> room table
-> heights/openings/walls/façades
-> annotations/comments
-> cross-check matrix
-> review items
-> preliminary workbook
-> optional Gemini second-brain review pass
-> ChatGPT/Skeleton synthesis
-> human review
```

## Gemini second-brain review pass

Gemini may be used as a Runner-mediated second-brain auditor after local/private extraction has produced preliminary tables and validation-gate results.

Gemini is evidence/review support only. It is not a geometry source of record, not an executor, not a canon writer, not a merger/deployer, and not the final quantity authority. ChatGPT/Skeleton remains the architect, control plane, privacy gate, and canon gate. Oleksii remains the final reviewer for ambiguous construction facts.

Use this review pattern:

```text
private drawings
-> local source inventory
-> local extraction/parsing
-> preliminary CSV/XLSX tables
-> validation gates
-> redacted/public-safe or approved private Gemini Intake Packet
-> Gemini anomaly/consistency review
-> adapter fail-closed output validation
-> ChatGPT/Skeleton synthesis
-> Oleksii review
```

Gemini may help answer:

```text
Are source priorities applied consistently?
Are room areas, wall areas, openings, heights, and façade values internally consistent?
Which rows look suspicious or need human review?
Which validation gates failed or are underspecified?
Are there conflicts between DXF/DWG, IFC, PDF, sections, façades, and scans?
Are assumptions clearly separated from extracted facts?
Are statuses and confidence levels assigned consistently?
```

Gemini must not:

```text
produce final billable quantity claims
execute commands
access parser/source files outside the Runner packet
update canon
merge, deploy, or touch server/runtime state
publish private project data
be treated as the geometry source of record
```

## Gemini Intake Packet for Construction Takeoff

The Runner may prepare a Gemini packet only after the privacy gate chooses a safe route:

```text
PUBLIC_SAFE = synthetic/redacted examples only.
STRICT_REDACTION = real-derived summaries after deterministic redaction.
INTERNAL_BHK = private/internal working packet allowed only inside approved Runner/server environment.
```

A Construction Takeoff Gemini packet should include only the minimum needed review surface:

```text
schema_version
packet_id
objective
mode
privacy_level
confirmed_canon
evidence summary
draft_artifact summary
exact_questions
forbidden_actions
```

The evidence summary should describe table/gate results and row identifiers, not raw private drawings. If real private data is used inside an approved private Runner environment, public reports must mention only artifact types, gate categories, and next safe steps.

## Gemini output handling

Gemini output must pass the Gemini Auditor adapter validation before ChatGPT/Skeleton uses it.

Fail closed if the response:

```text
sets canon_claim=true
returns non-empty commands
returns live access references
contains secret/private leakage
violates the output schema
claims final authority over quantities
```

After validation, ChatGPT/Skeleton must synthesize Gemini's findings into:

```text
confirmed observations
possible conflicts
review items
questions for Oleksii
next safe private runner step
```

Gemini notes may become REVIEW_ITEMS or ASSUMPTIONS only after ChatGPT/Skeleton review. They are not canon by themselves.

## Table schemas

### INPUT_SOURCES

Columns:

```text
source_id
private_source_ref
source_type
source_role
file_format
revision_or_date
scope_area
coordinate_system_known
scale_known
priority
privacy_status
parse_status
notes
```

### GLOBAL_COORD_MAP

Columns:

```text
coord_id
source_id
origin_description
x_axis_reference
y_axis_reference
rotation_deg
unit
confidence
status
notes
```

### AXES_INDEX

Columns:

```text
axis_id
source_id
axis_label
axis_type
geometry_ref
confidence
status
notes
```

### SECTION_CUTS_INDEX / SECTIONS_INDEX

Columns:

```text
section_id
source_id
section_label
cut_location_ref
view_direction
related_floor_or_area
height_datum_ref
confidence
status
notes
```

### SCALE_ANCHORS

Columns:

```text
anchor_id
source_id
anchor_type
printed_or_declared_length
measured_length
scale_factor
unit
confidence
status
notes
```

### LEGEND_DICTIONARY

Columns:

```text
legend_id
source_id
symbol_or_layer
meaning
category
confidence
status
notes
```

### ROOMS_PRELIM

Columns:

```text
room_id
source_id
floor
room_label
room_name
boundary_ref
area_m2_extracted
area_m2_printed
area_m2_selected
perimeter_m
height_ref
gross_wall_area_m2
ceiling_area_m2
floor_area_m2
confidence
status
review_item_id
notes
```

### HEIGHT_MEASUREMENTS_PRELIM

Columns:

```text
height_id
source_id
floor_or_area
height_type
datum
value_m
measurement_method
confidence
status
review_item_id
notes
```

### OPENINGS_PRELIM / WINDOW_SCHEDULE_PRELIM / DOOR_SCHEDULE_PRELIM

Columns:

```text
opening_id
source_id
floor
room_or_facade_ref
opening_type
label
width_m
height_m
area_m2
sill_height_m
count
confidence
status
review_item_id
notes
```

### WALLS_PRELIM

Columns:

```text
wall_id
source_id
floor
room_or_axis_ref
wall_type
length_m
height_m
gross_area_m2
opening_area_m2
net_area_m2
confidence
status
review_item_id
notes
```

### FACADES_PRELIM

Columns:

```text
facade_id
source_id
facade_label
area_gross_m2
opening_area_m2
area_net_m2
height_basis
source_relation
confidence
status
review_item_id
notes
```

### ANNOTATIONS_PRELIM

Columns:

```text
annotation_id
source_id
location_ref
text
category
linked_table
linked_row_id
confidence
status
notes
```

### CROSSCHECK_MATRIX

Columns:

```text
check_id
entity_type
entity_id
source_a
source_b
field_checked
value_a
value_b
difference
tolerance
result
status
review_item_id
notes
```

### SOURCE_RELATION_MAP

Columns:

```text
relation_id
source_a
source_b
relation_type
same_scope
coordinate_relation
revision_relation
confidence
status
notes
```

### REVIEW_ITEMS

Columns:

```text
review_item_id
severity
entity_type
entity_id
issue
recommended_action
owner
status
notes
```

### ASSUMPTIONS

Columns:

```text
assumption_id
scope
assumption_text
reason
impact
confidence
status
review_item_id
notes
```

## Deterministic statuses

Allowed row/status values:

```text
AUTO_EXTRACTED
CHECKED
FIELD_MEASURED_CURRENT_STATE
FIELD_MEASURED_FROM_METERRISS
ASSUMED_FROM_TYPICAL
NEEDS_FFB_OFFSET
NEEDS_DATUM_CHECK
NEEDS_SCALE_CHECK
NEEDS_SECTION_MAPPING
NEEDS_GEOMETRY_REVIEW
NEEDS_VISUAL_REVIEW
CONFLICT
CONFLICT_HEIGHT
CONFLICT_AREA
LOW_PRIORITY_CONTEXT
METADATA_ONLY
CONTEXT_ONLY
NOT_AVAILABLE
FAILED_PARSE
```

## Validation gates

Required gates:

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

A preliminary workbook is not reviewable unless each relevant gate is either passed or represented as a REVIEW_ITEMS row.

## DXF/DWG parser expectations

Skeleton v1 does not implement heavy DXF/DWG parsing. It defines the contract for a private/local runner.

Expected private runner behavior:

```text
read DXF/DWG locally
inspect layers/entities/blocks/text/dimensions
extract candidate geometry with ezdxf
normalize geometry with Shapely
write CSV/XLSX tables
write parser logs
mark confidence and review statuses
never upload private drawings or real extracted quantities to public GitHub
```

## Runner / Codex handoff roles

```text
ChatGPT/Skeleton: method, schema, gates, review framing, Gemini packet framing, synthesis
Runner/Codex: local/offline extraction scripts, parser execution, CSV/XLSX artifacts, logs, optional Gemini adapter call when explicitly approved
Gemini: stateless second-brain auditor over the prepared packet, evidence only
Oleksii: final review/acceptance of ambiguous construction facts
```

## Promotion criteria after private pilot

This skill may be promoted only after a private pilot demonstrates:

```text
local/private extraction produced a preliminary workbook
validation gates produced review items for uncertainties
optional Gemini review, if used, remained evidence-only and fail-closed
ChatGPT/Skeleton synthesized the findings without leaking private data
Oleksii reviewed one floor/object end-to-end
```

## Definition of done

This skill is not done just because the document exists.

Done requires:

```text
- skill document exists;
- runner task template exists;
- privacy route is explicit;
- table schemas and statuses exist;
- first private pilot run produces a workbook;
- optional Gemini second-brain review pass is tested safely when the bridge is verified;
- one floor/object is reviewed end-to-end;
- gaps are recorded;
- after review, status may be promoted from LIKELY_NEEDS_REVIEW to CONFIRMED_WORKFLOW.
```

## Current limitation

Status remains:

```text
LIKELY_NEEDS_REVIEW
```

Promotion requires one successful private pilot floor/object reviewed by Oleksii. If Gemini second-brain review is used, the Runner-side Gemini bridge must be verified first and the output must remain evidence only.
