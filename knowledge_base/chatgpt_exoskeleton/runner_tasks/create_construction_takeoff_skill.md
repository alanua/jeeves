# [skeleton-task] create-construction-takeoff-skill

## Active project

СК / ChatGPT Exoskeleton / Skeleton Core

This is Skeleton skill work, not Jeeves runtime work and not private project data extraction.

## Goal

Create a reusable public-safe Skeleton skill for construction takeoff / Aufmaß from mixed drawing sources.

The skill must turn repeated work like:

```text
architectural drawings -> DXF/PDF/scans/sections/façades -> source inventory -> preliminary Aufmaß tables -> review items
```

into a controlled workflow with clear source priorities, privacy routing, runner handoff, deterministic statuses, and review gates.

## Why this skill is needed

The user has a recurring practical need: analyze room/building drawings and prepare preliminary work-quantity tables for floors, ceilings, walls, openings, façades, heights, and volumes.

This is a good Skeleton skill candidate because it:

- removes repeated manual setup work;
- reduces risk of wrong quantities from noisy drawings;
- creates repeatable source-priority rules;
- keeps private project files out of public GitHub;
- connects ChatGPT planning with runner/Codex execution;
- produces auditable tables instead of unsupported final claims.

## Skill name

```text
Construction Takeoff / Aufmaß from Drawings
```

Suggested internal slug:

```text
construction_takeoff_from_drawings
```

## Skill status after this task

Initial status must be:

```text
LIKELY_NEEDS_REVIEW
```

Do not mark as confirmed until at least one real floor/object is processed end-to-end and reviewed by Oleksii.

## Sources to read first

```text
BOOTLOADER.md
knowledge_base/START_HERE_FOR_CHATGPT.md
knowledge_base/MEMORY_POLICY.md
knowledge_base/WORKING_PROTOCOL.md
knowledge_base/CHATGPT_BRANCH_CONTINUITY_BOOT.md
knowledge_base/chatgpt_exoskeleton/START_HERE.md
knowledge_base/chatgpt_exoskeleton/CURRENT_STATE.md
knowledge_base/chatgpt_exoskeleton/CONTROLLED_GROWTH.md
knowledge_base/chatgpt_exoskeleton/SKELETON_RUNNER_TASK_TEMPLATE.md
knowledge_base/CHATGPT_EXOSKELETON.md
knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md
```

## Allowed scope

Allowed:

- add public-safe skill documentation;
- add public-safe runner task templates;
- add public-safe synthetic fixtures only;
- add local/offline CLI helpers if they stay generic and public-safe;
- document source priority, table schemas, statuses, and gates;
- document privacy routing for real drawing packages;
- document runner/Codex handoff workflow;
- add tests for generic CLI helpers if implemented.

Forbidden:

- no private drawing packages;
- no real object address or client data in public GitHub;
- no raw extracted text from real project files;
- no private Drive URLs in public files;
- no live external model API calls;
- no direct PLN parsing claims;
- no final billable quantity claims;
- no merge/deploy/server/production changes;
- no secrets, `.env`, credentials, or tokens;
- no broad rewrite of Skeleton docs.

## Public/private routing rule

Public GitHub may contain only:

```text
generic workflow
generic schemas
generic statuses
generic synthetic examples
runner task template
safe acceptance criteria
```

Private project Drive may contain:

```text
real drawing files
real source inventory
real extracted CSV/JSON/XLSX
real run logs
real review items
object-specific assumptions
```

## Proposed files

Prefer a small public-safe docs-first implementation.

Create:

```text
knowledge_base/chatgpt_exoskeleton/skills/construction_takeoff_from_drawings.md
knowledge_base/chatgpt_exoskeleton/runner_tasks/construction_takeoff_runner_task_template.md
```

If the repository does not yet have these folders, create them.

Optional v1 CLI helper, only if it fits existing Skeleton Core conventions:

```text
tools/skeleton_core/construction_takeoff_profile.py
tests/skeleton_core/test_construction_takeoff_profile.py
tests/fixtures/construction_takeoff_profile_minimal.json
tests/fixtures/construction_takeoff_profile_private_blocked.json
```

Do not implement heavy DXF/PDF parsing inside Skeleton Core v1 unless explicitly approved. The first Skeleton skill can define the workflow and runner contract; parsing belongs to a private/local runner package or later dedicated tool.

## Skill document requirements

The skill document must include:

### 1. Purpose

Define the repeated task:

```text
mixed construction drawings -> preliminary Aufmaß tables with source confidence and review items
```

### 2. Activation rule

Activate when user provides or mentions:

```text
DXF / DWG / PDF / PLN / IFC / scans / sections / façades / room plans / Aufmaß / Massenberechnung / quantities / walls / floors / ceilings / volumes
```

### 3. Source priority

Document source priority:

```text
DXF/DWG geometry first
IFC if exported from BIM and trustworthy
PDF for labels, printed areas, legend, annotations, visual control
sections/façades for heights, roof slopes, openings, façade areas
field scans as current-state measurements with datum
PLN only as master upstream source via Archicad exports
```

### 4. Privacy rule

Real drawings and extracted real tables are private working data unless Oleksii explicitly approves redacted/public-safe publication.

### 5. Standard workflow

Include this workflow:

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
-> human review
```

### 6. Table schemas

Define at least:

```text
INPUT_SOURCES
GLOBAL_COORD_MAP
AXES_INDEX
SECTION_CUTS_INDEX
SCALE_ANCHORS
LEGEND_DICTIONARY
ROOMS_PRELIM
HEIGHT_MEASUREMENTS_PRELIM
OPENINGS_PRELIM
WINDOW_SCHEDULE_PRELIM
DOOR_SCHEDULE_PRELIM
WALLS_PRELIM
FACADES_PRELIM
SECTIONS_INDEX
ANNOTATIONS_PRELIM
CROSSCHECK_MATRIX
SOURCE_RELATION_MAP
REVIEW_ITEMS
ASSUMPTIONS
```

### 7. Deterministic statuses

Include statuses:

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

### 8. Validation gates

Include:

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

### 9. Runner handoff

Define runner/Codex role:

```text
ChatGPT/Skeleton: method, schema, gates, review
Runner/Codex: local/offline extraction scripts, parser execution, CSV/XLSX artifacts, logs
Oleksii: final review/acceptance of ambiguous construction facts
```

### 10. Definition of done

The skill is not done just because the document exists.

Done requires:

```text
- skill document exists;
- runner task template exists;
- privacy route is explicit;
- table schemas and statuses exist;
- first private pilot run produces a workbook;
- one floor/object is reviewed end-to-end;
- gaps are recorded;
- after review, status may be promoted from LIKELY_NEEDS_REVIEW to CONFIRMED_WORKFLOW.
```

## Runner task template requirements

Create a generic public-safe template for private extraction tasks.

It must contain placeholders, not real project data:

```text
<PRIVATE_PROJECT_FOLDER>
<WORKING_OUTPUT_FOLDER>
<GLOBAL_COORDINATION_DXF>
<MAIN_FLOOR_PLANS>
<SECTION_DXF_FILES>
<FACADE_DXF_FILES>
<SCAN_FOLDER>
<EXPECTED_WORKBOOK_NAME>
```

It must include:

- source priority;
- allowed tools: ezdxf, PyMuPDF, Shapely, pandas, openpyxl, Pillow/OpenCV, IfcOpenShell if available;
- forbidden public GitHub upload of private drawings/data;
- expected CSV/XLSX/log outputs;
- done condition;
- report format.

## Optional CLI helper requirements

If implementing the optional CLI helper, keep it narrow.

Proposed command:

```bash
python -m tools.skeleton_core.cli construction-takeoff-profile --input tests/fixtures/construction_takeoff_profile_minimal.json
```

Input: public-safe profile only, no real drawings.

Output statuses:

```text
profile_ready
blocked_private_data_in_public_packet
blocked_missing_required_source_role
unknown_needs_review
```

Output fields:

```text
status
skill_name
source_roles
required_gates
expected_tables
privacy_route
runner_task_ready
merge_allowed=false
deploy_allowed=false
```

This helper must not parse drawings or call external services.

## Validation required

If docs-only:

```bash
python -m tools.skeleton_core.cli validate-state
```

If optional CLI is implemented:

```bash
python -m pytest -q
python -m ruff check tools/skeleton_core tests/skeleton_core
python -m black --check tools/skeleton_core tests/skeleton_core
python -m tools.skeleton_core.cli construction-takeoff-profile --input tests/fixtures/construction_takeoff_profile_minimal.json
python -m tools.skeleton_core.cli construction-takeoff-profile --input tests/fixtures/construction_takeoff_profile_private_blocked.json
python -m tools.skeleton_core.cli validate-state
```

## Required output

Report briefly:

```text
What changed:
What was verified:
What was not changed:
Remaining risk/noise:
Next safe step:
```

## Done condition

A PR or local runner result exists with:

```text
- public-safe construction takeoff skill document;
- public-safe runner task template;
- optional CLI helper only if implemented safely;
- validation result;
- no private project data in public GitHub;
- next safe step for private pilot run.
```

## Next safe step after this Skeleton skill task

Use the skill on a private pilot dataset in Drive:

```text
private project folder
-> runner dispatch packet
-> local/private runner
-> preliminary workbook
-> ChatGPT/Skeleton review
-> Oleksii manual confirmation
```

Only after a successful pilot, consider promotion from:

```text
LIKELY_NEEDS_REVIEW
```

to:

```text
CONFIRMED_WORKFLOW
```
