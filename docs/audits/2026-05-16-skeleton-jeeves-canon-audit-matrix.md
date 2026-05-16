# Skeleton/Jeeves Canon Audit Matrix

## Summary
- total docs inspected: 103 markdown/docs files (`BOOTLOADER.md`, `README.md`, `docs/**`, `knowledge-base/**`, `knowledge_base/**`)
- main duplication clusters:
  - boot/startup/protocol (`BOOTLOADER.md`, `START_HERE_FOR_CHATGPT.md`, `WORKING_PROTOCOL.md`, `CHATGPT_BRANCH_CONTINUITY_BOOT.md`, `assistant_startup_prompt.md`, `CHATGPT_EXOSKELETON.md`, `CHATGPT_EXOSKELETON_RUNBOOK.md`, `chatgpt_exoskeleton/START_HERE.md`)
  - Jeeves runtime canon snapshots (`README.md`, `knowledge-base/README.md`, `knowledge-base/PROJECT_KNOWLEDGE_BASE.md`, `knowledge-base/01-12`, `projects/jeeves/*`)
  - diary/recovery/history (`assistant_diary.md`, `chatgpt_diary/*`, `recovery_audit/*`, `history_sources/*`, `skeleton_diary.md`, `runner_reports/*`)
  - lanes/skills/templates (`CONTROLLED_GROWTH.md`, `skill_inventory_activation_map.md`, `coding_lane_template_and_evidence_protocol.md`, runner task templates, skill docs)
  - project-structure duplication (`knowledge_base/project_state/*` vs `knowledge_base/projects/*`)
- main stale/risky areas:
  - `README.md` runtime status is older than the current audited repo state
  - `docs/dual_brain_state.md` mixes history, live-host claims, and architecture as if they are one current truth
  - `knowledge_base/assistant_startup_prompt.md` still blends global ChatGPT boot, Skeleton, and Jeeves runtime concerns
  - `knowledge_base/chatgpt_diary/project_write_index.md` points to an older expected layout that no longer matches the real `knowledge_base/projects/**` structure
  - operational logs/reports (`knowledge_base/skeleton_diary.md`, `knowledge_base/projects/jeeves/runner_reports/*`) sit too close to active canon
- proposed active core:
  - `WHAT_IS_SKELETON` -> `knowledge_base/CHATGPT_EXOSKELETON.md`
  - `START_HERE` -> `knowledge_base/chatgpt_exoskeleton/START_HERE.md`
  - `CURRENT_STATE` -> `knowledge_base/chatgpt_exoskeleton/CURRENT_STATE.md`
  - `OPERATING_PROTOCOL` -> currently split between `knowledge_base/WORKING_PROTOCOL.md` and `knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md`
  - `LANES_AND_ACTIVATION` -> currently split between `knowledge_base/chatgpt_exoskeleton/CONTROLLED_GROWTH.md` and `knowledge_base/chatgpt_exoskeleton/runner_tasks/coding_lane_template_and_evidence_protocol.md`; `skill_inventory_activation_map.md` should be supporting status only, not core canon
- proposed cleanup PR sequence:
  1. collapse duplicate startup entrypoints and mark one active read order
  2. refresh repo/runtime truth surface (`README.md` vs `knowledge-base/03_IMPLEMENTATION_STATE.md`)
  3. separate Skeleton canon from Jeeves runtime canon more explicitly
  4. move history/runner/task artifacts out of the active wake surface
  5. dedupe old project-state/template docs against `knowledge_base/projects/**`

## Proposed Active Core
- `WHAT_IS_SKELETON`
  - primary candidate: `knowledge_base/CHATGPT_EXOSKELETON.md`
  - role: single durable definition of the Skeleton layer
- `START_HERE`
  - primary candidate: `knowledge_base/chatgpt_exoskeleton/START_HERE.md`
  - keep `BOOTLOADER.md` as a tiny wake shim only
- `CURRENT_STATE`
  - primary candidate: `knowledge_base/chatgpt_exoskeleton/CURRENT_STATE.md`
  - Jeeves runtime state should remain separate in `knowledge-base/03_IMPLEMENTATION_STATE.md`
- `OPERATING_PROTOCOL`
  - current split: `knowledge_base/WORKING_PROTOCOL.md` + `knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md`
  - cleanup direction: one compact protocol truth, one supporting checklist/reference at most
- `LANES_AND_ACTIVATION`
  - current split: `knowledge_base/chatgpt_exoskeleton/CONTROLLED_GROWTH.md` + `knowledge_base/chatgpt_exoskeleton/runner_tasks/coding_lane_template_and_evidence_protocol.md`
  - current risk: `knowledge_base/chatgpt_exoskeleton/skill_inventory_activation_map.md` is statusful and ages fast

## Audit Matrix
| Path | Current apparent role | Recommended role | Duplicates/conflicts | Recommended action | Reason | Risk if left active |
|---|---|---|---|---|---|---|
| BOOTLOADER.md | Root wake entrypoint | ACTIVE_CORE | Overlaps START_HERE_FOR_CHATGPT.md and chatgpt_exoskeleton/START_HERE.md | Keep as a tiny pointer only | Useful single-command entrypoint | Duplicate boot truth if it grows |
| README.md | Repo landing page and runtime overview | STALE_OR_RISKY | Conflicts with knowledge-base/03_IMPLEMENTATION_STATE.md and current code state | Refresh in a later docs-only PR | Current runtime claims are older than the audited repo state | New contributors may trust stale architecture/runtime claims |
| docs/dual_brain_state.md | Historical architecture/status anchor | STALE_OR_RISKY | Conflicts with CURRENT_STATE.md and newer route/runner docs | Demote to reference/archive in a later PR | Mixes live-state claims, old milestones, and architecture in one file | Can be mistaken for current live operational truth |
| docs/transcript_roadmap_evidence.md | Roadmap evidence note | ROADMAP | Overlaps 05_ACTION_LAYER.md, 07_KNOWLEDGE_BASE_SUBSYSTEM.md, 12_DEPLOYMENT_AND_FAMILY_RUNTIME.md | Keep as evidence only | Clearly marked as evidence-backed roadmap input | Roadmap notes may be mistaken for accepted canon |
| knowledge-base/01_PROJECT_OVERVIEW.md | Jeeves identity/product overview | ACTIVE_CORE | Overlaps README.md and PROJECT_KNOWLEDGE_BASE.md | Keep | Compact durable project identity doc | Product thesis may fragment across multiple overview docs |
| knowledge-base/02_ARCHITECTURE_AND_PRINCIPLES.md | Jeeves architecture principles | ACTIVE_CORE | Overlaps PROJECT_KNOWLEDGE_BASE.md and README.md architecture text | Keep | Clear stable architecture rules | Architecture truth may split across overview files |
| knowledge-base/03_IMPLEMENTATION_STATE.md | Verified implementation state | ACTIVE_CORE | Conflicts with README.md and older Stage claims | Keep as implementation truth source | This is the cleanest audited repo-state document | Stale runtime claims elsewhere will keep winning by accident |
| knowledge-base/04_COORDINATION_AND_AGENTS.md | Agent/routing canon | ACTIVE_CORE | Overlaps PROJECT_KNOWLEDGE_BASE.md and 03_IMPLEMENTATION_STATE.md | Keep | Useful focused view of current agent structure | Agent semantics may drift into multiple docs |
| knowledge-base/05_ACTION_LAYER.md | Future action-layer design | ROADMAP | Overlaps transcript_roadmap_evidence.md and PROJECT_KNOWLEDGE_BASE.md | Keep as roadmap, not runtime truth | Accepted future slice, not live behavior | Could be misread as implemented capability |
| knowledge-base/06_MEMORY_AND_HANDOFF.md | Jeeves memory subsystem direction | ACTIVE_CORE | Overlaps MEMORY_POLICY.md and recovery docs at different scopes | Keep | Useful runtime-memory separation from docs continuity layer | Memory architecture remains ambiguous if this is diluted |
| knowledge-base/07_KNOWLEDGE_BASE_SUBSYSTEM.md | Future knowledge-base subsystem direction | ROADMAP | Overlaps transcript_roadmap_evidence.md and project KB docs | Keep as roadmap | Future subsystem direction, not active operating doc | Could be mistaken for current implementation |
| knowledge-base/08_MODEL_PROVIDER_AND_SKILLS_STRATEGY.md | Provider/skills strategy note | REFERENCE | Overlaps README.md, 09_ECOSYSTEM_WATCHLIST.md, transcript_roadmap_evidence.md | Keep as supporting reference | Useful strategy context but not primary canon entrypoint | Provider/skills strategy may get repeated elsewhere |
| knowledge-base/09_ECOSYSTEM_WATCHLIST.md | External signal watchlist | REFERENCE | Overlaps transcript_roadmap_evidence.md watchlist logic | Keep as reference only | Useful background, not canon or roadmap truth by itself | Watchlist noise can look like product policy |
| knowledge-base/10_SECURITY_AND_RELEASE_HYGIENE.md | Security and release hygiene canon | ACTIVE_CORE | Overlaps cyberiad/literary guardrail notes | Keep | Durable safety posture for the Jeeves runtime side | Safety rules fragment across metaphor docs and runtime docs |
| knowledge-base/11_CONTINUATION_GUIDE_AND_NEXT_STEPS.md | Continuation/handoff guide for Jeeves repo | ACTIVE_CORE | Overlaps projects/jeeves/handoff.md and README.md next-stage text | Keep | Strong continuation note tied to audited repo state | Continuation advice can diverge from current implementation truth |
| knowledge-base/12_DEPLOYMENT_AND_FAMILY_RUNTIME.md | Future deployment/family target | ROADMAP | Overlaps README.md deployment text and future product goals | Keep as roadmap | Accepted future direction, not current implementation | Readers may assume multi-user deployment is closer than it is |
| knowledge-base/PROJECT_KNOWLEDGE_BASE.md | Legacy one-file Jeeves snapshot | DUPLICATE | Superseded by knowledge-base/README.md and 01-12 series | Demote and point to the split KB | The newer split set is cleaner and already referenced as canonical | Parallel canon snapshots drift apart |
| knowledge-base/README.md | Jeeves KB entrypoint | ACTIVE_CORE | Overlaps README.md and PROJECT_KNOWLEDGE_BASE.md | Keep as the Jeeves canon entrypoint | Best concise read-order for the structured Jeeves KB | Parallel entrypoints dilute canon authority |
| knowledge-base/history_sources/2026-05-01-chatgpt-memory-snapshot.md | Historical recovery source note | ARCHIVE | Overlaps recovery_audit/2026-05-01_memory_overflow_branch.md | Keep as archive/reference only | Useful provenance, not active canon | Historical recovery sources can crowd active startup surface |
| knowledge_base/CHATGPT_BRANCH_CONTINUITY_BOOT.md | Boot continuity rationale/protocol | REFERENCE | Overlaps START_HERE_FOR_CHATGPT.md and BOOTLOADER.md | Keep as supporting rationale, not primary startup surface | Explains the anti-amnesia reason well | If treated as another startup source, boot surface keeps expanding |
| knowledge_base/CHATGPT_EXOSKELETON.md | Skeleton model/definition | ACTIVE_CORE | Overlaps START_HERE_FOR_CHATGPT.md and RUNBOOK at different depths | Keep as WHAT_IS_SKELETON candidate | Best durable statement of Skeleton identity | Skeleton identity will stay fuzzy without one primary definition |
| knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md | Skeleton operational runbook | ACTIVE_CORE | Overlaps WORKING_PROTOCOL.md and chatgpt_exoskeleton/START_HERE.md | Keep as OPERATING_PROTOCOL candidate | Best detailed behavior checklist for Skeleton work | Operational rules split across multiple docs |
| knowledge_base/CHATGPT_EXTERNAL_DIARY_PROTOCOL.md | Diary structure/protocol | REFERENCE | Overlaps assistant_diary.md and chatgpt_diary/README.md | Keep as supporting protocol | Useful diary shape, but not a top-level startup doc | Adds another continuity doc to read by default |
| knowledge_base/CHATGPT_SETTINGS_STARTER.md | Settings/custom-instructions snippet | REFERENCE | Overlaps START_HERE_FOR_CHATGPT.md and BOOTLOADER.md | Keep as implementation helper only | Useful bootloader snippet, not canon source | Settings text may be mistaken for primary truth |
| knowledge_base/MEMORY_POLICY.md | Global memory/public-private routing policy | ACTIVE_CORE | Overlaps knowledge-base/06_MEMORY_AND_HANDOFF.md and diary protocol docs | Keep | Durable routing/persistence rule set | Public/private/canon routing will drift across docs |
| knowledge_base/START_HERE_FOR_CHATGPT.md | Global ChatGPT collaboration startup anchor | ACTIVE_CORE | Overlaps BOOTLOADER.md, WORKING_PROTOCOL.md, CHATGPT_BRANCH_CONTINUITY_BOOT.md | Keep but narrow to startup routing only in a later PR | Still the main cross-project wake anchor | Too many boot docs create startup drift |
| knowledge_base/WORKING_PROTOCOL.md | Command/alias operating protocol | ACTIVE_CORE | Overlaps START_HERE_FOR_CHATGPT.md, CHATGPT_EXOSKELETON_RUNBOOK.md, assistant_startup_prompt.md | Keep as protocol truth | Best compact command/alias protocol today | Command semantics may split across boot and runbook docs |
| knowledge_base/assistant_diary.md | Global continuity diary | REFERENCE | Overlaps chatgpt_diary/README.md and project handoffs | Keep as supporting diary log | Useful continuity log but not canonical rule source | Diary entries can be mistaken for canon |
| knowledge_base/assistant_startup_prompt.md | Compact Jeeves/ChatGPT startup prompt | STALE_OR_RISKY | Overlaps START_HERE_FOR_CHATGPT.md, projects/jeeves/START_HERE.md, jeeves_runtime/START_HERE.md | Demote or split in a later cleanup PR | Still mixes global boot, Skeleton, and future Jeeves runtime concerns | Namespace confusion between Skeleton and Jeeves persists |
| knowledge_base/chatgpt_diary/README.md | Older diary entrypoint | DUPLICATE | Overlaps assistant_diary.md and START_HERE_FOR_CHATGPT.md | Demote or archive after redirecting references | Creates a second continuity entrypoint | Too many diary entrypoints increase boot surface |
| knowledge_base/chatgpt_diary/entries/2026-05-03-chatgpt-boot-and-diary-foundation.md | Historical diary entry | ARCHIVE | Overlaps assistant_diary.md and diary protocol docs | Keep as archive | Chronological evidence, not active canon | Historical entries can clutter the active wake surface |
| knowledge_base/chatgpt_diary/project_write_index.md | Write-map / project index from older structure | STALE_OR_RISKY | Conflicts with knowledge_base/projects/PROJECT_INDEX.md and actual project folder layout | Refresh or demote in a future cleanup PR | Contains expected future paths that no longer match the repo structure cleanly | Navigation drift and false path expectations |
| knowledge_base/chatgpt_exoskeleton/CONTROLLED_GROWTH.md | Skeleton skill growth/activation rule | ACTIVE_CORE | Overlaps skill_inventory_activation_map.md and coding_lane_template_and_evidence_protocol.md | Keep as LANES_AND_ACTIVATION candidate | Durable rule for how Skeleton skills become real gates | Skill sprawl stays unmanaged |
| knowledge_base/chatgpt_exoskeleton/CURRENT_STATE.md | Skeleton current handoff/state | ACTIVE_CORE | Overlaps docs/dual_brain_state.md, skeleton_diary.md, runner/task issue comments | Keep as CURRENT_STATE candidate | Best short current-state file for Skeleton | Operational truth will scatter into issues/logs/docs |
| knowledge_base/chatgpt_exoskeleton/RESEARCH_EXTERNAL_LLM_HARNESS_PATTERNS.md | External reference patterns | REFERENCE | Overlaps transcript_roadmap_evidence.md | Keep as reference only | Pattern source, not active policy | Reference material can be mistaken for approved architecture |
| knowledge_base/chatgpt_exoskeleton/SKELETON_RUNNER_TASK_TEMPLATE.md | Generic runner task template | REFERENCE | Overlaps coding_lane_template_and_evidence_protocol.md and project executor_tasks | Keep as template reference | Useful template, not canon truth | Template may be mistaken for active lane policy |
| knowledge_base/chatgpt_exoskeleton/START_HERE.md | Skeleton namespace entrypoint | ACTIVE_CORE | Overlaps START_HERE_FOR_CHATGPT.md and BOOTLOADER.md | Keep as START_HERE candidate | Best Skeleton-specific entrypoint | Skeleton wake path will stay ambiguous without one namespace start |
| knowledge_base/chatgpt_exoskeleton/behoerdenpost/BEHOERDENPOSTKONTUR_TASK.md | Domain-specific task spec | DOMAIN_SPECIFIC | Part of behoerdenpost workflow only | Keep outside active core | Task-specific workflow doc, not general canon | One-off task specs can clutter the active docs surface |
| knowledge_base/chatgpt_exoskeleton/runner_tasks/coding_lane_template_and_evidence_protocol.md | Coding lane protocol | ACTIVE_CORE | Overlaps CONTROLLED_GROWTH.md and SKELETON_RUNNER_TASK_TEMPLATE.md | Keep as lane protocol until a tighter single lane doc exists | Real cross-cutting Skeleton workflow gate | Coding-lane truth may drift into templates and inventories |
| knowledge_base/chatgpt_exoskeleton/runner_tasks/construction_takeoff_runner_task_template.md | Construction-takeoff runner template | DOMAIN_SPECIFIC | Overlaps construction_takeoff_from_drawings.md and semi-automatic takeoff docs | Keep as domain-specific workflow template | Useful only for the takeoff domain | Could be mistaken for general Skeleton policy |
| knowledge_base/chatgpt_exoskeleton/runner_tasks/create_construction_takeoff_skill.md | One-off skill creation task | ARCHIVE | Overlaps construction_takeoff docs and CONTROLLED_GROWTH.md | Keep as archive only | Historical implementation task | Task artifacts can be mistaken for living canon |
| knowledge_base/chatgpt_exoskeleton/runner_tasks/gemini_auditor_adapter_task.md | One-off Gemini adapter task | ARCHIVE | Overlaps gemini_auditor_node.md and CURRENT_STATE.md | Keep as archive only | Historical implementation task | Task artifacts can be mistaken for active capability docs |
| knowledge_base/chatgpt_exoskeleton/runner_tasks/semi_automatic_construction_takeoff_gemini_task_template.md | Semi-automatic takeoff template | DOMAIN_SPECIFIC | Overlaps semi_automatic_construction_takeoff_with_gemini.md | Keep as domain-specific workflow template | Useful only for the takeoff/Gemini pilot domain | Could be mistaken for general Skeleton workflow |
| knowledge_base/chatgpt_exoskeleton/skill_inventory_activation_map.md | Statusful skill inventory | STALE_OR_RISKY | Overlaps CONTROLLED_GROWTH.md and coding_lane_template_and_evidence_protocol.md | Replace later with a tighter lanes/activation doc | Contains dated status, issue references, and wiring priorities | Activation truth ages quickly and drifts |
| knowledge_base/chatgpt_exoskeleton/skills/construction_takeoff_from_drawings.md | Construction takeoff skill | DOMAIN_SPECIFIC | Overlaps takeoff runner templates and semi-automatic takeoff docs | Keep as domain-specific skill | Useful domain skill, not core Skeleton canon | Domain pilot docs may look like global rules |
| knowledge_base/chatgpt_exoskeleton/skills/gemini_auditor_node.md | Gemini auditor bridge skill | REFERENCE | Overlaps CURRENT_STATE.md and Gemini adapter task doc | Keep as supporting capability reference | Reusable Skeleton capability, but not startup canon | Capability docs can be mistaken for live verified status |
| knowledge_base/chatgpt_exoskeleton/skills/semi_automatic_construction_takeoff_with_gemini.md | Semi-automatic takeoff skill | DOMAIN_SPECIFIC | Overlaps takeoff skill and takeoff task template docs | Keep as domain-specific skill | Useful domain pilot workflow, not global canon | Pilot workflow docs may inflate the active core |
| knowledge_base/chatgpt_exoskeleton/tasks/2026-05-05_boot_queue_validation.md | One-off Skeleton task artifact | ARCHIVE | Overlaps CURRENT_STATE.md and issue history | Keep as archive only | Historical task artifact | Adds noise to the active Skeleton docs surface |
| knowledge_base/jeeves/cyberiad_test.md | Compact safety heuristic | REFERENCE | Overlaps literary_guardrail_tests.md and knowledge-base/10_SECURITY_AND_RELEASE_HYGIENE.md | Keep as supporting safety reference | Useful mnemonic, not primary policy document | Metaphor docs may crowd core security canon |
| knowledge_base/jeeves/literary_guardrail_tests.md | Expanded safety heuristics | REFERENCE | Overlaps cyberiad_test.md and knowledge-base/10_SECURITY_AND_RELEASE_HYGIENE.md | Keep as supporting safety reference | Useful guardrail catalog, not a startup doc | Can look more authoritative than the runtime security canon |
| knowledge_base/jeeves_runtime/START_HERE.md | Jeeves runtime namespace marker | REFERENCE | Overlaps projects/jeeves/START_HERE.md and assistant_startup_prompt.md | Keep as namespace separator | Helpful namespace marker but too thin to be the full runtime entrypoint | If treated as full canon, runtime truth stays scattered |
| knowledge_base/project_state/BAUCLOCK_PROJECT_STATE.md | Older single-file BauClock state note | DUPLICATE | Superseded by knowledge_base/projects/bauclock/current_state.md and related project files | Demote/archive later | Old single-file project state predates the per-project folder pattern | Two BauClock state surfaces will drift |
| knowledge_base/project_state/PROJECT_STATE_TEMPLATE.md | Older project state template | DUPLICATE | Superseded by knowledge_base/projects/TEMPLATE_PROJECT_STRUCTURE.md | Demote/archive later | Template has been replaced by the fuller project folder structure | Competing templates create structural confusion |
| knowledge_base/projects/PROJECT_INDEX.md | Cross-project navigation index | REFERENCE | Overlaps chatgpt_diary/project_write_index.md and START_HERE_FOR_CHATGPT.md | Keep as project navigation reference | Clean index of project folders | Index drift if multiple project maps stay active |
| knowledge_base/projects/TEMPLATE_PROJECT_STRUCTURE.md | Project doc template | REFERENCE | Overlaps project_state/PROJECT_STATE_TEMPLATE.md | Keep the newer template only | Useful structural reference for project docs | Competing templates fragment project structure |
| knowledge_base/projects/android_tv/START_HERE.md | Project startup entrypoint | DOMAIN_SPECIFIC | Part of knowledge_base/projects/android_tv/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/android_tv/current_state.md | Project working state | DOMAIN_SPECIFIC | Part of knowledge_base/projects/android_tv/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/android_tv/decisions.md | Project decisions log | DOMAIN_SPECIFIC | Part of knowledge_base/projects/android_tv/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/android_tv/handoff.md | Project handoff | DOMAIN_SPECIFIC | Part of knowledge_base/projects/android_tv/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/android_tv/open_questions.md | Project open questions | DOMAIN_SPECIFIC | Part of knowledge_base/projects/android_tv/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/android_tv/tasks.md | Project task list | DOMAIN_SPECIFIC | Part of knowledge_base/projects/android_tv/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/bauclock/START_HERE.md | Project startup entrypoint | DOMAIN_SPECIFIC | Part of knowledge_base/projects/bauclock/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/bauclock/current_state.md | Project working state | DOMAIN_SPECIFIC | Part of knowledge_base/projects/bauclock/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/bauclock/decisions.md | Project decisions log | DOMAIN_SPECIFIC | Part of knowledge_base/projects/bauclock/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/bauclock/handoff.md | Project handoff | DOMAIN_SPECIFIC | Part of knowledge_base/projects/bauclock/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/bauclock/open_questions.md | Project open questions | DOMAIN_SPECIFIC | Part of knowledge_base/projects/bauclock/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/bauclock/tasks.md | Project task list | DOMAIN_SPECIFIC | Part of knowledge_base/projects/bauclock/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/gewerbe/START_HERE.md | Project startup entrypoint | DOMAIN_SPECIFIC | Part of knowledge_base/projects/gewerbe/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/gewerbe/current_state.md | Project working state | DOMAIN_SPECIFIC | Part of knowledge_base/projects/gewerbe/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/gewerbe/decisions.md | Project decisions log | DOMAIN_SPECIFIC | Part of knowledge_base/projects/gewerbe/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/gewerbe/handoff.md | Project handoff | DOMAIN_SPECIFIC | Part of knowledge_base/projects/gewerbe/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/gewerbe/open_questions.md | Project open questions | DOMAIN_SPECIFIC | Part of knowledge_base/projects/gewerbe/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/gewerbe/tasks.md | Project task list | DOMAIN_SPECIFIC | Part of knowledge_base/projects/gewerbe/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/homelab/START_HERE.md | Project startup entrypoint | DOMAIN_SPECIFIC | Part of knowledge_base/projects/homelab/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/homelab/current_state.md | Project working state | DOMAIN_SPECIFIC | Part of knowledge_base/projects/homelab/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/homelab/decisions.md | Project decisions log | DOMAIN_SPECIFIC | Part of knowledge_base/projects/homelab/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/homelab/handoff.md | Project handoff | DOMAIN_SPECIFIC | Part of knowledge_base/projects/homelab/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/homelab/open_questions.md | Project open questions | DOMAIN_SPECIFIC | Part of knowledge_base/projects/homelab/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/homelab/tasks.md | Project task list | DOMAIN_SPECIFIC | Part of knowledge_base/projects/homelab/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/jeeves/START_HERE.md | Jeeves project startup entrypoint | ACTIVE_PROJECT | Overlaps knowledge-base/README.md, assistant_startup_prompt.md, jeeves_runtime/START_HERE.md | Keep as project-layer entrypoint | Good project-scoped startup note distinct from global boot | Project/runtime boundary stays blurry if this drifts |
| knowledge_base/projects/jeeves/current_state.md | Jeeves project working state | ACTIVE_PROJECT | Overlaps knowledge-base/03_IMPLEMENTATION_STATE.md and README.md | Keep as project-layer state only | Useful short project-state snapshot separate from deep repo audit | May conflict with audited implementation state |
| knowledge_base/projects/jeeves/decisions.md | Jeeves project decisions | ACTIVE_PROJECT | Overlaps knowledge-base/01-12 canon set | Keep | Good project-layer decision summary | Decision truth may split between project docs and Jeeves KB |
| knowledge_base/projects/jeeves/executor_tasks/2026-05-01_stage1_bootstrap_validation.approved.md | Closed runner approval artifact | ARCHIVE | Overlaps sibling task artifact | Keep as archive only | Historical task evidence | Task artifacts can masquerade as current process |
| knowledge_base/projects/jeeves/executor_tasks/2026-05-01_stage1_bootstrap_validation.md | Closed runner task artifact | ARCHIVE | Overlaps later Jeeves task/process docs | Keep as archive only | Historical execution artifact | Old task instructions may be mistaken for current workflow |
| knowledge_base/projects/jeeves/executor_tasks/2026-05-02_runner_health_cleanup.md | Closed runner task artifact | ARCHIVE | Overlaps handoff and runner report | Keep as archive only | Historical execution artifact | Old task instructions may be mistaken for active policy |
| knowledge_base/projects/jeeves/handoff.md | Jeeves project handoff | ACTIVE_PROJECT | Overlaps knowledge-base/11_CONTINUATION_GUIDE_AND_NEXT_STEPS.md and runner_reports | Keep as latest handoff only | Project continuation note is useful when kept short | Host-specific status can make handoff stale quickly |
| knowledge_base/projects/jeeves/open_questions.md | Jeeves project open questions | ACTIVE_PROJECT | Part of projects/jeeves cluster | Keep | Useful working backlog of unresolved questions | Open questions can drift out of sync with roadmap/canon |
| knowledge_base/projects/jeeves/runner_reports/20260502-085821-runner-status.md | Point-in-time runner report | STALE_OR_RISKY | Overlaps CURRENT_STATE.md, handoff.md, issue comments | Archive or clearly demote later | Very detailed operational report ages quickly | Readers may treat old operational status as current truth |
| knowledge_base/projects/jeeves/tasks.md | Jeeves project task list | ACTIVE_PROJECT | Part of projects/jeeves cluster | Keep | Useful working task surface | Task truth may scatter into issue comments and docs |
| knowledge_base/projects/lavalamp/START_HERE.md | Project startup entrypoint | DOMAIN_SPECIFIC | Part of knowledge_base/projects/lavalamp/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/lavalamp/current_state.md | Project working state | DOMAIN_SPECIFIC | Part of knowledge_base/projects/lavalamp/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/lavalamp/decisions.md | Project decisions log | DOMAIN_SPECIFIC | Part of knowledge_base/projects/lavalamp/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/lavalamp/handoff.md | Project handoff | DOMAIN_SPECIFIC | Part of knowledge_base/projects/lavalamp/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/lavalamp/open_questions.md | Project open questions | DOMAIN_SPECIFIC | Part of knowledge_base/projects/lavalamp/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/lavalamp/tasks.md | Project task list | DOMAIN_SPECIFIC | Part of knowledge_base/projects/lavalamp/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/van/START_HERE.md | Project startup entrypoint | DOMAIN_SPECIFIC | Part of knowledge_base/projects/van/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/van/current_state.md | Project working state | DOMAIN_SPECIFIC | Part of knowledge_base/projects/van/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/van/decisions.md | Project decisions log | DOMAIN_SPECIFIC | Part of knowledge_base/projects/van/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/van/handoff.md | Project handoff | DOMAIN_SPECIFIC | Part of knowledge_base/projects/van/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/van/open_questions.md | Project open questions | DOMAIN_SPECIFIC | Part of knowledge_base/projects/van/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/projects/van/tasks.md | Project task list | DOMAIN_SPECIFIC | Part of knowledge_base/projects/van/ cluster only | Keep in project folder; exclude from Skeleton/Jeeves active core | Active within its own project, not global Skeleton/Jeeves canon | Domain docs may be mistaken for global canon if surfaced too early |
| knowledge_base/recovery_audit/2026-05-01_memory_overflow_branch.md | Historical recovery audit note | ARCHIVE | Overlaps history_sources and current boot docs | Keep as archive | Useful provenance only | Historical recovery text may override current canon by accident |
| knowledge_base/skeleton_diary.md | Operational Skeleton trace log | STALE_OR_RISKY | Overlaps runner reports and audit comments as operational evidence | Demote to archive/log surface | Operational append-only log should not sit near active canon | Host/task traces can be mistaken for active policy or current state |


## Duplication Clusters

### 1. Boot / startup / protocol
Files:
- `BOOTLOADER.md`
- `knowledge_base/START_HERE_FOR_CHATGPT.md`
- `knowledge_base/WORKING_PROTOCOL.md`
- `knowledge_base/CHATGPT_BRANCH_CONTINUITY_BOOT.md`
- `knowledge_base/assistant_startup_prompt.md`
- `knowledge_base/CHATGPT_EXOSKELETON.md`
- `knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md`
- `knowledge_base/chatgpt_exoskeleton/START_HERE.md`

Observation:
- the same wake path, namespace split, and command behavior are explained repeatedly at different depths
- this is the biggest active-surface problem in the repo docs

### 2. Jeeves runtime canon snapshots
Files:
- `README.md`
- `knowledge-base/README.md`
- `knowledge-base/PROJECT_KNOWLEDGE_BASE.md`
- `knowledge-base/01_PROJECT_OVERVIEW.md`
- `knowledge-base/02_ARCHITECTURE_AND_PRINCIPLES.md`
- `knowledge-base/03_IMPLEMENTATION_STATE.md`
- `knowledge-base/11_CONTINUATION_GUIDE_AND_NEXT_STEPS.md`
- `knowledge_base/projects/jeeves/*`

Observation:
- the newer `knowledge-base/` split set is the cleanest Jeeves runtime canon
- `README.md` and `PROJECT_KNOWLEDGE_BASE.md` still compete with it
- `knowledge_base/projects/jeeves/*` is useful, but it is a working project layer, not the same thing as runtime canon

### 3. Diary / recovery / history / logs
Files:
- `knowledge_base/assistant_diary.md`
- `knowledge_base/chatgpt_diary/*`
- `knowledge_base/recovery_audit/*`
- `knowledge-base/history_sources/*`
- `knowledge_base/skeleton_diary.md`
- `knowledge_base/projects/jeeves/runner_reports/*`

Observation:
- the repo contains both durable continuity notes and low-level operational/history artifacts
- these should not be equally visible in default boot/read paths

### 4. Lanes / skills / templates
Files:
- `knowledge_base/chatgpt_exoskeleton/CONTROLLED_GROWTH.md`
- `knowledge_base/chatgpt_exoskeleton/skill_inventory_activation_map.md`
- `knowledge_base/chatgpt_exoskeleton/runner_tasks/coding_lane_template_and_evidence_protocol.md`
- `knowledge_base/chatgpt_exoskeleton/SKELETON_RUNNER_TASK_TEMPLATE.md`
- domain skill/task/template docs under `skills/`, `runner_tasks/`, and `behoerdenpost/`

Observation:
- the durable rule surface is smaller than the current file surface
- `CONTROLLED_GROWTH.md` and the coding-lane protocol look like the enduring rules
- the inventory map is useful but should not be treated as stable canon because it includes dated priorities/status

### 5. Project docs structure
Files:
- `knowledge_base/project_state/*`
- `knowledge_base/projects/*`
- `knowledge_base/chatgpt_diary/project_write_index.md`
- `knowledge_base/projects/PROJECT_INDEX.md`

Observation:
- the repo has already converged on `knowledge_base/projects/<project>/...`
- older single-file state docs and older expected-path indexes are now the confusing layer

## Ideas and Roadmap Handling
- active roadmap:
  - `knowledge-base/05_ACTION_LAYER.md`
  - `knowledge-base/07_KNOWLEDGE_BASE_SUBSYSTEM.md`
  - `knowledge-base/12_DEPLOYMENT_AND_FAMILY_RUNTIME.md`
- idea backlog / evidence backlog:
  - `docs/transcript_roadmap_evidence.md`
  - parts of `knowledge_base/chatgpt_exoskeleton/skill_inventory_activation_map.md` that are issue/status driven rather than stable canon
- reference ideas:
  - `knowledge_base/chatgpt_exoskeleton/RESEARCH_EXTERNAL_LLM_HARNESS_PATTERNS.md`
  - `knowledge-base/09_ECOSYSTEM_WATCHLIST.md`
- stale ideas / risky pseudo-roadmaps:
  - `docs/dual_brain_state.md` when used as current truth instead of historical anchor
  - `README.md` when used as current implementation state instead of landing page

## Skeleton vs Jeeves Separation
The cleanest practical split visible in the current repo is:
- `knowledge_base/chatgpt_exoskeleton/**` = Skeleton / ChatGPT-side operating layer
- `knowledge-base/**` = Jeeves runtime canon and repo-state documentation
- `knowledge_base/projects/**` = project working memory layer
- `knowledge_base/recovery_audit/**`, `knowledge-base/history_sources/**`, diary entries, runner reports, and task artifacts = archive/reference/evidence layer

Where they are still mixed:
- `README.md` presents runtime state, but the repo surface is actually a mixed Skeleton + Jeeves documentation repository
- `knowledge_base/assistant_startup_prompt.md` still bundles global boot, Skeleton behavior, and Jeeves runtime startup semantics
- `knowledge_base/projects/jeeves/*` is useful project memory but overlaps with the newer `knowledge-base/**` runtime canon set
- `knowledge_base/jeeves_runtime/START_HERE.md` is a good separator label, but most actual runtime canon still lives elsewhere

## Proposed Cleanup PR Sequence
1. **Boot Surface Compression**
   - keep `BOOTLOADER.md` tiny
   - choose one active global wake doc and one active Skeleton start doc
   - demote duplicate diary/boot entrypoints
2. **Jeeves Runtime Truth Refresh**
   - align `README.md` with `knowledge-base/03_IMPLEMENTATION_STATE.md`
   - demote `knowledge-base/PROJECT_KNOWLEDGE_BASE.md` as legacy snapshot
3. **Protocol and Lane Compression**
   - reduce split protocol truth across `WORKING_PROTOCOL.md`, runbook, continuity boot, and startup prompt
   - separate durable lane policy from dated skill inventory/status
4. **History / Logs Segregation**
   - move runner reports, task artifacts, and diaries out of default boot/read surfaces
   - keep one current state and one handoff surface per namespace/project
5. **Project Structure Dedup**
   - retire `knowledge_base/project_state/*` in favor of `knowledge_base/projects/*`
   - refresh or retire older write-index docs that still point to pre-`projects/` layouts
