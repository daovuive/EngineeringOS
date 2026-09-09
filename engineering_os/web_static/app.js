"use strict";

const $ = (id) => document.getElementById(id);
const state = {
  screen: "knowledge",
  askMode: "rag",
  workflow: "code-review",
  workflowResult: "",
  workflowSources: [],
  resultTab: "proposal",
  retryPath: null,
  organizationPreview: null,
  organizeMove: false,
  pendingConfirmation: null,
  activities: [],
  drawerOpener: null,
};
const ACTIVITY_KEY = "engineeringos.activity.v2";

function element(tag, className, textValue) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (textValue !== undefined) node.textContent = String(textValue);
  return node;
}

function clear(node) {
  node.replaceChildren();
  return node;
}

function showError(message) {
  const target = $("error");
  target.textContent = message;
  target.hidden = false;
  window.setTimeout(() => { target.hidden = true; }, 7000);
}

function showToast(message) {
  const target = $("toast");
  target.textContent = message;
  target.hidden = false;
  window.setTimeout(() => { target.hidden = true; }, 3500);
}

async function requestJson(path, options = {}) {
  const response = await fetch(path, { credentials: "same-origin", ...options });
  const payload = await response.json().catch(() => null);
  if (!response.ok && response.status !== 207) {
    throw new Error(payload?.error?.message || "EngineeringOS could not complete the request.");
  }
  return { payload, status: response.status };
}

async function action(actionId, values = {}) {
  const { payload } = await requestJson(`/api/v1/actions/${actionId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ values }),
  });
  return payload.result;
}

function persistActivities() {
  const safe = state.activities.slice(0, 8).map((item) => ({
    id: item.id,
    action: item.action,
    label: item.label,
    status: item.status,
    timestamp: item.timestamp,
    summary: String(item.summary || "").slice(0, 600),
    reconciliation: item.reconciliation || null,
  }));
  try {
    window.localStorage.setItem(ACTIVITY_KEY, JSON.stringify(safe));
  } catch (_) {
    // Activity remains available for this page when browser storage is disabled.
  }
}

function restoreActivities() {
  try {
    const stored = JSON.parse(window.localStorage.getItem(ACTIVITY_KEY));
    if (!Array.isArray(stored)) return;
    state.activities = stored.slice(0, 8).map((item) => ({
      ...item,
      status: item.status === "running" ? "unknown" : item.status,
      summary: item.status === "running"
        ? "The page reloaded before a final result was received. Check current state before retrying."
        : item.summary,
    }));
  } catch (_) {
    state.activities = [];
  }
}

function activitySummary(result) {
  if (!result || typeof result !== "object") return String(result || "Completed");
  if (typeof result.outcome === "string") return result.outcome;
  if (typeof result.report === "string") return result.report.slice(0, 500);
  if (typeof result.response === "string") return result.response.slice(0, 500);
  if (typeof result.effect === "string") return result.effect;
  if (typeof result.chunk_count === "number") return `${result.chunk_count} chunks indexed`;
  if (typeof result.error_count === "number") return result.error_count ? `${result.error_count} governance issues` : "Governance validation passed";
  return "Completed successfully";
}

function startActivity(actionId, label, reconciliation = null) {
  const item = {
    id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    action: actionId,
    label,
    status: "running",
    timestamp: new Date().toISOString(),
    summary: "Operation is running. No percentage is available.",
    reconciliation,
  };
  state.activities.unshift(item);
  state.activities = state.activities.slice(0, 8);
  persistActivities();
  renderActivities();
  $("progress-label").textContent = label;
  $("global-progress").hidden = false;
  return item;
}

function finishActivity(item, status, result) {
  item.status = status;
  item.summary = status === "completed" ? activitySummary(result) : String(result || "Operation failed").slice(0, 600);
  item.timestamp = new Date().toISOString();
  persistActivities();
  renderActivities();
  $("global-progress").hidden = true;
}

async function runOperation(actionId, label, callback, reconciliation = null) {
  const item = startActivity(actionId, label, reconciliation);
  try {
    const result = await callback();
    finishActivity(item, "completed", result);
    return result;
  } catch (error) {
    const message = error instanceof Error ? error.message : "Operation failed.";
    finishActivity(item, "failed", message);
    showError(message);
    throw error;
  }
}

function renderActivities() {
  $("activity-count").textContent = String(state.activities.length);
  for (const target of [$("activity-list"), $("project-activity")]) {
    clear(target);
    if (!state.activities.length) {
      target.append(element("p", "muted", "No activity recorded in this browser."));
      continue;
    }
    for (const item of state.activities) {
      const card = element("article", "activity-card");
      const status = element("span", `activity-state ${item.status}`, item.status === "unknown" ? "● Completion unknown" : item.status === "running" ? "◌ Running…" : item.status === "failed" ? "● Failed" : "● Completed");
      card.append(status, element("strong", "", item.label), element("p", "", item.summary), element("small", "muted", new Date(item.timestamp).toLocaleString()));
      if (item.status === "unknown" && item.reconciliation) {
        const button = element("button", "button full", "Check current state");
        button.type = "button";
        button.addEventListener("click", () => reconcileActivity(item));
        card.append(button);
      }
      target.append(card);
    }
  }
}

async function reconcileActivity(item) {
  try {
    const result = await action(item.reconciliation, {});
    finishActivity(item, "completed", result);
    showToast("Current state checked. Review the result before retrying.");
  } catch (_) {
    // The shared request helper already surfaced the safe failure.
  }
}

function switchScreen(name) {
  state.screen = name;
  document.querySelectorAll(".screen").forEach((node) => node.classList.toggle("active", node.id === `screen-${name}`));
  document.querySelectorAll(".nav-item[data-screen]").forEach((node) => node.classList.toggle("active", node.dataset.screen === name));
  const screen = $(`screen-${name}`);
  $("breadcrumb-section").textContent = screen.dataset.title;
  $("breadcrumb-page").textContent = screen.dataset.page;
  $("sidebar").classList.remove("open");
  $("mobile-menu").setAttribute("aria-expanded", "false");
  if (name === "knowledge") loadDocuments();
  if (name === "models") loadModelStatus();
  if (name === "project") loadProjectHealth();
}

function openDrawer() {
  state.drawerOpener = document.activeElement;
  $("drawer-backdrop").hidden = false;
  $("knowledge-drawer").hidden = false;
  $("drawer-close").focus();
}

function closeDrawer() {
  $("drawer-backdrop").hidden = true;
  $("knowledge-drawer").hidden = true;
  if (state.drawerOpener instanceof HTMLElement) state.drawerOpener.focus();
}

function formatBytes(value) {
  if (value < 1024) return `${value} B`;
  return `${(value / 1024).toFixed(value < 10240 ? 1 : 0)} KB`;
}

async function loadDocuments() {
  const params = new URLSearchParams();
  if ($("document-search").value.trim()) params.set("query", $("document-search").value.trim());
  if ($("folder-filter").value) params.set("folder", $("folder-filter").value);
  try {
    const { payload } = await requestJson(`/api/v1/knowledge/documents?${params}`);
    $("knowledge-total").textContent = String(payload.summary.documents);
    $("knowledge-indexed").textContent = String(payload.summary.indexed);
    $("knowledge-attention").textContent = String(payload.summary.needs_attention);
    const previousFolder = $("folder-filter").value;
    clear($("folder-filter")).append(new Option("All folders", ""));
    payload.folders.forEach((folder) => $("folder-filter").append(new Option(folder, folder)));
    $("folder-filter").value = previousFolder;
    renderDocumentRows(payload.documents);
    const warning = payload.index_error || (payload.summary.needs_attention ? `${payload.summary.needs_attention} document(s) are saved but not present in the compatible index.` : "");
    $("knowledge-warning").hidden = !warning;
    $("knowledge-warning-text").textContent = warning;
  } catch (error) {
    clear($("document-list")).append(documentRowMessage("Unable to load the knowledge library."));
    showError(error instanceof Error ? error.message : "Unable to load documents.");
  }
}

function documentRowMessage(message) {
  const row = element("tr");
  const cell = element("td", "empty-state", message);
  cell.colSpan = 4;
  row.append(cell);
  return row;
}

function renderDocumentRows(documents) {
  const body = clear($("document-list"));
  if (!documents.length) {
    body.append(documentRowMessage("No documents match these filters."));
    return;
  }
  for (const documentItem of documents) {
    const row = element("tr", "document-row");
    row.tabIndex = 0;
    const nameCell = element("td");
    nameCell.append(element("span", "document-name", `▤  ${documentItem.name}`));
    const folderCell = element("td", "document-folder", documentItem.folder);
    const statusCell = element("td");
    const status = element("span", `document-status ${documentItem.status}`);
    status.append(element("span", `status-dot ${documentItem.status === "indexed" ? "success" : "warning"}`), document.createTextNode(documentItem.status === "indexed" ? `Indexed · ${documentItem.chunk_count} chunks` : "Saved only"));
    statusCell.append(status);
    const actionCell = element("td", "", "›");
    const inspect = () => openDocumentDialog(documentItem.path);
    row.addEventListener("click", inspect);
    row.addEventListener("keydown", (event) => { if (event.key === "Enter") inspect(); });
    row.append(nameCell, folderCell, statusCell, actionCell);
    body.append(row);
  }
}

async function openDocumentDialog(path) {
  try {
    const response = await fetch(`/api/v1/knowledge/document?${new URLSearchParams({ path })}`, { credentials: "same-origin" });
    if (!response.ok) throw new Error("Unable to open the selected knowledge document.");
    const content = await response.text();
    $("document-title").textContent = path.split("/").pop();
    $("document-path").textContent = path;
    $("document-content").textContent = content;
    $("document-open-raw").href = `/api/v1/knowledge/document?${new URLSearchParams({ path })}`;
    $("document-dialog").showModal();
  } catch (error) {
    showError(error instanceof Error ? error.message : "Unable to open document.");
  }
}

async function readIngestionInput() {
  const file = $("ingest-file").files[0];
  const pasted = $("ingest-text").value;
  const uploadMode = !$("upload-panel").hidden;
  if (uploadMode) {
    if (!file) throw new Error("Choose one Markdown or text file.");
    if (file.size > 2 * 1024 * 1024) throw new Error("Upload exceeds the 2 MiB limit.");
    return { content: new TextDecoder("utf-8", { fatal: true }).decode(await file.arrayBuffer()), filename: file.name };
  }
  if (!pasted.trim()) throw new Error("Paste knowledge text before saving.");
  return { content: pasted };
}

async function submitIngestion() {
  if ($("ingest").disabled) return;
  $("ingest").disabled = true;
  $("retry-index").hidden = true;
  try {
    const input = await readIngestionInput();
    const result = await runOperation("knowledge.ingest", "Saving knowledge", async () => {
      const { payload } = await requestJson("/api/v1/knowledge/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...input, title: $("ingest-title").value.trim() || undefined, auto_index: $("auto-index").checked }),
      });
      return payload;
    }, "knowledge.index-status");
    state.retryPath = result.document_path;
    $("suggest-folder").disabled = false;
    $("open-document").href = result.open_url;
    $("open-document").hidden = false;
    if (result.indexing_state === "failed") {
      $("ingest-status").textContent = `Document saved. Indexing failed: ${result.error || "unknown error"}`;
      $("retry-index").hidden = false;
    } else if (result.indexing_state === "skipped") {
      $("ingest-status").textContent = `Saved at ${result.document_path}. Indexing was skipped.`;
    } else {
      $("ingest-status").textContent = `Ready for RAG · ${result.chunk_count} chunks`;
    }
    showToast("Knowledge saved.");
    loadDocuments();
  } catch (_) {
    $("ingest-status").textContent = "Knowledge was not saved.";
  } finally {
    $("ingest").disabled = false;
  }
}

async function retryIndexing() {
  if (!state.retryPath || $("retry-index").disabled) return;
  $("retry-index").disabled = true;
  try {
    const result = await runOperation("knowledge.retry-index", "Retrying knowledge indexing", async () => {
      const { payload } = await requestJson("/api/v1/knowledge/retry-index", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ document_path: state.retryPath }),
      });
      return payload;
    }, "knowledge.index-status");
    if (result.indexing_state === "failed") {
      $("ingest-status").textContent = `Document remains saved. Indexing failed: ${result.error || "unknown error"}`;
    } else {
      $("ingest-status").textContent = `Ready for RAG · ${result.chunk_count} chunks`;
      $("retry-index").hidden = true;
    }
    loadDocuments();
  } catch (_) {
    // Error is already visible and the saved document remains available.
  } finally {
    $("retry-index").disabled = false;
  }
}

async function suggestFolder(destination = null) {
  if (!state.retryPath) {
    showError("Save the document first, then request an approved folder suggestion.");
    return;
  }
  $("suggest-folder").disabled = true;
  try {
    const values = { document_path: state.retryPath };
    if (destination) values.destination = destination;
    const preview = await runOperation("knowledge.organize-preview", destination ? "Updating folder preview" : "Suggesting an approved folder", () => action("knowledge.organize-preview", values));
    state.organizationPreview = preview;
    renderFolderPreview(preview);
  } catch (_) {
    // Safe error is already visible.
  } finally {
    $("suggest-folder").disabled = false;
  }
}

function renderFolderPreview(preview) {
  $("folder-preview").hidden = false;
  $("folder-preview-path").textContent = `${preview.destination}/${preview.filename}`;
  $("folder-preview-reason").textContent = preview.reason;
  $("folder-preview-effect").textContent = preview.collision === "blocked" ? "The target already exists. Choose another approved folder." : preview.index_effect;
  clear($("folder-choice"));
  preview.allowed_destinations.forEach((path) => $("folder-choice").append(new Option(path, path)));
  $("folder-choice").value = preview.destination;
  $("organize-apply").disabled = preview.collision === "blocked";
}

function selectOrganizeMode(move) {
  state.organizeMove = move;
  $("organize-copy").classList.toggle("active", !move);
  $("organize-move").classList.toggle("active", move);
}

function applyOrganization() {
  const preview = state.organizationPreview;
  if (!preview) return;
  openConfirmation({
    title: `${state.organizeMove ? "Move" : "Copy"} knowledge document?`,
    description: "The source, approved destination, and document hash will be revalidated before placement.",
    plan: `${preview.document_path}\n→ ${preview.destination}/${preview.filename}\n\nIndex effect: ${preview.index_effect}`,
    label: state.organizeMove ? "Confirm move" : "Confirm copy",
    callback: async () => {
      const result = await runOperation("knowledge.organize-apply", "Organizing knowledge", () => action("knowledge.organize-apply", {
        document_path: preview.document_path,
        destination: preview.destination,
        source_sha256: preview.source_sha256,
        preview_token: preview.preview_token,
        reason: preview.reason,
        move: state.organizeMove,
        confirmed: true,
      }), "knowledge.index-status");
      $("ingest-status").textContent = `${result.action}: ${result.destination}. Rebuild the index to refresh citations.`;
      state.organizationPreview = null;
      $("folder-preview").hidden = true;
      showToast("Knowledge organization completed.");
      loadDocuments();
    },
  });
}

async function previewIndexRebuild() {
  try {
    const preview = await action("knowledge.index-preview", {});
    openConfirmation({
      title: "Rebuild knowledge index?",
      description: `${preview.document_count} governed Markdown document(s) will be embedded. The previous valid index remains until the complete replacement is ready.`,
      plan: `${preview.documents.slice(0, 12).join("\n")}${preview.documents.length > 12 ? `\n… and ${preview.documents.length - 12} more` : ""}\n\n${preview.effect}`,
      label: "Confirm rebuild",
      callback: async () => {
        const result = await runOperation("knowledge.index", "Rebuilding knowledge index", () => action("knowledge.index", { confirmed: true, preview_token: preview.preview_token }), "knowledge.index-status");
        showToast(`${result.chunk_count} chunks indexed.`);
        loadDocuments();
      },
    });
  } catch (_) {
    // Safe error is already visible.
  }
}

function openConfirmation({ title, description, plan, label, callback }) {
  $("confirm-title").textContent = title;
  $("confirm-description").textContent = description;
  $("confirm-plan").textContent = plan;
  $("confirm-submit").textContent = label;
  state.pendingConfirmation = callback;
  $("confirm-dialog").showModal();
}

function addMessage(target, kind, title, content) {
  const message = element("article", `message ${kind}`);
  const head = element("div", "message-head");
  head.append(element("strong", "", title), element("small", "muted", new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })));
  const body = element("pre", "", content);
  message.append(head, body);
  target.append(message);
}

async function submitAsk() {
  const query = $("ask-input").value.trim();
  if (!query || $("ask-submit").disabled) {
    if (!query) showError("Enter a question or search query.");
    return;
  }
  $("ask-submit").disabled = true;
  const conversation = $("ask-conversation");
  if (conversation.querySelector(".empty-conversation")) clear(conversation);
  addMessage(conversation, "user", "You", query);
  clear($("ask-sources"));
  try {
    if (state.askMode === "search") {
      const result = await runOperation("knowledge.search", "Searching knowledge", () => action("knowledge.search", { query, limit: Number($("ask-limit").value), include_memory: $("ask-memory").checked }));
      addMessage(conversation, "eos", "EOS · Search results", result.results.length ? `${result.results.length} matching source(s)` : "No indexed evidence met the search request.");
      const details = result.results.map((item) => ({ ...item, path: item.source.split("#", 1)[0], heading: item.source.split("#").slice(1).join("#"), excerpt: item.preview, open_url: `/api/v1/knowledge/document?${new URLSearchParams({ path: item.source.split("#", 1)[0] })}` }));
      renderAskSources(details);
    } else {
      const body = {
        query,
        limit: Number($("ask-limit").value),
        confidence_threshold: Number($("ask-confidence").value),
        include_memory: $("ask-memory").checked,
        role: $("ask-role").value,
      };
      const response = await runOperation("knowledge.ask", "Asking EngineeringOS", async () => (await requestJson("/api/v1/query", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })).payload);
      addMessage(conversation, "eos", response.answer_status === "insufficient_evidence" ? "EOS · More evidence needed" : "EOS · Grounded answer", response.answer);
      renderAskSources(response.source_details || []);
    }
  } catch (_) {
    addMessage(conversation, "eos", "EOS · No result", "The request did not complete. Review Activity before retrying a long operation.");
  } finally {
    $("ask-submit").disabled = false;
  }
}

function renderAskSources(details) {
  const target = clear($("ask-sources"));
  details.forEach((detail, index) => {
    const button = element("button", "source-card");
    button.type = "button";
    button.append(element("strong", "", `[${index + 1}] ${detail.heading || detail.path}`), element("small", "", detail.path));
    button.addEventListener("click", () => previewSource(detail));
    target.append(button);
  });
  if (details[0]) previewSource(details[0]);
}

function previewSource(detail) {
  const target = clear($("ask-source-preview"));
  target.append(element("strong", "", detail.heading || "Source"), element("p", "muted", `Path: ${detail.path}`), element("pre", "", detail.excerpt || "Open the document to inspect the complete source."));
  const link = element("a", "button", "Open document");
  link.href = detail.open_url || `/api/v1/knowledge/document?${new URLSearchParams({ path: detail.path })}`;
  link.target = "_blank";
  link.rel = "noopener";
  target.append(link);
}

const workflowMeta = {
  "code-review": ["Code change", "Provide source code or a diff for review.", "Review result"],
  "requirement-review": ["Requirements", "Provide requirements to inspect for quality and traceability.", "Requirement findings"],
  "adr-assistant": ["Decision brief", "Provide context, drivers, constraints, and alternatives.", "ADR draft"],
  "solution-architect": ["Architecture brief", "Provide the context for your architecture proposal.", "Solution proposal"],
};

function selectWorkflow(workflow) {
  state.workflow = workflow;
  document.querySelectorAll("[data-workflow]").forEach((node) => node.classList.toggle("active", node.dataset.workflow === workflow));
  const meta = workflowMeta[workflow];
  $("workflow-input-title").textContent = meta[0];
  $("workflow-input-help").textContent = meta[1];
  $("workflow-result-title").textContent = meta[2];
  $("workflow-draft").hidden = !["adr-assistant", "solution-architect"].includes(workflow);
}

async function submitWorkflow() {
  const input = $("workflow-input").value.trim();
  if (!input || $("workflow-submit").disabled) {
    if (!input) showError("Provide workflow input before running.");
    return;
  }
  $("workflow-submit").disabled = true;
  try {
    const response = await runOperation(state.workflow, `Running ${workflowMeta[state.workflow][2]}`, async () => (await requestJson(`/api/v1/workflows/${state.workflow}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input, source_name: $("workflow-file").files[0]?.name || "web-input", with_knowledge: $("workflow-knowledge").checked, knowledge_query: $("workflow-knowledge-query").value.trim() || undefined }),
    })).payload);
    state.workflowResult = response.result;
    state.workflowSources = response.sources || [];
    state.resultTab = "proposal";
    renderWorkflowResult();
    showToast("Workflow completed.");
  } catch (_) {
    state.workflowResult = "The workflow did not return a validated result.";
    renderWorkflowResult();
  } finally {
    $("workflow-submit").disabled = false;
  }
}

function mermaidSource(value) {
  const match = value.match(/```mermaid\s*([\s\S]*?)```/i);
  return match ? match[1].trim() : "No Mermaid source was present in this result.";
}

function renderWorkflowResult() {
  document.querySelectorAll("[data-result-tab]").forEach((node) => node.classList.toggle("active", node.dataset.resultTab === state.resultTab));
  const target = clear($("workflow-result"));
  if (state.resultTab === "evidence") {
    if (!state.workflowSources.length) target.append(element("p", "muted", "No project knowledge was cited for this result."));
    state.workflowSources.forEach((source, index) => {
      const button = element("button", "source-card full", `[${index + 1}] ${source}`);
      button.type = "button";
      button.addEventListener("click", () => openDocumentDialog(source.split("#", 1)[0]));
      target.append(button);
    });
    return;
  }
  target.append(element("pre", "", state.resultTab === "mermaid" ? mermaidSource(state.workflowResult) : state.workflowResult || "Run a workflow to see its validated output."));
}

async function copyWorkflowResult() {
  if (!state.workflowResult) return;
  try {
    await navigator.clipboard.writeText(state.resultTab === "mermaid" ? mermaidSource(state.workflowResult) : state.workflowResult);
    showToast("Result copied.");
  } catch (_) {
    showError("Clipboard access is unavailable. Select the plain-text result manually.");
  }
}

function downloadWorkflowResult() {
  if (!state.workflowResult) return;
  const blob = new Blob([state.workflowResult], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${state.workflow}-draft.md`;
  link.click();
  URL.revokeObjectURL(url);
}

async function loadModelStatus() {
  try {
    const result = await runOperation("llm.status", "Refreshing local model status", () => action("llm.status", {}));
    $("model-provider").textContent = result.provider;
    $("model-connection").textContent = "Available";
    $("model-connection-dot").className = "status-dot success";
    const roles = Object.entries(result.configured_models);
    $("model-configured").textContent = `${roles.length} models`;
    $("model-installed").textContent = `${result.available_models.length} models`;
    const body = clear($("model-role-list"));
    roles.forEach(([role, model]) => {
      const row = element("tr");
      const available = result.available_models.includes(model);
      row.append(element("td", "", role), element("td", "", model), element("td", available ? "document-status indexed" : "document-status", available ? "● Installed" : "○ Unavailable"));
      body.append(row);
    });
    updateChatModel(result.configured_models);
    $("health-runtime-state").textContent = "Available";
  } catch (_) {
    $("model-connection").textContent = "Unavailable";
    $("model-connection-dot").className = "status-dot warning";
    $("health-runtime-state").textContent = "Unavailable";
  }
}

function updateChatModel(models = null) {
  if (models) $("chat-role").dataset.models = JSON.stringify(models);
  try {
    const mapped = JSON.parse($("chat-role").dataset.models || "{}");
    $("chat-model-name").textContent = mapped[$("chat-role").value] || `${$("chat-role").value} role`;
  } catch (_) {
    $("chat-model-name").textContent = `${$("chat-role").value} role`;
  }
}

async function submitChat() {
  const prompt = $("chat-input").value.trim();
  if (!prompt || $("chat-submit").disabled) {
    if (!prompt) showError("Enter a message for the selected model.");
    return;
  }
  $("chat-submit").disabled = true;
  addMessage($("chat-messages"), "user", "You", prompt);
  try {
    const result = await runOperation("llm.chat", "Running local model chat", () => action("llm.chat", { prompt, role: $("chat-role").value }));
    addMessage($("chat-messages"), "eos", $("chat-model-name").textContent, result.response);
  } catch (_) {
    addMessage($("chat-messages"), "eos", "Model unavailable", "The configured runtime did not return a response.");
  } finally {
    $("chat-submit").disabled = false;
  }
}

async function generateEmbedding() {
  const textValue = $("embedding-input").value.trim();
  if (!textValue) { showError("Enter text to embed."); return; }
  try {
    const result = await runOperation("llm.embed", "Generating embedding", () => action("llm.embed", { text: textValue }));
    $("embedding-result").textContent = `Dimensions: ${result.dimensions}\nPreview: ${result.preview.join(", ")}`;
  } catch (_) { /* Safe error is already visible. */ }
}

async function showPullPlan() {
  try {
    const result = await action("llm.pull-plan", {});
    $("pull-plan-result").textContent = result.commands.length ? result.commands.join("\n") : "All configured models have no pending pull plan.";
  } catch (error) { showError(error instanceof Error ? error.message : "Unable to load pull plan."); }
}

async function loadProjectHealth() {
  try {
    const [version, validation, indexStatus] = await Promise.all([action("project.version", {}), action("project.validate", {}), action("knowledge.index-status", {})]);
    $("project-version").textContent = `Version · ${version.version}`;
    $("health-structure-state").textContent = validation.ok ? "Healthy" : `${validation.error_count} issue(s)`;
    $("health-knowledge-state").textContent = indexStatus.available ? `${indexStatus.document_count} documents · ${indexStatus.chunk_count} chunks` : "Index unavailable";
  } catch (_) {
    $("health-structure-state").textContent = "Status unavailable";
  }
  renderConfigurationRows();
}

async function validateProject() {
  try {
    const result = await runOperation("project.validate", "Validating project governance", () => action("project.validate", {}));
    $("health-structure-state").textContent = result.ok ? "Healthy" : `${result.error_count} issue(s)`;
    showToast(result.ok ? "Governance validation passed." : `Validation found ${result.error_count} issue(s).`);
  } catch (_) { /* Safe error is already visible. */ }
}

async function previewProjectMutation(operation) {
  try {
    const preview = await action("project.preview", { operation });
    if (preview.blocked) {
      const reasons = preview.governance_errors?.length
        ? ` ${preview.governance_errors.join(" ")}`
        : " Resolve template registry errors before retrying.";
      showError(`Project changes are blocked by governance.${reasons}`);
      return;
    }
    const changes = [...preview.folders.map((path) => `Folder  ${path}`), ...preview.files.map((path) => `File    ${path}`)];
    openConfirmation({
      title: `${operation === "init" ? "Initialize" : "Synchronize"} missing structure?`,
      description: `${preview.folder_count} folder(s) and ${preview.file_count} file(s) are missing. Existing content will be kept.`,
      plan: changes.length ? changes.join("\n") : "No missing governed content. Confirmation will make no changes.",
      label: operation === "init" ? "Confirm creation" : "Confirm synchronization",
      callback: async () => {
        const result = await runOperation(`project.${operation}`, `${operation === "init" ? "Initializing" : "Synchronizing"} governed content`, () => action(`project.${operation}`, { confirmed: true, preview_token: preview.preview_token }), "project.validate");
        showToast(result.created_count ? `${result.created_count} governed item(s) created.` : "Project structure was already current.");
        loadProjectHealth();
      },
    });
  } catch (_) { /* Safe error is already visible. */ }
}

async function runDoctor() {
  try {
    const result = await runOperation("project.doctor", "Running project diagnostics", () => action("project.doctor", {}));
    openTextDialog("Project diagnostics", "Read-only diagnostic report", result.report);
  } catch (_) { /* Safe error is already visible. */ }
}

function renderConfigurationRows() {
  const target = clear($("config-list"));
  for (const name of ["settings", "runtime", "structure", "templates", "skills"]) {
    const button = element("button", "configuration-row");
    button.type = "button";
    button.append(element("span", "", `${name[0].toUpperCase()}${name.slice(1)}`), element("span", "", "›"));
    button.addEventListener("click", () => showConfiguration(name));
    target.append(button);
  }
}

async function showConfiguration(name) {
  try {
    const result = await action("config.show", { name });
    openTextDialog(`${name[0].toUpperCase()}${name.slice(1)} configuration`, "Read-only project configuration", JSON.stringify(result.config, null, 2));
  } catch (error) { showError(error instanceof Error ? error.message : "Unable to load configuration."); }
}

function openTextDialog(title, path, content) {
  $("document-title").textContent = title;
  $("document-path").textContent = path;
  $("document-content").textContent = content;
  $("document-open-raw").hidden = true;
  $("document-dialog").showModal();
  $("document-dialog").addEventListener("close", () => { $("document-open-raw").hidden = false; }, { once: true });
}

function bindEvents() {
  document.querySelectorAll(".nav-item[data-screen]").forEach((button) => button.addEventListener("click", () => switchScreen(button.dataset.screen)));
  $("mobile-menu").addEventListener("click", () => { const open = $("sidebar").classList.toggle("open"); $("mobile-menu").setAttribute("aria-expanded", String(open)); });
  $("activity-open").addEventListener("click", () => { $("activity-drawer").hidden = false; $("activity-close").focus(); });
  $("activity-close").addEventListener("click", () => { $("activity-drawer").hidden = true; $("activity-open").focus(); });
  $("add-knowledge-open").addEventListener("click", openDrawer);
  $("drawer-close").addEventListener("click", closeDrawer);
  $("drawer-cancel").addEventListener("click", closeDrawer);
  $("drawer-backdrop").addEventListener("click", closeDrawer);
  $("upload-tab").addEventListener("click", () => setIngestionTab(true));
  $("paste-tab").addEventListener("click", () => setIngestionTab(false));
  $("ingest-file").addEventListener("change", () => { const file = $("ingest-file").files[0]; $("selected-file").hidden = !file; $("selected-file-name").textContent = file?.name || ""; $("selected-file-size").textContent = file ? formatBytes(file.size) : ""; });
  $("auto-index").addEventListener("change", () => { $("ingest").textContent = $("auto-index").checked ? "Save & index" : "Save knowledge"; });
  $("ingest").addEventListener("click", submitIngestion);
  $("retry-index").addEventListener("click", retryIndexing);
  $("suggest-folder").addEventListener("click", () => suggestFolder());
  $("folder-choice").addEventListener("change", () => suggestFolder($("folder-choice").value));
  $("organize-copy").addEventListener("click", () => selectOrganizeMode(false));
  $("organize-move").addEventListener("click", () => selectOrganizeMode(true));
  $("organize-apply").addEventListener("click", applyOrganization);
  $("rebuild-index").addEventListener("click", previewIndexRebuild);
  $("warning-action").addEventListener("click", previewIndexRebuild);
  let searchTimer;
  $("document-search").addEventListener("input", () => { window.clearTimeout(searchTimer); searchTimer = window.setTimeout(loadDocuments, 180); });
  $("folder-filter").addEventListener("change", loadDocuments);
  $("ask-rag-tab").addEventListener("click", () => setAskMode("rag"));
  $("ask-search-tab").addEventListener("click", () => setAskMode("search"));
  $("ask-confidence").addEventListener("input", () => { $("ask-confidence-value").textContent = Number($("ask-confidence").value).toFixed(2); });
  $("ask-submit").addEventListener("click", submitAsk);
  $("ask-input").addEventListener("keydown", (event) => { if (event.key === "Enter" && event.ctrlKey) { event.preventDefault(); submitAsk(); } });
  document.querySelectorAll("[data-workflow]").forEach((button) => button.addEventListener("click", () => selectWorkflow(button.dataset.workflow)));
  $("workflow-paste-tab").addEventListener("click", () => setWorkflowInputMode(true));
  $("workflow-upload-tab").addEventListener("click", () => setWorkflowInputMode(false));
  $("workflow-file").addEventListener("change", async () => { const file = $("workflow-file").files[0]; if (file) { try { $("workflow-input").value = new TextDecoder("utf-8", { fatal: true }).decode(await file.arrayBuffer()); } catch (_) { showError("Workflow input file must be valid UTF-8 text."); } } });
  $("workflow-submit").addEventListener("click", submitWorkflow);
  document.querySelectorAll("[data-result-tab]").forEach((button) => button.addEventListener("click", () => { state.resultTab = button.dataset.resultTab; renderWorkflowResult(); }));
  $("workflow-copy").addEventListener("click", copyWorkflowResult);
  $("workflow-download").addEventListener("click", downloadWorkflowResult);
  $("models-refresh").addEventListener("click", loadModelStatus);
  $("chat-role").addEventListener("change", () => updateChatModel());
  $("chat-submit").addEventListener("click", submitChat);
  $("embedding-submit").addEventListener("click", generateEmbedding);
  $("pull-plan").addEventListener("click", showPullPlan);
  $("runtime-config-link").addEventListener("click", () => { switchScreen("project"); showConfiguration("runtime"); });
  $("project-validate").addEventListener("click", validateProject);
  $("project-init").addEventListener("click", () => previewProjectMutation("init"));
  $("project-sync").addEventListener("click", () => previewProjectMutation("sync"));
  $("project-doctor").addEventListener("click", runDoctor);
  $("health-structure").addEventListener("click", validateProject);
  $("health-runtime").addEventListener("click", loadModelStatus);
  $("health-knowledge").addEventListener("click", previewIndexRebuild);
  $("confirm-dialog").addEventListener("close", async () => { const callback = state.pendingConfirmation; state.pendingConfirmation = null; if ($("confirm-dialog").returnValue === "default" && callback) { try { await callback(); } catch (_) { /* The operation already exposed a safe error. */ } } });
  const dropZone = document.querySelector(".drop-zone");
  dropZone.addEventListener("dragover", (event) => { event.preventDefault(); dropZone.classList.add("dragging"); });
  dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragging"));
  dropZone.addEventListener("drop", (event) => {
    event.preventDefault();
    dropZone.classList.remove("dragging");
    if (event.dataTransfer?.files?.length === 1) {
      $("ingest-file").files = event.dataTransfer.files;
      $("ingest-file").dispatchEvent(new Event("change"));
    } else {
      showError("Drop exactly one Markdown or text file.");
    }
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !$("knowledge-drawer").hidden) closeDrawer();
    if (event.key === "Tab" && !$("knowledge-drawer").hidden) trapDrawerFocus(event);
  });
}

function setIngestionTab(upload) {
  $("upload-panel").hidden = !upload;
  $("paste-panel").hidden = upload;
  $("upload-tab").classList.toggle("active", upload);
  $("paste-tab").classList.toggle("active", !upload);
}

function setAskMode(mode) {
  state.askMode = mode;
  $("ask-rag-tab").classList.toggle("active", mode === "rag");
  $("ask-search-tab").classList.toggle("active", mode === "search");
  $("ask-rag-tab").setAttribute("aria-selected", String(mode === "rag"));
  $("ask-search-tab").setAttribute("aria-selected", String(mode === "search"));
  $("ask-submit").setAttribute("aria-label", mode === "rag" ? "Ask with RAG" : "Search knowledge");
}

function setWorkflowInputMode(paste) {
  $("workflow-paste-tab").classList.toggle("active", paste);
  $("workflow-upload-tab").classList.toggle("active", !paste);
  $("workflow-file-label").hidden = paste;
}

function trapDrawerFocus(event) {
  const controls = Array.from($("knowledge-drawer").querySelectorAll("button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), a[href]"));
  if (!controls.length) return;
  const first = controls[0];
  const last = controls[controls.length - 1];
  if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
  if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
}

async function initialize() {
  restoreActivities();
  renderActivities();
  bindEvents();
  selectWorkflow(state.workflow);
  renderConfigurationRows();
  try {
    const { payload } = await requestJson("/health");
    const connected = payload.status === "ok";
    $("connection-label").textContent = connected ? "Application connected" : "Application unavailable";
    $("connection-pill").textContent = connected ? "LOCAL · CONNECTED" : "NOT CONNECTED";
    $("connection-pill").classList.add(connected ? "connected" : "disconnected");
  } catch (_) {
    $("connection-label").textContent = "Application unavailable";
    $("connection-pill").textContent = "NOT CONNECTED";
    $("connection-pill").classList.add("disconnected");
  }
  loadDocuments();
}

initialize();
