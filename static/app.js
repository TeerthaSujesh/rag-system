const form = document.getElementById("query-form");
const input = document.getElementById("question-input");
const askButton = document.getElementById("ask-button");
const statusLine = document.getElementById("status-line");
const chatFeed = document.getElementById("chat-feed");
const emptyState = document.getElementById("empty-state");

let turnCount = 0;

// Generate a unique session ID once and reuse it
const sessionId =
  localStorage.getItem("session_id") || crypto.randomUUID();

localStorage.setItem("session_id", sessionId);

function setStatus(message, isError = false) {
  statusLine.textContent = message;
  statusLine.classList.toggle("is-error", isError);
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function sourceLabel(metadata) {
  if (!metadata) return "unknown source";
  const source = metadata.source || "unknown source";
  if (metadata.page) return `${source} · p.${metadata.page}`;
  return source;
}

function appendTurn(question, data) {
  emptyState.hidden = true;
  turnCount += 1;

  const turn = document.createElement("div");
  turn.className = "turn";
  turn.innerHTML = `
    <div class="message message-user">
      <p>${escapeHtml(question)}</p>
    </div>
    <div class="message message-assistant">
      <p class="answer-label">Answer</p>
      <p class="answer-text">${escapeHtml(data.answer)}</p>
      <p class="answer-source">
        ${
          data.retrieved_results.length > 0
            ? `Source: ${escapeHtml(sourceLabel(data.retrieved_results[0].metadata))}`
            : ""
        }
      </p>
    </div>
  `;

  chatFeed.appendChild(turn);
  chatFeed.scrollTop = chatFeed.scrollHeight;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const question = input.value.trim();
  if (!question) return;

  askButton.disabled = true;
  input.value = "";
  setStatus("Searching the knowledge base…");

  try {
    const response = await fetch("/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        session_id: sessionId,
        question: question,
      }),
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(errorBody.detail || `Request failed (${response.status})`);
    }

    const data = await response.json();
    setStatus("");
    appendTurn(question, data);
  } catch (err) {
    setStatus(err.message || "Something went wrong.", true);
  } finally {
    askButton.disabled = false;
    input.focus();
  }
});