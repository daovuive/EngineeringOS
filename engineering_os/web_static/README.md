# engineering_os/web_static

[Parent directory](../README.md) · [Structure Governance](../../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

Local, dependency-free browser assets served by the EngineeringOS HTTP adapter.
They provide task-oriented knowledge query, ingestion, engineering workflow,
and allowlisted EOS action controls. Business rules, filesystem access, model
calls, and RAG behavior remain in the Python application.

The shared shell has five workspaces: Knowledge, Ask EOS, Engineering, Models,
and Project. Every browser session uses the real local API and configured
runtime; the production bundle contains no demo-data mode. See the canonical
[WebUI Guide](../../docs/WEBUI_GUIDE.md).

## Extension Rules

Keep assets local and dependency-free. Do not add remote resources, telemetry,
credentials, prompts, knowledge bodies, or dynamic filesystem routing to
browser storage. The bounded last-action status/result may use `localStorage`;
an in-flight marker must become completion-unknown after reload and must never
replay a mutation automatically. Model output must remain plain text and must
never be inserted as HTML.
