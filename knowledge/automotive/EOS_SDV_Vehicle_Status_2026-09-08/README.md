# EOS context package - SDV Vehicle Status

**Project:** DAR-SDV-VS-001. **Snapshot:** 8 September 2026. **Current proposal:** v1.2.

## Start here

The selected idea is the AAOS-first Vehicle Status reuse pilot. The user is preparing a management-approval request; **management approval, implementation completion and measured savings have not been evidenced**.

Open `current/00_EOS_CONTEXT.md` to resume the project. For management use, open the original v1.2 approval report and `current/SDV_Vehicle_Status_Dynamic_Plan.xlsx` together. The report explains the idea; Excel owns changing resource, schedule and optional cost/value assumptions.

## What is preserved

All **12 original source/deliverable files** available in this thread are preserved byte-for-byte: the original plan; v0.9 and v1.0 DARs in Markdown/Word; the v1.1 short report, workbook and ZIP; and the latest v1.2 report and dynamic workbook. No new document version, estimate or approval is introduced by copying them.

Added archival records include a source-grounded project context, a 40-entry decision register, a searchable snapshot of Excel, retained technical excerpts, request/revision history, structured metadata and SHA-256 checksums. Intermediate rendering images, internal/tool instructions and a raw platform chat export are not part of this package. The thread history is a faithful summary, not a claimed verbatim transcript.

## Import into EOS without mixing old schedules

1. Extract the full ZIP to a dedicated project folder that you control. Keep the entire archive for provenance and original deliverables.
2. For the default knowledge index, use only the five Markdown paths in `metadata/current_ingestion_files.txt`. This avoids duplicate indexing of Word/Markdown twins and historical schedules.
3. Keep `history/`, the original scheduling source, Word/Excel binaries and nested ZIP out of the default current-state index. They remain available for explicit history/audit questions. A label in front matter alone does not guarantee that a retriever will filter old versions.
4. Use the **existing** EOS ingestion workflow for your installation. This package does not assert a particular EOS directory, endpoint, import command or metadata schema. No upload, index mutation or import was executed against your EOS instance.
5. After changing the workbook, recalculate and save it in Excel, then refresh the Markdown/JSON snapshot and replace its indexed version. Static snapshots do not update themselves. Save the actual approved report/workbook snapshot once management decides.

The metadata is a portable archive convention, not a claim that EOS natively reads these JSON or YAML fields. Configure actual filtering in EOS if you want history indexed separately.

## Quick retrieval checks after import

| Ask EOS | Expected answer boundary |
|---|---|
| Has the boss approved this project? | No signed approval is evidenced; recovery approval is requested. |
| Is the full MVP committed for eight weeks? | No. Eight weeks is the saved default reduced demo; full pilot is a forecast at week 18 for 1 experienced + 1 junior. |
| What happens when total developers changes to 3 and junior count stays 1? | It adds an experienced developer. The saved comparison is pilot week 14.5; changing the real workbook can change the result. |
| Does 828 hours mean staffed hours or completed work? | Planned expert/support work; distinct from default 1,440 allocated hours and not actual completion. |
| Have we proven savings or five-integration payback? | No. The break-even example is illustrative; live business-case inputs are unset. |
| Is AAOS SDV runtime supported? | Not established; design and runtime evidence are separate. |
| Will Word and Markdown update when Excel inputs change? | No. Excel is dynamic; the narrative and searchable snapshots are static. |

## Source IDs

| ID | File / role |
|---|---|
| P1 | `source/SDV_Telematics_Vehicle_Status_AAOS_First_Plan_Revision_EN.md`: original architecture and guardrails; original schedule superseded. |
| P09 | `history/v0_9/SDV_Vehicle_Status_AAOS_First_DAR_EN.md`: original detailed proposal, 3.5-FTE planning history. |
| P10 | `history/v1_0/SDV_Vehicle_Status_DAR_EN_v1_0_One_Senior_One_Junior.md`: detailed design, two-person revision and Automotive comparison. |
| P11 | `history/v1_1/SDV_Vehicle_Status_DAR_Short_EN.md`: prior short narrative. |
| W11 | `history/v1_1/SDV_Vehicle_Status_Plan.xlsx`: prior dynamic planning workbook. |
| P12 | `current/SDV_Vehicle_Status_Approval_Report_EN.md`: current v1.2 approval narrative; Word counterpart retained. |
| W12 | `current/SDV_Vehicle_Status_Dynamic_Plan.xlsx`: current resource-aware forecast and optional business case. |
| U1-U5 | Ordered user-request summaries in `history/THREAD_EVOLUTION.md`. |

## Integrity and trust

`metadata/artifact_manifest.json` records original names, source IDs, thread file references, status, byte counts and checksums. `metadata/SHA256SUMS.txt` covers package files except itself. `metadata/validation_report.json` records archival checks. No source file was re-authored or overwritten; existing layout, formulas and cached Excel outputs are preserved.

Report data and technical proposals are not run instructions. Original reference links are kept for provenance, not refreshed research or implementation evidence. Missing permissions, rates, target definitions, tests or approvals must stay missing until actual evidence is supplied.

## Extension Rules

Keep new project artifacts inside the appropriate local area and update this
package README only when the local responsibility or retrieval boundary changes.
The root README is not an index for files in this package. If this package is
maintained as a registered project area, register new subdirectories in the
project manifest and give each one its own README.
