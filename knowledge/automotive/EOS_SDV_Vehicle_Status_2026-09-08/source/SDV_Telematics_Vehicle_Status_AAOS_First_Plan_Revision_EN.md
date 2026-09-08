# AAOS-First Revision for the SDV Telematics Vehicle Status MVP Plan

## Document Purpose

This revision changes the MVP execution strategy from a **Linux-first runtime baseline** to an **AAOS-first runtime baseline**.

The existing AAOS PoC becomes the starting implementation and the primary runtime baseline. A host-executable environment is retained only as a deterministic behavioral test harness for continuous integration and golden-scenario validation. It is not treated as a product deployment target.

The revised plan preserves the original architectural objective:

> Demonstrate a reusable Vehicle Status capability whose domain and application behavior remain stable while vehicle mappings, cloud adapters, and platform integrations are replaced.

---

## 1. Revised Planning Decision

### 1.1 Decision

Use the existing AAOS PoC as:

- The starting implementation.
- The primary runtime baseline for the MVP.
- The source from which the current architecture and dependencies must be recovered.
- The integration environment in which the reusable Vehicle Status capability is stabilized and demonstrated.

Use a host-executable deterministic test runner only for:

- Canonical input traces.
- Domain validation.
- Publish-policy behavior.
- Bounded configuration decisions.
- Retry and outcome normalization.
- Repeatable golden-scenario execution in CI.

The host environment is not a product platform claim and is not a separate Linux deployment baseline.

### 1.2 Revised baseline model

| Concern | Revised decision |
|---|---|
| Primary runtime baseline | Existing AAOS PoC, recovered and refactored into explicit boundaries |
| Portable core test environment | Host-executable deterministic behavioral test runner |
| First vehicle integration | AAOS vehicle-data integration and mapping profile A |
| Replacement vehicle proof | Controlled mapping profile or vehicle-data provider B |
| Primary cloud path | MQTT over TLS |
| Replacement cloud path | HTTPS over TLS |
| Next platform target | AAOS SDV |
| Linux product deployment | Removed from the MVP baseline |

---

## 2. Rationale for the AAOS-First Approach

### 2.1 It uses the existing implementation as project evidence

An AAOS PoC already exists. The immediate architectural gap is not the absence of an implementation, but the lack of a documented separation between:

- Domain and application behavior.
- Android or AAOS platform dependencies.
- Vehicle-data acquisition and mapping.
- Cloud protocol and provider binding.
- Security and credential integration.
- Offline storage behavior.
- Lifecycle, IPC, permissions, packaging, and observability.

Starting with architecture recovery avoids creating a separate Linux integration before understanding the technical debt and coupling in the existing AAOS implementation.

### 2.2 It exposes abstraction leaks earlier

An AAOS-first recovery can reveal whether the current business flow directly depends on:

- Android service lifecycle.
- Binder or Android framework types.
- VHAL or vehicle-service types.
- Android permissions.
- Android-specific storage paths.
- Platform credential APIs.
- MQTT or cloud SDK types.
- Provider-specific payloads and errors.

These dependencies must not remain inside the portable core.

### 2.3 It provides a clearer transition story

The revised transition is:

```text
Existing AAOS PoC
        |
        v
Recover architecture and dependencies
        |
        v
Separate portable Vehicle Status behavior
        |
        +--> AAOS vehicle/platform adapter
        |
        +--> MQTT cloud adapter
        |
        +--> HTTPS replacement adapter
        |
        v
Validate golden scenarios on AAOS
        |
        v
Port the same core and scenarios to AAOS SDV
```

This creates a direct relationship between the current implementation, the reusable architecture, and the next target platform.

---

## 3. Architectural Guardrails

### 3.1 AAOS-first must not become Android-first architecture

AAOS is the first runtime baseline, but it must not define the reusable core.

The dependency direction remains:

```text
AAOS platform adapter
        |
        v
Project-owned platform ports
        |
        v
Portable Vehicle Status core
        ^
        |
Project-owned vehicle, cloud, security, and offline ports
```

The portable core must not know that it currently runs on AAOS.

### 3.2 The existing AAOS PoC is not automatically reuse evidence

The existing implementation is the starting point, not proof of portability.

It may be considered reusable architecture evidence only after:

- Its current boundaries are documented.
- Platform and provider dependencies are identified.
- Domain behavior is separated from integration behavior.
- Canonical semantics are frozen.
- Golden scenarios validate the resulting behavior.

### 3.3 Core changes are allowed during architecture recovery

The original requirement that domain and application core source changes equal zero should not be applied during the initial recovery phase.

Changes may be necessary to:

- Remove Android dependencies from business logic.
- Establish a canonical Vehicle Status contract.
- Separate cloud mapping from application behavior.
- Introduce project-owned capability boundaries.
- Normalize cloud outcomes.
- Make offline and security responsibilities explicit.
- Establish deterministic behavioral tests.

After the AAOS baseline has been stabilized, the portability gate becomes stricter.

### 3.4 Portability gate after stabilization

For the subsequent AAOS-to-AAOS-SDV port:

- Domain and application behavior changes must equal zero.
- Domain and application core source changes should equal zero.
- Any exceptional portability fix must be explicitly reviewed and approved.
- The canonical contract must remain unchanged unless a governed contract change is intentionally approved.
- The same golden scenarios must be reused.

---

## 4. Revised Architecture Baseline

```text
                         Golden Input Traces
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
        Host Behavioral Test Runner       AAOS Integration
        CI and test evidence only                 |
                                           AAOS Vehicle Adapter
                                                   |
                                                   v
                                      Portable Vehicle Status Core
                                                   |
                             +---------------------+------------------+
                             |                     |                  |
                             v                     v                  v
                      MQTT Adapter          HTTPS Adapter      Offline/Security
                             |                     |
                             v                     v
                         Cloud A               Cloud B
```

### 4.1 Role of the host test runner

The host runner provides repeatability without becoming a deployment claim.

It validates:

- Canonical input and output traces.
- Validation rules.
- Publish eligibility.
- Correlation behavior.
- Bounded configuration decisions.
- Normalized outcomes.
- Golden-scenario equivalence.

It does not require:

- A Linux vehicle integration.
- Linux service packaging.
- A Linux-specific cloud deployment.
- A Linux runtime demonstration.
- A claim of Linux product support.

---

## 5. Revised Reuse Proof

### 5.1 Vehicle-side replacement proof

Replace the original Linux Simulator A and Simulator B runtime story with an AAOS-centered proof.

```text
AAOS Vehicle Source / Mapping A
          |
          v
Canonical VehicleStatus

Controlled Mapping or Provider B
          |
          v
Same Canonical VehicleStatus
```

Mapping B may be implemented as:

- A deterministic injected vehicle-data provider.
- A controlled alternate AAOS vehicle adapter.
- A test mapping profile representing a second OEM vocabulary.

The proof must include semantic differences, not only renamed fields. Examples include:

- Raw versus filtered SOC.
- Usable versus absolute SOC.
- Estimated versus authoritative odometer.
- Missing, stale, invalid, or delayed values.
- Unit conversion and precision differences.

### 5.2 Cloud-side replacement proof

The cloud replacement proof remains unchanged in principle:

```text
Same Portable Core
       |
       +--> MQTT/TLS --> Cloud A
       |
       +--> HTTPS/TLS --> Cloud B
```

For the same canonical input, both paths must preserve:

- The pre-provider canonical envelope.
- Publish eligibility.
- The status identifier.
- Correlation behavior.
- Normalized outcome semantics.

Protocol capability differences must remain visible. For example, MQTT subscription behavior must not be falsely generalized as an HTTPS capability.

### 5.3 Platform transition proof

```text
AAOS
  |
  +--> Recover and separate architecture
  |
  +--> Stabilize portable core
  |
  +--> Freeze canonical contract and behavior
  |
  v
AAOS SDV
  |
  +--> Replace platform binding
  +--> Reuse the same core
  +--> Reuse the same contract
  +--> Reuse the same golden scenarios
```

This transition becomes the primary platform-portability proof.

---

## 6. Revised Claim Matrix

| Environment | Revised status | Permitted claim |
|---|---|---|
| Host behavioral test runner | CI and test utility | Deterministic core-behavior evidence only |
| Existing AAOS PoC | Starting implementation | Implementation evidence; no portability claim before recovery |
| Refactored AAOS baseline | Required MVP runtime baseline | Runtime PoC and behavioral reuse evidence |
| AAOS SDV | Next porting target | Design target until runtime evidence exists |
| Embedded Linux | Optional future target | No MVP baseline claim |
| QNX | Architectural target | Adapter concept only |
| Bosch SdV.OS | Architectural target | Platform-adapter concept only |

---

## 7. Revised Acceptance Gates

### Gate A: AAOS architecture recovery

The gate passes when:

- The current AAOS service or application boundary is documented.
- Vehicle-data acquisition and mapping are identified.
- Android lifecycle and IPC dependencies are identified.
- Permissions and credential access are documented.
- Cloud and protocol coupling are documented.
- Persistence and observability responsibilities are documented.
- Unknowns are recorded instead of inferred.

### Gate B: Portable core establishment

The gate passes when:

- Canonical Vehicle Status semantics are approved.
- OEM vocabulary is absent from the core.
- Android framework types are absent from the core.
- Provider-specific payloads and SDK types are absent from the core.
- The three publish triggers are frozen.
- Bounded configuration rules are frozen.
- Cloud outcomes are normalized.
- Deterministic behavioral scenarios pass.

### Gate C: AAOS runtime baseline

The gate passes when:

- The refactored AAOS integration uses explicit project-owned boundaries.
- AAOS vehicle and platform dependencies remain in adapters.
- MQTT publication works through the cloud port.
- Offline and security responsibilities are explicit.
- Golden scenarios S1 through S6 pass on the AAOS-centered architecture.

### Gate D: AAOS-to-AAOS-SDV portability proof

The gate passes when:

- The AAOS SDV lifecycle and service boundary are documented.
- Vehicle-data access and IPC are mapped to approved AAOS SDV interfaces.
- Permissions, packaging, update, resources, and observability gaps are listed.
- Platform-specific dependencies remain isolated.
- The portable core is unchanged, except for explicitly approved portability fixes.
- The same canonical contract and golden scenarios are reused.
- The validation claim matches the available evidence.

---

## 8. Revised Eight-Week MVP Plan

### Weeks 1-2: Recover the existing AAOS architecture

#### Focus

- Inventory the existing AAOS implementation.
- Identify the current service or application boundary.
- Identify the vehicle-data source.
- Identify Android lifecycle, IPC, and permission dependencies.
- Identify cloud SDK and protocol coupling.
- Identify persistence, credentials, and logging dependencies.
- Capture current observable behavior.
- Record unknowns and design gaps.

#### Exit evidence

- AAOS current-state architecture map.
- Dependency inventory.
- Core, adapter, and platform classification.
- Known-unknown list.
- Initial golden input and outcome traces.

### Week 3: Establish the canonical contract and portable core boundary

#### Focus

- Freeze Vehicle Status business meaning.
- Remove OEM signal vocabulary from the core.
- Remove Android types from the canonical model.
- Freeze the three publish triggers.
- Freeze bounded configuration rules.
- Define normalized cloud outcomes.
- Establish the deterministic behavioral test runner.

#### Exit evidence

- Canonical contract approved.
- Core dependency rule verified.
- Golden scenarios S1 and S2 pass in deterministic behavioral tests.

### Week 4: Rebuild the AAOS integration around explicit boundaries

#### Focus

- Introduce or stabilize the AAOS vehicle adapter.
- Introduce the AAOS lifecycle and platform adapter.
- Separate permission and credential responsibilities.
- Map AAOS observability into project-owned boundaries.
- Route the existing MQTT integration through the cloud port.

#### Exit evidence

- AAOS runtime path uses the portable core.
- Android and framework types are absent from the core.
- MQTT baseline for S3 passes.

### Week 5: Prove cloud replacement

#### Focus

- Add the HTTPS replacement adapter.
- Keep provider mapping outside the core.
- Compare the canonical envelope, status ID, and publish decision.
- Document MQTT and HTTPS capability differences.

#### Exit evidence

- S3 passes for MQTT and HTTPS.
- Core behavior remains unchanged when the cloud path is replaced.

### Week 6: Demonstrate offline retention and recovery

#### Focus

- Add or stabilize the bounded offline queue.
- Preserve a stable status identifier across retry.
- Define retry and backoff behavior.
- Demonstrate reconnect recovery.
- Make duplicate behavior observable.

#### Exit evidence

- S4 passes on AAOS.
- Queue capacity, retention, overflow, and retry policy are declared.

### Week 7: Demonstrate the security boundary and controlled downlink

#### Focus

- Demonstrate the selected TLS and test-credential binding.
- Implement or validate the TELEMETRY_PROFILE_UPDATE allowlist.
- Validate authorization, freshness, replay, schema, and range conditions.
- Produce audit-safe rejection evidence.
- Confirm that no actuator path exists.

#### Exit evidence

- S5 passes.
- Invalid, expired, replayed, unauthorized, out-of-range, and vehicle-control messages are rejected with observable reasons.

### Week 8: Complete the reuse proof and AAOS SDV porting package

#### Focus

- Complete mapping or provider B.
- Run S1 through S6 on the AAOS baseline.
- Freeze the portable core baseline.
- Define the AAOS SDV lifecycle, service, IPC, permission, and packaging mapping.
- Produce the AAOS-to-AAOS-SDV gap matrix.
- Prepare the OEM demonstration and evidence package.

#### Exit evidence

- S1 through S6 pass on the validated AAOS baseline.
- Two vehicle mappings are demonstrated.
- Two cloud adapters are demonstrated.
- The AAOS architecture is documented.
- The portable core baseline is frozen.
- The AAOS SDV porting design and backlog are complete.
- No AAOS SDV runtime-support claim is made without runtime evidence.

---

## 9. Revised OEM Demonstration Story

### Demo 1: Existing AAOS implementation and recovered boundary

Show:

- The original AAOS implementation.
- The identified platform dependencies.
- The separation into core, vehicle adapter, cloud adapter, offline, security, and AAOS platform responsibilities.

### Demo 2: Vehicle mapping replacement

Show:

- AAOS vehicle mapping A producing canonical Vehicle Status.
- Controlled mapping B producing the same canonical Vehicle Status.
- Equivalent validation and publish decisions.

### Demo 3: Primary cloud publication

Show:

- Canonical Vehicle Status through MQTT Cloud A.
- Status identifier.
- Publish-policy decision.
- Normalized outcome.
- Provider mapping outside the core.

### Demo 4: Cloud replacement

Show:

- The same core through HTTPS Cloud B.
- The same canonical envelope before provider mapping.
- The same publish decision and correlation behavior.
- Explicitly documented protocol differences.

### Demo 5: Network loss and recovery

Show:

- Valid status creation while disconnected.
- Retention in a bounded queue.
- Reconnect and resend behavior.
- Stable identifier.
- Observable duplicate handling or limitation.

### Demo 6: Controlled configuration

Show:

- One accepted telemetry-profile update.
- Rejection of invalid, expired, replayed, unauthorized, and out-of-range updates.
- Rejection of a vehicle-control message.
- Confirmation that no actuator path exists.

### Demo 7: AAOS-to-AAOS-SDV transition evidence

Show:

```text
Existing AAOS implementation
        |
        v
Recovered responsibilities and dependencies
        |
        v
Stabilized portable core and AAOS adapters
        |
        v
AAOS SDV lifecycle and service-boundary design
        |
        v
Same core, contract, and golden scenarios for the next port
```

The demonstration must distinguish a documented AAOS SDV porting design from a completed AAOS SDV runtime result.

---

## 10. Revised Scope-Control Rule

If AAOS platform cleanup, production PKI integration, production persistence, or AAOS SDV runtime integration threatens the MVP scope:

- Move production hardening work to the backlog.
- Preserve the behavioral acceptance criteria.
- Do not weaken the canonical contract or golden scenarios.
- Do not claim platform validation without evidence.
- Do not turn the Vehicle Status capability into a generic vehicle gateway.

The host test runner must remain lightweight and focused on deterministic behavior. It must not evolve into a second product implementation.

---

## 11. Revised Final Decision

Adopt **Option C: Hardware-Agnostic Telematics Hub** for the MVP PoC.

Use the existing AAOS implementation as the starting point and AAOS as the primary runtime baseline. Recover and document the current architecture, separate the portable Vehicle Status behavior behind project-owned boundaries, and validate it through deterministic golden scenarios.

Retain a host-executable test harness only for repeatable behavioral verification and CI. Do not treat it as a Linux product deployment baseline.

Prove reuse through:

- Two vehicle mappings.
- One portable Vehicle Status behavior.
- MQTT Cloud A as the primary cloud path.
- HTTPS Cloud B as the replacement cloud path.
- Bounded offline recovery.
- One bounded telemetry configuration message.
- Golden scenarios S1 through S6.
- Explicit separation of AAOS platform dependencies.

Use the stabilized AAOS baseline, unchanged portable core, canonical contract, and the same golden scenarios as the starting evidence for the subsequent AAOS SDV port.

Do not claim:

- Universal binary portability.
- Linux as the MVP product baseline.
- Completed AAOS SDV runtime support before runtime evidence exists.
- Exactly-once transport.
- Production compliance.
- Production-grade PKI or HSM behavior.
- QNX or Bosch SdV.OS runtime support without validation.

---

## 12. Revised Architecture Success Statement

The revised MVP succeeds when the existing AAOS implementation has been recovered into explicit architectural boundaries, two vehicle mappings and two cloud paths use the same portable Vehicle Status behavior, and golden scenarios S1 through S6 pass on the AAOS-centered architecture.

The host environment provides deterministic behavioral evidence only. It is not a deployment baseline.

The resulting AAOS baseline must provide a stable portable core, canonical contract, and reusable golden scenarios for the next AAOS SDV port without requiring a redesign of the domain or cloud architecture.
