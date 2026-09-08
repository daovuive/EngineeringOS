---
document_id: EOS-SDV-VS-PLAN-SNAPSHOT-2026-09-08
project_id: DAR-SDV-VS-001
as_of: 2026-09-08
record_type: static_excel_snapshot
status: model_forecast_not_commitment
source_sha256: 3783214abdc7eee61c7be2613df06b865bc8114c14d4d86ae60151836233c3d6
---

# Dynamic plan - searchable saved snapshot

**Authority:** `SDV_Vehicle_Status_Dynamic_Plan.xlsx` (W12). This text is a read-only snapshot of saved inputs and cached results, not a live model. Editing Excel does not update this Markdown. Refresh the exported snapshot before re-indexing after changes. No workbook inputs, formulas or formatting were altered for this archive.

**Approval/evidence status:** forecasts only. No sponsor approval, completed work, test pass or savings is established. Blank dates/costs/value outputs are intentional where required inputs are unset.

## 1. Executive report

| Field | Saved value | Source cell |
| --- | --- | --- |
| Reduced demo - end week | 8 | Report!A7 |
| Full pilot - end week | 18 | Report!C7 |
| With reserve - end week | 20 | Report!F7 |
| Allocated hours excluding reserve | 1440 | Report!C27 |
| Allocated hours including reserve | 1600 | Report!F27 |
| Model check | OK - formulas consistent; estimates require approval | Report!C35 |

Selected team: 2 developers (1 experienced + 1 junior). Estimated delivery work: 828 hours, including review and tests. This is planned work, not completed work.

Approve recovery only: 2.0 elapsed weeks and 160 allocated hours. Money cap not set; enter rates/costs in Business Case. Re-estimate and confirm a consuming team at Gate A before funding the build.

## 2. Inputs and role-aware capacity

| Input / calculation | Saved value | Cell |
| --- | --- | --- |
| Total developers | 2 | Inputs!C5 |
| Intern / fresher count | 1 | Inputs!C6 |
| Experienced developer count | 1 | Inputs!C7 |
| Paid hours per person / week | 40 | Inputs!C8 |
| Experienced allocation | 1 | Inputs!C9 |
| Junior allocation | 1 | Inputs!C10 |
| Experienced usable time before mentoring | 0.85 | Inputs!C12 |
| Junior accepted work rate, after recovery | 0.6 | Inputs!C13 |
| Junior accepted work rate, during recovery | 0.3 | Inputs!C14 |
| Mentoring hours per allocated junior / week | 6 | Inputs!C15 |
| Maximum experienced contributors per phase | 2 | Inputs!C16 |
| Maximum junior contributors per phase | 2 | Inputs!C17 |
| Planning start date | (blank) | Inputs!C19 |
| Desired reduced-demo week | 8 | Inputs!C20 |
| Desired full-MVP week | 18 | Inputs!C21 |
| Sponsor-controlled reserve (weeks) | 2 | Inputs!C22 |
| Schedule rounding step (weeks) | 0.5 | Inputs!C23 |
| Work estimate multiplier | 1 | Inputs!C24 |
| Calendar days per elapsed week | 7 | Inputs!C25 |
| Experienced pool: delivery hours / week | 28 | Inputs!C27 |
| Experienced: delivery hours per person | 28 | Inputs!C28 |
| Junior: hours per person after recovery | 24 | Inputs!C29 |
| Junior: hours per person during recovery | 12 | Inputs!C30 |
| Nominal allocated team hours / week | 80 | Inputs!C31 |
| Input validation | OK | Inputs!C32 |

Percentage cells are represented as numeric fractions here: 1 = 100%, 0.85 = 85%, 0.6 = 60%, 0.3 = 30%. Changing total developers without changing junior count changes experienced headcount. Keep at least one suitably skilled experienced developer.

## 3. Phase work and default forecast

| ID | Phase | Expert h | Support h | Min weeks | Critical expert slots | Wait weeks | Duration weeks | Finish week |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | Review current AAOS prototype | 56 | 24 | 2 | 1 | 0 | 2 | 2 |
| P2 | Define common reporting rules | 56 | 48 | 1 | 2 | 0 | 2 | 4 |
| P3 | Verify the shared rules | 28 | 24 | 1 | 1 | 0 | 1 | 5 |
| P4 | Connect AAOS vehicle data | 28 | 24 | 1 | 1 | 0 | 1 | 6 |
| P5 | Demo first backend path | 56 | 36 | 1 | 2 | 0 | 2 | 8 |
| P6 | Test replacement connection | 56 | 40 | 1 | 2 | 0 | 2 | 10 |
| P7 | Test outage and restart | 84 | 56 | 2 | 2 | 0 | 3 | 13 |
| P8 | Protect reporting settings | 48 | 30 | 1 | 1 | 0 | 2 | 15 |
| P9 | Validate reuse and hand over | 64 | 70 | 2 | 2 | 0 | 3 | 18 |

| Phase | Checkpoint | Required evidence |
| --- | --- | --- |
| P1 | Gate A | Reproduce build and access; identify dependencies, consumer, risks and revised estimate. |
| P2 | Core foundation | Agree data meanings, reporting triggers and connection boundaries; prepare repeatable inputs. |
| P3 | Gate B | S1-S2 pass; the shared rules build without Android or backend-specific code. |
| P4 | AAOS integration | Vehicle reads, lifecycle, permissions and mapping A use the same shared rules. |
| P5 | Reduced demo | Mapping A -> shared rules -> MQTT/TLS -> receiver receipt. Remote settings stay off. |
| P6 | S3 | S3: MQTT/HTTPS keep report meaning, IDs, decisions and equivalent receiver confirmation. |
| P7 | S4 | S4: bounded restart-safe queue, retries, expiry and visible losses/duplicates. |
| P8 | S5 | S5: only authorized reporting changes; reject bad/replayed input and vehicle-control requests. |
| P9 | Gate C / D-Design | S1-S6 across A/B and both paths; fixed baseline, runbook and substantiated next-platform design. |

Totals: 476 expert-only hours + 352 support hours = 828 planned accepted-work hours at the saved multiplier of 1. These are not nominal staffed hours and not completed work.

## 4. Saved team comparisons - estimates, not recommendations

| Scenario | Experienced | Junior | Total | Demo week | Pilot week | With reserve | Allocated hours |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Current inputs | 1 | 1 | 2 | 8 | 18 | 20 | 1440 |
| 2 developers | 1 | 1 | 2 | 8 | 18 | 20 | 1440 |
| 3 developers | 2 | 1 | 3 | 7 | 14.5 | 16.5 | 1740 |
| 4 developers | 3 | 1 | 4 | 7 | 14 | 16 | 2240 |
| 2 developers | 2 | 0 | 2 | 7.5 | 15 | 17 | 1200 |
| 3 developers | 1 | 2 | 3 | 12 | 24.5 | 26.5 | 2940 |

All comparisons retain current scope, work estimates and other assumptions. More juniors can lengthen expert-critical work under this mentoring model; this is not a general productivity claim.

## 5. Optional budget and reuse-value model

| Item | Saved value | Cell |
| --- | --- | --- |
| Currency / unit | (blank) | Business Case!C5 |
| Experienced cost / allocated hour | (blank) | Business Case!C6 |
| Junior cost / allocated hour | (blank) | Business Case!C7 |
| Recovery non-labour cap | (blank) | Business Case!C8 |
| Full-pilot non-labour cap | (blank) | Business Case!C9 |
| Reserve non-labour cap | (blank) | Business Case!C10 |
| Budget input check | NOT SET | Business Case!C11 |
| Allocated labour cost / week | (blank) | Business Case!C12 |
| Recovery phase | (blank) | Business Case!C16 |
| Full pilot, excluding reserve | (blank) | Business Case!C17 |
| Additional reserve | (blank) | Business Case!C18 |
| Maximum planning envelope | (blank) | Business Case!C19 |
| One later integration without reuse (h) | (blank) | Business Case!C25 |
| One later integration with reuse (h) | (blank) | Business Case!C26 |
| Extra one-time reuse investment (h) | (blank) | Business Case!C27 |
| Additional maintenance in period (h) | (blank) | Business Case!C28 |
| Expected later integrations (count) | (blank) | Business Case!C29 |
| Evidence / comparison period | (blank) | Business Case!C30 |
| Value input check | NOT QUANTIFIED | Business Case!C31 |
| Time saved per later integration (h) | (blank) | Business Case!C33 |
| Break-even later integrations | (blank) | Business Case!C34 |
| Forecast net effort saved (h) | (blank) | Business Case!C35 |

Illustration only (not the live inputs): 80 h without reuse; 40 h with reuse; 160 h extra setup; 40 h added maintenance. Break-even is 5 later integrations. The pilot itself does not prove those values. Compare like-for-like effort; do not mix delivery-capacity hours with nominal staffed hours.

## 6. Exact saved model guidance

### Change the team

Inputs!C5 = total developers; C6 = juniors. Experienced count is calculated. Example: 3 total and 1 junior means 2 experienced developers.

Source: W12, Guide!A6:B6.

### Review capacity

Check allocation, accepted-work rates and mentoring. Defaults reproduce the v1.0 assumptions: 28 experienced hours/week; junior 12 in recovery and 24 after recovery.

Source: W12, Guide!A8:B8.

### Review forecast

Report shows milestones, schedule variance and allocated hours. Plan shows phase calculations. Scenarios compares role mixes without changing the active plan.

Source: W12, Guide!A10:B10.

### Edit the estimate

Plan blue cells change work, minimum duration, critical lead slots and waits. Inputs!C24 applies one work multiplier. Save a baseline copy before changing estimates.

Source: W12, Guide!A12:B12.

### Share the report

Use Report with the companion approval report. Excel updates without macros. Word/Markdown explain the stable idea, examples, risks and approval criteria; they are not rewritten when inputs change.

Source: W12, Guide!A14:B14.

### Capacity

Experienced pool = people x paid hours x allocation x usable-time rate minus allocated-junior mentoring. Split mentoring evenly across the experienced pool.

Source: W12, Guide!A18:B18.

### Work assignment

Expert-only work cannot be delegated to juniors. Support work may be done by juniors or spare experienced capacity; total work is counted once.

Source: W12, Guide!A20:B20.

### Duration

For each phase, take MAX(minimum weeks, expert work / expert critical capacity, all work / combined capacity). Multiply work by the estimate factor and round up to the selected step.

Source: W12, Guide!A22:B22.

### Sequence and waits

Phases are sequential. Roles may work together within a phase. Waiting weeks are added before that phase; the team is assumed allocated through waits and reserve.

Source: W12, Guide!A24:B24.

### Scope and limits

No automatic initiative switch or test pass. No holiday calendar, individual join dates, actual-progress tracking, overtime or independent assurance. Leave start blank until agreed. Review parallel-work assumptions for larger teams.

Source: W12, Guide!A26:B26.

### Planning source [P1]

SDV_Telematics_Vehicle_Status_AAOS_First_Plan_Revision_EN.md: AAOS-first baseline, core separation, mapping/cloud substitutions, S1-S6 and claim limits.

Source: W12, Guide!A30:B30.

### Resource source [P2]

SDV_Vehicle_Status_DAR_EN_v1_0_One_Senior_One_Junior.md: sections 20 and 20B supply the capacity assumptions and 476 expert / 352 junior-work hours. Sections 2A-3A supply the Automotive alternatives.

Source: W12, Guide!A32:B32.

### Model additions

Phase W5-W6 split equally for the Gate B checkpoint. Junior work becomes a shared-work pool. Phase floors, contributor caps, rounding, scenario staffing and wait controls are editable modeling assumptions, not measured facts.

Source: W12, Guide!A34:B34.

### Baseline reconciliation

The original workload is preserved: 476 expert-only + 352 support hours. Default forecasts remain recovery W2, core W5, demo W8, full pilot W18 and reserve W20. Dates now remain blank until a start is entered.

Source: W12, Guide!A36:B36.

### Approvals still needed

Sponsor confirms objective, people, start, capacity and funding. Senior validates workload, skills, semantics, security and gate evidence. Re-estimate after recovery; record accepted deviations.

Source: W12, Guide!A38:B38.

### Budget

Business Case C5:C10: enter currency, rates and non-labour caps. Recovery cost appears in Report. Full cost includes recovery once; reserve is separate. Blank inputs mean not quantified.

Source: W12, Guide!A42:B42.

### Practical value

Business Case C25:C30: enter comparable hours, incremental setup, period maintenance, expected future integrations and evidence. Break-even and net effort are forecasts, not cash savings or measured adoption.

Source: W12, Guide!A44:B44.

### Save the approval

Sponsor records the selected team, allocation, recovery cap, start and Gate A conditions. Save the approved workbook snapshot. Changing resources recalculates a proposal; it does not grant approval.

Source: W12, Guide!A46:B46.

### Prior short DAR [P3]

SDV_Vehicle_Status_DAR_Short_EN.md and SDV_Vehicle_Status_Plan.xlsx (v1.1): prior scope, six test groups and dynamic forecast. The current approval report adds management examples and an optional cost/value model.

Source: W12, Guide!A48:B48.

## 7. Snapshot integrity

The workbook contains 258 formulas. No cached Excel error cells were found. The 23 empty formula outputs are the expected date, cost and value fields whose required inputs are blank. The complete saved cell/formula export is in `../metadata/workbook_snapshot.json`. This structural check is not a new business estimate, a gate pass or a claim of end-to-end Excel retesting.
