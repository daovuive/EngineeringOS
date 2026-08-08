# Telematics in Software-Defined Vehicles (SDV)
## Research Note & Architecture Decision Workbook

**Purpose:** Nghiên cứu vai trò của Telematics trong SDV.OS / SDV.Suite và chuẩn bị cho các Architecture Decision (ADR).  
**Language:** Vietnamese with English technical terminology.  
**Context:** Bosch SDV ecosystem, COVESA, Eclipse SDV, AUTOSAR, telematics runtime, vehicle data, cloud connectivity.

---

# 1. Executive Summary

Telematics trong SDV không còn nên được xem chỉ là một **TCU (Telematics Control Unit)** gồm modem + GPS + CAN parser.

Trong kiến trúc SDV hiện đại, Telematics có xu hướng trở thành một **cross-layer software service plane** kết nối:

- Vehicle data
- Vehicle applications
- Diagnostics
- Connectivity
- Security
- OTA
- Edge processing
- Cloud services
- Fleet management
- Observability

Telematics có liên hệ với cả:

- **SDV.OS**: phần runtime chạy trên vehicle / CCU / HPC / TCU.
- **SDV.Suite**: phần toolchain để develop, configure, simulate, validate, deploy và operate telematics functions.

Cơ hội sản phẩm đáng chú ý nhất không nằm ở việc làm thêm một “TCU box”, mà ở việc xây một:

> **Portable Software-Defined Telematics Platform**

có khả năng chạy trên nhiều hardware / OS / OEM platform và cung cấp:

- Vehicle Data Acquisition
- Edge Telemetry
- Connectivity Management
- Store-and-Forward
- Remote Diagnostics
- Remote Command
- Security
- Observability
- Cloud abstraction
- Configuration from backend

---

# 2. Legacy Telematics vs SDV Telematics

## 2.1 Legacy model

```text
             LEGACY TELEMATICS

CAN
 │
 ▼
┌───────────────┐
│      TCU      │
│               │
│ GPS           │
│ Modem         │
│ CAN parser    │
│ eCall         │
│ Fleet client  │
└───────┬───────┘
        │
       LTE
        │
        ▼
      Cloud
```

Đặc điểm:

- Hardware-centric
- CAN-centric
- Fixed-function
- Logic tightly coupled to TCU
- Cloud backend thường hard-coded
- Difficult to port across vehicle platforms
- Limited dynamic configuration

## 2.2 SDV-native model

```text
                 SDV TELEMATICS

 Vehicle Applications
 ADAS / Energy / Body / Diagnostics / IVI
                   │
                   ▼
════════════════════════════════════════════
        VEHICLE SERVICE / DATA LAYER
     VSS / Vehicle APIs / Data Broker
════════════════════════════════════════════
                   │
                   ▼
       ┌────────────────────────┐
       │  TELEMATICS SERVICES   │
       │                        │
       │ Data acquisition       │
       │ Edge processing        │
       │ Connectivity manager   │
       │ Store & forward        │
       │ Remote command         │
       │ Cloud connector        │
       │ Security               │
       │ Diagnostics bridge     │
       │ Telemetry policy       │
       │ Observability          │
       └────────────┬───────────┘
                    │
             Connectivity API
                    │
         ┌──────────┼──────────┐
         ▼          ▼          ▼
       5G/LTE     Wi-Fi       V2X
         │
         └──────────┼──────────┘
                    ▼
                  CLOUD
```

Key transition:

> **Telematics chuyển từ một hardware box thành một software service plane.**

---

# 3. Telematics nằm ở đâu trong SDV.OS?

```text
             SDV.FEATURES

      Fleet / Energy / ADAS
      Diagnostics / eCall
      Remote Vehicle Control
                │
                ▼
═══════════════════════════════════════
             VEHICLE API
         COVESA VSS / VISS
═══════════════════════════════════════
                │
                ▼
┌─────────────────────────────────────┐
│       TELEMATICS PLATFORM           │
│                                     │
│ Connectivity Manager                │
│ Data Acquisition Manager            │
│ Telemetry Engine                    │
│ Edge Processing                     │
│ Cloud Gateway                       │
│ Remote Command Gateway              │
│ Device Identity / Security          │
│ Offline Store-and-Forward           │
│ Diagnostics Gateway                 │
│ Observability                       │
└──────────────────┬──────────────────┘
                   │
═══════════════════════════════════════
              SDV.OS
   S-CORE / Linux / AUTOSAR / RTOS
═══════════════════════════════════════
                   │
            CCU / Central HPC
                   │
            Modem / eSIM / Wi-Fi
```

**Architecture principle:** Telematics nên là **portable runtime component**, tránh phụ thuộc trực tiếp vào CAN IDs, ECU cụ thể, modem vendor, cloud provider hoặc OEM-specific APIs.

---

# 4. Telematics nằm ở đâu trong SDV.Suite?

```text
                    SDV.Suite

Developer
   │
   ▼
Telematics SDK
   │
   ├── Vehicle simulator
   ├── VSS signal simulator
   ├── Network simulator
   ├── Cloud emulator
   ├── Security test
   ├── Offline test
   ├── Packet-loss test
   ├── Fleet simulator
   └── Data-policy editor
            │
            ▼
        CI / CD
            │
            ▼
        SDV.OS
            │
            ▼
    Telematics Runtime
```

SDV.Suite side có thể bao gồm:

- SDK
- Configuration tools
- Test harness
- Vehicle signal simulation
- Cloud endpoint simulation
- Network fault injection
- Security validation
- Dynamic telemetry profile definition
- CI/CD integration
- Deployment packaging
- Fleet-level validation

---

# 5. Candidate Product Architecture

## Software-Defined Telematics Runtime

```text
                Applications
                     │
            ┌────────▼────────┐
            │ Vehicle API/VSS │
            └────────┬────────┘
                     │
      ╔══════════════▼══════════════╗
      ║    TELEMATICS RUNTIME       ║
      ║                             ║
      ║  Data Acquisition Engine    ║
      ║  Data Policy Engine         ║
      ║  Edge Analytics             ║
      ║  Connectivity Manager       ║
      ║  Secure Cloud Gateway       ║
      ║  Remote Commands            ║
      ║  Diagnostics Adapter        ║
      ║  OTA Transport              ║
      ║  Store & Forward            ║
      ║  Observability              ║
      ╚══════════════╤══════════════╝
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Bosch      OEM HPC     Other TCU
        CCU
```

Core product principles:

1. Hardware-agnostic
2. OS-agnostic
3. Cloud-agnostic
4. Vehicle-data-model driven
5. Policy-driven
6. Secure-by-design
7. Observable
8. Offline-capable
9. Scalable from one ECU to fleet
10. Integrable with SDV development toolchains

---

# 6. Module A — Vehicle Data Acquisition Engine

```text
Cloud Configuration
       │
       ▼
"Collect:
 Vehicle.Speed @10 Hz
 Battery.SoC @1 Hz
 Inverter.Temp @5 Hz

 IF Temp > 100°C:
     capture 30 sec
     upload immediately"
       │
       ▼
Telematics Data Acquisition
       │
       ├── subscribe VSS
       ├── sampling
       ├── filtering
       ├── trigger
       ├── aggregation
       └── compression
```

Desired capabilities:

- Dynamic signal subscription
- Configurable sampling
- Trigger-based acquisition
- Circular buffer
- Pre-event / post-event capture
- Compression
- Local aggregation
- Data prioritization
- Configurable upload windows
- Backend-controlled telemetry profiles

**ADR candidate:** Có nên dùng VSS/VISS làm canonical internal model hay sử dụng OEM-native schema và map tại boundary?

---

# 7. Module B — Edge Data Policy Engine

```text
Vehicle
   │
   ▼
Telemetry Policy
   │
   ├── sample
   ├── filter
   ├── aggregate
   ├── detect event
   ├── calculate features
   │
   ▼
Only useful data
   │
   ▼
 Cloud
```

Ví dụ:

```text
normal operation
BatteryTemperature
       │
       └── upload every 60 sec

IF > 55°C
       │
       ├── sampling → 10 Hz
       ├── capture voltage
       ├── capture current
       ├── capture coolant
       └── upload incident bundle
```

Potential implementation concepts:

- Rules engine
- Event-driven pipeline
- Streaming processing
- WASM sandbox
- Plugin architecture
- Lua-like scripting
- Declarative policy DSL
- Remote policy rollout
- Versioned policy packages

### ADR-001 — Telemetry policy execution model

Options:

- Static configuration
- Declarative rules
- Sandboxed scripts
- Native plugin modules

Decision drivers:

- Safety
- Updatability
- Determinism
- Runtime overhead
- Security
- OEM acceptance
- Tooling complexity

---

# 8. Module C — Connectivity Manager

Application không nên biết modem/network details.

```text
upload(
    priority = CRITICAL,
    deadline = 5 sec
)
```

thay vì:

```text
if LTE_available:
    send_over_LTE()
elif WiFi_available:
    send_over_WiFi()
```

Architecture:

```text
                 Connectivity Manager

                  Message
                     │
             ┌───────┴───────┐
             │               │
        Critical?          Normal?
             │               │
           LTE/5G        Wi-Fi preferred
             │               │
             ▼               ▼
          Upload          Queue
```

Candidate capabilities:

- Network interface abstraction
- LTE/5G/Wi-Fi policy
- Roaming policy
- Cost-aware routing
- QoS awareness
- Failover
- Retry
- Connection health
- Bandwidth budget
- Battery-aware upload
- Priority-based transmission

### ADR-002 — Connectivity abstraction level

Options:

- Socket-level abstraction
- Message-level abstraction
- Service-level abstraction
- Cloud-connector abstraction

Recommended direction: **message/service-level abstraction**.

---

# 9. Module D — Store-and-Forward

```text
        Vehicle data
             │
             ▼
        Local Queue
             │
      ┌──────┴──────┐
 network OK      network down
     │               │
     ▼               ▼
  upload           persist
                     │
                     ▼
                retry later
```

Priority model:

```text
P0 Safety / Emergency
P1 Diagnostics
P2 OTA
P3 Fleet
P4 Analytics
```

Design dimensions:

- Persistent storage
- Encryption at rest
- Quota management
- Retry strategy
- TTL
- Priority queue
- Backpressure
- Crash consistency
- Wear leveling
- Flash lifetime
- Data loss policy

### ADR-003 — Local persistence engine

Options:

- SQLite
- RocksDB-like KV store
- Custom ring buffer
- Journaled file storage
- Embedded message queue

Decision drivers:

- Write amplification
- Flash wear
- Recovery time
- Latency
- Footprint
- Transaction needs

---

# 10. Module E — Remote Command Gateway

```text
Cloud
 │
 ├── Start diagnostics
 ├── Change telemetry config
 ├── Activate feature
 ├── Pre-condition battery
 ├── Request logs
 └── OTA command
      │
      ▼
Remote Command Gateway
      │
 Authentication
 Authorization
 Policy
 Rate limit
 Vehicle state check
      │
      ▼
 Vehicle Service
```

Security requirements:

- Strong authentication
- Authorization
- Command whitelisting
- Vehicle-state constraints
- Replay protection
- Nonce / timestamp
- Audit logging
- Rate limiting
- Safety interlock
- Fail-safe behavior

### ADR-004 — Remote command security model

Possible approaches:

- OAuth2-like token model
- mTLS + signed command
- OEM PKI
- Hardware-backed identity
- Capability-based authorization

---

# 11. Module F — Remote Diagnostics

```text
Vehicle
 │
DTC / Logs / Software version
 │
Telematics
 │
Cloud
 │
Remote Diagnostics
 │
Predict failure
```

Potential API:

```text
DiagnosticsService

getDTC()
getECUHealth()
getSoftwareVersion()
captureLogs()
startDiagnosticRoutine()
```

Future alignment candidates:

- UDS
- DoIP
- SOVD
- Vehicle Health APIs
- Cloud diagnostics

### ADR-005 — Diagnostics abstraction

Question:

> Direct UDS/DoIP exposure hay higher-level diagnostic service abstraction?

Recommended principle:
**Do not expose raw diagnostic transport directly to cloud applications.**

---

# 12. Module G — Vehicle Observability

```text
             Vehicle Apps

 App A      App B      App C
   │          │          │
   └─────── telemetry ───┘
              │
              ▼
    Vehicle Observability Agent
              │
       ┌──────┼───────┐
       ▼      ▼       ▼
     Logs   Metrics   Traces
              │
              ▼
          Edge filter
              │
              ▼
             Cloud
```

Không chỉ:

```text
Vehicle.Speed
Battery.SoC
```

mà còn:

```text
ADAS CPU = 78%
App crash count = 3
Camera service latency = 40 ms
DDS message lost = 120
Container restart = 2
OTA agent status
Disk usage
Network quality
```

Potential concept:

> **OpenTelemetry for Vehicles**

Potential scope:

- Metrics
- Logs
- Distributed traces
- App lifecycle
- Container health
- Service latency
- IPC health
- Resource usage
- Network telemetry
- ECU/HPC health

### ADR-006 — Observability data model

Options:

- OpenTelemetry-compatible
- Proprietary schema
- VSS extension
- Hybrid

---

# 13. Module H — Multi-Cloud Adapter

```text
Europe
   │
  AWS

China
   │
Alibaba / Huawei / Tencent

OEM internal cloud

Fleet customer Azure
```

Potential architecture:

```text
              Vehicle Apps
                  │
                  ▼
          Telematics API
                  │
        Cloud Abstraction
                  │
     ┌────────────┼─────────────┐
     ▼            ▼             ▼
    AWS         Azure         OEM
                                │
                           China Cloud
```

### ADR-007 — Cloud coupling strategy

Options:

1. Hard-coded cloud provider
2. Adapter interface
3. MQTT abstraction
4. HTTP/gRPC abstraction
5. Cloud-neutral message API

Recommended default:
**cloud-neutral internal contract + pluggable adapters**.

---

# 14. Candidate Two-Part Product

```text
                 YOUR PRODUCT

╔══════════════════════════════════════════════╗
║             TELEMATICS SDK                  ║
║                SDV.Suite side               ║
║                                             ║
║  Config tools                               ║
║  VSS schema                                 ║
║  Vehicle simulator                          ║
║  Cloud simulator                            ║
║  Network fault injection                    ║
║  Data-policy editor                         ║
║  Test framework                             ║
╚══════════════════════╤═══════════════════════╝
                       │
                    CI/CD
                       │
                       ▼
╔══════════════════════════════════════════════╗
║         TELEMATICS EDGE RUNTIME              ║
║               SDV.OS side                   ║
║                                             ║
║ Vehicle Data Adapter                        ║
║ VSS / VISS                                  ║
║ Data Acquisition                            ║
║ Event / Trigger Engine                      ║
║ Edge Processing                             ║
║ Store-and-Forward                           ║
║ Connectivity Manager                        ║
║ Diagnostics                                 ║
║ Remote Command                              ║
║ Security                                    ║
║ Observability                               ║
║ Cloud Connector                             ║
╚══════════════════════╤═══════════════════════╝
                       │
                   Modem API
                       │
                       ▼
                  LTE / 5G
                       │
                       ▼
                     CLOUD
```

---

# 15. Opportunity Assessment

| Component | Opportunity | Comment |
|---|---:|---|
| Modem / TCU hardware | ★★☆☆☆ | Competition + certification nặng |
| Basic CAN → Cloud gateway | ★★☆☆☆ | Dễ commoditize |
| VSS Vehicle Data Agent | ★★★★☆ | Good SDV portability |
| Configurable Data Acquisition | ★★★★★ | Strong fleet / R&D value |
| Edge Telemetry Engine | ★★★★★ | Reduces bandwidth and cloud cost |
| Connectivity Abstraction | ★★★★☆ | Cross-platform value |
| Store-and-Forward | ★★★★☆ | Automotive-specific problem |
| Remote Diagnostics Gateway | ★★★★★ | High business value |
| SDV Observability | ★★★★★ | Emerging and strategic |
| Multi-cloud Connector | ★★★★☆ | Global OEM relevance |
| OTA transport | ★★★☆☆ | Competitive space |
| Complete OTA management | ★★★☆☆ | Safety / regulatory complexity |
| Fleet backend | ★★★☆☆ | Crowded market |
| Telematics SDK / Test Suite | ★★★★★ | High differentiation potential |

---

# 16. Recommended Initial Product Scope

# Vehicle Telemetry & Observability Agent

```text
                     Applications

             ADAS   Energy   Body
               │      │       │
               └──────┼───────┘
                      ▼
                 VSS / VISS
                      │
                      ▼
╔════════════════════════════════════════════╗
║        TELEMETRY / OBSERVABILITY AGENT    ║
║                                            ║
║ Signal subscription                        ║
║ Dynamic sampling                           ║
║ Trigger engine                             ║
║ Event recording                            ║
║ Local calculations                         ║
║ Log collection                             ║
║ Metrics                                    ║
║ App health                                 ║
║ Compression                                ║
║ Store & forward                            ║
╚═════════════════════╤══════════════════════╝
                      │
                      ▼
              Cloud-independent API
                      │
           ┌──────────┼──────────┐
           ▼          ▼          ▼
         OEM        Bosch       AWS
        Cloud       Cloud
```

Suggested evolution:

```text
Phase 1
Telemetry Agent
     │
     ▼
Phase 2
Observability
     │
     ▼
Phase 3
Remote Diagnostics
     │
     ▼
Phase 4
Connectivity Manager
     │
     ▼
Phase 5
Remote Command
     │
     ▼
Phase 6
Complete SDV Telematics Platform
```

---

# 17. Bosch Integration View

```text
                     BOSCH SDV

                 SDV.Features
                      │
                      ▼
                  Vehicle APIs
                      │
                      ▼
             ┌──────────────────┐
             │ YOUR TELEMATICS  │
             │    PLATFORM      │
             └────────┬─────────┘
                      │
                   SDV.OS
                      │
                Bosch CCU/HPC
                      │
                    Cloud


Development side:

                 SDV.Suite
                      │
             ┌────────▼─────────┐
             │ YOUR TELEMATICS  │
             │ SDK + Simulator  │
             │ + Test Tooling   │
             └──────────────────┘
```

Recommended positioning:

> **A software-defined vehicle data plane that allows an OEM to define from the cloud what data to collect, when to collect it, how to process it at the edge, and where to deliver it — independently of vehicle architecture, operating system, and cloud provider.**

---

# 18. Architecture Decision Backlog

## ADR-001 — Canonical Vehicle Data Model

**Question:** Có sử dụng COVESA VSS làm canonical model hay không?

Options:

- COVESA VSS
- OEM-native model
- AUTOSAR service model
- Internal proprietary model
- Hybrid mapping layer

Decision drivers:

- Portability
- OEM acceptance
- Tooling
- Performance
- Schema governance
- Version compatibility

## ADR-002 — Runtime Deployment Model

Options:

- Dedicated TCU process
- Linux service
- Container
- AUTOSAR Adaptive application
- Eclipse S-CORE component
- Mixed deployment

Decision drivers:

- Isolation
- Safety
- OTA
- Portability
- Startup time
- Resource footprint

## ADR-003 — IPC / Service Communication

Options:

- SOME/IP
- DDS
- gRPC
- D-Bus
- Zenoh
- Custom IPC
- VISS-based API

Decision drivers:

- Real-time needs
- Payload size
- Discovery
- QoS
- OEM stack
- Safety certification
- Tool support

## ADR-004 — Cloud Protocol

Options:

- MQTT
- HTTP/REST
- gRPC
- WebSocket
- AMQP
- Proprietary protocol

Decision drivers:

- Intermittent connectivity
- Data volume
- Command channel
- Security
- Firewall traversal
- Scalability

## ADR-005 — Local Data Storage

Options:

- SQLite
- Embedded KV store
- Ring buffer
- Journal
- Custom persistence

Decision drivers:

- Flash wear
- Recovery
- Throughput
- Storage budget
- Data integrity

## ADR-006 — Edge Policy Engine

Options:

- Static config
- JSON/YAML rules
- DSL
- Lua
- WASM
- Native plugins

Decision drivers:

- Security
- Remote update
- Performance
- Determinism
- Debuggability

## ADR-007 — Security Identity

Options:

- TPM
- HSM
- Secure element
- OEM PKI
- Device certificate
- eSIM identity

Decision drivers:

- Hardware availability
- Lifecycle management
- Rotation
- Manufacturing flow
- Regional regulation

## ADR-008 — Diagnostics Interface

Options:

- Raw UDS/DoIP
- SOVD
- High-level Diagnostic Service API
- Cloud-native diagnostics abstraction

Recommended bias:
Prefer **service abstraction above transport**.

## ADR-009 — Observability

Options:

- OpenTelemetry
- Proprietary metrics/log format
- VSS extensions
- Hybrid model

Research question:
Can OpenTelemetry semantics be adapted efficiently for constrained automotive runtime?

## ADR-010 — OTA Relationship

Options:

- Telematics owns OTA transport
- Telematics only provides connectivity
- Separate OTA agent
- Shared transport service

Important:
Avoid coupling telemetry data-plane logic tightly with safety-critical OTA orchestration.

---

# 19. Non-Functional Requirements to Research

## Performance
- CPU overhead
- Memory footprint
- Network bandwidth
- Serialization cost
- Signal latency
- Startup time

## Reliability
- Crash recovery
- Offline operation
- Data persistence
- Network failover
- Graceful degradation

## Security
- Authentication
- Authorization
- Encryption in transit
- Encryption at rest
- Certificate rotation
- Secure boot integration
- Signed configuration
- Replay protection

## Safety
- Interaction with safety-critical services
- Read-only vs write access
- Command gating
- Failure containment

## Maintainability
- Plugin model
- Versioning
- API compatibility
- Schema migration
- OTA updates

## Portability
- Linux
- QNX
- AUTOSAR Adaptive
- S-CORE
- Android Automotive
- Bosch CCU/HPC
- OEM-specific HPC

## Operability
- Logs
- Metrics
- Tracing
- Remote health
- Fleet rollout
- Rollback

---

# 20. Research Questions

1. COVESA VSS vs AUTOSAR service model
2. VISS architecture and deployment
3. Eclipse KUKSA databroker
4. Eclipse SDV Blueprints
5. Eclipse S-CORE
6. Bosch SDV.OS integration boundaries
7. Bosch CCU container/runtime environment
8. AUTOSAR Adaptive Execution Management
9. SOME/IP vs DDS vs Zenoh
10. SOVD for remote diagnostics
11. OTA architecture and Uptane
12. OpenTelemetry on embedded Linux
13. eSIM / SIM lifecycle management
14. MQTT QoS in intermittent automotive networks
15. Edge compression and event-triggered telemetry
16. Data privacy / regional storage requirements
17. Cybersecurity regulations affecting telematics
18. UNECE R155 / R156 implications
19. ISO 21434 implications
20. China-specific connected vehicle requirements
21. EU Data Act and automotive data access
22. Backend multi-tenancy
23. Fleet-scale device management
24. Signal schema versioning
25. Policy rollout strategy
26. Store-and-forward storage design
27. Zero-trust vehicle-to-cloud
28. Secure remote command execution
29. Vehicle observability model
30. Remote troubleshooting workflows

---

# 21. Suggested Proof-of-Concept

## POC-1 — Basic Vehicle Telemetry Agent

```text
VSS simulator
    │
    ▼
Telemetry Agent
    │
    ├── dynamic subscription
    ├── 1 Hz / 10 Hz sampling
    ├── event trigger
    ├── local buffering
    └── MQTT upload
            │
            ▼
        Test Cloud
```

Minimum features:

- VSS input
- MQTT output
- Runtime configuration
- Local persistent queue
- Offline reconnect
- Metrics

## POC-2 — Vehicle Observability

Add:

- CPU
- memory
- application health
- process restart
- IPC latency
- network status
- trace IDs

## POC-3 — Remote Diagnostics

Add:

- Read DTC
- Read software version
- Trigger log collection
- Request diagnostic snapshot

## POC-4 — Multi-cloud

Add adapters for:

- MQTT broker A
- AWS IoT
- Azure IoT
- OEM mock backend

---

# 22. Suggested Evaluation Matrix

| Criterion | Weight | Notes |
|---|---:|---|
| Portability | High | Must run across multiple vehicle platforms |
| Security | Critical | Remote vehicle access |
| Offline robustness | Critical | Automotive connectivity is intermittent |
| Dynamic configuration | High | Core SDV capability |
| Vehicle-data abstraction | High | Avoid CAN lock-in |
| Cloud independence | Medium/High | Important for global OEM |
| Runtime footprint | High | Embedded constraint |
| Observability | High | Essential for SDV operations |
| Diagnostics integration | High | Strong business value |
| OTA compatibility | Medium | Important but avoid over-coupling |
| Safety isolation | Critical | Must not destabilize vehicle control |
| Tooling quality | High | OEM adoption depends on developer UX |

---

# 23. Key Architectural Principle

Move from:

```text
CAN → TCU → MQTT → Cloud
```

to:

```text
Vehicle Service/Data Layer
          │
          ▼
Software-Defined Telematics Runtime
          │
          ├── Policy
          ├── Edge compute
          ├── Diagnostics
          ├── Observability
          ├── Security
          └── Connectivity abstraction
          │
          ▼
Cloud-neutral transport
          │
          ▼
OEM / Bosch / AWS / Azure / China Cloud
```

---

# 24. Glossary

| Term | Meaning |
|---|---|
| **TCU** | Telematics Control Unit |
| **CCU** | Connectivity Control Unit / Central Control Unit depending on context |
| **SDV** | Software-Defined Vehicle |
| **SDV.OS** | Vehicle software foundation/runtime concept |
| **SDV.Suite** | Development, integration, simulation and validation toolchain |
| **VSS** | Vehicle Signal Specification |
| **VISS** | Vehicle Information Service Specification |
| **COVESA** | Connected Vehicle Systems Alliance |
| **AUTOSAR** | AUTomotive Open System ARchitecture |
| **S-CORE** | Safe Open Vehicle Core |
| **SOME/IP** | Service-Oriented Middleware over IP |
| **DDS** | Data Distribution Service |
| **SOVD** | Service-Oriented Vehicle Diagnostics |
| **UDS** | Unified Diagnostic Services |
| **DoIP** | Diagnostics over Internet Protocol |
| **OTA** | Over-the-Air update |
| **MQTT** | Message Queuing Telemetry Transport |
| **eSIM** | Embedded SIM |
| **HSM** | Hardware Security Module |
| **PKI** | Public Key Infrastructure |
| **Observability** | Logs, metrics, traces and runtime-health visibility |
| **Store-and-Forward** | Local persistence and later transmission when network returns |
| **Edge Processing** | Processing data inside/on-near the vehicle before cloud upload |
| **Telemetry Policy** | Rules that define what to collect, when, how and where to send |
| **Vehicle Data Plane** | Software layer that moves and transforms vehicle data |

---

# 25. References / Starting Points

- Bosch Mobility — SDV Portfolio  
  https://www.bosch-mobility.com/en/mobility-topics/sdv-portfolio/

- Bosch Mobility — Connectivity Control Unit  
  https://www.bosch-mobility.com/en/solutions/connectivity/connectivity-control-unit-cv/

- Bosch Mobility — Vehicle Connectivity Services  
  https://www.bosch-mobility.com/en/solutions/connectivity/vehicle-connectivity-services-cv/

- Bosch Mobility — Open In-Vehicle API  
  https://www.bosch-mobility.com/en/solutions/software-and-services/open-in-vehicle-api/

- Bosch Mobility — Functions for Connected Services Infrastructure  
  https://www.bosch-mobility.com/en/solutions/software-and-services/functions-for-connected-services-infrastructure/

- ETAS  
  https://www.etas.com/

- COVESA — Vehicle Signal Specification  
  https://covesa.global/project/vehicle-signal-specification/

- COVESA — Vehicle Information Service Specification  
  https://covesa.global/project/vehicle-information-service-specification/

- Eclipse SDV Blueprints — Fleet Management  
  https://sdv-blueprints.eclipse.dev/docs/fleet-management/introduction/

- Eclipse Software Defined Vehicle  
  https://sdv.eclipse.org/

---

# 26. Recommended Next Study

So sánh ba candidate implementation:

1. **Telematics Runtime on Linux Container**
2. **Telematics Runtime as AUTOSAR Adaptive Application**
3. **Telematics Runtime on Eclipse S-CORE / SDV-native platform**

Cho mỗi candidate, đánh giá:

- Deployment model
- IPC
- Vehicle data API
- Security
- Diagnostics
- OTA
- Memory
- CPU
- Storage
- Cloud connectivity
- Toolchain
- Certification impact
- OEM portability
- Bosch integration effort

Kết quả của comparison này có thể chuyển trực tiếp thành các formal ADR.
