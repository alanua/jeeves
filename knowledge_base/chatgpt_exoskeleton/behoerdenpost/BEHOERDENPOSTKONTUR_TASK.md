# BEHOERDENPOSTKONTUR — Skeleton Task

Status: LIKELY_NEEDS_REVIEW
Scope: ChatGPT Exoskeleton / private document-handling contour
Last updated: 2026-05-06

## Purpose

Design a Skeleton-side contour that helps ChatGPT process private official documents, scans, PDFs, images, and correspondence related to life in Germany.

This is separate from the Gewerbe accounting contour. Gewerbe documents may be cross-indexed only when directly relevant, but the general official-life document memory must not pollute the Gewerbe-only database.

## Core principle

Original documents must always be preserved.

Recognized text, OCR, summaries, translations, classifications, and extracted deadlines are metadata. They do not replace the original scan, PDF, image, or email.

## Required private storage target

Use a private Google Drive / Google Sheets memory, not public GitHub, for actual documents and personal data.

Current intended private database name:

```text
Private KB - Leben in Deutschland / Behördenpost
```

Expected private sheets:

```text
Index
Documents
Correspondence
Authorities_Contacts
Deadlines_Tasks
Knowledge
```

Actual private filenames, document links, identifiers, correspondence content, personal data, scans, OCR text, and case numbers must not be committed to GitHub.

## Scope

The contour should support official German-life administration, including but not limited to:

- Ausländerbehörde / Aufenthalt
- Bürgeramt / Anmeldung
- Finanzamt in private-life context
- Krankenkasse in private-life context
- Jobcenter / Familienkasse / Kindergeld if applicable
- Schule / Kita if applicable
- Stadt / Kommune / Behördenpost
- banks and contracts when they are part of official administration
- legal deadlines and official requests for documents

Keep this separate from business-only bookkeeping unless a document explicitly belongs to Gewerbe.

## Document intake flow

When the user provides a scan, PDF, image, screenshot, email, or pasted official correspondence:

1. Preserve the original file in private Drive.
2. Create a document row in the private Behördenpost database.
3. Extract visible metadata:
   - document date
   - received date if known
   - authority / institution
   - document type
   - subject
   - reference number / Aktenzeichen if visible
   - deadline / Frist if visible
   - required action
   - status
4. Run OCR / text extraction when available.
5. Store OCR text or extracted text as metadata.
6. Summarize in plain language.
7. Classify the document domain.
8. Create a task/deadline row if action is required.
9. Mark uncertain or unreadable items as PRIVATE_REVIEW.

## Classification

Use these high-level classes:

```text
PRIVATE_CANON
PRIVATE_REVIEW
TEMPORARY_DO_NOT_CANONIZE
ARCHIVE_ONLY
ACTION_REQUIRED
WAITING_FOR_REPLY
DEADLINE
DONE
```

Use these domain examples:

```text
Aufenthalt
Anmeldung
Finanzamt_private
Krankenkasse_private
Familienkasse
Schule_Kita
Bank_private
Vertrag_private
Gericht_legal
Stadt_Kommune
Other_Behörde
Gewerbe_cross_reference
```

## Evidence hierarchy

```text
official document / original scan / official PDF / official email
> user-provided screenshot
> user message
> assistant inference
```

Never finalize a legal/administrative conclusion from inference alone.

## Original preservation rule

Every processed item must keep a link/reference to the original file.

Required fields in the private document table:

```text
ID
Class
Domain
Authority / Institution
Document Type
Subject
Document Date
Received Date
Reference / Aktenzeichen
Status
Next Action
Deadline / Frist
Source
Original File Link
OCR / Extracted Text
Short Summary
```

If no original file can be preserved, the row must state why and remain PRIVATE_REVIEW unless the user confirms otherwise.

## Correspondence handling

Emails, letters, portal messages, WhatsApp screenshots, or pasted correspondence should be stored in a separate correspondence table and linked to documents/tasks when relevant.

Required fields:

```text
ID
Class
Domain
Authority / Institution
Channel
From
To
Subject
Date
Status
Next Action
Linked Document
Notes
```

## Deadline handling

If a document contains a deadline or implies action:

- create a task row;
- include source document ID;
- include deadline date if explicit;
- include uncertainty note if inferred;
- optionally create a Google Calendar reminder only after user approval or when the workflow explicitly allows it.

No fake deadlines.

## Security and privacy rules

- No raw private data in public GitHub.
- No document scans, OCR text, case numbers, addresses, family details, or official correspondence in public repo.
- GitHub may contain only generic schemas, runbooks, code, tests, and public-safe process rules.
- Private Drive is the storage layer for real documents.
- Assistant must not make legal decisions autonomously.
- Assistant may summarize and flag tasks, but final actions remain user-controlled.

## Required Skeleton modules

Suggested modules:

```text
behoerdenpost_intake.py
original_file_vault.py
ocr_extractor.py
document_classifier.py
correspondence_ingest.py
deadline_extractor.py
private_sheet_writer.py
audit_log.py
notebook_export.py
```

## Future NotebookLM / external memory

After enough official documents accumulate, design a separate NotebookLM or equivalent private memory for Behördenpost.

Rules for that memory:

- include only official-life documents and correspondence;
- do not mix unrelated projects;
- cross-link Gewerbe only through references, not raw duplication, unless needed;
- preserve original file links;
- keep document summaries and deadlines queryable.

## Deliverables

Create or update public-safe Skeleton docs:

```text
knowledge_base/chatgpt_exoskeleton/behoerdenpost/BEHOERDENPOSTKONTUR_DESIGN.md
knowledge_base/chatgpt_exoskeleton/behoerdenpost/BEHOERDENPOSTKONTUR_SCHEMA.md
knowledge_base/chatgpt_exoskeleton/behoerdenpost/BEHOERDENPOSTKONTUR_RUNBOOK.md
knowledge_base/chatgpt_exoskeleton/behoerdenpost/BEHOERDENPOSTKONTUR_TASKS.md
```

Optional code package:

```text
tools/behoerdenpostkontur/
```

## Definition of done

- Public-safe task/design exists in GitHub.
- Private data remains only in Drive/private systems.
- Original-preservation rule is explicit.
- OCR/extracted text is treated as metadata, not replacement.
- Document classification schema exists.
- Deadline/task extraction flow exists.
- Gewerbe separation rule exists.
- NotebookLM/private memory export is planned but not created until reviewed.

## First implementation phase

Build only docs, schema, runbook, and safe task breakdown first.

Do not implement production automation or external memory export before review.
