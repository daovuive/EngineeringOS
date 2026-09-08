---
document_id: EOS-SDV-VS-CONTEXT-2026-09-08
project_id: DAR-SDV-VS-001
title: Vehicle Status Reuse Pilot - retained thread context
as_of: 2026-09-08
record_type: source_grounded_context_summary
status: current_proposal_pending_management_approval
language: en
aliases: [EngineeringOS, EOS, SDV Vehicle Status, AAOS-first, Hardware-Agnostic Telematics Hub]
---

# Vehicle Status Reuse Pilot - context for EOS

## 1. Purpose and actual status

The user is preparing a request for management approval, not reporting an approved or completed project. The retained idea is **Option C: Hardware-Agnostic Telematics Hub, limited to reusable Vehicle Status**. Start from the existing Android Automotive OS (AAOS) proof of concept and separate reporting rules from vehicle, platform and backend connections. [P1, sections 1-3 and 11; P12, section 1]

The thread produced proposal documents and planning models. It does **not** contain a signed sponsor decision, confirmed project start, actual implementation results, passed acceptance gates, measured reuse savings or validated AAOS SDV runtime support. The source says an AAOS PoC exists; the thread does not independently establish that its current code builds or is reusable. [P1, sections 2-3; P12, sections 1 and 5]

The current management position is: **approve recovery first; fund the remaining build only after confirming feasibility, a real consuming team and an acceptable revised forecast**. This is a recommendation awaiting approval. [P12, sections 1 and 5]

## 2. Authoritative files and reading order

| Information needed | Current authority |
|---|---|
| Business idea, examples, disadvantages and approval request | `SDV_Vehicle_Status_Approval_Report_EN.md` and its identical-purpose Word version, v1.2. |
| Resource inputs, schedule, scenarios and optional cost/value calculations | `SDV_Vehicle_Status_Dynamic_Plan.xlsx`, especially Inputs, Report and Business Case. |
| Decisions and their status | `01_DECISION_REGISTER.md`; source-linked summary, not a signed decision record. |
| Searchable snapshot of the saved Excel assumptions and values | `02_DYNAMIC_PLAN_SNAPSHOT.md`; static snapshot only, not a replacement calculation engine. |
| Retained technical proposal and scenario definitions | `03_TECHNICAL_ACCEPTANCE_REFERENCE.md`, excerpted from v1.0 with original proposal qualifications. |
| Why earlier plans differ | `../history/THREAD_EVOLUTION.md` and the preserved earlier files. |

The latest report and workbook supersede earlier resource/schedule presentations. Older documents remain evidence of the discussion, not parallel current commitments. The source IDs P1, P09, P10, P11, P12, W11 and W12 are resolved in `../README.md` and `../metadata/artifact_manifest.json`.

## 3. How the idea works, in plain English

Keep the same reporting process while changing its translators and delivery channels. A vehicle-side adapter translates a source into an agreed meaning; shared rules decide what to report; a backend adapter delivers the report. Android-specific lifecycle, permissions and services remain outside the shared rules. The host test runner uses the **same core** solely for repeatable testing and continuous integration. It is not a separate Linux product. [P1, sections 1-5; P12, sections 1 and 4]

**Important example:** 12,345.6 kilometres and 12,345,600 metres can represent the same distance. Convert units while preserving meaning. Two differently defined battery-charge values must not be made equivalent merely because they share a field name. Missing battery data is unavailable, not 0%. [P12, sections 1-3]

The intended users are vehicle-software integration teams. The proposed benefit is less repeated development and retesting during later integrations, and clearer evidence that changed connections preserve behavior. This benefit remains a hypothesis. [P12, sections 1-3]

## 4. Scope retained throughout the revisions

| Included in the full pilot | Boundary that must remain visible |
|---|---|
| One recovered/refactored AAOS runtime using shared Vehicle Status rules. | No general vehicle gateway and no new Linux product runtime. |
| Vehicle mappings A and B. | Mapping B may be controlled/injected data; a second live manufacturer is not assumed. |
| MQTT over TLS and HTTPS over TLS. | Two protocols on one controlled backend prove protocol replacement, not independence from all cloud vendors. |
| Bounded, durable offline storage and recovery. | Expiry and overflow can cause declared loss; no zero-loss or exactly-once promise. |
| One authorized reporting-profile update. | No vehicle control; remote settings remain disabled until the required checks pass. |
| Six groups of test evidence, a frozen core and reproducible runbook. | A forecast date or a demo is not a test pass. |
| AAOS SDV porting design and backlog. | Actual next-platform runtime support requires separate execution evidence. |

Production certification, independent security assurance, production PKI/HSM guarantees, a second production cloud deployment and validated QNX/Bosch SdV.OS support are outside the pilot claim. [P1, sections 6 and 10-11; P12, sections 4-5]

## 5. What would make the idea better than a one-off implementation?

The intended advantage is **preserved meaning and tested behavior under substitution**, not merely successful upload. A vehicle or backend change should not require rewriting the reporting rules. However, each new source still needs permissions, mapping, integration and tests. [P12, section 2]

A direct prototype extension may be cheaper for one disposable demo. Reuse adds restructuring, abstractions, tests and maintenance now, and pays back only when later projects actually adopt it. Existing tools may already cover the need; recovery must check overlap before funding custom infrastructure. [P12, sections 2 and 4]

Do not infer savings from reused lines of code or a lower headcount. Compare like-for-like development, review, integration, testing and support. Record one-time incremental reuse effort separately from later adaptation. A named consuming team and a repeatable handover are part of the practical effectiveness check. [P12, section 3]

## 6. Other Automotive ideas retained in the record

| Idea | When it can be a better choice |
|---|---|
| I1. Reusable Vehicle Status - selected proposal | The objective is reusable in-vehicle AAOS/SDV integration and there is a recoverable PoC plus a consumer. |
| I2. Signal replay and semantic validation | Early engineering usefulness and reproducing mapping defects matter more than a runtime capability. |
| I3. Engineering/diagnostic knowledge assistant | Document/log retrieval is the main pain point and an authorized, versioned corpus is available. |
| I4. EV charging and energy observability | An operator has usable charging data and needs session/energy checks. |
| I5. Read-only fleet health dashboard | A real operator workflow and existing data ingestion are available. |
| I6. Predictive-maintenance experiment | Representative failure/maintenance data and a domain partner exist. |
| I7. OTA/update-campaign observability sandbox | An existing updater/simulator and update team need failure/rollback evidence. |

The user explicitly retained I1. The alternatives are not additional funded workstreams. Earlier numerical rankings and pilot windows are preserved under history as proposed judgments for the then-assumed team, not market facts. Adding developers changes the Excel forecast; it does not automatically select another idea or recalculate those historical initiative ratings. [P10, sections 2A-3A; P12, section 2; user requests U3-U4]

## 7. Main disadvantages, dependencies and stop conditions

The principal risks are upfront restructuring, a non-buildable or tightly coupled PoC, missing signal/target access, ambiguous data meaning, experienced-developer bottlenecks, junior mentoring load, unsupported next-platform hosting and too few future integrations to justify maintenance. A limited pilot also lacks production-level assurance. [P10, sections 4 and 21; P12, section 4]

An experienced lead retains responsibility for semantics, architecture, lifecycle, credentials, persistence, concurrency and security decisions. Juniors can deliver bounded implementation, fixtures, automation and evidence under review. Sponsor/domain owners provide approvals and access; they are not hidden implementation staff. [P10, sections 19-21; P11, section 4]

Replan, reduce scope or stop when recovery fails, permissions remain unavailable, a major unbudgeted rewrite is required, accepted throughput misses capacity assumptions, critical work exceeds the forecast, or no consumer is identified. Defer extra signals, UI polish, generic frameworks and production hardening before weakening mandatory evidence. [P10, section 21; P12, sections 4-5]

## 8. Acceptance and evidence, not just a demo

| Group | Required demonstration; definitions remain proposed until approved |
|---|---|
| S1 | Correct signal meaning, units and quality for equivalent and deliberately incompatible mappings. |
| S2 | Approved reporting triggers, timing, boundaries and profile behavior; retries retain identity. |
| S3 | Backend/protocol replacement preserves canonical data, decisions, IDs and equivalent receipt meaning. |
| S4 | Bounded durable queue, outage/restart behavior, expiry, overflow, retry, visible loss and duplicates. |
| S5 | Only authorized settings apply; reject invalid, expired, replayed, wrong-target and vehicle-control inputs. |
| S6 | Integrated A/B x MQTT/HTTPS results and core-change evidence, with a frozen tested baseline. |

Gate A evaluates recovery; Gate B approves the common rules and core tests; the reduced demo validates only one mapping/backend slice; Gate C requires full pilot evidence. The target-design checkpoint and actual SDV runtime port are separate. Record PASS, FAIL or NOT RUN; missing mandatory evidence is not a pass. [P1, section 7; P10, sections 17-19; P12, section 5]

Core changes are allowed during recovery. After stabilization, adapter substitutions and the later port must preserve behavior; any exceptional core fix requires review and repeated tests. Distinguish host tests, injected AAOS inputs, actual vehicle-interface acquisition and receiver evidence. [P1, section 3; P10, sections 11 and 18-19]

## 9. Dynamic resource plan - saved snapshot, not a commitment

The current saved workbook defaults to one experienced developer plus one junior, both allocated full-time. Inputs are 40 nominal hours per person per week, 85% experienced usable time before mentoring, 6 mentoring hours per allocated junior, and junior accepted-work rates of 30% during recovery and 60% afterwards. These yield 28 experienced delivery hours/week and 12/24 junior hours/week at the default mix. These are assumptions, not measured productivity. [W12, Inputs!C5:C32]

The saved default forecast is Gate A at week 2, Gate B at week 5, a reduced demo at week 8, full pilot at week 18 and reserve through week 20. The model contains 476 expert-only plus 352 support-work hours (828 planned work hours), compared with 1,440 nominal allocated hours before reserve. These are different units of accounting. Neither is completed work. [W12, Report and Plan]

Changing Inputs!C5 from 2 to 3 while keeping C6 at 1 adds an experienced developer. The saved comparison forecasts demo week 7, full pilot week 14.5 and 1,740 allocated hours. Additional people can shorten elapsed time while increasing allocated hours. Other role mixes have different results; do not divide duration by headcount. [W12, Scenarios!A9:I14]

The model applies a single team from the start. It includes mentoring, contributor caps, phase floors, upward rounding and waiting time. It does not track actual progress, individual joining dates or a holiday calendar. The current start date is blank. Dates, hiring and cost have not been authorized. [W12, Inputs and Guide]

## 10. Practical value and funding assumptions

Budget inputs are blank: currency, loaded rates and non-labour caps still need entry. The workbook states **NOT SET**, not zero cost. Comparable effort, incremental reuse investment, period maintenance, expected integrations and evidence are also blank; value is **NOT QUANTIFIED**, not proven ROI. [W12, Business Case]

The report's break-even example is explicitly illustrative: 80 hours per later integration without reuse, 40 with reuse, 160 extra setup hours and 40 maintenance hours across the comparison period. Break-even is (160 + 40) / (80 - 40) = 5 later integrations. These are not project estimates, measurements, realized cash savings or revenue. [P12, section 3]

## 11. User requirements for all future revisions

Keep this idea and its approval-seeking context. Reports for the boss must be short, easy for a non-technical reader to follow, explain the main idea and practical advantage, disclose drawbacks and limits, and give examples at important points. The report is in English and is supplied in both Markdown and Word. The resource-aware plan and management forecast live in Excel. [User requests U1-U4]

Excel updates automatically when resources change; the Markdown and Word narrative **does not automatically rewrite itself**. Keep changing figures in Excel to avoid divergent copies. Save the approved workbook version once approval actually happens. [P12, section 5; W12, Guide]

## 12. What must be resolved next

Name the sponsor and consuming team; confirm actual AAOS build/access and signal meanings; validate workload and skill mix; choose the actual target/hosting path; agree triggers, bounds and test definitions; enter rates, infrastructure allowances and a start date; and record Gate A continuation conditions. No approval signatures or tested implementations are supplied by this archive. [P12, section 5; W12, Guide]

**Resume instruction:** continue from the v1.2 approval report and the dynamic workbook. Treat older schedules as historical. Preserve the selected idea and evidence limits. Do not describe forecasts, illustrative examples, source assumptions or proposed technical limits as completed results or approvals.
