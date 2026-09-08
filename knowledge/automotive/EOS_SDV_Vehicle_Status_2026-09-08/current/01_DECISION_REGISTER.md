---
document_id: EOS-SDV-VS-DECISIONS-2026-09-08
project_id: DAR-SDV-VS-001
as_of: 2026-09-08
record_type: decision_register
status: proposal_record_not_signed_approval
---

# Decision register - current proposal and user requirements

This record distinguishes user instructions, the retained source baseline, proposed design choices and model assumptions. **No entry below is evidence that management approved funding or that an acceptance test passed.** Older conflicting schedules are recorded in `../history/THREAD_EVOLUTION.md`, not as current commitments.

Source IDs resolve in `../README.md` and `../metadata/artifact_manifest.json`. U1-U5 are request summaries in the thread-evolution record.

## D01 - Purpose

**Status:** USER_REQUIREMENT. **Management approval evidenced:** No.

Prepare a request for management approval, not an implementation-completion report.

**Reason / boundary:** The user needs a report for the boss; no signed approval appears in the thread.

**Source:** U1; U4; P12:1,5.

## D02 - Communication

**Status:** USER_REQUIREMENT. **Management approval evidenced:** No.

Keep the approval narrative in English, short and understandable to a non-technical manager.

**Reason / boundary:** Explain the main idea, practical effectiveness, advantages, disadvantages and examples.

**Source:** U1; U3; U4.

## D03 - Deliverables

**Status:** USER_REQUIREMENT. **Management approval evidenced:** No.

Provide the same approval narrative in .md and .docx, with a separate dynamic Excel plan.

**Reason / boundary:** Excel owns changing assumptions; the narrative owns the stable idea and approval criteria.

**Source:** U3; U4; P12:5.

## D04 - Selected idea

**Status:** RETAINED_PROPOSAL. **Management approval evidenced:** No.

Keep Option C: Hardware-Agnostic Telematics Hub, limited to reusable Vehicle Status.

**Reason / boundary:** No switch to another Automotive idea and no universal gateway expansion.

**Source:** P1:11; U3; U4; P12:1.

## D05 - Runtime

**Status:** SOURCE_BASELINE. **Management approval evidenced:** No.

Use the existing AAOS PoC as the starting implementation and primary runtime baseline.

**Reason / boundary:** Its existence is not proof of buildability, clean architecture or portability.

**Source:** P1:1-3; P12:1.

## D06 - Host runner

**Status:** SOURCE_BASELINE. **Management approval evidenced:** No.

Use a lightweight deterministic runner executing the same core for tests and CI only.

**Reason / boundary:** No separate Linux product deployment and no duplicate reimplementation of the core.

**Source:** P1:1,4,10; P12:4.

## D07 - Dependency boundary

**Status:** RETAINED_TECHNICAL_PROPOSAL. **Management approval evidenced:** No.

Keep Android, OEM vocabulary, cloud SDK/payload and storage implementation types outside the core.

**Reason / boundary:** Project-owned contracts separate shared behavior from integration details.

**Source:** P1:3-4; P10:5.

## D08 - Core changes

**Status:** SOURCE_BASELINE. **Management approval evidenced:** No.

Permit recovery/refactoring changes, then freeze behavior and govern exceptional post-freeze changes.

**Reason / boundary:** A zero-change requirement does not prohibit the initial extraction; later changes require review and regression evidence.

**Source:** P1:3.3-3.4; P10:18-19.

## D09 - Vehicle replacement

**Status:** SOURCE_BASELINE. **Management approval evidenced:** No.

Demonstrate A and B mappings, with B allowed to be deterministic/injected or controlled.

**Reason / boundary:** No second live OEM integration is assumed in the pilot.

**Source:** P1:5.1; P12:4.

## D10 - Meaning

**Status:** RETAINED_TECHNICAL_PROPOSAL. **Management approval evidenced:** No.

Preserve units, quality, timestamps and semantic basis; reject unsupported equivalence.

**Reason / boundary:** Missing is not zero; a unit conversion is not a license to equate different battery-charge definitions.

**Source:** P1:5.1; P10:6; P12:2-3.

## D11 - Backend connections

**Status:** SOURCE_BASELINE. **Management approval evidenced:** No.

Use MQTT/TLS as the primary connection and HTTPS/TLS as the replacement.

**Reason / boundary:** Preserve data, publish decisions, IDs and outcome meaning; do not invent equivalent subscription capabilities.

**Source:** P1:5.2; P10:8.

## D12 - Cloud claim

**Status:** RETAINED_SCOPE_LIMIT. **Management approval evidenced:** No.

A shared controlled backend with two protocols proves protocol substitution only.

**Reason / boundary:** Independent cloud-vendor portability needs a separately evidenced integration.

**Source:** P10:8,12; P12:2.

## D13 - Status identity

**Status:** RETAINED_TECHNICAL_PROPOSAL. **Management approval evidenced:** No.

Generate one immutable status identity and retain its envelope and ID through queueing and retry.

**Reason / boundary:** Retry is not a new publish trigger; protocol packet IDs are not application status IDs.

**Source:** P10:6-9.

## D14 - Receipts

**Status:** RETAINED_TECHNICAL_PROPOSAL. **Management approval evidenced:** No.

Separate transport acceptance from the declared receiver application-confirmation step.

**Reason / boundary:** Do not delete a retained record as delivered before the approved receipt condition.

**Source:** P10:8-9; P11:3.

## D15 - Offline recovery

**Status:** RETAINED_TECHNICAL_PROPOSAL. **Management approval evidenced:** No.

Use bounded durable retention, declared overflow/expiry and observable retries, losses and duplicates.

**Reason / boundary:** No unlimited storage, zero-loss or exactly-once transport claim.

**Source:** P1:8,11; P10:9; P12:4.

## D16 - Vehicle safety boundary

**Status:** RETAINED_SCOPE_LIMIT. **Management approval evidenced:** No.

Read vehicle status only; expose no actuator/write path for this capability.

**Reason / boundary:** This internal pilot is not approval for vehicle control.

**Source:** P1:8,11; P10:10; P12:4.

## D17 - Controlled settings

**Status:** RETAINED_TECHNICAL_PROPOSAL. **Management approval evidenced:** No.

Allow only TELEMETRY_PROFILE_UPDATE, with authorization, target, freshness, replay, schema and range checks.

**Reason / boundary:** Apply valid changes atomically; keep remote configuration disabled until the required checks pass.

**Source:** P10:7,10; P12:4-5.

## D18 - Reporting triggers

**Status:** PROPOSED_NOT_APPROVED. **Management approval evidenced:** No.

Periodic, material-change and first-valid-snapshot are the proposed three triggers.

**Reason / boundary:** The source required three triggers without fully defining them; these must be reconciled or approved at Gate B.

**Source:** P1:7-8; P10:7; P11:3.

## D19 - Technical limits

**Status:** PROPOSED_NOT_APPROVED. **Management approval evidenced:** No.

Retain numerical schema, queue, freshness, profile and command limits as proposed starting values only.

**Reason / boundary:** No operating measurements or approved production sizing substantiate these defaults.

**Source:** P10:6-10.

## D20 - Six test groups

**Status:** RETAINED_TECHNICAL_PROPOSAL. **Management approval evidenced:** No.

Retain S1-S6 operational definitions for meaning, policy, replacement, recovery, security and integrated reuse.

**Reason / boundary:** Definitions require approval; the thread contains no actual test-pass evidence.

**Source:** P10:17-19; P12:5.

## D21 - Funding gate

**Status:** RETAINED_PROPOSAL. **Management approval evidenced:** No.

Request recovery funding first; use Gate A to continue, reduce scope or stop.

**Reason / boundary:** Do not automatically release full-project funding.

**Source:** P12:1,5.

## D22 - Reduced demo

**Status:** RETAINED_SCOPE_LIMIT. **Management approval evidenced:** No.

A reduced demo shows mapping A to core to MQTT/TLS to receiver receipt.

**Reason / boundary:** It is not full reuse acceptance; remote settings remain off and crash durability is not claimed before S4.

**Source:** P10:14; P11:1; P12:5.

## D23 - Next platform

**Status:** RETAINED_SCOPE_LIMIT. **Management approval evidenced:** No.

Keep AAOS SDV design readiness separate from actual target runtime validation.

**Reason / boundary:** A porting design, host result or source assumption cannot establish runtime support.

**Source:** P1:6-8; P10:22; P12:4-5.

## D24 - Production exclusions

**Status:** RETAINED_SCOPE_LIMIT. **Management approval evidenced:** No.

Exclude production certification, independent assurance, production PKI/HSM guarantees and untested platform support.

**Reason / boundary:** Internal checks by the implementation team are not independent security assurance.

**Source:** P1:11; P10:19,22; P12:4.

## D25 - Resource changes

**Status:** USER_REQUIREMENT. **Management approval evidenced:** No.

Make total developers and junior count editable; derive experienced count and update the forecast.

**Reason / boundary:** The prior fixed two-person constraint is now the default scenario, not a permanent headcount lock.

**Source:** U2; U3; U4; W12:Inputs!C5:C7.

## D26 - Role-aware capacity

**Status:** RETAINED_PLANNING_ASSUMPTION. **Management approval evidenced:** No.

Model mentoring and junior ramp-up; reserve critical technical decisions for experienced developers.

**Reason / boundary:** Junior capacity cannot be substituted blindly for experienced critical work; no hidden specialist team is assumed.

**Source:** P10:20-20B; W12:Inputs,Guide.

## D27 - Scheduling method

**Status:** RETAINED_PLANNING_ASSUMPTION. **Management approval evidenced:** No.

Use sequential phases, contributor/critical-role caps, minimum duration, waits and upward rounding.

**Reason / boundary:** Additional staff do not automatically produce a proportional schedule reduction.

**Source:** W12:Plan,Guide.

## D28 - Current default forecast

**Status:** MODEL_SNAPSHOT_NOT_COMMITMENT. **Management approval evidenced:** No.

At the saved 1 experienced + 1 junior defaults, forecast recovery W2, core W5, demo W8, pilot W18, reserve W20.

**Reason / boundary:** The old 8-week full-MVP plan is superseded; dates and approvals remain unset.

**Source:** W12:Report,Inputs; H01.

## D29 - Effort units

**Status:** RETAINED_REPORTING_RULE. **Management approval evidenced:** No.

Distinguish 828 planned expert/support work hours from 1,440 default allocated staffed hours.

**Reason / boundary:** Do not label either as actual completed work or directly compare accepted-work hours with an old nominal staffing estimate.

**Source:** W12:Plan!C20:D20,Report!C27; P10:20.

## D30 - Cost

**Status:** RETAINED_REPORTING_RULE. **Management approval evidenced:** No.

Leave unentered money inputs as NOT SET; price only explicit rates and costs.

**Reason / boundary:** Blank does not mean free. Full cost includes recovery once; reserve is additional and needs release.

**Source:** W12:Business Case!C5:C19.

## D31 - Value

**Status:** RETAINED_REPORTING_RULE. **Management approval evidenced:** No.

Leave reuse value NOT QUANTIFIED until comparable effort, incremental setup, maintenance, adoption and evidence are entered.

**Reason / boundary:** Forecast effort savings are not realized cash savings, ROI or revenue.

**Source:** P12:3; W12:Business Case!C25:C35.

## D32 - Break-even

**Status:** ILLUSTRATION_ONLY. **Management approval evidenced:** No.

The report illustrates 80 h without reuse, 40 h with reuse, 160 extra setup h and 40 maintenance h: break-even at 5 later integrations.

**Reason / boundary:** These figures are not live business-case inputs, measured savings or project estimates.

**Source:** P12:3; W12:Business Case!A37.

## D33 - Consumer and effectiveness

**Status:** RETAINED_PROPOSAL. **Management approval evidenced:** No.

Require a named consuming team, comparable work measurement and a reproducible handover.

**Reason / boundary:** A successful upload and a reuse percentage alone do not establish practical return.

**Source:** P12:3.

## D34 - Portfolio options

**Status:** RETAINED_ALTERNATIVE_NOT_SELECTED. **Management approval evidenced:** No.

Keep I2-I7 as considered alternatives, not concurrent projects.

**Reason / boundary:** I2 can be a better early-value choice; the user retained I1 for this approval request.

**Source:** P10:2A-3A; P12:2; U3-U4.

## D35 - Execution options

**Status:** RETAINED_EXECUTION_PROPOSAL. **Management approval evidenced:** No.

Prefer E3 AAOS-first controlled extraction after selecting I1.

**Reason / boundary:** E1 is demo-speed comparator; E2 adds Linux scope; E4 depends on actual SDV target access and fit.

**Source:** P10:2-3; P11:2.

## D36 - Build versus reuse

**Status:** RETAINED_PROPOSAL. **Management approval evidenced:** No.

Check existing platform/library overlap and avoid rebuilding a broker, simulator or generic platform unnecessarily.

**Reason / boundary:** Existing ecosystem context in older files is historical reference, not newly verified in this export.

**Source:** P10:2D; P12:2,4.

## D37 - Dynamic versus static

**Status:** RETAINED_WORKFLOW. **Management approval evidenced:** No.

Excel recalculates resources and management outputs; Markdown and Word do not rewrite themselves.

**Reason / boundary:** Preserve a dated approved workbook when a decision actually occurs.

**Source:** U3-U4; P12:5; W12:Guide.

## D38 - Forecast limits

**Status:** RETAINED_MODEL_LIMIT. **Management approval evidenced:** No.

The workbook models one team from the start, not actual progress, joining dates or a holiday calendar.

**Reason / boundary:** Changing a forecast is not a hiring decision, test pass or approval; rebaseline an in-flight project explicitly.

**Source:** W12:Guide,Scenarios.

## D39 - Replanning

**Status:** RETAINED_PROPOSAL. **Management approval evidenced:** No.

Re-estimate after recovery and when critical work, access, availability or actual throughput diverges.

**Reason / boundary:** Reduce optional scope, release authorized reserve or change the schedule; do not weaken full-acceptance evidence silently.

**Source:** P10:21; P12:4-5.

## D40 - EOS archive

**Status:** USER_REQUIREMENT. **Management approval evidenced:** No.

Preserve the thread ideas, decisions and every available source/report version for EOS.

**Reason / boundary:** Keep current sources separate from superseded history; copying a package is not proof of EOS ingestion.

**Source:** U5.
