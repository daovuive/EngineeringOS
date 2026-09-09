# engineering_os/web_static

[Parent directory](../README.md) · [Structure Governance](../../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

Local, dependency-free browser assets served by the EngineeringOS HTTP adapter.
They provide a small query interface only; the API and RAG behavior remain in
the Python application.

## Extension Rules

Keep assets local and dependency-free. Do not add remote resources, browser
storage, telemetry, or dynamic filesystem routing. Model output must remain
plain text and must never be inserted as HTML.
