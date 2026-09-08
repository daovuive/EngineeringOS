# Historical external references and comparative analysis

**Status:** source record retained from v1.0, not newly verified research. Do not treat the numerical scores or time-sensitive platform/product statements as current facts solely because this archive exists.

The full comparison and rationale are in `v1_0/SDV_Vehicle_Status_DAR_EN_v1_0_One_Senior_One_Junior.md`, sections 2A-3A. The current approval report uses a qualitative comparison and retains Vehicle Status.

## Historical excerpt: 2A. Automotive initiative shortlist

Source: P10, lines 89-111. These are historical proposed judgments/recorded research, not approvals or measurements.

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

## Historical excerpt: 2D. Existing ecosystem: build, reuse or avoid

Source: P10, lines 172-195. These are historical proposed judgments/recorded research, not approvals or measurements.

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

## Historical excerpt: 3. Execution-strategy evaluation

Source: P10, lines 196-229. These are historical proposed judgments/recorded research, not approvals or measurements.

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

## Historical excerpt: 3A. Initiative ranking and decision rule

Source: P10, lines 230-268. These are historical proposed judgments/recorded research, not approvals or measurements.

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

## Preserved external reference definitions

**[R1]** [CMMI Institute / ISACA. July 2013 Quality Tip - Decision Analysis and Resolution](https://cmmiinstitute.com/resource-files/public/quality/quality-corner/july-2013-quality-tip-decision-analysis-and-reso).

**[R2]** [Android Developers. CarPropertyManager API reference](https://developer.android.com/reference/android/car/hardware/property/CarPropertyManager).

**[R3]** [AOSP. SDV architecture](https://source.android.com/docs/automotive/sdv/sdv-system-architecture).

**[R4]** [AOSP. Logical architecture](https://source.android.com/docs/automotive/sdv/core-areas/what-service).

**[R5]** [AOSP. Quick start: Create and execute SDV service bundles](https://source.android.com/docs/automotive/sdv/workstreams/core/service-bundle-development).

**[R6]** [AOSP. Implement business logic](https://source.android.com/docs/automotive/sdv/core-areas/vsidl/implement-business).

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
