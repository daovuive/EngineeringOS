# Thread evolution and superseded positions

**Project:** DAR-SDV-VS-001. **Archive as of:** 8 September 2026.

This is a source-grounded summary of the visible requests and resulting artifacts, **not a verbatim chat export**. Ordering is preserved; no unsupported per-message timestamps are invented. All report versions retain their own wording. Files and filenames, rather than page counts stated in prior messages, identify the archived versions.

## U1 - Analyze the original idea and prepare an English DAR

The user supplied `SDV_Telematics_Vehicle_Status_AAOS_First_Plan_Revision_EN.md` and requested analysis, an implementation plan and an English DAR for discussion with management.

**Source position:** move from Linux-first to AAOS-first; recover the existing PoC; use the same-core host runner only for deterministic tests; prove mapping/cloud substitutions and plan the later AAOS SDV port. The source contained an eight-week sequence.

**P09 outcome:** a detailed v0.9 DAR with E1-E4 execution alternatives, gated funding, proposed canonical contract, triggers, receipt/offline/security design, S1-S6 and a planning estimate of 3.5 FTE x 8 weeks = 28 person-weeks / 1,120 nominal hours. A proposed 20% effort reserve was separate from that calendar. Recovery was initially sized as 7 person-weeks at that staffing level.

**H01 - SUPERSEDED FOR RESOURCES AND SCHEDULE:** The 3.5-FTE/eight-week full-MVP model and its 7-person-week recovery tranche are historical. They must not be used as the current two-person or dynamic forecast. The architectural and evidence guardrails were retained, not discarded.

## U2 - Use one senior and one intern/fresher; compare Automotive ideas

The user restricted the team to exactly one senior developer plus one intern/fresher and requested comparison with other Automotive ideas.

**P10 outcome:** v1.0 retained Vehicle Status but rebaselined the full outcome to a proposed 18 weeks, with a reduced demo at week 8 and sponsor-controlled weeks 19-20 for contingency. There was no hidden architect/QA/cloud/security implementer. Credited capacity was senior 28 h/week, junior 12 h/week in recovery and 24 afterwards, under stated assumptions. The detailed allocation totaled 476 senior and 352 junior-work hours. Nominal staffing was 1,440 hours over 18 weeks, not 828.

The comparison added I1-I7 and distinguished initiative selection from E1-E4 execution selection. I2 was recommended for the strongest early small-team usefulness; I1 was retained for an explicit SDV reuse objective. Scores were proposed workshop judgments and not measured market rankings. No initiative was funded in the record.

**H02 - NOW A DEFAULT, NOT A FIXED HEADCOUNT RULE:** The exact two-person constraint was later relaxed into an editable role-aware Excel model. Its configuration remains the default. Do not silently carry the old 18-week target across all staffing changes.

**H03 - RESERVE CHANGED:** v1.0 used two extra calendar weeks, not the v0.9 20% effort reserve. The current workbook has an editable two-week reserve default. These are distinct quantities.

## U3 - Shorten the DAR; put a dynamic plan in Excel

The user requested a shorter, easily understood DAR and automatic resource-driven reporting, giving changing from two to three developers as an example. The idea had to remain unchanged. Plan in Excel; idea and detail in .md and .docx.

**P11/W11 outcome:** a short v1.1 DAR and an Excel workbook with Report, Inputs, Plan, Scenarios and Guide. Inputs separated total developers from junior count, computed experienced count and applied role-aware capacity, floors, caps, waits and rounding. Word/Markdown remained static narrative, not linked auto-rewritten documents. A ZIP of these v1.1 artifacts was also delivered and is preserved byte-for-byte.

**H04 - PRESENTATION SUPERSEDED:** The v1.1 narrative and workbook are historical predecessors of v1.2. Do not use their dates or metadata as the latest approval record. The core scope and automatic-planning design were retained.

## U4 - Focus on obtaining approval from a non-technical boss

The user clarified that the purpose was to get approval for this idea. The report had to make the main concept easy to understand, explain weaknesses, practical effectiveness and relative advantages, and include examples at important points. The requested deliverables remained one English .md, one English .docx and a dynamic-resource Excel plan.

**P12/W12 outcome - CURRENT:** the v1.2 Vehicle Status Reuse Pilot approval report and `SDV_Vehicle_Status_Dynamic_Plan.xlsx`. The report recommends approving recovery first. It presents everyday examples of translating distance units, preserving missing-data meaning, handling outages and rejecting unsafe configuration; compares Automotive alternatives qualitatively; and explains how actual reuse value should be measured.

The workbook added an optional Business Case sheet. Blank rates/costs produce NOT SET; blank effort/value evidence produces NOT QUANTIFIED. Planning start remains blank. The report's 80/40/160/40-hour break-even example is illustrative, not a live input or measured result.

**H05 - CURRENT APPROVAL PRESENTATION:** P12 and W12 are the current sources for management communication and dynamic planning. Prior technical detail remains reference material where compatible, with proposed limits and unverified assumptions explicitly preserved.

## U5 - Preserve everything for EOS

The user asked to save all ideas, decisions and reports from the thread for import into EOS (EngineeringOS).

**This archive:** preserves the 12 original source/deliverable files without modification; adds a current-context record, 40-entry decision register, searchable Excel snapshot, retained technical excerpts, source inventory and integrity checks. It separates current knowledge from historical schedules and includes portable ingestion guidance. It does not claim to be a native EOS export, a raw transcript, or a completed EOS import.

## Historical numeric comparisons - preserve interpretation

P10 proposed a small-team initiative ranking: I1 76, I2 89, I3 65, I4 72, I5 73, I6 47, I7 50 out of 100. Under its SDV-reuse weights, scores were I1 89, I2 81, I3 59, I4 72, I5 73, I6 60, I7 61. They reflected the original two-person scenario and assumptions. The current Excel resource model does not automatically rescore ideas.

The historical E3 execution score changed from 87 in P09 to 79 in P10 because speed, predictability and capacity were reassessed. That is a revision of proposed judgment, not a measured deterioration of code quality. The original Option A/B definitions were not supplied; E1-E4 and I1-I7 were newly defined alternatives, not reconstructions of missing source options.

## Persistent limitations

There is no implementation repository, benchmark, real-vehicle result, approved salary/rate, committed consumer, approved start or signature in this archive. Historical external citations are retained as supplied research context; they have not been refreshed as part of this archival task. A future team must verify applicable versions and access before relying on ecosystem availability claims.
