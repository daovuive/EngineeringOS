# SDV Vehicle Status
## Decision Analysis and Resolution
### AAOS-First MVP | Two-Person Delivery Revision

**Decision ID:** DAR-SDV-VS-001  
**Version:** 1.0 | **Date:** 8 September 2026  
**Status:** Proposed - management approval pending  
**Delivery team:** One senior developer and one full-time intern/fresher

### Decision requested

Conditionally retain **Option C: Hardware-Agnostic Telematics Hub**, constrained to the reusable Vehicle Status capability. Use the existing AAOS PoC and the same-core host test harness. Do not create a general gateway or a second product runtime. [P1, sections 1, 10-12]

Approve **two weeks of recovery first**, an **eight-week reduced-scope demonstration checkpoint**, and a **proposed 18-week full MVP baseline**, with weeks 19-20 reserved for sponsor-approved contingency. This explicitly replaces the earlier eight-week full-MVP commitment; it does not remove its mandatory reuse or security evidence.

| Approval item | Proposed management position |
|---|---|
| People | Exactly 1 senior + 1 intern/fresher. No additional architect, QA, cloud or security implementer is assumed. |
| Full outcome | AAOS baseline; mappings A/B; MQTT/HTTPS; bounded durable recovery; one authorized configuration command; S1-S6; target-port package. |
| Capacity / funding | 18 weeks = 720 hours per person, 1,440 nominal staffed hours. Two-week reserve adds 160 hours only when released. |
| First tranche | 2 weeks = 160 nominal staffed hours. Gate A decides continuation and confirms the estimate. |
| Portfolio choice | Prefer this idea for an explicit SDV reuse objective. Prefer a signal replay/validation tool when useful delivery within 6-8 weeks is the main objective. |

### Management implication

**Two people are not two interchangeable senior engineers.** The senior owns architecture, platform integration, data semantics, fault recovery and security-sensitive code. The junior owns bounded implementation, test fixtures, automation and evidence under review. Training and review are scheduled rather than hidden.

### Recommendation and reading guide

Approve only one initiative. Sections 2A-2D compare seven Automotive ideas; section 3A tests the ranking under different priorities. Sections 12-16 and 20-20B contain the resource-loaded plan. The full technical contract and S1-S6 remain in sections 5-11 and 17-19. AAOS SDV runtime validation remains a separately funded follow-on, not an automatic week-18 claim.

<!-- PAGE -->
# 1. Assessment of the idea

### What is strong in the source proposal

The source chooses a concrete AAOS runtime, separates the host behavioral runner from deployment claims, permits recovery changes before stabilization, and demands controlled vehicle and cloud substitutions. Its explicit exclusions prevent a PoC from being sold as universal portability or production readiness. These are useful architectural controls. [P1, sections 1, 3, 5-6, 11]

### What should be strengthened before execution

| Gap or risk | Required implementation response |
|---|---|
| Architecture recovery could become open-ended cleanup. | Time-box discovery to weeks 1-2, document only the end-to-end Vehicle Status path, and maintain a prioritized coupling inventory. |
| AAOS-to-AAOS-SDV could require more than an adapter change. | Verify the target language/runtime, service lifecycle and packaging in weeks 1-2, before core implementation choices are frozen. |
| S1-S6 and three publish triggers are referenced but not formally specified in this revision. | Recover the original definitions or approve the proposed operational definitions in this DAR at Gate B. Do not silently treat proposed values as existing requirements. |
| Mapping substitution could prove renamed fields, not semantics. | Test equivalent and deliberately non-equivalent SOC/odometer meanings. Reject unsupported equivalence rather than force matching outputs. |
| A transport acknowledgment could be mistaken for successful ingestion. | Separate broker/HTTP acceptance from application receipt; compare the same declared delivery milestone. |
| Security appears late in the weekly plan. | Start threat modeling, credentials and command constraints in week 1; complete the controlled-downlink evidence in weeks 14-15. |

### Business value and measurement

The expected benefit is lower change effort when a vehicle vocabulary, cloud interface or platform binding changes. This is a hypothesis to test, not a quantified saving. Record engineering hours, files changed, regression defects and scenario pass rates for each substitution. A zero-core-change swap is stronger evidence than a high aggregate code-reuse percentage.

A later business case can use: **net reuse value = avoided repeated integration effort - extraction cost - ongoing adapter maintenance**. Avoid ROI percentages until at least one comparable integration and its actual effort have been measured.

**Current-platform fit:** review the native telemetry and hosting comparison in section 2D before approving custom infrastructure. [R3, R4, R13]

<!-- PAGE -->
# 2. DAR scope and alternatives

### Decision scope

Separate two decisions: **which Automotive initiative to fund (I1-I7)** and **how to execute Vehicle Status if I1 is chosen (E1-E4)**. The source names Option C; the initiative shortlist in sections 2A-2D is a new comparison, not a reconstruction of its original Option A/B. Execution alternatives E1-E4 remain below. [P1, section 11]

The evaluation method uses mandatory constraints, weighted criteria, sensitivity checks and evidence-based review. Documented criteria and a visible rationale support repeatable decision-making; this document does not claim a CMMI appraisal result. [R1]

| Alternative | Approach | Principal trade-off |
|---|---|---|
| E1 - Extend the current PoC | Add demonstrations directly to the existing AAOS implementation with limited restructuring. | Potentially the quickest demonstration; weak separation makes later reuse difficult to substantiate. |
| E2 - Linux-first extraction | Establish a portable core and a separate Linux runtime before returning to AAOS. | Could expose OS dependencies, but adds a runtime and integration path outside the revised MVP baseline. |
| E3 - AAOS-first controlled extraction | Recover the PoC; isolate the same core behind owned ports; add host tests and controlled substitutions. | Best alignment with the revised evidence plan, provided recovery and target compatibility are bounded. |
| E4 - AAOS-SDV-first integration | Start on the named SDV target and assess native telemetry/service infrastructure as the implementation base. | Direct target alignment and possible infrastructure reuse; depends on target access and may discard useful PoC implementation. |

### Mandatory constraints before selection

C1. Vehicle access is read-only; no vehicle-control command or actuator call path is introduced.

C2. The proposal must expose where domain decisions end and platform/provider behavior begins. A telemetry demo alone is insufficient.

C3. Claims must match evidence: host tests are not Linux product validation; an SDV design is not an SDV runtime result.

C4. Costs, access and security dependencies must fit exactly one senior and one full-time junior. A failed mandatory condition cannot be offset by a high numerical score. These constraints screen I1 execution; different initiatives use the portfolio criteria in section 3A.

### Screening result

E1 remains a schedule comparator, but cannot meet the full reuse objective without substantial restructuring. E2 would require an explicit scope change to reintroduce a Linux product baseline. E4 is conditional on a named, accessible target and a fit-gap assessment. E3 is the recommended eligible approach, subject to Gate A findings.

<!-- PAGE -->
# 2A. Automotive initiative shortlist

### Common comparison basis

Compare the smallest **decision-quality, non-production deliverable** for the same two-person team. Windows below are planning judgments, not market benchmarks or equivalent product maturity. They start after required data and access are available. Only I1 has a source-defined implementation baseline; I2-I7 are newly proposed investment alternatives.

| Initiative | Smallest useful deliverable / proposed window | Main prerequisite or limitation |
|---|---|---|
| I1 - AAOS Vehicle Status reuse capability | Week-8 vertical slice; full S1-S6 reuse MVP in 18 weeks, reserve to week 20. | Buildable PoC, permitted AAOS signals, compatible core strategy; senior-heavy integration. |
| I2 - Vehicle signal replay and semantic validation toolkit | 6-8-week internal pilot: replay, mapping checks, semantic diffs and CI evidence for one team. | Representative traces and approved signal meaning. Not a full HIL platform or vehicle runtime product. |
| I3 - Automotive engineering / diagnostic knowledge assistant | 8-10-week internal pilot: cited document/log retrieval, evidence-linked answers and no-answer behavior. | Authorized corpus, version metadata and expert-reviewed evaluation questions. No autonomous diagnosis or vehicle action. |
| I4 - EV charging and energy observability | 8-12-week pilot: charging-session anomalies, energy reconciliation and data-quality report. | Approved session/meter exports; one data feed. No charging control, billing settlement or battery-health guarantee. |
| I5 - Read-only fleet health dashboard | 8-12-week pilot: last-known status, freshness, simple alerts and maintenance triage. | Existing ingestion plus an operator workflow. Building a collector as well expands the estimate. |
| I6 - Predictive-maintenance experiment | 12-16-week retrospective feasibility study; operational validation is separate. | Historical failures/maintenance labels, representative usage and a held-out evaluation set. |
| I7 - OTA campaign observability sandbox | 10-14-week pilot: campaign state, failure injection and simulated rollback evidence. | Approved event contract and simulator/existing update system. No actual ECU flashing or OTA production platform. |

### Screening out oversized proposals

A new ADAS stack, a complete autonomous-driving feature, a universal vehicle gateway, a full multi-OEM OTA platform and a production battery-health model are not comparable two-person MVPs. A narrow offline experiment may be considered separately; its demo must not imply production readiness.

**Do not fund these ideas in parallel.** The shortlist is a choice of investment, not seven workstreams for the same senior. I2 can be selected as an independent tool only through a changed scope decision; within I1, the host runner remains an internal test utility. [P1, sections 1 and 10]

<!-- PAGE -->
# 2B. Comparative value: I1-I3

### I1 - reusable Vehicle Status capability

**Customer and value hypothesis:** OEM/Tier-1 integration teams repeatedly bind similar status behavior to different vehicle vocabularies and cloud interfaces. The proposed asset is an integration accelerator plus evidence, not another generic telemetry broker. Measure core changes, accepted scenario equivalence, adaptation hours and regression defects. [P1, sections 2-5]

**Best fit:** management explicitly needs an AAOS reference capability and a credible SDV transition story. The existing PoC is useful only to the extent that recovery proves it can be reused. **Weakness:** much of the business value arrives through later integrations; a single polished upload demo does not establish savings.

**Two-person split:** senior owns contract, architecture and risky integration; junior owns fixtures, contract-test automation, evidence and a bounded HTTPS skeleton. Choose I1 only with the revised schedule and an identified consumer of the reusable artifact.

### I2 - signal replay and semantic validation toolkit

**Customer and value hypothesis:** AAOS integration and test engineers need to reproduce signal defects and detect mapping regressions without repeatedly setting up a vehicle. The pilot would replay recorded/synthetic observations and compare units, quality, freshness and approved semantic meaning. Its value is reproducible defect evidence, not simulated coverage of every vehicle interface.

AOSP already provides reference fake vehicle hardware; Eclipse examples use recorded signals and VSS mappings. Reuse appropriate infrastructure rather than build another simulator from scratch. These components do not themselves prove the project's semantic oracles. [R12, R15]

**Best fit:** a strict 6-8-week delivery target and internal engineering adoption. **Weakness:** differentiation is modest unless the toolkit catches real mapping defects and fits the team's CI. Proposed pilot evidence: three repeatable defect cases, a clean-machine replay, and one consuming engineering team.

**Two-person split:** senior defines adapters and test oracles; junior contributes the majority of trace processing, CLI, reports and CI tasks. This is the strongest default small-team option in section 3A. Under I1, implement only the subset needed by S1-S6, not a standalone product.

### I3 - evidence-grounded engineering assistant

**Customer and value hypothesis:** internal engineers spend less time finding the correct specification, known issue or diagnostic explanation. Restrict the initial corpus to one project and version; require citations, access control, no-answer decisions and human review for consequential guidance.

Bosch announced an ESI[tronic] AI assistant on 21 July 2026, with introduction planned for the end-of-2026 update. This shows established-player activity, not proof of availability today or demand for another generic assistant. Compete on authorized project knowledge and evaluation quality, not a broad chatbot claim. [R16]

**Two-person split:** senior owns retrieval/evaluation/security; junior curates versioned content and test questions. Proposed pilot: 50 reviewed questions plus unsupported/conflicting-source cases. A corpus without usage rights or reliable answers blocks useful validation; an attractive chat UI does not remove that dependency.

<!-- PAGE -->
# 2C. Comparative value: I4-I7

### I4 - EV charging and energy observability

**Customer:** charging operations or EV fleet engineering. Start with one feed of session/meter records and a report for missing sessions, inconsistent energy totals and abnormal durations. OCPP addresses charging-station-to-management-system communication; it is not an in-vehicle battery-state interface. Use existing approved exports before considering a new OCPP integration. [R17]

**Value test:** an operator validates three useful anomaly cases and the reconciliation logic. Senior owns event/time/energy semantics; junior handles ingestion, reports and fixtures. Attractive with an available charging-data partner; weaker than I1 when the sponsor's goal is in-vehicle software reuse. Do not infer battery state of health from simple SOC or session data.

### I5 - read-only fleet health dashboard

**Customer:** a fleet operator or maintenance coordinator. Show current/last-known status, stale-data indicators and a few agreed triage rules using an existing feed. AOSP telemetry explicitly identifies vehicle-health and fleet-management use cases; the proposed dashboard is an application on top, not replacement collection infrastructure. [R13]

**Value test:** an operator completes a defined triage workflow and distinguishes a stale feed from a healthy vehicle. Senior owns data contracts/authentication/alert rules; junior owns bounded views and tests. This can be commercially tangible earlier than I1, but customer workflow and authorized live data matter more than a simulated dashboard.

### I6 - predictive maintenance

**Customer:** maintenance/reliability engineering. Begin with one component and an offline comparison against a simple threshold or rule baseline. Separate time/vehicle-held-out evaluation from model development; record label quality, lead time and false alerts.

Battery-diagnostic research illustrates that degradation depends on chemistry, operating conditions and history, and that moving from controlled simulation to real-data validation is a separate step. This supports a data-readiness gate, not a universal estimate for all maintenance models. [R18]

Senior owns problem definition and evaluation; junior owns data-quality checks and reproducible experiments. Without representative labels, select an anomaly-exploration study and say so. A synthetic failure demo cannot validate predictive maintenance. Not recommended as this team's first commitment without a named data/domain partner.

### I7 - OTA campaign observability sandbox

**Customer:** release or update-validation engineering. Observe a simulated campaign and inject disconnect, incompatible-version and failed-install outcomes. Reuse an existing updater interface or simulator; do not build firmware distribution, trust infrastructure and vehicle flashing in this pilot.

Uptane defines a broader secure-update system with repository roles, signed metadata and in-vehicle verification. A campaign dashboard or simulated rollback is only a small part of that responsibility. [R19]

Senior owns the event/state model and safety boundaries; junior builds scenarios, dashboards and reports. Useful when an existing OTA team needs evidence tooling; otherwise access and integration costs are substantial. No production update, rollback-safety or standards-conformance claim is permitted from this sandbox alone.

<!-- PAGE -->
# 2D. Existing ecosystem: build, reuse or avoid

### Differentiation must survive the fit-gap review

The project should not justify itself by asserting that vehicle-data normalization, telemetry or simulation are absent from the ecosystem. Its defensible hypothesis is a **small, governed Vehicle Status contract with reproducible behavior under replacement**. The following external capabilities inform implementation choices; they are not required dependencies.

| Existing capability | Verified context | Proposed project response |
|---|---|---|
| COVESA VSS | A technology-agnostic vehicle-data model and vocabulary. [R14] | Map the minimal canonical subset to suitable VSS semantics. Keep freshness, eligibility and receipts explicit; shared names alone do not establish equivalence. |
| Eclipse Kuksa | A vehicle-data broker exposing VSS-oriented APIs and provider integrations. [R20] | Evaluate it only if already available or a short adapter spike saves work. Do not introduce a new broker merely to appear standards-aligned. |
| AOSP VHAL reference | FakeVehicleHardware supplies simulated behavior; its reference does not access a real vehicle bus. [R12] | Reuse it where compatible with the named AAOS build. Label simulated and physical acquisition evidence separately. |
| AAOS SDV Telemetry | Configurable collection, edge processing and simulation are documented platform capabilities. [R13] | Test the actual target's fit for the required triggers, contracts and lifecycle. Reuse behind ports where it reduces code; preserve the Vehicle Status acceptance contract. |
| AWS IoT FleetWise | AWS stopped accepting new customers on 30 April 2026; existing customers may continue. [R21] | Do not plan a new-account dependency. Use controlled MQTT/HTTPS endpoints for this MVP; assess alternatives separately if cloud procurement is needed. |
| Diagnostic AI products | Bosch's July 2026 announcement schedules its assistant for a later 2026 release. [R16] | For I3, differentiate through a specific authorized engineering corpus and measured answer quality, not generic AI branding. |

### Bounded fit-gap spike at Gate A

The senior allocates at most one delivery day within the recovery budget to document existing-stack overlap and the highest-risk hosting question. Check source/license constraints, current access, supported runtime, semantics and operational burden. Do not install every listed component or broaden the core into an integration framework.

A reuse candidate passes only when the team can show the required behavior at lower forecast implementation and maintenance effort. The score for I1 must fall if native capabilities cover its proposed differentiator. Conversely, adapting existing infrastructure can reduce the implementation burden without changing the business contract.

**Claim boundary:** VSS alignment, platform telemetry integration and use of a broker each require specific evidence. None automatically establishes multi-OEM portability, independent cloud-vendor portability or production compliance.

<!-- PAGE -->
# 3. Execution-strategy evaluation

### Conditional on choosing I1

This comparison selects E1-E4 only after management chooses the Vehicle Status initiative. Ratings are proposed engineering judgments, not completed measurements. Scale: 1 = poor fit/high unresolved burden; 3 = workable with conditions; 5 = strong fit/low additional burden. Re-score at Gate A.

| Criterion | Weight | E1 | E2 | E3 | E4 |
|---|---:|---:|---:|---:|---:|
| Speed to useful AAOS evidence | 20% | 5 | 2 | 3 | 1 |
| Verifiable behavioral reuse | 25% | 1 | 4 | 5 | 4 |
| Readiness for the next target | 15% | 2 | 3 | 4 | 4 |
| Scope and schedule predictability | 15% | 4 | 2 | 3 | 1 |
| Maintainable integration boundaries | 10% | 1 | 4 | 5 | 4 |
| Testable security/offline responsibilities | 10% | 2 | 4 | 4 | 3 |
| Incremental effort/toolchain fit | 5% | 5 | 2 | 3 | 1 |
| **Weighted score / 100** | **100%** | **54** | **61** | **79** | **54** |

Calculation: sum(weight x rating) / 5. E3's score is reduced from v0.9 because the senior's integration load and junior ramp-up materially affect speed and predictability. A numerical lead does not waive mandatory constraints or prove a buildable PoC.

### Sensitivity to management priorities

| Scenario; weights in the order above | E1 | E2 | E3 | E4 |
|---|---:|---:|---:|---:|
| Delivery-heavy: 40/15/10/15/5/5/10 | 72 | 52 | 71 | 40 |
| Next-target-heavy: 10/25/30/10/10/10/5 | 46 | 64 | 82 | 63 |
| Demo-only: 70/5/5/5/5/5/5 | 85 | 47 | 66 | 31 |

E1 can win when immediate demo speed dominates, but it does not satisfy the original reuse objective without further restructuring. E2 adds the Linux product baseline removed by the source. E4 remains conditional on actual target access and native-telemetry fit. E3 remains the preferred I1 execution path for an 18-week evidence-based MVP. [P1, sections 1-5]

### Reopen the execution decision

Re-score if extraction requires a major language migration, early senior workload exceeds the capacity model, target access is unavailable, or an existing capability can satisfy the approved semantics with materially less custom implementation. The options are a changed schedule, a changed claim/scope, or a different initiative - not unrecorded overtime or hidden extra staff.

<!-- PAGE -->
# 3A. Initiative ranking and decision rule

### Proposed small-team scoring model

Weights: **R** reusable SDV integration value 20%; **L** leverage of the known AAOS PoC 15%; **F** feasibility for 1 senior + 1 junior 25%; **A** access/data readiness 15%; **T** speed to decision-quality evidence 15%; **D** defensible differentiation 10%. Ratings: 1 = weak, 3 = conditional, 5 = strong. Higher is better, including access and speed.

| Initiative | R | L | F | A | T | D | /100 |
|---|---:|---:|---:|---:|---:|---:|---:|
| I1 - Vehicle Status | 5 | 5 | 3 | 3 | 3 | 4 | **76** |
| I2 - Signal validation | 4 | 4 | 5 | 5 | 5 | 3 | **89** |
| I3 - Knowledge assistant | 3 | 2 | 4 | 3 | 4 | 3 | **65** |
| I4 - EV observability | 4 | 3 | 4 | 3 | 4 | 3 | **72** |
| I5 - Fleet dashboard | 4 | 4 | 4 | 3 | 4 | 2 | **73** |
| I6 - Predictive study | 4 | 2 | 2 | 1 | 2 | 3 | **47** |
| I7 - OTA sandbox | 4 | 2 | 2 | 2 | 2 | 3 | **50** |

Formula: sum(weight x rating) / 5. Ratings assume no additional customer dataset, ML expert, security engineer or platform team is committed. These are decision-workshop starting values, not industry rankings or evidence of market size. One rating point on feasibility changes the total by 5 points; close scores should not be treated as precise distinctions.

### Strategic-priority sensitivity

Reweight to 45/20/10/5/5/15 when reusable in-vehicle SDV capability is the sponsor's primary goal. Keep the ratings unchanged so the effect is visible.

| Initiative | Small-team priority | SDV-reuse priority |
|---|---:|---:|
| I1 - Vehicle Status | 76 | 89 |
| I2 - Signal validation | 89 | 81 |
| I3 - Knowledge assistant | 65 | 59 |
| I4 - EV observability | 72 | 72 |
| I5 - Fleet dashboard | 73 | 73 |
| I6 - Predictive study | 47 | 60 |
| I7 - OTA sandbox | 50 | 61 |

### Recommended resolution

**Strict early value / 6-8-week constraint:** select I2 for a scoped internal validation pilot, provided a consuming team and traces exist. **Explicit SDV reuse / 18-week investment:** conditionally select I1 with E3, using only the necessary replay tooling inside its test harness. Do not operate I1 and a standalone I2 product in parallel.

Select I3, I4 or I5 instead only when management names the relevant knowledge/data owner and a real pilot workflow. Defer I6 without representative outcome data and I7 without an existing update-system partner. A stronger score cannot compensate for absent data rights, an unavailable runtime or an unowned business use case.

<!-- PAGE -->
# 4. Entry conditions and open decisions

### Gate 0 - start the clock only with executable prerequisites

The proposed 18-week clock starts when both developers are assigned full-time, the PoC repository/build and a named AAOS runtime are accessible, vehicle reads are authorized, and test endpoints are available. An emulator can support a declared virtual-runtime PoC; it does not prove physical vehicle integration. Access delays and holidays move the calendar unless explicitly absorbed by a revised capacity plan.

| Required decision / evidence | Responsible implementer | Due |
|---|---|---|
| Reproduce commit, language/toolchain, package and runtime image. | Senior; junior records clean-build steps. | Week 1 |
| Identify permitted signals, actual semantics, quality and read permissions. | Senior obtains authoritative interface definitions. | Week 1 |
| Confirm full-time junior availability and assess a small independent task. | Senior; sponsor confirms allocation. | Week 2 |
| Name target release/hosting path and bound any compatibility migration. | Senior; target access is an external prerequisite. | Gate A |
| Select one initiative and the reduced/full outcome to fund. | Sponsor, informed by senior's evidence. | Gate A |
| Approve fields, triggers, S1-S6, receipt/queue/configuration contracts. | Senior proposes; sponsor records domain approval. | Gate B, week 5 |
| Confirm rates, infrastructure, risks and remaining capacity. | Sponsor; senior supplies estimate and actuals. | Gate A / week 8 |

### Core-language and hosting decision

Keep the existing language where feasible; do not start an optional rewrite with this team. A JVM core can support host tests without proving it can run in the intended SDV service environment. Native code likewise needs a supported toolchain, ABI and lifecycle binding. Current SDV guidance includes Rust/C++ service implementation, but only the chosen release and hosting evidence resolve the actual compatibility question. [R5, R6]

If a major migration is required, either rebaseline the full effort, continue with an explicitly AAOS-only claim, or choose a different initiative. A later reimplementation is not an unchanged-source port.

### No hidden supporting team

Sponsor/domain/data owners provide decisions or access, not assumed implementation capacity. No architect, cloud engineer, QA engineer, DevOps engineer or security specialist is added to the delivery model. The senior performs those technical responsibilities within the planned hours. Independent security assurance is not implied; without it, release claims remain an internal, non-production PoC.

Track every unknown with owner, due date, closure evidence and impact. Missing target access can leave a documented target gap; it blocks Gate D-Design when the required target definition cannot be substantiated and always blocks Gate D-Runtime.

<!-- PAGE -->
# 5. Target architecture and ownership

### Architecture rule

Runtime flow goes from the AAOS adapter into the reusable core and out through cloud, storage and security adapters. **Compile-time dependencies point inward:** adapters depend on project-owned contracts; the core never imports Android, vehicle middleware, cloud SDK or database types. The host runner invokes the same core source or library, not a rewritten simulation. [P1, sections 3-4]

| Module / boundary | Responsibility | Must not own |
|---|---|---|
| Domain model and policy | Canonical semantics, validity, publish eligibility and bounded configuration rules. | Android lifecycle, OEM property IDs, endpoints or SDK errors. |
| Application coordinator | Snapshot creation, stable IDs, queue workflow, retry decisions and outcome normalization. | Sockets, Binder calls, database implementation or key material. |
| Vehicle adapter A / B | Read approved source; interpret source semantics; map to canonical observations. | Cloud publication decisions or undocumented semantic conversion. |
| AAOS platform adapter | Service lifecycle, executor/event delivery, permissions, reconnect, packaging and diagnostics. | Business thresholds or provider payloads. |
| MQTT / HTTPS adapters | Provider mapping, protocol operations, receipt correlation and capability declarations. | Canonical meaning or publish-policy changes. |
| Storage / identity adapters | Durable transactions, credential handles, verification and platform resource access. | Independent retry policy or hidden configuration authorization. |

### Minimal project-owned contracts

Define typed contracts for VehicleObservation, Clock, IdGenerator, TelemetrySink, OfflineStore, CredentialHandle, CommandVerifier and Diagnostics. Contract names are proposed; preserve appropriate existing equivalents discovered during recovery. Split responsibilities without creating a generic plugin framework.

Clock exposes monotonic timing separately from trusted wall time. OfflineStore exposes atomic operations, not database rows. TelemetrySink returns structured disposition and acceptance stage, not a Boolean. Credentials remain opaque handles. Vehicle access exposes only the operations required for reading approved status signals.

### Incremental extraction approach

First characterize the current flow and freeze observable traces. Introduce one boundary at a time behind the existing AAOS entry point. Compare old and new behavior in a non-publishing shadow path where practical; only one path may publish. Each change must have a regression test and a reversible integration commit.

### Enforcement

Use build-level dependency restrictions plus source/compiled-dependency checks. A keyword scan alone cannot prove isolation. The core build must succeed without Android or provider SDK dependencies. Record the approved core path set, public contract and build artifact in the evidence manifest.

<!-- PAGE -->
# 6. Canonical Vehicle Status contract

### Proposed seed contract - approve at Gate B

The source requires canonical semantics but does not enumerate a complete schema. The following is a proposed implementation contract. SOC and odometer form an illustrative EV-oriented test fixture, not confirmation that the existing PoC exposes those signals. The product owner must approve the actual minimal field set. [P1, sections 3, 5, 7]

| Field or concept | Proposed semantics |
|---|---|
| schemaVersion | Versioned project contract; reject unsupported major versions. Provider payload versions remain outside the core. |
| statusId / correlationId | statusId identifies one immutable status; generate once and preserve through queueing, protocol replacement and retry. correlationId links the originating trigger/session, not a protocol packet ID. |
| vehicleAlias | Approved pseudonymous test identity. Do not require raw VIN, location or personal data for the MVP. |
| capturedAt / timeQuality | Wall time and its trust state at snapshot creation; preserve measurement timestamps and their clock domains separately. |
| measurements | Canonical signal key, value or null, unit, quality, semantic basis and relevant observation/measurement time. |
| profileVersion / triggerReasons | The policy version and all reasons that caused creation; immutable for that status. |

### Validity and freshness

Represent valid, unavailable, stale, invalid and unsupported-meaning states explicitly. Missing data is not zero. Check availability before reading values; Android property documentation explicitly warns that a value is meaningless when unavailable. Preserve platform timestamp semantics at the adapter boundary. [R7]

Approve a per-signal freshness rule and a maximum snapshot skew. A provisional 30-second freshness window is suitable only for test sources that support the required observations. Do not re-date a cached value to make it fresh, or confuse an on-change timestamp with a new measurement. A successful authoritative read may establish current-state validity only under the documented source contract.

### Semantic substitution, not field renaming

For the seed fixture, define exactly which SOC basis is accepted and whether odometer is authoritative lifetime distance. Usable SOC is not interchangeable with absolute SOC; an estimated odometer is not silently promoted to authoritative. A conversion requires a documented domain-approved relationship. Otherwise mark the measurement unsupported and apply the approved eligibility rule. [P1, section 5.1]

An approved fixture may convert 12,345,600 meters to 12,345.6 kilometers. Equality requires equivalent meaning, rounding, timestamps and quality, not merely close numeric values.

### Immutable-envelope rule

Compare the complete canonical envelope before provider mapping, using controlled clocks and ID generation. Keep adapter names and provider diagnostics outside that envelope. Genuine semantic-basis or quality differences must remain visible and should produce different expected results.

<!-- PAGE -->
# 7. Publish policy and bounded configuration

### Proposed three-trigger definition

The revision requires three frozen triggers but does not name them. The following proposal must be reconciled with the original requirements or explicitly approved at Gate B. It is not presented as a recovered requirement. [P1, sections 7-8]

| Trigger | Proposed rule | Required tests |
|---|---|---|
| T1 - Periodic | Create an eligible snapshot after the approved interval from the last durably admitted snapshot. | Just before/at deadline; missing required data; restart and clock movement. |
| T2 - Material change | Create when an approved signal changes by at least its threshold relative to the last durably admitted snapshot. | Below/at/above threshold; unit equivalence; unavailable values; simultaneous changes. |
| T3 - First valid snapshot | Create once after a declared operational-session start when the required data becomes eligible. | Delayed data; repeated readiness notifications; process restart; no duplicate within a session. |

An operational session is an explicitly defined application event, not an assumed vehicle drive cycle. The AAOS adapter supplies the event; the core does not consume Android lifecycle types.

### Arbitration and overload control

Serialize policy inputs. Coalesce simultaneous triggers into one status with multiple reasons. Apply a proposed fixed 10-second minimum creation interval; retain a pending change and re-evaluate it when the interval allows. A retry is not a new trigger and never creates a new statusId.

Update policy reference state only after a status and its admission metadata are durably stored. A failed queue write must not suppress the next eligible status. On restart, recover the last admitted policy state or use the documented initialization rule.

### Proposed configurable values

| Allowlisted key | Default | Allowed range |
|---|---:|---:|
| publishIntervalSeconds | 60 | 10-300 |
| socDeltaPercentagePoints | 1.0 | 0.5-10.0 |
| odometerDeltaKm | 1.0 | 0.1-10.0 |

These illustrative values depend on the approved field set and data-volume budget. Use "percentage points" for SOC differences. Do not accept unknown keys, alternate types, NaN/infinity or partial application of a rejected profile.

TELEMETRY_PROFILE_UPDATE may change only the approved telemetry profile. It cannot change vehicle permissions, mapping semantics, endpoints, trust anchors, the minimum interval, queue limits or actuator behavior. Apply a valid profile atomically to future decisions; previously queued envelopes retain their original profileVersion. Define a versioned local rollback operation for support, not an unrestricted remote command channel.

<!-- PAGE -->
# 8. Cloud adapters and delivery semantics

### Comparable behavior; visible protocol differences

Both adapters consume the same canonical envelope, preserve identifiers and produce the same project-owned result vocabulary. The MQTT path may receive subscribed messages; the HTTPS replacement is not assumed to offer equivalent subscription behavior. Controlled configuration can remain on the MQTT path for the MVP. [P1, section 5.2]

| Result concept | Required meaning |
|---|---|
| TRANSPORT_ACCEPTED | The declared transport peer accepted responsibility. Record whether that peer is the broker or HTTP endpoint. |
| APPLICATION_CONFIRMED | The approved receiver returned a receipt for the same statusId after its declared acceptance step. |
| RETRYABLE_FAILURE | A temporary failure with an explicit retry decision and optional backoff hint. |
| PERMANENT_FAILURE | Authentication, schema or other non-retryable failure classified under the adapter contract. |
| UNKNOWN | Completion cannot be established, including timeout after a possible delivery. Retain the same ID for retry. |

MQTT QoS 1 provides at-least-once delivery to its protocol receiver and uses PUBACK; it is not proof that a downstream application committed the record. HTTP 202 explicitly means processing has not completed. The portable model must not collapse these stages into a misleading "success". [R8, R9]

### Proposed MVP receipt contract

Use controlled test receivers for both paths. Each validates the envelope, records or recognizes statusId, then emits an application receipt. MQTT uses a separate receipt topic. HTTPS returns a documented receipt after the receiver's acceptance step; an asynchronous endpoint needs a declared status/receipt mechanism. A bare HTTP status is not sufficient unless its endpoint contract establishes the required milestone.

Complete the offline record only at APPLICATION_CONFIRMED. Until then, retain it within the bounded retention policy. Compare receipt identity and normalized meaning, not protocol packets or wire payload equality.

### Provider and protocol proof boundaries

Provider serializers, authentication details, topic names, URLs and error mapping stay outside the core. Record whether Cloud A and Cloud B are distinct providers, distinct services or merely protocol endpoints on one controlled backend. The last case proves protocol substitution, not independent cloud-vendor portability.

### Required negative cases

Exercise TLS validation failure, unauthorized identity, malformed payload, broker rejection, HTTP failure, receiver timeout, lost receipt and duplicate receipt. Preserve attempt diagnostics without altering statusId. Test receiver deduplication is observable evidence for that receiver only; it does not establish exactly-once transport or universal backend deduplication.

<!-- PAGE -->
# 9. Offline retention and recovery

### Proposed durable workflow

Create an immutable status and policy-admission state in one local transaction. Move the record through **PENDING -> IN_FLIGHT -> CONFIRMED**. Retryable or unknown outcomes return it to PENDING. Permanent failures move to a bounded quarantine or a terminal record with a reason. Expiry and overflow are explicit terminal outcomes, not successful deliveries.

Use the existing suitable storage engine when possible. Storage technology is an adapter decision; capacity, retention, retry and loss semantics are application decisions.

| Control | Proposed MVP starting value / behavior |
|---|---|
| Capacity | At most 1,000 envelopes and 8 MiB of application-accounted serialized envelope data, whichever is reached first. Measure database/WAL overhead separately. |
| Retention | 60 minutes from original status creation; retries do not extend the lifetime. |
| Overflow | Remove expired records first; otherwise drop the oldest pending record with an observable reason. Do not evict an active in-flight record. |
| Retry | Exponential delay starting at 1 second, normally capped at 60 seconds, with controlled jitter. Respect longer server backoff within retention. |
| Concurrency | One in-flight send initially; recover ambiguous in-flight records as pending after restart. |
| Drain | Proposed maximum 10 attempts/second, still constrained by backoff, receiver capacity and the remaining retention period. |

Values are proposed for Gate B approval, not production sizing. Quarantine shares a declared bounded budget. Enforce and test a physical storage ceiling after measuring implementation overhead; serialized-byte limits alone do not bound all filesystem usage.

### Sizing check

At one new status every 60 seconds, an hour creates 60 envelopes. At the proposed 10-second minimum, the worst sustained creation rate is 360/hour. Assuming 2 KiB per serialized envelope, that is about 720 KiB of envelope data, excluding indexes, logs and receipts. Validate actual size and disk usage on the AAOS build before accepting these limits.

### Crash and outage behavior

Preserve statusId, envelope, attempt metadata and the receipt boundary across reconnects and process restart. Test crashes before send, after send/before receipt, and after receipt/before local completion. The ambiguous cases can produce duplicates; the receiver must expose them.

Use monotonic time for in-process scheduling and trusted wall time for persisted expiry decisions. After reboot, do not reuse an old monotonic timestamp as if it belonged to the new clock epoch. When wall-time trust is unavailable, hold expiry-sensitive actions under a documented conservative policy and report the condition.

<!-- PAGE -->
# 10. Security and controlled downlink

### Boundary established from week 1

Use synthetic/test telemetry and approved test identities. Require TLS peer and hostname validation; prohibit trust-all certificates and credentials in source code or logs. Bind authentication through opaque credential handles. Android Keystore can provide restricted key use, but hardware-backed protection depends on actual device support and configuration; verify it rather than claim it. [R10]

### One command, narrowly authorized

TELEMETRY_PROFILE_UPDATE is the only remotely accepted business command. Proposed envelope: commandId, targetAlias, commandType, schemaVersion, profileVersion, issuedAt, expiresAt and the allowlisted profile. Use an approved message-authentication/signature mechanism when needed for the selected trust boundary; TLS alone does not establish authorization of every downstream command origin.

| Check | Required behavior |
|---|---|
| Size and schema | Bound input size before processing; proposed limit 4 KiB. Reject unsupported type/version, duplicate/unknown fields and malformed values. |
| Origin and target | Authenticate the issuer, authorize profile changes and require an exact target match. |
| Freshness | Require trusted time; proposed maximum command lifetime 5 minutes and clock tolerance 30 seconds. Fail closed when time cannot be trusted. |
| Replay and order | Persist command identity/payload digest and the accepted profile version. Reject replay or non-increasing versions, including after restart. |
| Range and atomicity | Validate all keys before changing anything. Atomically persist the new profile, version and replay state before acknowledging acceptance. |
| Audit | Record acceptance/rejection code, safe correlation reference and version; exclude secrets and unnecessary payload data. |

These are proposed controls to be reviewed against the selected infrastructure. An identical replay must not reapply the update; return an observable replay/duplicate reason. A reused commandId with different content is a separate rejection case. Bound replay storage using expiry and version policy.

### No actuator path

The Vehicle Status component exposes no write port and holds only required read permissions. Review manifests, service permissions and call paths; reject a vehicle-control message before dispatch. Where the existing application has broader privileges, isolate the telemetry component or demonstrate an enforceable boundary before claiming no actuator access.

### Security acceptance and exclusions

Test valid update, bad signature/identity, unauthorized issuer, wrong target, expiry, future timestamp, replay after restart, malformed schema, out-of-range values and vehicle control. Production PKI, manufacturing provisioning, HSM guarantees, certification and production fleet operations remain separate work. Deferring hardening must not weaken command rejection or basic TLS validation. [P1, sections 8, 10-11]

<!-- PAGE -->
# 11. AAOS runtime integration

### Recover the actual integration path

Determine whether the PoC is an application/service using CarPropertyManager, a platform-native component, or a vendor integration. CarPropertyManager is an application-facing vehicle-property API. VHAL interface details depend on the platform generation; current AOSP documents the transition from HIDL to AIDL. Do not select direct VHAL access without confirming the component's permitted layer. [R2, R11]

| Concern | Implementation and evidence required |
|---|---|
| Startup / readiness | Record service ownership, supported startup mechanism, user context and how vehicle-service readiness is detected. |
| Subscription lifecycle | Register once, handle reconnect, unregister on stop and prove repeated start/stop does not multiply callbacks. |
| Execution model | Move network and disk operations away from vehicle callbacks; use bounded input queues and a serialized policy coordinator. |
| Permissions | Record every requested/granted permission and each signal it authorizes. Missing access becomes an observable integration failure. |
| Power and restart | Specify what happens during suspend, resume, process death and reboot. Preserve durable queue and profile state. |
| Packaging and update | Record package/signing identity, install path, configuration ownership, persistent-data location and rollback behavior. |
| Diagnostics | Expose safe counters and structured reasons through project-owned diagnostics and the approved AAOS logging surface. |

### Separate four validation surfaces

**Host behavior:** deterministic clocks, IDs, traces and fake ports exercise the same core. This is not a runtime or Linux deployment claim.

**AAOS injected integration:** controlled observations exercise the core through the AAOS lifecycle and adapters. Label the input as injected; it does not validate the real vehicle-data acquisition path.

**AAOS real interface:** validate permitted property access, subscriptions, quality states and disconnect handling through the selected AAOS vehicle interface. Record whether its underlying source is simulated or physical.

**Receiver integration:** prove both cloud paths and their receipt contracts against controlled endpoints. Keep its evidence separate from core-only simulation.

### Resource measurements

Capture idle and active CPU, process memory, storage growth, queue depth and callback latency on the named image/hardware. Approve absolute budgets at Gate A from the platform allocation; do not invent production limits. Use repeated lifecycle and long-outage tests to find growth trends. An environment that cannot execute a test receives a limitation record, not an automatic pass.

<!-- PAGE -->
# 12. Revised 18-week delivery baseline

### Explicit resource-driven rebaseline

The source's full acceptance objective is retained, but its eight-week schedule is superseded for this two-person team. The former v0.9 plan assumed 3.5 FTE. This plan uses only one senior and one junior, serializes senior-critical work and makes week 8 an **intermediate demonstration**, not Gate C. [P1, section 8; P2]

| Window | Senior-critical outcome | Junior contribution / exit |
|---|---|---|
| W1-W2 | Recover PoC, permissions, hosting risks and cost; Gate A. | Reproduce build, record traces and dependency evidence. |
| W3-W4 | Draft contract, triggers and ports; begin core extraction. | Deterministic fixtures, test runner and dependency checks. |
| W5-W6 | Gate B at W5; stabilize core and AAOS boundaries. | S1-S2 regression, mapping fixtures and CI. |
| W7-W8 | AAOS mapping A -> core -> MQTT; reduced demo. | Receipt recorder, smoke tests and clean-reset runbook. |
| W9-W10 | HTTPS adapter and comparable receipt contract; S3 both paths. | Adapter tests, receiver fixtures and envelope comparisons. |
| W11-W13 | Durable bounded queue, restart and loss accounting; S4. | Outage/crash matrix, storage metrics and regression. |
| W14-W15 | One authorized profile update and abuse cases; S5. | Rejection fixtures, replay tests and safe audit evidence. |
| W16-W18 | Mapping B, full S1-S6, freeze and target-port package. | Four-combination matrix, evidence index and demo rehearsal. |
| W19-W20 | Sponsor-released contingency only. | Defect closure / blocked acceptance; no new features. |

### Scope kept small without weakening correctness

Limit the field set to the approved minimum, initially about 3-5 signals if available; use one AAOS image, one runtime language and one controlled receiver implementation exposing two protocol paths. Reuse existing broker/TLS/storage libraries. Keep mapping B deterministic, as permitted by the source. No new UI framework, second production backend, full OTA service, live second OEM or optional platform port is in the estimate.

If both protocol paths use one backend, claim **protocol substitution**, not independent cloud-vendor portability. A genuine second-provider integration requires confirmed access and re-estimation. Core semantics, application receipts, durable recovery, unsafe-command rejection and S1-S6 remain mandatory for the full MVP.

### Critical path

Access/build -> approved semantics -> same-core host build -> AAOS/MQTT -> HTTPS -> durable fault recovery -> controlled configuration -> mapping matrix/freeze. Mapping fixtures and documentation run in parallel only within junior capacity. The senior does not concurrently lead several unresolved platform integrations.

<!-- PAGE -->
# 13. Detailed plan: weeks 1-2

### Senior developer - own discovery and the first decision

1. Rebuild and run the exact PoC commit on the named AAOS image. Trace one observation through mapping, eligibility, serialization, transport, persistence and logs. Record permission and credential boundaries.
2. Classify core, adapter and platform dependencies. Identify only the cleanup needed for Vehicle Status; rank language/runtime incompatibility, service lifecycle and persistence coupling.
3. Start the threat model and obtain test identity/endpoint access. Keep vehicle access read-only and disable unneeded remote command paths.
4. Bound the native-telemetry / existing-component fit-gap and target hosting spike. Treat a major migration as a rebaseline decision, not a junior task.
5. Review the initiative shortlist with the sponsor. Identify the team/customer that will consume I1 evidence or the alternative pilot.

### Intern/fresher - establish reproducible evidence

Follow the recorded setup on a clean environment; capture sanitized normal, missing-data and outage traces. Build the dependency/permission inventory from a senior-provided template. Add one small characterization test and demonstrate the test/runbook without step-by-step prompting. No security, concurrency or semantic decisions are delegated without review.

### Proposed task budget and ramp-up

Across the first two weeks: senior 56 delivery hours and junior 24 credited delivery hours. This includes WP1 recovery plus early target/governance evidence. Nominal staffing is 80 hours per person; the difference covers mentoring, coordination and junior onboarding as specified in section 20. Do not treat 160 staffed hours as 160 accepted implementation hours.

### Gate A - end of week 2

Required evidence: reproducible baseline or an explicit blocked result; current-state diagram and dependency inventory; actual signal/access facts; junior capability assessment; hosting disposition; approved initiative; estimated remaining work and constraints.

**Continue** only if the senior-critical workload still fits the plan and the PoC is recoverable without a major rewrite. **Re-scope** to the reduced AAOS demonstration or I2 if schedule/value priorities demand it. **Pause** when source access or essential permissions are absent. Any extra discovery is charged to released contingency or a newly approved baseline.

### First ten working days

Days 1-2: build, credentials and one status trace. Days 3-4: coupling/permission map and initial tests. Days 5-6: semantics questions and junior task review. Days 7-8: hosting/fit-gap spike and fixture catalogue. Days 9-10: backlog loading, decision workshop and Gate A record. This sequence is a proposed working order, not a promise of access resolution by a specific day.

<!-- PAGE -->
# 14. Detailed plan: weeks 3-8

### Weeks 3-5 - contract, tests and core extraction

**Senior:** approve the minimal signal meanings with the domain authority; define units, quality, clock domains, required data and degraded behavior. Freeze the three triggers, status identity, receipt vocabulary and bounded profile. Introduce only the needed ports and remove Android/provider types from selected core paths. Make a same-source host build work before deeper integration.

**Junior:** implement supplied fixtures, deterministic clocks/IDs, expected/actual reports and build dependency checks. Cover threshold boundaries, missing/stale data, semantic mismatch and failed queue admission. Senior approves each oracle; the junior does not invent domain meaning from field names.

**Gate B at week 5:** contract and scenario catalogue approved; S1-S2 host tests pass; forbidden dependencies are absent. Keep unresolved cases visible. If this gate slips by more than one week, review the week-8 outcome immediately rather than dropping tests.

### Weeks 5-6 - reconnect to AAOS

**Senior:** bind approved vehicle reads, lifecycle/readiness and serialized input to the same core. Keep disk/network work out of vehicle callbacks. Isolate MQTT serialization, credential handles and receipts behind the sink contract; preserve known-good integration tags.

**Junior:** prepare start/stop/reconnect smoke tests, expected mapping A traces, clean install scripts and a receiver receipt recorder. Start mapping B fixtures, not a second live integration. Test source-of-data labeling: host fake, injected AAOS data or actual AAOS interface.

### Weeks 7-8 - demonstrate one complete vertical slice

Demonstrate mapping A -> canonical core -> MQTT/TLS -> controlled receiver, with correlated status IDs and an explicit application receipt. Run lifecycle smoke tests and the approved S1-S2 suite. Show basic invalid-data rejection and the dependency boundary. Keep remote downlink disabled; use a local approved profile until S5 is complete.

The week-8 demo may expose offline-store interfaces or basic buffering, but **must not claim durable crash recovery** until S4 passes. HTTPS, full mapping B substitution and remote configuration remain scheduled work, not implied completions.

### Week-8 management checkpoint - not Gate C

Deliver the runnable AAOS slice, recorded test results, measured senior/junior throughput and an updated remaining estimate. Sponsor chooses continue toward the full MVP, stop at the explicitly reduced demonstrator, or change initiative. A stop is a legitimate partial outcome; it cannot be advertised as two-mapping/two-cloud reusable Vehicle Status.

**Rollback control:** one active publisher only. Revert to the last known-good integration if the smoke test fails; never bypass the core merely to keep the display looking successful.

<!-- PAGE -->
# 15. Detailed plan: weeks 9-13

### Weeks 9-10 - HTTPS substitution and S3

**Senior owns:** sink behavior, TLS/authentication, timeout and error classification, receipt acceptance and the source-diff review. Use a controlled test receiver with MQTT and HTTPS entry points to bound backend effort. Distinct production providers are not assumed.

**Junior owns under review:** HTTPS adapter skeleton from the approved interface, payload/receipt fixtures, receiver test utilities and trace-comparison scripts. The senior reviews all identity, failure and retry paths before merge.

Replay the same input with controlled clocks and IDs. Compare eligibility, the pre-provider envelope, statusId/correlation and the same declared acceptance stage. Inject unknown delivery, rejection, bad TLS and lost/duplicate receipts. MQTT subscription remains a protocol capability; the MVP does not invent an equivalent HTTPS downlink.

**Exit:** S3 passes on AAOS for both paths, and the core behavior is unchanged by the swap. A missing abstraction is reviewed and regression-tested across both adapters, not silently patched in one provider serializer.

### Weeks 11-13 - durable offline recovery and S4

**Senior owns:** transactional queue admission and policy state, durable identifiers, retry/backoff, capacity/retention/overflow, ambiguous in-flight recovery and physical storage limits. Reuse a suitable existing database; avoid custom storage machinery.

**Junior owns under review:** network-outage orchestration, queue fixtures, boundary-case scripts, restart/crash test automation, reason-counter checks and resource measurements. Do not delegate transaction design or clock-recovery semantics solely to the junior.

Test crashes before send, after send/before receipt and after receipt/before local completion. Test count/byte limits, expiry, storage-write failure, untrusted wall time and long receiver backoff. Every undelivered record must have an expected reason; duplicates must be observable and keep the same immutable envelope/ID.

**Exit:** S4 passes on the named AAOS environment. The no-loss 120-record fixture reconciles unique receiver IDs, and limit/expiry fixtures reconcile declared losses. Record actual disk growth, CPU/memory and drain time against the approved test budget.

### Senior-load rule

The loaded plan assigns 56 senior delivery hours to weeks 9-10 and 84 to weeks 11-13: these windows are fully loaded at 28 hours/week. New feature requests, repeated integration rework or access delays cannot be absorbed by assigning more architecture work to the junior. Consume approved reserve, reduce optional scope or change the calendar.

<!-- PAGE -->
# 16. Detailed plan: weeks 14-18

### Weeks 14-15 - controlled configuration and S5

**Senior:** complete the selected identity/trust binding, issuer/target authorization, size/schema/freshness/range validation, replay protection and atomic profile/version persistence. Verify the actual component has no vehicle-write path. Use established security libraries; do not design custom cryptography.

**Junior:** implement the approved negative-case catalogue and safe evidence capture. Test valid next-version update; wrong target; unauthorized or bad identity; expiry/future date; replay before/after restart; reused ID with changed content; malformed/unknown fields; range failure; and vehicle-control messages.

Run TLS/identity tests on AAOS, not only in host fakes. The senior records the security test disposition. The sponsor acknowledges that two-person internal review is not independent security assurance or production authorization. If the required controls cannot be demonstrated, keep downlink disabled and mark full Gate C blocked.

### Weeks 16-17 - mapping B and integrated reuse

**Senior:** implement/review the controlled B adapter against already approved semantics. Resolve no new business meaning merely to make outputs match. Complete remaining lifecycle and release checks.

**Junior:** execute A+MQTT, A+HTTPS, B+MQTT and B+HTTPS; run applicable S1-S5 negative cases. Capture fixtures, canonical hashes, result diffs and core/adapter versions. Equivalent inputs should match; incompatible meaning should produce the explicitly different expected outcome.

Measure actual effort and core-file changes for each substitution. This is evidence of the tested reuse case, not proof of universal portability or a revenue forecast.

### Week 18 - freeze, acceptance and target package

Freeze the core path set, canonical schema, profiles, fixtures and release tag. Deliver S1-S6 results, a clean-reset demo, limitations/claims, residual defects and support runbook. The junior should reproduce the demonstration without unpublished senior-only steps.

Complete the named AAOS SDV lifecycle, data/IPC, permission, packaging and storage gap matrix. **Gate C** concerns the full AAOS MVP; **Gate D-Design** concerns the substantiated target package. They are separate decisions. Missing target access may block D-Design even when C passes. Actual SDV execution remains a later Gate D-Runtime.

### Weeks 19-20 - controlled reserve

Release reserve only for a recorded blocker, acceptance defect or underestimated critical task. Preserve mandatory tests and claim limits; do not add UI polish, extra signals or a runtime port. If the approved plan still cannot complete, issue a revised commitment rather than silently treating week 20 as an unlimited extension.

<!-- PAGE -->
# 17. Golden scenarios: S1-S3

### Status of these definitions

The revision references S1-S6 without complete test specifications. The following is a **proposed operationalization**, aligned to its weekly sequence. Reconcile against the original scenario catalogue or approve a new version at Gate B. Test data values below are synthetic. [P1, sections 7-8]

### S1 - canonical mapping and data quality

**Purpose:** verify approved semantics independent of vehicle vocabulary.

**Setup and steps:** replay mapping A and B traces for the same approved state. For an illustrative equivalent case, normalize 12,345,600 m to 12,345.6 km and two representations of the same SOC basis. Repeat with unavailable, stale, invalid, delayed and out-of-order observations. Include a deliberately incompatible SOC basis or estimated odometer.

**Pass oracle:** equivalent inputs produce the approved values, units, quality and eligibility; incompatible meanings are rejected/marked unsupported according to contract, not coerced into equality. Missing values never become zero. Out-of-order handling follows the approved policy.

**Surfaces and evidence:** host plus AAOS injected integration; separately validate mapping A acquisition through the actual interface. Store raw input fixture, mapping version, canonical output, quality reasons and expected/actual diff. Domain owner approves the expected output.

### S2 - publish policy and bounded profile behavior

**Purpose:** verify the three triggers and policy arbitration.

**Setup and steps:** set the proposed profile to 60 seconds, SOC delta 1 percentage point and odometer delta 1 km. Drive a controlled clock to just before/at the periodic deadline; vary each signal below/at/above threshold; delay required data at startup; issue simultaneous triggers. Exercise queue admission failure, profile change and restart.

**Pass oracle:** exact expected creation count, reasons and profileVersion; one snapshot for coalesced triggers; stable last-admitted reference; no new status for retries. Boundary-invalid profiles leave the active profile unchanged. No wall-clock jump causes a policy burst.

**Surfaces and evidence:** host decision trace and AAOS integration trace with identical logical event ordering. Store clock/ID seeds, admission outcomes and expected publish-decision sequence.

### S3 - cloud substitution and outcome normalization

**Purpose:** preserve core behavior while replacing MQTT with HTTPS.

**Setup and steps:** replay identical canonical fixtures through both adapters; inject acceptance, receiver rejection, TLS failure, timeout and duplicate/lost receipt.

**Pass oracle:** equal pre-provider envelopes, eligibility, IDs and correlation; equivalent normalized disposition at the same declared milestone; correct retention until application receipt. Protocol capabilities remain explicitly different.

**Surfaces and evidence:** AAOS plus controlled receivers, with host adapter-contract tests. Store canonical hashes, receiver receipts, safe transport diagnostics and core source diff. A shared backend is identified as protocol-substitution evidence only.

<!-- PAGE -->
# 18. Golden scenarios: S4-S6

### S4 - bounded offline recovery and duplicate visibility

**Purpose:** demonstrate predictable behavior during outage and uncertain delivery.

**Setup and steps:** create a proposed 120 eligible statuses while the link is unavailable and restore it before retention expires. Repeat with crashes before send, after send/before receipt, and after receipt/before local completion. Separately fill the count/byte limits, advance past retention and inject disk-write failure. For the capacity case, use an accelerated clock or direct queue fixture instead of pretending ordinary traffic exceeds a limit it cannot reach.

**Pass oracle:** the controlled receiver confirms 120 unique IDs in the no-loss case; any duplicate attempts are visible. Retries preserve complete envelopes. Every missing record in limit/expiry tests has the expected terminal reason. Restart restores queue and profile state. Storage accounting stays within approved bounds.

**Evidence:** queue snapshots, fault timing, attempt/receipt correlation, receiver unique/duplicate counts, reason counters and physical storage measurements. Run on AAOS; use host tests for precise policy boundaries.

### S5 - security and configuration boundary

**Purpose:** prove one authorized configuration path and rejection of unsafe inputs.

**Setup and steps:** accept one valid next-version profile. Try unauthorized issuer, wrong target, bad authentication, expired/future time, untrusted clock, replay before/after restart, reused ID with changed payload, malformed schema, unknown keys, out-of-range values and vehicle control. Interrupt storage during profile application.

**Pass oracle:** only the valid update changes future policy; rejected updates do not partially apply. Replay/version state survives restart. The accepted profile and replay record commit atomically. All rejections have safe reason codes; no actuator call or permission is used by the component.

**Evidence:** command catalogue, before/after profile state, safe audit log, permissions/call-path review and security reviewer disposition. Host rule tests do not replace TLS/identity tests on AAOS.

### S6 - integrated reuse and baseline freeze

**Purpose:** demonstrate substitutions without hidden core edits.

**Setup and steps:** execute the positive canonical fixture across A+MQTT, A+HTTPS, B+MQTT and B+HTTPS; replay applicable negative S1-S5 cases. Use a non-publishing recorder so comparison instrumentation does not create duplicate application traffic. Verify the actual released core and adapter identifiers.

**Pass oracle:** equivalent inputs preserve approved behavior across all four combinations. Non-equivalent inputs produce their explicitly different expected outcomes. Core behavior is unchanged across substitution runs; after final freeze, core source changes are zero unless an approved exception is documented and all tests are repeated.

**Evidence:** test matrix, fixture/contract versions, core path hashes, source diffs, result bundle and claim matrix. This proves the declared AAOS-centered reuse case. It does not complete an AAOS SDV runtime port. [P1, sections 3.4, 5-6]

<!-- PAGE -->
# 19. Acceptance gates and evidence controls

### Same mandatory behavior, revised dates and real owners

| Gate / planned checkpoint | Required evidence | Decision responsibility |
|---|---|---|
| Gate 0 - before week 1 | Named two-person capacity, runtime/build, authorized data and endpoints. | Sponsor; senior verifies prerequisites. |
| Gate A - week 2 | PoC recovery, dependencies/unknowns, hosting disposition, junior assessment, initiative choice and re-estimate. | Sponsor; senior supplies technical recommendation. |
| Gate B - week 5 | Approved semantics/triggers/bounds; same-core host build; no forbidden dependencies; S1-S2 pass. | Senior; sponsor records domain approval. |
| Reduced demo - week 8 | Mapping A + MQTT AAOS slice, receipts and declared limitations. Not full reuse acceptance. | Sponsor continue/stop decision. |
| Gate C - week 18 | AAOS boundaries, mappings A/B, both cloud paths, S1-S6 and complete offline/security evidence. | Senior signs technical results; sponsor accepts PoC scope. |
| Gate D-Design - week 18 target | Named target and substantiated lifecycle/hosting/IPC/permissions/packaging gaps with an executable backlog. | Senior; sponsor accepts the design claim. |
| Gate D-Runtime - separately scheduled | Actual named target executes same contract/scenarios; behavior preserved; core changes governed. | Approvers named in follow-on plan. |

Gate D-Design is not a substitute for the source's runtime-portability proof. Missing evidence is FAIL or NOT RUN, not an implicit pass. The junior compiles the result bundle; the senior reviews oracles and reruns critical faults. No separate QA/security team is implied. [P1, sections 7-8]

### Full-MVP release measures

Mandatory applicable cases: **100% pass**. Forbidden core dependencies: **zero**. Unreviewed post-freeze core changes: **zero**. Accepted unsafe commands/actuator calls: **zero**. Undeclared queue loss: **zero**. Any reduced-scope release uses a separate claim statement and cannot pass full Gate C.

Retain the proposed 120-record no-loss outage fixture and recovery target of 120 seconds after receiver/link readiness, without throttling, subject to Gate A approval. Compare resource use against the named runtime's approved budget; do not invent production limits.

### Evidence integrity and assurance limit

Record tag, core hashes, image/build, adapter versions, schema/profile/fixture versions, input surface, clock/ID seed, expected/actual outputs, receipts, resource results and deviations. Require a clean-reset runbook and a junior-led replay. Capture source diffs for each substitution.

The senior is both implementer and reviewer of some critical paths. Automated negative tests, reproducible evidence and explicit sponsor risk acceptance reduce opacity, but do not create independent assurance. Production use or a stronger security claim requires separately resourced review.

<!-- PAGE -->
# 20. Staffing, capacity and cost

### Exactly two full-time people - planning assumptions

| Capacity item | Senior developer | Intern/fresher |
|---|---:|---:|
| Nominal availability | 40 hours/week | 40 hours/week |
| Credited delivery capacity | 28 hours/week | 12 hours/week in W1-W2; 24 thereafter |
| Other scheduled time | 6 mentoring + 4 coordination + 2 environment/support hours/week | 28 hours/week initially; 16 thereafter for learning, guided practice and rework |
| 18-week delivery capacity | 504 hours | 408 hours |
| Planned accepted work (section 20A) | 476 hours | 352 hours |
| Unassigned delivery headroom | 28 hours | 56 hours |
| Nominal staffed hours, 18 weeks | 720 hours | 720 hours |

These are planning assumptions, not general productivity claims about juniors. Delivery includes implementation, ordinary PR review, test execution and technical evidence. Extra mentoring is reserved separately; do not count the same review hour in both categories. Junior hours credit reviewed, accepted work rather than time merely spent at the keyboard.

The workload fits total capacity but is tightly loaded early; aggregate junior headroom cannot replace senior-critical work. Validate accepted output and review effort at weeks 2, 5 and 8. Part-time internship, substantial leave, competing assignments or a senior unfamiliar with the platform invalidates this baseline.

### Staffing and funding envelopes

Initial recovery: **160 nominal hours / 4 staffed person-weeks**. Eight-week checkpoint: **640 nominal hours / 16 staffed person-weeks**. Full baseline: **1,440 nominal hours / 36 staffed person-weeks**. Two-week reserve: **160 additional hours / 4 staffed person-weeks**. Maximum authorized 20-week envelope: **1,600 nominal hours / 40 staffed person-weeks**.

With approved loaded hourly rates S and J: recovery labor = 80S + 80J; full-baseline labor = 720S + 720J; released reserve = 80S + 80J. Add approved infrastructure and any separately authorized external review. No salary or cloud-price assumptions are made.

The v0.9 baseline was 1,120 nominal hours across 3.5 FTE for eight weeks. The revision increases nominal hours by 320 (28.6%) while changing the skill mix and sequencing. Lower headcount is not automatically lower total cost; calculate with actual rates. The 828 accepted-work hours in section 20A are a different measure and must not be compared directly with the old nominal hours.

### Calendar, not hidden overtime

Eighteen weeks is a proposed delivery baseline, not a statistical confidence interval. Weeks 19-20 are about 11.1% additional calendar/staffing, not the old 20% reserve. No overtime or extra developer is assumed. Gate A can approve a longer schedule when risk or actual throughput warrants it.

<!-- PAGE -->
# 20A. Work allocation and workload checks

### Bottom-up work-package estimate

Hours below are proposed credited delivery hours after the capacity deductions in section 20. They include planned tests/review and are not additional to staffed hours. Work windows overlap only where the phase-level capacity check allows.

| Package / window | Senior h | Junior h | Ownership boundary |
|---|---:|---:|---|
| WP1 Recovery; W1-W2 | 52 | 20 | Senior recovers architecture; junior reproduces evidence. |
| WP2 Contract/core tests; W3-W5 | 60 | 60 | Senior approves semantics/ports; junior implements fixtures/CI. |
| WP3 AAOS/core/MQTT; W5-W8 | 80 | 44 | Senior integrates platform; junior tests and records receipts. |
| WP4 HTTPS/receiver; W9-W10 | 56 | 40 | Senior owns security/outcomes; junior supplies bounded adapter/tests. |
| WP5 Offline/crash recovery; W11-W13 | 84 | 56 | Senior owns transactions/timing; junior automates faults/metrics. |
| WP6 Security/config; W3-W4, W7-W8, W14-W15 | 64 | 40 | Early design; senior owns all security decisions and merge approval. |
| WP7 Mapping B/reuse; W3-W6 fixtures, W16-W18 | 44 | 64 | Senior signs semantic oracles; junior runs matrix/evidence. |
| WP8 Target/gates/runbook; W1-W8, W16-W18 | 36 | 28 | Senior produces target disposition; junior maintains reproducibility. |
| **Total planned delivery** | **476** | **352** | **828 hours within 912 available delivery hours.** |

### Responsibility and review boundaries

| Work area | Senior remains accountable for | Junior can deliver under review |
|---|---|---|
| Core and vehicle mapping | Meaning, architecture, timing and input validity. | Fixtures, pure mapping functions and regression scripts. |
| Cloud and offline state | Identity, receipts, transactions, retry and recovery. | Adapter scaffolding, controlled receiver utilities and fault automation. |
| Security and release | Authorization, replay defense, no-write boundary and gate judgment. | Negative tests, evidence indexing, safe logs and runbook rehearsal. |

### Junior-ready task definition

Each ticket has a bounded input/output contract, one worked example, a test oracle, prohibited changes and a reviewer. Prefer tasks of 0.5-2 working days. A task is complete only after tests and senior review, not when code is first submitted.

The junior is a developing contributor, not an independent replacement for QA, cloud engineering or security review. Increase scope only after demonstrated accepted output. Keep the most consequential state transitions under senior ownership.

<!-- PAGE -->
# 20B. Capacity checks and delivery controls

### Phase loading - planned / available delivery hours

| Window | Senior planned / capacity | Junior planned / capacity |
|---|---:|---:|
| W1-W2 | 56 / 56 | 24 / 24 |
| W3-W4 | 56 / 56 | 48 / 48 |
| W5-W6 | 56 / 56 | 48 / 48 |
| W7-W8 | 56 / 56 | 36 / 48 |
| W9-W10 | 56 / 56 | 40 / 48 |
| W11-W13 | 84 / 84 | 56 / 72 |
| W14-W15 | 48 / 56 | 30 / 48 |
| W16-W18 | 64 / 84 | 70 / 72 |
| **Total** | **476 / 504** | **352 / 408** |

Senior delivery alone requires 476/28 = **17 working weeks** before sequencing; 18 weeks leaves limited headroom. At 24 senior delivery hours/week, it requires at least 19.8 weeks before sequencing, so the 18-week promise fails. If junior sustained accepted capacity is 16 rather than 24 hours/week after onboarding, only 280 hours are available over 18 weeks, leaving a 72-hour shortfall. Re-plan instead of assuming the senior absorbs it.

**Work-in-progress limit:** one senior-critical implementation stream plus one junior-ready task. A junior ticket should have an example, expected output, test and review boundary, normally fitting 0.5-2 working days. Architecture, credentials, concurrency and persistent-state transitions always require senior ownership.

### Weekly operating rhythm

Use the reserved coordination time for one short sponsor/evidence review and backlog planning. Protect the six senior mentoring hours as planned pairing and junior unblock time. Ordinary code review and technical testing stay inside the 28-hour delivery budget.

Track accepted work, review queue age, blocked days and remaining senior-critical effort. A weekly progress report should show runnable evidence and next-gate risk, not only completed ticket counts. Re-estimate at weeks 2, 5 and 8; the sponsor decides whether to use reserve or change the commitment.

<!-- PAGE -->
# 21. Risks and scope-control rules

### Initial qualitative assessment - update at Gate A

| Risk / priority | Trigger | Response / owner |
|---|---|---|
| PoC/access failure / H | Build or permitted signal access cannot be reproduced. | Senior escalates; sponsor pauses or re-scopes. Injected data is not physical integration proof. |
| Senior bottleneck / H | Critical PRs/tasks wait over two working days; rework consumes planned delivery. | Stop new streams, reduce optional scope and rebaseline. Senior/sponsor. |
| Junior ramp-up / H | Accepted throughput below model for two review periods. | Smaller tickets, more guided tasks; recalculate remaining effort. Do not transfer security ownership. Senior. |
| Single-person dependency / H | Senior absence or unpublished setup knowledge blocks work. | Daily runbook updates, clean-reset replay by junior, known-good tags. Absence on critical work moves dates. |
| Hidden specialist dependency / H | Work assumes an unassigned platform/security/backend engineer. | Record as a prerequisite or remove assumption; no invisible third implementer. Sponsor. |
| Semantic mismatch / H | B requires unsupported SOC/odometer equivalence. | Obtain authoritative meaning; reject mismatch rather than alter the oracle. Senior/domain authority. |
| Persistence/security fault / H | Lost queue records, premature completion, replay or write path. | Block full Gate C; fix and rerun negative cases. Senior. |
| Major hosting migration / H | Named SDV environment cannot host the core strategy. | Rebaseline or limit AAOS-only claim; do not promise a zero-change port. Senior/sponsor. |
| Ecosystem overlap / M | Native telemetry or existing tooling covers the differentiator. | Reuse components or choose I2/another initiative. Gate A fit-gap. |
| Unproven business adoption / M | No consumer for the reusable asset or pilot output. | Sponsor names a pilot owner and measurable workflow before further funding. |
| Claims exceed results / H | Week-8 demo is labeled full MVP; design called runtime support. | Use gate-specific release notes and explicit PASS/FAIL/NOT RUN. Senior/sponsor. |

### Replanning triggers

Rebaseline when Gate B slips by more than one week, the senior's remaining work exceeds remaining credited capacity, either person's actual availability changes, or access is blocked for more than five working days. Waiting time is not erased by theoretical parallelism. Review the remaining critical path at each checkpoint.

### What may be deferred

Defer extra fields, UI polish, generic abstractions, performance optimization, second live OEM integration, independent cloud-provider deployment and production hardening. Release the calendar reserve only with a named blocker. Keep the core contract, mandatory S1-S6, durable recovery and security rejections intact for a full-MVP claim. [P1, section 10]

<!-- PAGE -->
# 22. AAOS SDV porting package

### Required target definition

Record the exact target release/build, VM or device, supported core language/toolchain, service ownership, vehicle-data producer and access policy. Current SDV service bundles have their own lifecycle and authorization model and are packaged in APEX-based SDV packages; this is not assumed to be an unchanged APK deployment. [R4, R5]

| Integration topic | Week-18 design deliverable | Later runtime proof |
|---|---|---|
| Core hosting | Approved language/library/ABI or hosted-runtime strategy; build spike result and remaining gaps. | Same core source compiles/loads on the target. |
| Lifecycle / resources | Map start/stop/suspend/reconnect to project-owned events and resource ownership. | Repeated lifecycle tests without duplicate work or leaked resources. |
| Vehicle data / IPC | Map canonical observations to approved target topics/channels/interfaces; keep generated types in adapters. | Target data access, quality and timestamp cases pass. |
| Permissions / identity | Service authorization, network rights, key/trust ownership and no-write constraints. | Real identity and negative authorization tests. |
| Packaging / update | Build/deployment artifact, signing, persistent-data compatibility and rollback plan. | Install/update/restart preserves the declared state. |
| Offline / observability | Storage location/limits, metrics and safe diagnostics binding. | S4 plus resource/diagnostic evidence on the target. |
| Cloud path | Confirm whether existing adapters can be reused or require new bindings. | S3 with the same canonical and receipt contracts. |

### Reuse versus built-in telemetry

AOSP describes a native telemetry facility for collecting and processing data into reports. Assess whether it can supply acquisition, transport or operational components while the project retains the agreed Vehicle Status contract and bounded publish behavior. Do not replace the capability with a generic collection engine without a new decision. [R3]

### Follow-on sequence after MVP

**P1:** establish target build/hosting and minimal adapter. **P2:** bind real lifecycle, data, identity and persistence. **P3:** run the same S1-S6, fault/resource tests and change audit. Estimate these work packages after Gate A/target access; week 18 does not imply a funded or completed runtime port.

### Claim progression

Host evidence permits deterministic-behavior claims. The refactored AAOS result permits the demonstrated runtime and reuse claims. The porting package permits design-readiness claims. Only Gate D-Runtime permits support claims for the actual tested AAOS SDV configuration. QNX, Bosch SdV.OS, universal binary portability and production compliance remain outside the validated scope. [P1, sections 6, 11]

<!-- PAGE -->
# 23. Management discussion and decision record

### Proposed opening statement

> With one senior developer and one intern/fresher, we propose a staged investment rather than the previous eight-week full-MVP commitment. We can target a reduced AAOS/MQTT demonstration at week 8 and a complete reuse MVP at week 18, with a controlled two-week reserve. If the priority is useful delivery within 6-8 weeks rather than reusable in-vehicle capability, a signal replay and semantic-validation toolkit is the stronger small-team option.

### Questions to resolve in the meeting

| Management question | Proposed answer |
|---|---|
| Which initiative should we fund? | I1/E3 for an explicit SDV reuse objective; I2 for the strongest near-term small-team fit. Select one, not both products. |
| What changes from v0.9? | 3.5 FTE becomes exactly two people; full acceptance moves to week 18; week 8 becomes a reduced checkpoint. |
| Why is the junior not a second senior? | Contracts, platform faults and security still need senior decisions and review. Ramp-up is explicitly budgeted. |
| What is approved immediately? | Two-week recovery: 80 hours per person, 160 nominal hours total, plus a capped infrastructure allowance. |
| What does week 8 prove? | A declared AAOS mapping-A/MQTT vertical slice and core/test boundary, not full cloud/mapping replacement or durable recovery. |
| What does week 18 prove? | Full AAOS S1-S6 evidence and the substantiated target-port package; not automatic SDV runtime support. |
| Is the smaller team cheaper? | Not necessarily. Compare 720S + 720J plus infrastructure with the old role-rate cost; do not infer savings from headcount. |
| What stops the project? | Failed recovery/access, an unapproved major migration, no consumer, or remaining senior work that cannot fit the approved schedule. |

### Approval record - complete at the decision workshop

| Field | Decision to record |
|---|---|
| Sponsor / initiative | Name: __________  Select I1-I7: __________ |
| Objective / pilot owner | Reuse capability / near-term tool / other; named consuming team: __________ |
| Capacity | Senior and junior names; full-time dates, leave and other commitments: __________ |
| Approved tranche | Recovery only / through week 8 / full week 18; funding cap: __________ |
| Reserve authority | Who may release weeks 19-20 and for which triggers: __________ |
| Technical/assurance limits | Internal PoC, reviewer constraints, data/runtime restrictions: __________ |
| Conditions / dissent / signatures | Sponsor and senior; domain/target approvals where required: __________ |

<!-- PAGE -->
# References and traceability

### Source and revision control

**[P1]** AAOS-First Revision for the SDV Telematics Vehicle Status MVP Plan. Supplied file: SDV_Telematics_Vehicle_Status_AAOS_First_Plan_Revision_EN.md. Source of the AAOS-first architecture, host-only harness, reuse evidence, Gates A-D and claim limits.

**[P2]** SDV Vehicle Status DAR, v0.9, 8 September 2026. Prior working baseline: SDV_Vehicle_Status_AAOS_First_DAR_EN.docx / .md. Its 3.5-FTE/eight-week capacity and related dates are superseded by this revision.

**[P3]** Resource constraint and comparison request: one senior developer plus one intern/fresher; compare with other Automotive ideas. The 40-hour availability, ramp-up, 18-week schedule and workload estimates remain proposed assumptions for approval.

| Source / change | Treatment in v1.0 |
|---|---|
| P1 architecture, semantics and guardrails | Preserved in sections 5-11, 17-19 and 22. |
| P1 eight-week sequence | Acceptance intent preserved; schedule explicitly rebaselined in sections 12-16. |
| P2 multi-role delivery model | Replaced by two-person ownership and capacity in sections 4, 19-21. |
| P3 Automotive initiative comparison | New I1-I7 shortlist, ecosystem fit-gap and sensitivity in sections 2A-2D and 3A. |
| Existing E1-E4 execution comparison | Retained as a separate decision; re-scored for the constrained team in section 3. |

**Proposal register:** initiative list, weights/ratings, time windows, capacity/WBS, pilot targets and replanning triggers are proposed judgments. They are not market statistics, customer commitments or completed test results. Prior proposed schema, triggers, numerical queue/configuration limits and S1-S6 operational definitions still require the stated approvals.

### External sources - official documentation checked 8 September 2026

The references inform platform facts and ecosystem comparisons; they do not establish compatibility with the actual PoC. Pin the chosen platform and dependencies during recovery. Time-sensitive findings: AWS FleetWise is not open to new customers from 30 April 2026; Bosch's diagnostic assistant was announced for a later 2026 update, not represented as already released. [R16, R21]

**[R1]** [CMMI Institute / ISACA. July 2013 Quality Tip - Decision Analysis and Resolution](https://cmmiinstitute.com/resource-files/public/quality/quality-corner/july-2013-quality-tip-decision-analysis-and-reso).

**[R2]** [Android Developers. CarPropertyManager API reference](https://developer.android.com/reference/android/car/hardware/property/CarPropertyManager).

**[R3]** [AOSP. SDV architecture](https://source.android.com/docs/automotive/sdv/sdv-system-architecture).

**[R4]** [AOSP. Logical architecture](https://source.android.com/docs/automotive/sdv/core-areas/what-service).

**[R5]** [AOSP. Quick start: Create and execute SDV service bundles](https://source.android.com/docs/automotive/sdv/workstreams/core/service-bundle-development).

**[R6]** [AOSP. Implement business logic](https://source.android.com/docs/automotive/sdv/core-areas/vsidl/implement-business).

<!-- PAGE -->
# References: Technical and Automotive ecosystem

**[R7]** [Android Developers. CarPropertyValue API reference](https://developer.android.com/reference/android/car/hardware/CarPropertyValue).

**[R8]** [OASIS. MQTT Version 5.0, section 4.3.2](https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html).

**[R9]** [IETF. RFC 9110: HTTP Semantics, section 15.3.3](https://www.rfc-editor.org/rfc/rfc9110.html#section-15.3.3).

**[R10]** [Android Developers. Android Keystore system](https://developer.android.com/privacy-and-security/keystore).

**[R11]** [AOSP. Vehicle HAL overview](https://source.android.com/docs/automotive/vhal).

**[R12]** [AOSP. VHAL reference implementation](https://source.android.com/docs/automotive/vhal/reference-implementation).

**[R13]** [AOSP. SDV Telemetry overview](https://source.android.com/docs/automotive/sdv/workstreams/telemetry).

**[R14]** [COVESA. Vehicle Signal Specification](https://covesa.global/vehicle-signal-specification/).

**[R15]** [Eclipse SDV Blueprints. Communication workflow and recorded signal replay](https://sdv-blueprints.eclipse.dev/docs/e2e-demo-blueprint/communication-workflow/).

**[R16]** [Bosch. AI assistant for ESI[tronic], announcement dated 21 July 2026](https://www.bosch-presse.de/pressportal/de/en/efficiently-find-the-right-repair-solution-ai-assistant-optimizes-esitronic-diagnostic-software-from-bosch-283840.html).

**[R17]** [Open Charge Alliance. Open Charge Point Protocol](https://openchargealliance.org/protocols/open-charge-point-protocol/).

**[R18]** [National laboratory research. Artificial Intelligence Models Improve Efficiency of Battery Diagnostics](https://www.nlr.gov/news/detail/program/2025/artificial-intelligence-models-improve-efficiency-of-battery-diagnostics).

**[R19]** [Uptane. Standard 2.1.0](https://uptane.org/docs/latest/standard/uptane-standard).

**[R20]** [Eclipse Kuksa. Databroker project documentation](https://github.com/eclipse-kuksa/kuksa-databroker).

**[R21]** [AWS. IoT FleetWise availability change](https://docs.aws.amazon.com/iot-fleetwise/latest/developerguide/iotfleetwise-availability-change.html).

### Abbreviations

AAOS: Android Automotive OS. SDV: software-defined vehicle. DAR: Decision Analysis and Resolution. PoC: proof of concept. SOC: state of charge. FTE: full-time equivalent. VHAL: Vehicle Hardware Abstraction Layer. VSS: Vehicle Signal Specification. OTA: over-the-air update. HIL: hardware-in-the-loop. CI: continuous integration. PR: pull request.

### Decision integrity

Keep source facts, proposed engineering estimates and external product claims distinct. A sponsor's selected weighting and risk acceptance must be recorded; a high weighted score is not evidence of safety, demand, profitability or completed portability. No production certification or independent security assurance is claimed by this two-person PoC plan.
