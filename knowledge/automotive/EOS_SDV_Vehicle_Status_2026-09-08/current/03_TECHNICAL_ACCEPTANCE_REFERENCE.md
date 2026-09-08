---
document_id: EOS-SDV-VS-TECHNICAL-REFERENCE-2026-09-08
project_id: DAR-SDV-VS-001
as_of: 2026-09-08
record_type: attributed_technical_excerpts
status: retained_design_proposals_not_test_results
---

# Retained technical detail and acceptance proposals

These excerpts preserve the detailed v1.0 design retained by the current approval report. They do not restore the old fixed schedule or staffing presentation. **All numerical defaults, schema details, trigger definitions and scenario operationalizations retain their proposed status. No implementation or test has been verified in this archival task.**

Source: `../history/v1_0/SDV_Vehicle_Status_DAR_EN_v1_0_One_Senior_One_Junior.md` (P10). The current business request is P12 and the live planning authority is W12. References such as [R7] are the original reference IDs, resolved below; they are not fresh web verification. Original source line ranges are recorded for traceability.

**Excerpt source:** P10, original lines 298-327. **Status:** retained design proposal; approval and validation pending.

## 5. Target architecture and ownership

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

**Excerpt source:** P10, original lines 328-359. **Status:** retained design proposal; approval and validation pending.

## 6. Canonical Vehicle Status contract

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

**Excerpt source:** P10, original lines 360-392. **Status:** retained design proposal; approval and validation pending.

## 7. Publish policy and bounded configuration

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

**Excerpt source:** P10, original lines 393-423. **Status:** retained design proposal; approval and validation pending.

## 8. Cloud adapters and delivery semantics

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

**Excerpt source:** P10, original lines 424-453. **Status:** retained design proposal; approval and validation pending.

## 9. Offline retention and recovery

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

**Excerpt source:** P10, original lines 454-483. **Status:** retained design proposal; approval and validation pending.

## 10. Security and controlled downlink

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

**Excerpt source:** P10, original lines 484-514. **Status:** retained design proposal; approval and validation pending.

## 11. AAOS runtime integration

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

**Excerpt source:** P10, original lines 658-694. **Status:** retained design proposal; approval and validation pending.

## 17. Golden scenarios: S1-S3

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

**Excerpt source:** P10, original lines 695-727. **Status:** retained design proposal; approval and validation pending.

## 18. Golden scenarios: S4-S6

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

## Original reference definitions

External references below are copied from P10 for attribution. Availability, document versions and technical claims must be checked for the actual selected environment; the archive does not update them.

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

P1 means the original AAOS-first source in `../source/`. P10 means the preserved v1.0 DAR. For current resource, business and approval assumptions use P12 and W12.
