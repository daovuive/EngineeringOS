# Vehicle Status Reuse Pilot
## Approval Request
**DAR-SDV-VS-001 | Version 1.2 | 8 September 2026 | Proposed for approval**

## 1. The decision in one minute
**Recommendation: approve a limited review of the existing prototype first. Approve the remaining build only after that review confirms feasibility, a real user and an acceptable forecast.**

### What is the idea?
Build a reusable software component that reads vehicle status, applies agreed reporting rules and sends it to a receiving server (backend). Start with the existing **Android Automotive OS (AAOS)** prototype. Separate the shared reporting rules (the core) from vehicle and backend connections, so those connections can change without rewriting the rules. [P1]

This is the Vehicle Status part of **Option C: Hardware-Agnostic Telematics Hub**. It is an engineering capability, not a new customer app or a universal vehicle gateway.

### A simple example
Project A supplies distance in kilometres; Project B supplies it in metres. A small **adapter** translates each source into the same agreed format. The shared component then applies the same reporting rules. Changing the backend connection should also leave those rules unchanged.

**Think of it as keeping the same reporting process while changing its translators and delivery channels.** If the two sources mean different things, the software must flag the difference rather than pretend they are equivalent.

### Why invest?
The intended users are vehicle-software integration teams. The value hypothesis is less repeated development and retesting in later projects, with clearer evidence that data still means the same thing. **Savings, customer adoption and platform portability have not yet been demonstrated.** [P1; P2]

| Management question | Proposed answer |
|---|---|
| What are we asking for now? | The recovery phase only: review the prototype, access, dependencies, reusable scope and business need. |
| Where are people, dates and budget? | The companion Excel file. Inputs changes the team; Report shows the live forecast; Business Case prices the plan when rates and costs are entered. |
| What happens next? | At Gate A, a review checkpoint, choose continue, reduce scope or stop. Do not automatically release the full budget. |
| Who owns the decision? | The sponsor approves scope and funding. An experienced technical lead is accountable for feasibility and test evidence. |

**Decision principle:** fund evidence of useful reuse, not an assumption that an existing demo is already reusable.

<!-- PAGE -->
# 2. Where this idea is stronger - and where it is not

### Advantages we intend to demonstrate
| Intended advantage | Example a manager can understand | Important limit |
|---|---|---|
| Less repeated integration work | A second vehicle data source needs a new translator, not a second copy of all reporting rules. | Every new source still needs access, mapping and tests. |
| More consistent information | Missing battery data is reported as unavailable, not as a misleading 0% charge. | A shared format cannot repair an incorrect or ambiguous source. |
| Easier backend changes | Change from MQTT to HTTPS, two connection methods, while keeping the same report content and identity. | Two methods on one test backend do not prove independence from every cloud vendor. |
| More predictable fault handling | After a network outage, resend retained reports with the same IDs and make duplicates visible. | Storage is limited; expiry and overflow can cause declared losses. |

**Compared with extending the prototype directly:** this approach adds work now to separate responsibilities and create repeatable tests. That is worthwhile only if later integrations actually use the result. For one disposable demonstration, direct extension may be cheaper. [P1; P2]

### Automotive alternatives considered
The following is a qualitative investment comparison from the earlier DAR, not a market ranking. Vehicle Status remains the selected idea for the objective of reusable in-vehicle integration. [P2]

| Alternative | When it would be a better investment |
|---|---|
| Signal replay and validation tool | The priority is helping an internal team reproduce signal defects quickly, rather than building a vehicle runtime capability. |
| Engineering knowledge assistant | Document search is the main pain point and an authorized, reliable knowledge set is available. |
| EV charging observability | A charging operator has usable data and needs session or energy checks. |
| Read-only fleet dashboard | An operator needs visible status and triage, and data collection already exists. |
| Predictive-maintenance study | Representative failure history and a domain partner are available for a narrow experiment. |
| Update-campaign observability sandbox | An existing update team needs failure evidence; this does not build a full vehicle-update system. |

**Why retain Vehicle Status:** it directly addresses reuse of the existing AAOS implementation. Its proposed distinction is tested behavior under replacement, not merely sending data to the cloud. Reuse suitable existing components where they satisfy the need; do not build a new broker, simulator or general platform for its own sake. Select one initiative, not parallel products. [P1; P2]

<!-- PAGE -->
# 3. How we will judge practical effectiveness

### Prove the benefit with comparable work
A successful upload is not enough. Before claiming efficiency, compare a normal integration with an adapter-based integration for the **same signals, quality requirements and test coverage**. Include development, review, integration and testing time. If no credible comparison exists, report technical reuse only - not a saving.

| Question | Evidence required | Example / decision rule |
|---|---|---|
| Did the information keep its meaning? | Two mappings produce the expected results, including missing, stale and incompatible data. | 12,345.6 km and 12,345,600 m should match. Two different definitions of battery charge must not be forced to match. |
| Did replacement leave the rules unchanged? | Compare outputs, decisions and source changes across both mappings and both backend connections. | A connection change must not silently change when a report is sent. |
| Was future integration effort reduced? | Record comparable hours and defects; separate one-time setup from later adaptation and maintenance. | Less coding alone is not a saving if testing or support costs increase. |
| Can the next engineer use it? | A clean setup guide, repeatable tests and a replay by someone other than the original implementer. | The junior reproduces the demo from the written instructions. |
| Is there a real consumer? | A named team and an agreed follow-on integration or evaluation. | No consuming team weakens the case for funding the full reusable asset. |

These are proposed management checks. Technical acceptance retains the six test groups from the earlier DAR. Business-value targets should be agreed at Gate A, before measuring the result. [P2; P3]

### A break-even example - illustration only
Assume a later integration costs **80 hours** without reuse and **40 hours** with it, including testing and review. Assume reuse requires **160 extra setup hours** beyond the work needed anyway, plus **40 maintenance hours** across the comparison period.

**Break-even = (160 + 40) / (80 - 40) = 5 later integrations.**

At five integrations, both choices total 400 hours. At six, reuse saves 40 hours under these assumptions. These are illustrative numbers, not project estimates or measured results. Hours saved are not automatically cash saved or revenue gained.

**Implication:** reuse can be attractive when repeated integrations are likely. It may not pay back for a single use. The optional Business Case tab accepts comparable effort and maintenance inputs; it remains **not quantified** until those inputs are provided. Its savings output is a forecast, not realized benefit.

<!-- PAGE -->
# 4. What we will deliver, and the disadvantages

### A deliberately limited pilot
The full pilot includes one AAOS runtime, two vehicle mappings, two backend connection methods, restart-safe temporary storage, one authorized reporting-settings update, a reusable test package and a design/backlog for the next AAOS software-defined vehicle (SDV) platform. The second mapping may use controlled test data; a second live vehicle manufacturer is not required. [P1; P2]

| Important situation | Expected behavior and limit |
|---|---|
| The vehicle loses network access | Keep reports within the approved storage and retention limits. Retry after reconnect with stable IDs. Record any expiry, overflow or duplicate; do not promise zero loss or exactly-once delivery. |
| Someone changes reporting settings | Accept only an authorized update within approved bounds; for example, change an agreed reporting interval. Reject an expired/replayed update or any request to control the vehicle. |
| Management asks about the next platform | Deliver the porting design and remaining work. Do not say the software runs on AAOS SDV until it has actually been tested there. |

### Main drawbacks and controls
| Drawback / risk | Business consequence | Proposed control |
|---|---|---|
| Upfront code restructuring and tests | The first useful demo may take longer than a direct extension. | Fund recovery first; limit cleanup to the selected capability. |
| Few future integrations, or existing tools already cover the need | The reusable asset may not justify its maintenance cost. | Confirm a consumer and assess existing-stack overlap at Gate A. |
| Hidden prototype problems or unavailable access | Estimates can increase before new features appear. | Reproduce the build and permitted data path before committing to the full plan. |
| Experienced-developer bottleneck | Extra juniors can increase mentoring rather than shorten delivery. | Use role-aware capacity, limited parallel work and measured throughput. |
| Different signal meanings | Incorrect reports can look consistent while being wrong. | Approve meanings and test deliberate mismatches, not just matching field names. |
| Pilot evidence is narrower than production needs | A demo can be mistaken for a production-ready service. | Keep read-only vehicle access and separate production/security approval from this pilot. |

**Not funded by this approval:** a generic gateway, vehicle control, a new Linux product, production certification, independent security assurance, a second production cloud or a completed next-platform runtime port. The host test runner is a lightweight test utility using the same core, not another product. [P1; P2]

<!-- PAGE -->
# 5. Approval, delivery checkpoints and next action

### Approve work in stages
| Stage | What management should see | Decision |
|---|---|---|
| Recovery - Gate A | Working prototype, permitted data, dependencies, consumer and revised estimate. | Continue only with a feasible scope and credible use case. |
| Shared rules - Gate B | Agreed data meaning and reporting rules; repeatable tests independent of the connection. | Approve the rules before further integration. |
| Reduced demo | One mapping and backend connection on AAOS, with receiver confirmation. | Continue or stop at a limited demo; not full reuse acceptance. |
| Full pilot - Gate C | Both mappings/connections, outage and security evidence; all mandatory tests passed. | Accept the tested capability, not an unproven production claim. |
| Next-platform design | Named target, known gaps and an executable porting backlog. | Approve design readiness separately from a future runtime port. |

The reduced demo keeps remote settings off. Full acceptance requires all six groups: **data meaning, reporting rules, backend replacement, offline recovery, configuration security and integrated reuse**. Incomplete crash recovery or missing mandatory results block the full-pilot claim. [P2; P3]

### Resource and funding control
In **SDV_Vehicle_Status_Dynamic_Plan.xlsx**, change blue Inputs cells for the team, availability and start date. Report and Scenarios recalculate timing and hours. Business Case calculates costs only after rates and non-labour inputs are entered.

**Example:** 2 to 3 developers with one junior adds an experienced developer. Adding a junior instead is a different forecast. Neither change removes required tests or integration limits.

The workbook models one team from the start, not actual progress. Resources update Excel, not this narrative. Save the approved workbook snapshot.

### Decision to record
**Sponsor and consuming team:** ____________________  
**Decision:** Approve recovery / approve with conditions / defer / reject  
**Named resources and allocations:** ____________________  
**Approved recovery budget and start:** ____________________  
**Gate A review date and continuation conditions:** ____________________  
**Reserve authority and accepted risks:** ____________________

**First action:** reproduce the prototype and capture one status example before restructuring code.

### Source record
[P1] *AAOS-First Revision for the SDV Telematics Vehicle Status MVP Plan*, sections 1-7 and 11-12.  
[P2] *SDV Vehicle Status DAR v1.0 - Two-Person Delivery Revision*: alternatives, controls and capacity.  
[P3] *Vehicle Status Short DAR v1.1* and *SDV_Vehicle_Status_Plan.xlsx*: scope, six test groups and planning model. Full source filenames are in Excel Guide. Examples and break-even figures are illustrations, not test results.
