# Semi-automatic Construction Takeoff + Gemini Runner Task Template

Status: TEMPLATE
Scope: private/local runner task framing
Privacy: public-safe placeholders only
Related skill: `semi_automatic_construction_takeoff_with_gemini`

## Purpose

Prepare or run a controlled semi-automatic Construction Takeoff / Aufmaß pilot with optional Gemini second-brain review.

This template is generic. Replace placeholders only in private task packets, private Drive handoff, or local Runner context.

## Private placeholders

```text
<PRIVATE_SOURCE_FOLDER>
<PRIVATE_OUTPUT_FOLDER>
<PILOT_SCOPE>
<QUANTITY_TARGET>
<SOURCE_PRIORITY_RULE>
<GEMINI_PRIVACY_LEVEL>
<RUNNER_MODE>
```

## Default first-pilot target

```text
quantity_target = room areas + wall areas by room
scope = one floor or bounded zone
openings = review layer unless source is clear
Gemini = optional review after preliminary tables
```

## Required source inventory fields

```text
source_id
private_source_ref
source_type
file_format
floor_or_scope
source_role
revision_or_date
priority_for_this_object
parse_status
notes
```

## Required room/wall metadata fields

```text
source_pdf_ref
source_vector_ref
version_match_status
measurement_source
confidence
review_item_id
```

## Object-specific mixed-source rule

Use this rule when private handoff says PDF is the current version and DWG/DXF are precise but mixed:

```text
PDF selects the current variant/state.
DWG/DXF provides precise vector dimensions only after matching the relevant candidate geometry to the PDF.
Mixed vector versions must be separated and reviewed.
```

## Runner stages

```text
1. Read private handoff.
2. Confirm source folder and scope.
3. Build source_inventory.csv.
4. Read legend/source-priority notes.
5. Extract PDF text/labels/printed areas where available.
6. Extract vector candidate geometry from DXF/DWG where available.
7. Match vector candidates to current PDF variant.
8. Produce rooms_prelim.csv.
9. Produce walls_prelim.csv by room, with height assumptions/statuses.
10. Produce crosscheck_matrix.csv.
11. Produce review_items.csv for conflicts/missing data.
12. Produce workbook.xlsx.
13. Prepare optional Gemini intake packet from summaries.
14. Run Gemini adapter only if bridge and privacy level are approved.
15. Validate Gemini output fail-closed.
16. Add Gemini findings only as review items/candidate notes.
```

## Manual checkpoints

Stop and report at these checkpoints if data is uncertain:

```text
source inventory complete
scope/target mismatch detected
PDF/vector version conflict detected
height source missing for wall areas
Gemini packet ready but not approved
Gemini output failed validation
```

## Gemini packet questions

```text
Are PDF-current-state and vector-measurement sources applied consistently?
Which rows likely mix different vector versions or states?
Which room or wall area rows look inconsistent with source references?
Which rows require human review before use?
Are assumptions separated from extracted facts?
Are conflicts captured in REVIEW_ITEMS?
Are confidence/status values internally consistent?
```

## Forbidden

```text
No private drawings or extracted quantities in public GitHub.
No final billable quantity claims.
No raw API keys, .env values, SSH details, tokens, or credentials.
No merge/deploy/runtime changes.
No treating Gemini as final authority.
No trusting mixed DWG/DXF geometry without PDF matching.
```

## Public report format

```text
Status:
Pilot scope:
Artifact types created:
Validation gates:
Gemini review status:
Blocked/needs review:
Next safe step:
```

Do not include real folder links, object names, addresses, client data, drawing names, extracted quantities, or private assumptions in public reports.
