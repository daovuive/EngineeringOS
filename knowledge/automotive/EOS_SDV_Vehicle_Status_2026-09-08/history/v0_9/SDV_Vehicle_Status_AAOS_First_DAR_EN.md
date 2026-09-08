# SDV Vehicle Status
## Decision Analysis and Resolution
### AAOS-First MVP and Implementation Plan

**Decision ID:** DAR-SDV-VS-001  
**Version:** 0.9 | **Date:** 8 September 2026  
**Status:** Proposed - management approval pending  
**Audience:** Engineering sponsor, architecture, AAOS/platform, cloud, verification and security leads

### Decision requested

Approve an AAOS-first, stage-gated MVP for the reusable Vehicle Status capability. Retain the source plan's **Option C: Hardware-Agnostic Telematics Hub**, but constrain implementation to Vehicle Status rather than a general vehicle gateway. Use the existing AAOS PoC as the starting implementation and the host runner only for deterministic behavioral tests. [P1, sections 1, 10-12]

Authorize an initial two-week recovery tranche. Release the remaining six-week plan only after the architecture, access prerequisites, target-runtime compatibility and revised estimate are reviewed at Gate A. This is a proposed funding control, not a change to the source's eight-week delivery objective.

| Approval item | Proposed management position |
|---|---|
| Delivery outcome | One stabilized AAOS runtime; two vehicle mappings; MQTT and HTTPS paths; bounded offline recovery; one safe configuration command; scenario evidence. |
| Planning capacity | 3.5 full-time-equivalent staff over eight weeks: 28 person-weeks. Reserve up to 20% contingency, subject to sponsor release. These are planning estimates, not a quotation. |
| Scope boundary | Read-only telemetry. No actuator control, generic gateway, production certification or new Linux product baseline. |
| Next-platform commitment | Deliver the AAOS SDV porting design and backlog in week 8. Approve runtime validation separately; do not present design readiness as completed portability. |

### Why approve this approach

The proposal converts an existing implementation into reusable behavior instead of funding a second deployment baseline before its dependencies are understood. The architectural value is **preserved business meaning under controlled substitution**, not merely successful telemetry upload. [P1, sections 2-5]

### Conditions that must remain visible

The current PoC's code quality, language, permissions and real vehicle interfaces require recovery. The target AAOS SDV release and hosting model must be named before promising unchanged-source reuse. Formal definitions of S1-S6 and the three publish triggers must be approved before implementation is judged against them.

**Recommendation:** conditionally approve the approach and the recovery tranche; defer unconditional delivery and portability commitments until Gate A.

**Reading guide:** sections 1-4 cover the decision; 5-11 define the proposed implementation; 12-20 cover delivery and acceptance; 21-23 cover risk, the next port and approval.

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
| Security appears late in the weekly plan. | Start threat modeling, credentials and command constraints in week 1; retain week 7 as the formal security demonstration. |

### Business value and measurement

The expected benefit is lower change effort when a vehicle vocabulary, cloud interface or platform binding changes. This is a hypothesis to test, not a quantified saving. Record engineering hours, files changed, regression defects and scenario pass rates for each substitution. A zero-core-change swap is stronger evidence than a high aggregate code-reuse percentage.

A later business case can use: **net reuse value = avoided repeated integration effort - extraction cost - ongoing adapter maintenance**. Avoid ROI percentages until at least one comparable integration and its actual effort have been measured.

### Important current-platform context

Current AOSP documentation describes AAOS SDV as a separate service-oriented environment integrated with AAOS IVI, and includes a platform telemetry capability. The project should therefore check both hosting compatibility and overlap with native telemetry before creating additional infrastructure. This is external context, not evidence that the present PoC already supports those interfaces. [R3, R4]

<!-- PAGE -->
# 2. DAR scope and alternatives

### Decision scope

Select the execution strategy for proving reusable Vehicle Status behavior. Do not reopen the source's entire product strategy or infer its original alternatives. The source names Option C, but this revision does not contain the original Option A/B comparison. The alternatives below are newly defined **execution alternatives E1-E4**. [P1, section 11]

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

C4. Costs, capacity, access and security dependencies must be visible. A failed mandatory condition cannot be offset by a high numerical score.

### Screening result

E1 remains a schedule comparator, but cannot meet the full reuse objective without substantial restructuring. E2 would require an explicit scope change to reintroduce a Linux product baseline. E4 is conditional on a named, accessible target and a fit-gap assessment. E3 is the recommended eligible approach, subject to Gate A findings.

<!-- PAGE -->
# 3. Evaluation and decision rationale

### Proposed criteria and scoring

Approve criteria and weights before the decision workshop scores alternatives. The values below are an initial architectural assessment, **not measurements or a record of stakeholder consensus**. Scale: 1 = poor fit/high unresolved risk; 3 = adequate with material conditions; 5 = strong fit/low additional burden.

| Criterion | Weight | E1 | E2 | E3 | E4 |
|---|---:|---:|---:|---:|---:|
| Speed to useful AAOS evidence | 20% | 5 | 2 | 4 | 1 |
| Verifiable behavioral reuse | 25% | 1 | 4 | 5 | 4 |
| Readiness for the next target | 15% | 2 | 3 | 4 | 4 |
| Scope and schedule predictability | 15% | 4 | 2 | 4 | 1 |
| Maintainable integration boundaries | 10% | 1 | 4 | 5 | 4 |
| Testable security/offline responsibilities | 10% | 2 | 4 | 4 | 3 |
| Incremental effort/toolchain risk | 5% | 5 | 2 | 4 | 1 |
| **Weighted score / 100** | **100%** | **54** | **61** | **87** | **54** |

Calculation: sum of each percentage weight multiplied by the rating, divided by 5. For E3: (20x4 + 25x5 + 15x4 + 15x4 + 10x5 + 10x4 + 5x4) / 5 = 87.

### Why E3 leads in this assessment

E3 uses the stated AAOS implementation while making reuse demonstrable through the exact substitutions required by the revision. Its principal uncertainty is the cost of separating the existing code, not the absence of a starting runtime. A strong score does not establish that the PoC is buildable or that the target can host its language. [P1, sections 2-5]

### Sensitivity analysis

| Weighting scenario, in criterion order above | E1 | E2 | E3 | E4 |
|---|---:|---:|---:|---:|
| Delivery-heavy: 40/15/10/15/5/5/10 | 72 | 52 | 84 | 40 |
| Next-target-heavy: 10/25/30/10/10/10/5 | 46 | 64 | 87 | 63 |
| Demo-only stress case: 70/5/5/5/5/5/5 | 85 | 47 | 82 | 31 |

The recommendation is not universal: E1 overtakes E3 when immediate demo speed dominates. That choice would require management to reduce the reuse objective rather than claim the same result with less evidence.

### Reopen the decision when

Re-score after recovery if core extraction exceeds available capacity, the target cannot host the chosen core, the AAOS baseline cannot be accessed, or platform-native telemetry satisfies the required semantics with materially less custom code. Record dissent, changed assumptions and the sponsor's resolution.

<!-- PAGE -->
# 4. Entry conditions and open decisions

### Gate 0 - authorize work only with an executable starting point

The eight-week clock starts when the team has source/build access, an identified AAOS runtime, authorized vehicle-data access, test endpoints and named engineering capacity. An emulator is acceptable for a declared virtual-runtime PoC, but does not establish physical vehicle integration. Any access delay must be visible in the schedule.

| Decision / evidence required | Accountable role | Due |
|---|---|---|
| Reproduce the current build; identify language, modules, dependency versions, branch/tag and runtime image. | AAOS lead | Week 1 |
| Name the actual vehicle source, available properties, units, quality states and read permissions. | Vehicle/platform owner | Week 1 |
| Identify the target AAOS SDV release, execution environment and available service interfaces. | Target platform owner | Week 2 |
| Select the supported core language/hosting strategy; demonstrate a compile/link or hosting spike where access permits. | Architect | Gate A |
| Recover or approve canonical fields, required-signal set, three triggers and S1-S6 definitions. | Product/domain owner | Gate B |
| Approve cloud receipt boundary, queue policy and security test identity. | Cloud and security leads | Gate B |
| Confirm staffing, loaded rates, infrastructure access and recovery-adjusted estimate. | Sponsor / delivery lead | Gate A |

### Core implementation selection rule

Preserve the existing implementation language where it supports both the current runtime and the approved next-target hosting strategy. A pure JVM core may support host tests without proving it can run inside the intended SDV service environment. A native core also needs an approved ABI, toolchain and lifecycle binding; native code is not automatically portable.

Current SDV documentation includes Rust service generation and C++ business-logic integration guidance. Validate the chosen release and actual hosting path rather than inferring compatibility from the name "AAOS". [R5, R6]

When compatibility requires a language migration, complete the approved migration during recovery/stabilization or rebaseline the plan. Do not perform a later reimplementation and label it an unchanged-source port.

### Dependency register discipline

Every unknown has an owner, a due date, the evidence needed to close it and its effect on the next gate. An unresolved target may permit continued AAOS-only work through explicit risk acceptance, but it blocks an unconditional unchanged-source portability commitment.

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
# 12. Eight-week delivery baseline

### Planning principles

Preserve the source's weekly objectives, while starting semantic fixtures, security design and target compatibility earlier to remove late surprises. Formal security demonstration remains in week 7; mapping B and final reuse evidence remain due in week 8. [P1, section 8]

| Week | Primary outcome | Acceptance anchor |
|---|---|---|
| 1 | Build and behavior recovered; dependencies, permissions and target questions assigned. | Reproducible baseline and evidence inventory. |
| 2 | Architecture map, semantic fixtures, target hosting decision and revised estimate. | Gate A - recovery / continue decision. |
| 3 | Canonical contract, triggers, ports and deterministic runner. | Gate B; proposed S1-S2 pass on host. |
| 4 | Refactored AAOS path with MQTT through the owned port. | Runtime integration checkpoint; S3 MQTT. |
| 5 | HTTPS substitution and common receipt semantics. | S3 on both cloud paths; no core behavior change. |
| 6 | Durable bounded offline recovery and duplicate observation. | S4 on AAOS. |
| 7 | Bounded command acceptance/rejection and security evidence. | S5; no actuator path. |
| 8 | Full mapping/cloud matrix, frozen core and target-port package. | Gate C plus Gate D-Design; final evidence review. |

### Work-package allocation - planning estimate

| Work package | Window | Person-weeks |
|---|---|---:|
| WP1 - Current-state recovery and dependency analysis | W1-W2 | 4 |
| WP2 - Contract, semantic fixtures and host runner | W2-W3 | 3 |
| WP3 - Core extraction and AAOS integration | W3-W4 | 5 |
| WP4 - Cloud adapters and receipt comparison | W4-W5 | 3 |
| WP5 - Offline storage and fault recovery | W5-W6 | 4 |
| WP6 - Security and bounded configuration | W1-W7 | 3 |
| WP7 - Mapping B and final reuse evidence | W2-W8 | 4 |
| WP8 - Target package and delivery governance | W1-W8 | 2 |
| **Total, including cross-cutting work** | **8 weeks** | **28** |

Windows overlap; this is a total effort allocation, not eight independent teams. The delivery lead must load the backlog against named availability at Gate A.

### Critical path

Build/access -> architecture recovery -> approved semantics and hosting strategy -> portable core -> AAOS/MQTT -> cloud and offline proof -> full scenario matrix -> release evidence. Keep receiver preparation, mapping B fixtures, threat modeling and target analysis parallel where capacity permits.

<!-- PAGE -->
# 13. Detailed plan: weeks 1-2

### Week 1 - recover before redesigning

**Owners:** architect and AAOS engineer; vehicle owner, cloud engineer, QA and security specialist contribute.

1. Rebuild and run the existing PoC from a recorded commit on the named AAOS image. Record exact commands, prerequisites, package identity and runtime limitations.
2. Trace one vehicle observation through acquisition, normalization, eligibility, serialization, transport, storage and logging. Identify each library, thread, callback, permission and credential dependency involved.
3. Capture current behavior for normal input, unavailable data, one network failure and restart. Separate intended behavior from defects; characterization tests preserve evidence, not bugs as requirements.
4. Inventory all platform/provider types crossing into business logic. Classify each as core, adapter or platform responsibility and rank extraction risks.
5. Assign the target AAOS SDV release/hosting investigation. Start the test identity, threat model and receiver-access requests immediately.

**Artifacts:** reproducible baseline, current-state architecture, dependency/permission inventory, initial traces, defect list and open-decision register.

**Exit check:** the team can reproduce the baseline, or explicitly demonstrate and escalate why it cannot. Do not spend the second week silently compensating for unavailable access.

### Week 2 - establish the recoverable scope

**Owners:** architect and core engineer; QA owns fixture reproducibility; target owner owns hosting evidence.

1. Approve the proposed responsibility map and narrow port contracts. Plan extraction as small reversible changes rather than a big-bang rewrite.
2. Obtain actual signal definitions and create mapping A fixtures. Design mapping B fixtures containing at least one semantic mismatch, one unit conversion and one unavailable/stale case.
3. Recover the original S1-S6 and publish triggers, or circulate the proposed definitions in sections 7 and 17-18 for approval.
4. Run a target compatibility spike where access permits: build/link the candidate core or prove the approved hosting mechanism. Document unresolved runtime assumptions explicitly.
5. Compare native SDV telemetry capabilities with required Vehicle Status semantics; decide what to reuse behind adapters and what remains project-owned.
6. Re-estimate the backlog, staff loading, endpoint effort and physical test requirements. Approve initial resource budgets and demonstration scope.

**Gate A evidence:** signed architecture inventory, owned unknowns, target hosting disposition, tested baseline and revised estimate. Sponsor chooses continue, targeted extension or re-scope. Proposed tranche: 7 person-weeks over two weeks at the planning capacity.

<!-- PAGE -->
# 14. Detailed plan: weeks 3-4

### Week 3 - establish the contract and portable core

**Owners:** core engineer and architect; QA supplies deterministic oracles; domain owner approves semantics.

1. Approve the actual field set, required-signal policy, units, quality states, timestamps and semantic bases. Resolve SOC/odometer examples against available data rather than assume equivalence.
2. Freeze the three triggers, arbitration, configuration bounds, status identity and result vocabulary. Define whether the required data set can produce a degraded status or must be suppressed.
3. Introduce project-owned clocks, IDs, storage and sink contracts. Remove Android/OEM/provider types from the selected core paths.
4. Build the same core in the host runner with fake ports. Add boundary, missing-data, invalid-data, timing and retry tests; inject deterministic time and ID sequences.
5. Add dependency checks to CI and trace manifests with schema/profile/fixture versions. Execute proposed S1 and S2 using approved expected outputs.

**Gate B evidence:** approved contract and scenario definitions, dependency report, deterministic test results and unresolved decisions explicitly closed or deferred with a scope limitation. Approval freezes behavior; implementation refactoring can continue under regression control until the AAOS baseline is stabilized.

### Week 4 - reconnect the core to AAOS

**Owners:** AAOS engineer and core engineer; cloud engineer owns the MQTT binding.

1. Connect actual vehicle reads and lifecycle events to the approved ports. Preserve quality/timestamp semantics and verify required permissions.
2. Replace direct cloud calls in business logic with the MQTT adapter. Keep authentication, topics and provider serialization inside the adapter.
3. Connect the durable-store and credential interfaces, even where their complete scenario coverage arrives later. Prevent disk/network work on the vehicle callback path.
4. Exercise start, stop, reconnect, permission failure and process restart. Compare injected traces with the same host expectations while separately testing real interface acquisition.
5. Demonstrate S3 on MQTT, including receiver receipt and an unknown outcome. Record any behavioral differences and resolve them before substitution work.

**Checkpoint evidence:** AAOS integration uses the portable core; no forbidden dependencies remain; MQTT trace and receiver receipt correlate to the expected statusId; lifecycle errors are observable.

**Control:** keep the previous known-good integration tag available. Revert the integration change if the build cannot complete the agreed smoke test; do not bypass the core to keep the demo appearing successful.

<!-- PAGE -->
# 15. Detailed plan: weeks 5-6

### Week 5 - prove cloud replacement

**Owners:** cloud engineer and QA; core engineer reviews contract compliance.

1. Implement HTTPS serialization, authentication, timeout/error mapping and the declared receipt mechanism behind TelemetrySink.
2. Replay the same canonical fixtures through MQTT and HTTPS. Use the same controlled clock and IDs; capture the pre-provider envelope and decision trace.
3. Compare publish eligibility, envelope, statusId, correlation and equivalent acceptance stages. Do not require wire payloads or transport-specific acknowledgments to be identical.
4. Inject receiver timeout, rejection, TLS failure and duplicate/lost receipts. Verify classification and retry decisions without changing domain policy.
5. Record cloud/provider identities and capability differences, including the controlled-downlink path. Produce a source diff showing what changed for the swap.

**Exit evidence:** S3 passes for both adapters; no domain/application behavior change is needed; all provider mapping stays outside the core. A discovered missing abstraction requires review and re-running both paths, not an undocumented exception.

### Week 6 - demonstrate offline retention and restart

**Owners:** core engineer and AAOS engineer; QA owns fault injection.

1. Implement or stabilize atomic queue admission, immutable envelope persistence, capacity/byte accounting, retention and quarantine behavior.
2. Persist policy reference state and profile version consistently with queue admission. Define recovery of in-flight and partially acknowledged records.
3. Implement retry/backoff and rate-limited drain using project clocks. Add safe counters for enqueue, retry, receipt, overflow, expiry and permanent failure.
4. Run network loss followed by reconnect, and crash at the three send/receipt boundaries. Verify unchanged IDs and receiver-observed duplicates.
5. Exercise both capacity and byte limits, retention boundary, long server backoff, unavailable wall time and storage-write failure.
6. Measure physical storage overhead and choose an enforceable AAOS storage ceiling. Record CPU/memory and queue-drain observations on the named target.

**Exit evidence:** S4 passes on AAOS; the queue policy and loss behavior are declared; no record disappears without confirmation or a documented terminal reason. Remaining production durability work is listed separately from the tested PoC guarantees.

**Contingency:** prioritize correctness of the bounded queue over throughput optimization. Do not replace durable recovery with an in-memory demonstration while retaining a restart-persistence claim.

<!-- PAGE -->
# 16. Detailed plan: weeks 7-8

### Week 7 - close security and controlled configuration

**Owners:** security specialist and core engineer; AAOS/cloud engineers provide identity and transport integration; QA executes abuse cases.

1. Verify the selected trust chain and credential binding on the actual runtime. Record test-only limitations and remove debug trust bypasses.
2. Enforce the one-command allowlist, issuer/target authorization, schema limits, freshness, replay protection and range checks.
3. Persist accepted profile and replay/version state atomically. Demonstrate application of the new profile only to future status decisions.
4. Execute valid, invalid, expired, future-dated, unauthorized, wrong-target, replayed, malformed and out-of-range command cases, including replay after restart.
5. Send a vehicle-control message and confirm rejection before dispatch. Review write APIs, granted permissions and runtime call paths.
6. Inspect logs and exported traces for secrets or unnecessary identifiers. Exercise recovery/rollback of a faulty but valid profile through an approved support procedure.

**Exit evidence:** S5 passes, the security reviewer records disposition, and no-actuator-path evidence covers the actual component boundary.

### Week 8 - complete reuse evidence and the next-port package

**Owners:** architect, QA and delivery lead; all implementation owners sign their evidence.

1. Complete mapping/provider B against the already-approved fixtures. Do not redesign the canonical model simply to make B pass.
2. Run the positive and negative S1-S6 cases on the AAOS baseline across mapping A/B and MQTT/HTTPS where applicable. Record virtual, injected and physical evidence separately.
3. Freeze core paths, schema, profiles, fixtures, adapter versions and the release tag. Produce source diffs and evidence manifests for each substitution.
4. Rehearse the OEM/management demonstration from a clean reset. Show original coupling, the recovered boundary, replacements, outage recovery and command rejections.
5. Complete the target lifecycle/service/permission/packaging gap matrix with owner, effort band and test obligation for each gap.
6. Review all deviations, resource measurements, unresolved defects and permitted claims. Publish the follow-on backlog and formal decision record.

**Exit evidence:** Gate C passes for the AAOS MVP. Gate D-Design can pass for the target package. Full Gate D-Runtime remains a separate acceptance event unless actual target execution and all required evidence exist.

**Release discipline:** a missing mandatory scenario cannot be renamed a limitation and counted as a full pass. The sponsor may accept a reduced-scope demonstration, but the release and claims must state that reduced scope.

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

### Preserve the original gates; distinguish design from runtime

| Gate | Required evidence and pass condition | Accountable approver |
|---|---|---|
| Gate 0 - proposed entry gate | Access, runtime, endpoints, authorized data and named capacity are available; limitations are declared. | Sponsor / delivery lead |
| Gate A - architecture recovery | Reproducible PoC; current boundaries, platform/cloud/security/storage dependencies and unknowns documented; target hosting disposition and revised estimate reviewed. | Architect + sponsor |
| Gate B - portable core | Approved semantics, triggers, bounds and scenario catalogue; no forbidden core dependencies; S1-S2 deterministic tests pass. | Domain owner + architect + QA |
| Gate C - AAOS MVP | Owned boundaries used on AAOS; two mappings and two cloud paths demonstrated; S1-S6 pass; offline/security evidence complete. | Engineering lead + QA + security |
| Gate D-Design - proposed checkpoint | Target version/hosting and lifecycle/IPC/permission/packaging gaps documented; executable port backlog and test mapping approved. | Target owner + architect |
| Gate D-Runtime - full portability gate | Actual named target executes the same contract/scenarios; behavior unchanged; core source unchanged except approved fixes; claim matches runtime evidence. | Target owner + QA + architect |

Gate D-Design is not a substitute for the source's platform-portability proof. The source's week-8 output is a porting package, not an automatic runtime pass. [P1, sections 7-8]

### Release measures

Mandatory scenario cases: **100% pass in their declared applicable environments**. Forbidden core dependencies: **zero**. Unreviewed post-freeze core changes: **zero**. Accepted unsafe commands and actuator calls: **zero**. Undeclared queue loss in fault tests: **zero**.

For the demonstrator, propose a 120-record outage fixture and a recovery target of at most 120 seconds after link/receiver readiness, with no server throttling. Approve or adjust the target at Gate A. Report measured CPU, memory, disk overhead and runtime latency against platform-approved budgets rather than unverified production expectations.

### Evidence bundle

For every run, record commit/tag, core path hashes, build/image identifiers, adapter versions, schema/profile versions, fixture hashes, test surface, clock/ID seed, expected/actual traces, receipt evidence, resource results and deviations. A reproducible runbook must recreate the scenario from a clean reset.

QA owns result integrity. Developers supply evidence; accountable reviewers approve the gate. Record PASS, FAIL or NOT RUN explicitly. A missing mandatory result blocks full acceptance; a scope concession changes the release claim rather than converting NOT RUN to PASS.

<!-- PAGE -->
# 20. Staffing, cost and governance

### Proposed capacity model

| Role | Average allocation | Eight-week effort |
|---|---:|---:|
| Portable core engineer | 1.00 FTE | 8 person-weeks |
| AAOS / vehicle integration engineer | 1.00 FTE | 8 person-weeks |
| Cloud / backend engineer | 0.50 FTE | 4 person-weeks |
| QA / automation engineer | 0.50 FTE | 4 person-weeks |
| Architect / technical lead | 0.25 FTE | 2 person-weeks |
| Security specialist | 0.125 FTE | 1 person-week |
| Delivery lead | 0.125 FTE | 1 person-week |
| **Total** | **3.50 FTE** | **28 person-weeks** |

Allocations are role capacity, not assumed people already assigned. One person may fill multiple roles only within their real availability. Specialists contribute earlier than their formal acceptance week. The vehicle and target-platform owners must also provide timely interface/access decisions.

### Funding request and assumptions

At 40 hours per person-week, base effort is **1,120 hours**. Proposed 20% reserve is **224 hours**, for a maximum planning envelope of **1,344 hours**. Price using approved loaded rates by role; no salary, hardware or cloud prices are assumed.

**Budget = sum(role hours x approved loaded hourly rate) + approved infrastructure costs + released contingency.** Obtain quotes for any missing AAOS target, CI capacity, test endpoints, certificates or target-environment access. Existing hardware and a working PoC are assumptions to validate, not free assets to presume.

A reserve is not automatically time inside the eight-week plan. Consuming the full reserve requires approximately **0.7 additional average FTE** for the same duration, or approximately **1.6 additional weeks** at 3.5 FTE, subject to the critical path. With only two FTE, the same base effort implies at least 14 calendar weeks before sequencing constraints.

### Governance and decision rights

The sponsor owns scope and funding. The architect owns boundaries and portability exceptions. The domain owner approves meaning and triggers. Security approves identity/downlink constraints. QA owns scenario oracles and evidence completeness. The target owner approves target interfaces and runtime claims.

Hold a weekly evidence/risk review and formal reviews at Gates A, B and C. Any proposed core exception after freeze records rationale, changed paths, semantic impact, regression results and approvers. Any change to the three triggers, canonical meaning or claim matrix requires domain/architecture review, not an adapter-only ticket.

<!-- PAGE -->
# 21. Risk register and scope control

### Initial assessment - validate during recovery

Ratings are qualitative planning judgments. H = high priority; M = medium priority. Owners must update likelihood, impact and response after actual evidence arrives.

| ID / priority | Risk and trigger | Response / owner |
|---|---|---|
| R01 / H | PoC cannot be rebuilt or required access is absent in week 1. | Escalate immediately; pause the clock or approve a bounded recovery extension. AAOS lead. |
| R02 / H | Core language/runtime cannot be hosted on the named SDV target. | Resolve before implementation freeze; approve migration during stabilization or change the port commitment. Architect. |
| R03 / H | Required vehicle permissions/signals are unavailable. | Agree an authorized read path; injected data is labeled and cannot substitute for acquisition proof. Vehicle owner. |
| R04 / H | Two mappings contain incompatible business meanings. | Obtain authoritative definitions; reject unsupported semantics rather than force equality. Domain owner. |
| R05 / H | Receipt ambiguity causes premature queue deletion or false success. | Separate transport and application stages; run lost-receipt/crash tests. Cloud lead. |
| R06 / H | Command replay, wrong-target update or hidden write privilege exists. | Durable replay/version state, narrow authorization and no-actuator review. Security lead. |
| R07 / H | Recovery exceeds the approved extraction budget. | Re-estimate at Gate A; defer nonessential cleanup, not acceptance behavior. Delivery lead. |
| R08 / M | Queue growth, disk-full behavior or clock reset breaks recovery. | Bound records/bytes; measure physical storage; test reboot and unknown time. Core lead. |
| R09 / M | Host simulation passes while AAOS lifecycle fails. | Separate host, injected and actual-interface results; require runtime tests. QA lead. |
| R10 / M | Custom hub duplicates available platform telemetry. | Complete a capability fit-gap; reuse suitable components behind stable contracts. Architect. |
| R11 / M | Late mapping B or endpoint access invalidates the demo. | Start fixtures and endpoint requests in week 2; review weekly. Vehicle/cloud leads. |
| R12 / M | Demo language exceeds validated platform/provider scope. | Approve a claim matrix and use it in slides, runbook and release notes. Sponsor + QA. |

### Contingency order

First defer production hardening, broad abstractions, extra signals, performance optimization and unrequired UI polish. Next use the sponsor-controlled reserve or extend the calendar. Do not weaken semantics, remove safety rejections, silently drop a cloud/mapping proof or turn the host runner into a second product. [P1, section 10]

Preserve the prior AAOS tag and configuration snapshot for integration rollback. Stop outbound publication before reverting to avoid two active publishers. Retain safe traces and queue state under the declared retention policy so failures remain diagnosable.

<!-- PAGE -->
# 22. AAOS SDV porting package

### Required target definition

Record the exact target release/build, VM or device, supported core language/toolchain, service ownership, vehicle-data producer and access policy. Current SDV service bundles have their own lifecycle and authorization model and are packaged in APEX-based SDV packages; this is not assumed to be an unchanged APK deployment. [R4, R5]

| Integration topic | Week-8 design deliverable | Later runtime proof |
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

**P1:** establish target build/hosting and minimal adapter. **P2:** bind real lifecycle, data, identity and persistence. **P3:** run the same S1-S6, fault/resource tests and change audit. Estimate these work packages after Gate A/target access; week 8 does not imply a funded or completed runtime port.

### Claim progression

Host evidence permits deterministic-behavior claims. The refactored AAOS result permits the demonstrated runtime and reuse claims. The porting package permits design-readiness claims. Only Gate D-Runtime permits support claims for the actual tested AAOS SDV configuration. QNX, Bosch SdV.OS, universal binary portability and production compliance remain outside the validated scope. [P1, sections 6, 11]

<!-- PAGE -->
# 23. Management discussion and decision record

### Proposed opening statement

> We propose an AAOS-first, eight-week MVP to turn the existing Vehicle Status PoC into a reusable capability. We will demonstrate reuse with two vehicle mappings and two cloud paths, supported by deterministic tests and AAOS runtime evidence. We request approval for a two-week recovery tranche first, followed by a gate-based release of the remaining work. The output includes an AAOS SDV porting package, not a claim that the next-platform runtime is already validated.

### Questions to settle in the approval meeting

| Management question | Recommended position |
|---|---|
| Why not continue the PoC without refactoring? | That can optimize immediate demo speed, but does not meet the agreed reuse proof. Approve it only with a reduced objective. |
| Why not build Linux first? | It adds a deployment baseline the revision explicitly removes. The host runner is enough for deterministic core evidence. |
| What is the main early risk? | The actual extraction cost and whether the chosen core can be hosted on the named AAOS SDV target. Resolve both at Gate A. |
| What will we show after eight weeks? | A traceable AAOS demonstration, substitutions, offline and command tests, frozen core/contract and the next-port design backlog. |
| How much should we authorize now? | The proposed recovery tranche is 7 person-weeks; the full planning baseline is 28, with controlled contingency. |
| What must not be advertised? | Exactly-once transport, production compliance, physical/OEM validation or next-platform runtime support not evidenced by the tests. |

### Approval record - complete in the meeting

| Decision field | Record |
|---|---|
| Sponsor / decision authority | Name and role: ____________________ |
| Decision | Approve E3 / approve with conditions / defer / select another alternative |
| Recovery tranche and start conditions | Approved capacity, spending cap and Gate 0 evidence: ____________________ |
| Gate A review date | ____________________ |
| Full-plan capacity / funding | Approved roles, rates and contingency authority: ____________________ |
| Conditions, dissent and accepted risks | ____________________ |
| Required claims and excluded claims | Approved claim-matrix version: ____________________ |
| Sign-off | Sponsor / architect / domain / QA / security / target owner, with dates |

### First action after approval

Schedule a baseline-reproduction session with the AAOS, core and QA owners. Start from the exact current commit and runtime image, capture one end-to-end status trace, and open the architecture/dependency register before making structural changes.

<!-- PAGE -->
# References and traceability

### Planning source

**[P1]** *AAOS-First Revision for the SDV Telematics Vehicle Status MVP Plan.* Supplied file: SDV_Telematics_Vehicle_Status_AAOS_First_Plan_Revision_EN.md. The source defines the AAOS-first baseline, host-only test role, reuse proof, Gates A-D, eight-week sequence and claim limits.

| Source area | Where it is implemented in this DAR |
|---|---|
| Sections 1-4: runtime baseline and guardrails | Executive decision; DAR sections 2, 4-5 and 11. |
| Section 5: vehicle/cloud/platform reuse | DAR sections 6, 8, 17-18 and 22. |
| Sections 6-7: claims and acceptance gates | DAR sections 19 and 22. |
| Section 8: eight-week plan | DAR sections 12-16. |
| Sections 9-12: demo, scope and success | DAR sections 18-19 and 21-23. |

**Proposal register:** E1-E4, scores/weights, staffing/cost model, added entry/design checkpoints, schema details, trigger definitions, numerical limits, receipt design and S1-S6 operational definitions are proposed additions requiring the indicated approvals. They are not represented as approved source requirements or completed results.

### External technical references

Official sources checked on 8 September 2026. Apply documentation to the selected platform release; current documentation alone does not establish compatibility with the PoC.

[R1] CMMI Institute / ISACA. *July 2013 Quality Tip - Decision Analysis and Resolution.* Decision criteria and transparent rationale.

[R2] Android Developers. *CarPropertyManager API reference.* Application-facing vehicle-property access.

[R3] Android Open Source Project. *SDV architecture.* Relationship to AAOS IVI and platform telemetry.

[R4] Android Open Source Project. *Logical architecture.* SDV topics/channels, service bundles, authorization and deployment.

[R5] Android Open Source Project. *Quick start: Create and execute SDV service bundles.* Target build, generated services and packaging.

[R6] Android Open Source Project. *Implement business logic.* Rust and C++ service implementation guidance.

[R7] Android Developers. *CarPropertyValue API reference.* Availability and timestamp semantics.

[R8] OASIS. *MQTT Version 5.0*, section 4.3.2. QoS 1 delivery and acknowledgment semantics. Verify the actual MQTT version used by the PoC.

[R9] IETF. *RFC 9110: HTTP Semantics*, section 15.3.3. Meaning of HTTP 202 Accepted.

[R10] Android Developers. *Android Keystore system.* Key restrictions and device-dependent secure hardware support.

[R11] Android Open Source Project. *Vehicle HAL overview.* VHAL layering and AIDL/HIDL generation differences.

**Abbreviations:** AAOS - Android Automotive OS; SDV - software-defined vehicle; DAR - Decision Analysis and Resolution; PoC - proof of concept; SOC - state of charge; FTE - full-time equivalent; VHAL - Vehicle Hardware Abstraction Layer.
