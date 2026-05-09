# Semi-automatic Construction Takeoff with Gemini Review

Status: LIKELY_NEEDS_REVIEW
Priority: HIGH
Scope: reusable public-safe Skeleton skill/protocol
Related skill: `construction_takeoff_from_drawings`
Private route: real drawings, folder links, extracted tables, logs, and Gemini packets stay private only

## Purpose

Coordinate semi-automatic Construction Takeoff / Aufmaß work without pretending the workflow is fully autonomous.

Target loop:

```text
private drawing source set
-> source inventory
-> human-approved quantity scope
-> local/PDF/vector extraction step
-> validation gates
-> optional Gemini review packet
-> Gemini consistency/anomaly review
-> ChatGPT/Skeleton synthesis
-> Oleksii review
```

The goal is to reduce manual work while keeping source control, privacy, and human review strict.

## Activation rule

Activate this skill when the user asks to prepare or run Construction Takeoff / Aufmaß work with partial automation, Gemini, Runner, Drive drawings, DXF/DWG/PDF/PLN, or room/wall/floor/ceiling quantities.

If the user says to stop real analysis and prepare the workflow, do not continue extracting quantities in the current chat. Switch to preparation mode.

## Non-goals

This skill does not:

```text
make final billable quantity claims
replace Oleksii review
trust mixed vector drawings blindly
publish private drawings or quantities
require fully autonomous runner execution
merge or deploy runtime changes
```

## Roles

```text
Oleksii = owner, final reviewer, scope selector, ambiguity resolver.
ChatGPT/Skeleton = architect, source-priority controller, packet framer, review synthesizer, privacy gate.
Runner = private/local executor for parsing, extraction scripts, table/workbook creation, optional Gemini adapter call.
Gemini = stateless second-brain reviewer for conflicts, consistency, suspicious rows, missing evidence, and assumptions.
Public GitHub = reusable public-safe protocols only.
Private Drive/local runner = real source set and real outputs.
```

## Semi-automatic operating principle

```text
Automate extraction candidates.
Do not automate trust.
```

Every produced number must keep source references, confidence, and review status.

## Required user scope before extraction

Do not begin real extraction until the user has provided or confirmed:

```text
quantity target: room areas, wall areas, floor, ceiling, openings, façade, height, volume, etc.
scope: floor, zone, room group, façade, or object slice
source folder/location: private Drive folder or local Runner path
Gemini privacy level: PUBLIC_SAFE / STRICT_REDACTION / INTERNAL_BHK / no Gemini
output expectation: CSV/XLSX/report/review-only
```

If source folder and source priority are already confirmed in private handoff, do not ask again; load the handoff.

## Source priority handling

Use generic source priority from `construction_takeoff_from_drawings.md` unless a private handoff provides an object-specific priority.

When object-specific priority exists, follow it.

Common mixed-source rule:

```text
PDF may be the current-version selector and visual truth layer.
DWG/DXF may be the precise measurement/vector layer.
DWG/DXF can contain mixed adjacent versions and must be version-matched against PDF before use.
```

Required extraction metadata for each quantity row:

```text
source_pdf_ref
source_vector_ref
version_match_status
measurement_source
confidence
review_item_id
```

Recommended statuses:

```text
PDF_CURRENT_VARIANT
VECTOR_MEASURED_MATCHED_TO_PDF
VECTOR_CANDIDATE_NEEDS_VERSION_MATCH
VECTOR_CONFLICT_WITH_PDF
MIXED_VECTOR_GEOMETRY_REVIEW
```

## Manual checkpoints

Semi-automatic work must pause at these checkpoints when uncertain:

```text
1. source inventory complete
2. scope and target confirmed
3. legend/source-priority confirmed
4. first extraction candidate produced
5. validation gates summarized
6. Gemini packet preview ready, if Gemini is used
7. Gemini output validated
8. final review items ready for Oleksii
```

A checkpoint can be skipped only when the user explicitly asks for a faster rough pass and privacy boundaries are still respected.

## Runner mode choices

Use one of these modes:

```text
manual_runner_shell = user or operator runs private commands manually and returns outputs
reviewed_runner_route = a source-controlled runner route exists and can safely run the task
no_runner = ChatGPT only prepares packet/checklist, no extraction
```

Do not claim live runner pickup unless the route is verified.

If the live runner is not generic for the task, prefer `manual_runner_shell` for the first pilot.

## Gemini use conditions

Gemini may be used only after:

```text
Runner-side Gemini bridge is verified or explicitly approved for the private environment
privacy level is chosen
packet contains only the minimum needed review surface
adapter output validation is fail-closed
```

Gemini packet should include:

```text
confirmed source-priority rules
source inventory summary
quantity table summaries
validation gate results
crosscheck matrix summary
review item candidates
exact questions
forbidden actions
```

Gemini must not receive unnecessary raw private drawings if summaries are enough.

## Gemini review question template

```text
1. Are PDF-current-state and vector-measurement sources applied consistently?
2. Which rows likely mix different vector versions or states?
3. Which room area or wall area values look inconsistent with perimeter/height/source references?
4. Which rows require Oleksii review before being used?
5. Are assumptions clearly separated from extracted facts?
6. Are conflicts represented in REVIEW_ITEMS instead of being silently resolved?
7. Are confidence/status values internally consistent?
```

## Output contract

The private runner should produce, as relevant:

```text
source_inventory.csv
legend_dictionary.csv
scale_anchors.csv
rooms_prelim.csv
walls_prelim.csv
openings_prelim.csv
height_measurements_prelim.csv
crosscheck_matrix.csv
review_items.csv
assumptions.csv
workbook.xlsx
runner_log.md
gemini_intake_packet.json optional
gemini_auditor_output.json optional
```

Public reports may mention only:

```text
pilot prepared / run completed / blocked
artifact types created
validation gate categories
Gemini used / not used / blocked
next safe step
```

Public reports must not include real source folder links, object names, addresses, client data, drawings, extracted rows, quantities, or private assumptions.

## Stop/resume rule

If the user says stop, stop real extraction immediately.

Then record:

```text
what was started
what was not run
current private source folder status
current scope status
next safe branch/task
```

Do not continue analysis in the stopped chat unless the user explicitly resumes.

## Ready-to-run checklist

Before a real pilot run, verify:

```text
private source folder confirmed
quantity scope confirmed
floor/zone confirmed
source-priority rule confirmed
output folder confirmed or created privately
Gemini level confirmed or Gemini disabled
runner mode chosen
no public GitHub leakage risk
```

## First-pilot recommendation

For the first run, prefer:

```text
one floor or one bounded zone
room areas first
wall areas by room second
openings as review layer, not final subtraction unless source is clear
PDF + matching DWG/DXF + legend/source-priority check
Gemini review only after preliminary tables exist
```

## Failure handling

If parsing fails:

```text
write FAILED_PARSE in source inventory
keep the source as visual/control evidence if useful
create REVIEW_ITEMS row
continue with other sources if safe
```

If source conflict occurs:

```text
never silently choose one source
record PDF/vector conflict
assign review_item_id
ask Oleksii only when the conflict blocks the target quantity
```

## Promotion criteria

This skill can move from `LIKELY_NEEDS_REVIEW` to `CONFIRMED_WORKFLOW` only after:

```text
one private pilot scope is completed
room/wall quantities are produced with source refs and confidence
Gemini review, if used, stays evidence-only
Oleksii reviews the output
lessons learned are folded back into this skill or the main takeoff skill
```
