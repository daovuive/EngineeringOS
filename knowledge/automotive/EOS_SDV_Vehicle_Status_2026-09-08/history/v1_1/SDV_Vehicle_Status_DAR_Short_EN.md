# Vehicle Status | Short DAR
**Decision Analysis and Resolution**  
**DAR-SDV-VS-001 | Version 1.1 | 8 September 2026 | Proposed for approval**

## 1. Decision in one minute
Keep **Option C: Hardware-Agnostic Telematics Hub**, but build only the **reusable Vehicle Status capability**. Start with the existing Android Automotive OS (AAOS) proof of concept. Separate its business rules from vehicle, Android and cloud code. Do not build a general vehicle gateway. [P1; P2]

**The idea:** change the vehicle mapping or cloud connection without changing what Vehicle Status means or when it should be published.

**Why it matters:** a future integration should reuse the tested behavior rather than rebuild it. This is a value hypothesis, not a proven saving. Measure adaptation hours, core changes and regression defects when replacing an adapter.

**Approval requested:** fund architecture recovery first. At Gate A, use the actual build, dependencies, team capability and remaining estimate to decide whether to continue. The live staffing and milestone forecast is in **SDV_Vehicle_Status_Plan.xlsx -> Report**.

### What we will deliver
| Included in the full MVP | Not included |
|---|---|
| One AAOS baseline using a shared, testable core. | A new Linux product runtime or a generic gateway. |
| Vehicle mappings A/B and MQTT/HTTPS cloud paths. | A live second OEM or a second production cloud deployment. |
| Bounded durable offline recovery and one authorized telemetry-profile update. | Vehicle control, production certification or independent security assurance. |
| S1-S6 evidence, frozen core and an AAOS SDV porting design/backlog. | Completed AAOS SDV runtime support before target execution is proven. |

### Keep the milestones honest
The **reduced demo** shows mapping A -> core -> MQTT/TLS -> receiver receipt. It is not full reuse acceptance; remote configuration stays disabled and durable crash recovery is not claimed yet.

The **full MVP** requires both mappings, both cloud paths, offline/security evidence and all applicable S1-S6 cases. The target-port design is a separate approval from actually running on AAOS SDV. A forecast date never means a gate has passed.

<!-- PAGE -->
# 2. Why keep this Automotive idea?
The decision is about the objective, not the most attractive demo. Retain Vehicle Status when the sponsor wants reusable in-vehicle SDV integration. A replay/validation tool is the main alternative when early internal usefulness matters more. Select **one initiative**, not parallel products. [P2, sections 2A-3A]

| Idea | Best reason to choose it | Main condition or limitation |
|---|---|---|
| **I1. Reusable Vehicle Status — selected** | Build AAOS integration capability with evidence that adapters can change without changing behavior. | Needs a recoverable PoC, permitted signals and experienced integration capacity. |
| I2. Signal replay and semantic validation | Give engineers a focused tool for reproducing signal defects and checking mappings. | Needs representative traces, agreed meanings and a consuming engineering team. |
| I3. Engineering knowledge assistant | Help engineers find evidence-linked answers in project documents and logs. | Needs authorized, versioned content and an expert-reviewed answer/no-answer test set. |
| I4. EV charging observability | Find charging-session anomalies and reconcile energy records. | Needs an approved charging-data feed; not battery-health prediction or charging control. |
| I5. Read-only fleet health dashboard | Support an operator's status and maintenance-triage workflow. | Needs existing ingestion, authorized data and a real operator workflow. |
| I6. Predictive-maintenance study | Test whether historical data predicts a narrowly defined failure. | Needs representative failure labels; an offline study is not an operational model. |
| I7. OTA observability sandbox | Observe update campaigns and simulate failure/rollback outcomes. | Needs an existing updater or simulator; no real ECU flashing or production OTA platform. |

### Why AAOS-first rather than the other execution options?
Extending the current PoC can produce a quick demo but does not by itself prove reuse. Linux-first adds a product runtime outside the chosen scope. AAOS-SDV-first depends on target access and hosting readiness. **AAOS-first controlled extraction** keeps the starting implementation while making its boundaries testable. [P2, sections 2-3]

### What makes this more than another telemetry collector?
The deliverable is **governed signal meaning plus repeatable reuse evidence**, not simply uploading vehicle data. During recovery, compare the existing stack and native capabilities before adding infrastructure. Reuse suitable libraries behind the agreed boundaries; do not build a new broker or simulator just for this project.

Adding people changes the delivery forecast. It does not automatically change the selected initiative, remove prerequisites or prove business value.

<!-- PAGE -->
# 3. Implementation detail and acceptance
### Architecture in plain English
**Vehicle source A or controlled source B -> vehicle adapter -> shared Vehicle Status core -> MQTT or HTTPS adapter -> receiver.** Storage and credential access sit behind separate interfaces. AAOS lifecycle and permissions stay in its platform adapter. The host runner tests the **same core**; it is not a second product runtime. [P1; P2, sections 5-11]

### Rules that must survive every replacement
**Signal meaning.** Keep units, timestamps, quality and semantic basis explicit. Missing or stale data is not zero. Equivalent inputs must match; incompatible meanings must be rejected or marked unsupported, not forced to match.

**Stable decisions and identity.** Keep the same canonical envelope, publish decision, status ID and correlation across retries and adapter swaps. Freeze the approved triggers and configuration limits at Gate B. The prior DAR proposes periodic, material-change and first-valid-snapshot triggers; they still need approval.

**Delivery and offline behavior.** Distinguish transport acceptance from a receiver's application receipt. Retain each durable record until that receipt or an explicit expiry, overflow or failure outcome. Bound storage and retries. Test outages and process crashes; preserve IDs and make duplicates or losses visible. Do not claim exactly-once transport.

**Security.** Validate TLS and use approved test credentials. Allow only `TELEMETRY_PROFILE_UPDATE`, with issuer/target authorization, freshness, replay, schema and range checks. Apply valid changes atomically. Expose no vehicle-write path. Keep downlink off until these controls pass.

### Six evidence groups — proposed definitions retained from v1.0
| Test | What must be demonstrated |
|---|---|
| **S1 — Meaning and quality** | A/B mappings handle equivalent values, unit conversion, stale/missing data and deliberate semantic mismatch correctly. |
| **S2 — Publish policy** | Approved triggers, boundaries, timing and profile rules give the expected decisions; retries do not create new IDs. |
| **S3 — Cloud replacement** | MQTT/HTTPS preserve the canonical data, decisions, IDs and equivalent receipt meaning without core changes. |
| **S4 — Offline recovery** | Queue bounds, expiry, overflow, retry and crash recovery work; every loss has a reason and duplicates are observable. |
| **S5 — Configuration security** | Valid updates apply; unauthorized, expired, replayed, malformed, out-of-range and vehicle-control inputs are rejected. |
| **S6 — Integrated reuse** | A/B x MQTT/HTTPS passes the applicable cases; core/contract versions and change evidence are frozen. |

**Evidence boundaries:** distinguish host, injected AAOS, actual vehicle-interface and receiver tests. Two protocols on one backend prove protocol substitution, not independent cloud-vendor portability. Record PASS, FAIL or NOT RUN; missing mandatory evidence blocks full acceptance. [P2, sections 17-19]

<!-- PAGE -->
# 4. Use the living plan and approve the next step
### One place for changing numbers
**Excel owns resources, work estimates, forecast dates and the management report.** This Markdown/Word DAR owns the idea, scope and acceptance rules. It deliberately does not duplicate changing milestone dates. The document files are not automatically rewritten when Excel changes.

| Workbook tab | What to do |
|---|---|
| **Inputs** | Edit blue cells: team size, junior count, allocation, capacity, mentoring, start date, targets and reserve. |
| **Report** | Read or print the recalculated management summary and target variances. |
| **Plan** | Review phases, work estimates, waits, minimum durations and required evidence. |
| **Scenarios** | Compare role mixes using the same scope and current assumptions. |
| **Guide** | Read the calculation method, limitations and source traceability. |

**Example:** change `Inputs!C5` from 2 to 3 and leave `C6` at 1. The model becomes two experienced developers plus one junior. To add a junior instead, also increase `C6`. Review the different result; a junior is not interchangeable with an experienced developer.

### How the forecast works
The work estimate stays fixed unless edited. Experienced capacity is reduced for coordination and mentoring; junior capacity is lower during recovery. Each phase lasts at least the largest of its minimum duration, the time needed for expert-only work, or the time needed for all work. Support work can use spare experienced capacity without counting those hours twice.

Phases run in order. Contributor caps, rounding and waiting time prevent simple headcount-based compression. These controls are **planning assumptions**, not measured productivity. The model uses one team from the planning start; it does not track actual progress, joining dates or a holiday calendar.

### Ownership and stop conditions
The experienced lead owns semantics, architecture, lifecycle, credentials, persistent state and security decisions. Juniors contribute bounded implementation, fixtures, automation and evidence under review. Sponsor/domain owners provide approvals and access, not hidden implementation capacity.

Replan when the PoC cannot be recovered, access is missing, a major hosting rewrite is needed, throughput misses the model, or critical work exceeds capacity. Defer extra signals, UI polish and production hardening before weakening mandatory evidence.

**Approval record:** sponsor/pilot owner; named team and allocations; approved start and recovery budget; Gate A review; accepted risks; reserve authority. Continue beyond recovery only after the senior's re-estimate and sponsor approval.

### Source record
**[P1]** *SDV_Telematics_Vehicle_Status_AAOS_First_Plan_Revision_EN.md*: architecture, reuse objective, gates and claim limits.  
**[P2]** *SDV_Vehicle_Status_DAR_EN_v1_0_One_Senior_One_Junior.md*: Automotive comparison, proposed technical rules, capacity and phase workload. The workbook introduces explicit scheduling controls; it preserves the source workload at default settings.
