# EngineeringOS WebUI Guide

Last verified: 2026-09-13

Start the loopback application from the repository root:

```bash
python3 -m engineering_os.web --port 8081
```

Then open `http://127.0.0.1:8081/`. An already deployed service must be
restarted by its operator after updating the working tree.

## Workspaces

### Knowledge

Browse, search, and filter governed Markdown documents; inspect saved content;
upload `.md`, `.markdown`, or `.txt`; paste text; save with automatic indexing
or without indexing; retry a failed index update; and preview/confirm a complete
index rebuild.

After a document is saved in the inbox, **Suggest folder with local LLM** asks
the configured reasoning role to choose only from approved destinations. The
preview shows the source, target, collision state, reason, and citation/index
effect. Selecting another folder creates a new server-bound preview. Copy or
move occurs only after confirmation and server revalidation. Rebuild the index
after organization to refresh citation paths.

### Ask EOS

Choose **Ask with RAG** for a grounded answer or **Search only** for retrieval
without generation. Select the RAG or reasoning role, optionally include recent
project memory, set the retrieval limit and confidence threshold, and inspect
bounded source excerpts. Full source opening remains restricted to governed
knowledge documents. Empty or weak retrieval produces an explicit no-evidence
state rather than invented support.

### Engineering

Run Code Review, Requirement Review, ADR Draft, or Solution Architecture over
pasted UTF-8 text or a file read by the browser. Optional knowledge retrieval
uses the existing index. Results remain plain text and provide Result, Mermaid
source, and Evidence views plus copy and Markdown download. ADR and architecture
outputs remain visibly marked Draft and never modify reviewed input.

### Models

Refresh the actual configured provider/model status, inspect logical-role
mapping and availability, chat through a selected configured role, generate an
embedding preview, view the non-executing pull plan, and open read-only runtime
configuration.

### Project

Inspect version, structure, runtime, and index status; run governance validation
and diagnostics; preview and confirm initialize/synchronize operations; and
view Settings, Runtime, Structure, Templates, and Skills as read-only JSON.
Mutation previews are revalidated immediately before execution.
If validation reports governance or template errors, initialize/synchronize is
blocked until those errors are resolved; confirmation cannot bypass the gate.

Server lifecycle, configuration-path editing, systemd/port/SSH/Cloudflare host
inspection, deployment, production restart, and ADR approval remain outside the
website.

## Activity and recovery

Only the control that started a request is disabled. Long work uses truthful
indeterminate progress because model and embedding runtimes do not expose a
reliable percentage. The browser stores a bounded summary of recent operations,
not prompts, full documents, or credentials.

If the page reloads during a request, Activity changes it to **Completion
unknown** and never repeats it automatically. Consequential index/project
operations provide a current-state reconciliation action before retry.

## Accessibility and responsive behavior

All controls have labels and visible keyboard focus. Native confirmation and
document dialogs manage modal focus; the knowledge drawer traps focus and
closes with Escape. Below 760px, navigation collapses, columns stack, tables
reduce secondary detail, and the knowledge drawer uses the full viewport width.

## Production data behavior

The browser bundle has no demo-data switch. Every URL, including one with an
old `?demo=1` query parameter, loads current project state from the local API
and calls only the configured runtime. If the API or runtime is unavailable,
the interface reports that state and does not substitute sample results.

Historical implementation screenshots are retained in
[WebUI Screenshots](webui-screenshots/README.md); they are visual records only
and cannot be reproduced through a runtime demo mode.

Security boundaries and CLI equivalents are indexed in
[EOS Command and Web Coverage](COMMAND_COVERAGE.md). Knowledge-specific failure
recovery remains canonical in the
[Knowledge Ingestion Guide](KNOWLEDGE_INGESTION.md).
