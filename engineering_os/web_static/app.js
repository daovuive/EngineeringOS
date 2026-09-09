"use strict";

const queryElement = document.getElementById("query");
const askButton = document.getElementById("ask");
const loadingElement = document.getElementById("loading");
const errorElement = document.getElementById("error");
const answerElement = document.getElementById("answer");
const answerStatusElement = document.getElementById("answer-status");
const sourcesSectionElement = document.getElementById("sources-section");
const sourcesElement = document.getElementById("sources");

function showError(message) {
  errorElement.textContent = message;
  errorElement.hidden = false;
}

function clearError() {
  errorElement.textContent = "";
  errorElement.hidden = true;
}

function clearSources() {
  sourcesElement.replaceChildren();
  sourcesSectionElement.hidden = true;
}

function renderSources(sources) {
  clearSources();
  if (!Array.isArray(sources) || sources.length === 0) {
    return;
  }

  for (const source of sources) {
    const item = document.createElement("li");
    item.textContent = String(source);
    sourcesElement.append(item);
  }
  sourcesSectionElement.hidden = false;
}

async function askQuestion() {
  if (askButton.disabled) {
    return;
  }

  const query = queryElement.value;
  if (!query.trim()) {
    showError("Enter a question before asking.");
    return;
  }

  askButton.disabled = true;
  loadingElement.hidden = false;
  clearError();
  answerElement.textContent = "";
  answerStatusElement.textContent = "Waiting for answer";
  clearSources();

  try {
    const response = await fetch("/api/v1/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify({ query }),
    });
    const payload = await response.json().catch(() => null);
    if (!response.ok || !payload || typeof payload.answer !== "string") {
      const message = payload?.error?.message;
      throw new Error(typeof message === "string" ? message : "Unable to process query.");
    }

    answerElement.textContent = payload.answer;
    answerStatusElement.textContent = payload.answer_status === "insufficient_evidence"
      ? "Insufficient evidence"
      : "Answered";
    renderSources(payload.sources);
  } catch (error) {
    answerStatusElement.textContent = "No answer available";
    showError(error instanceof Error ? error.message : "Unable to process query.");
  } finally {
    loadingElement.hidden = true;
    askButton.disabled = false;
  }
}

askButton.addEventListener("click", askQuestion);
queryElement.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && event.ctrlKey) {
    event.preventDefault();
    askQuestion();
  }
});
