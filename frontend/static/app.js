/* ===== Renty AI Analytics — ChatGPT-style frontend ===== */
"use strict";

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];

const SUGGESTIONS = [
  { title: "Top branches by contracts", text: "Show me the top 5 branches by total contracts in 2025" },
  { title: "Monthly contract trend", text: "What is the monthly contract trend for 2025?" },
  { title: "Bookings by category", text: "Break down bookings by vehicle category for the last 12 months" },
  { title: "Utilization overview", text: "What does fleet utilization look like across the main branches?" },
];

const State = {
  conversations: {},   // id -> {id, title, messages: [{role, content, meta}], updated}
  activeId: null,
  streaming: false,
  abort: null,
};

/* ---------- persistence ---------- */
const STORE_KEY = "renty_conversations_v1";
function loadStore() {
  try {
    const raw = localStorage.getItem(STORE_KEY);
    if (raw) {
      const data = JSON.parse(raw);
      State.conversations = data.conversations || {};
      State.activeId = data.activeId || null;
    }
  } catch (e) { console.warn("store load failed", e); }
}
function saveStore() {
  try {
    localStorage.setItem(STORE_KEY, JSON.stringify({
      conversations: State.conversations,
      activeId: State.activeId,
    }));
  } catch (e) { console.warn("store save failed", e); }
}

/* ---------- conversation helpers ---------- */
function newConversation() {
  const id = "c_" + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
  State.conversations[id] = { id, title: "New chat", messages: [], updated: Date.now() };
  State.activeId = id;
  saveStore();
  return id;
}
function activeConv() {
  if (!State.activeId || !State.conversations[State.activeId]) {
    newConversation();
  }
  return State.conversations[State.activeId];
}
function deleteConversation(id) {
  delete State.conversations[id];
  if (State.activeId === id) {
    const ids = Object.keys(State.conversations).sort((a, b) => State.conversations[b].updated - State.conversations[a].updated);
    State.activeId = ids[0] || null;
  }
  if (!State.activeId) newConversation();
  saveStore();
  renderSidebar();
  renderThread();
}

/* ---------- minimal, safe markdown ---------- */
function escapeHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
          .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
function renderInline(text) {
  let t = escapeHtml(text);
  // inline code
  t = t.replace(/`([^`]+)`/g, (_, c) => `<code class="inline">${c}</code>`);
  // bold then italic
  t = t.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  t = t.replace(/(^|[^*])\*([^*]+)\*/g, "$1<em>$2</em>");
  // links [text](url)
  t = t.replace(/\[([^\]]+)\]\((https?:[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  return t;
}
function renderMarkdown(src) {
  if (!src) return "";
  const lines = src.replace(/\r\n/g, "\n").split("\n");
  let html = "", i = 0;
  const flushList = (buf, ordered) => {
    if (!buf.length) return "";
    const tag = ordered ? "ol" : "ul";
    return `<${tag}>` + buf.map(x => `<li>${renderInline(x)}</li>`).join("") + `</${tag}>`;
  };
  while (i < lines.length) {
    let line = lines[i];

    // fenced code block
    const fence = line.match(/^```(\w*)/);
    if (fence) {
      const lang = fence[1] || "";
      const code = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) { code.push(lines[i]); i++; }
      i++; // skip closing
      html += codeBlockHtml(code.join("\n"), lang);
      continue;
    }

    // table (header | --- | rows)
    if (/\|/.test(line) && i + 1 < lines.length && /^\s*\|?[\s:|-]+\|[\s:|-]+/.test(lines[i + 1])) {
      const header = line.split("|").map(s => s.trim()).filter((s, idx, arr) => !(idx === 0 && s === "") && !(idx === arr.length - 1 && s === ""));
      i += 2;
      const rows = [];
      while (i < lines.length && /\|/.test(lines[i])) {
        const cells = lines[i].split("|").map(s => s.trim());
        if (cells[0] === "") cells.shift();
        if (cells[cells.length - 1] === "") cells.pop();
        rows.push(cells); i++;
      }
      html += "<table><thead><tr>" + header.map(h => `<th>${renderInline(h)}</th>`).join("") + "</tr></thead><tbody>";
      html += rows.map(r => "<tr>" + r.map(c => `<td>${renderInline(c)}</td>`).join("") + "</tr>").join("");
      html += "</tbody></table>";
      continue;
    }

    // headings
    const h = line.match(/^(#{1,3})\s+(.*)$/);
    if (h) { html += `<h${h[1].length}>${renderInline(h[2])}</h${h[1].length}>`; i++; continue; }

    // blockquote
    if (/^>\s?/.test(line)) {
      const buf = [];
      while (i < lines.length && /^>\s?/.test(lines[i])) { buf.push(lines[i].replace(/^>\s?/, "")); i++; }
      html += `<blockquote>${renderInline(buf.join(" "))}</blockquote>`;
      continue;
    }

    // unordered list
    if (/^\s*[-*]\s+/.test(line)) {
      const buf = [];
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) { buf.push(lines[i].replace(/^\s*[-*]\s+/, "")); i++; }
      html += flushList(buf, false);
      continue;
    }
    // ordered list
    if (/^\s*\d+\.\s+/.test(line)) {
      const buf = [];
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) { buf.push(lines[i].replace(/^\s*\d+\.\s+/, "")); i++; }
      html += flushList(buf, true);
      continue;
    }

    // blank line
    if (line.trim() === "") { i++; continue; }

    // paragraph (gather consecutive non-blank, non-special lines)
    const para = [line]; i++;
    while (i < lines.length && lines[i].trim() !== "" &&
           !/^```/.test(lines[i]) && !/^(#{1,3})\s/.test(lines[i]) &&
           !/^\s*[-*]\s+/.test(lines[i]) && !/^\s*\d+\.\s+/.test(lines[i]) &&
           !/^>\s?/.test(lines[i])) {
      para.push(lines[i]); i++;
    }
    html += `<p>${renderInline(para.join(" "))}</p>`;
  }
  return html;
}
function codeBlockHtml(code, lang) {
  const id = "cb_" + Math.random().toString(36).slice(2, 8);
  return `<div class="codeblock">
    <div class="codeblock-head"><span>${lang || "code"}</span>
      <button class="copy-code" data-target="${id}">📋 Copy</button></div>
    <pre><code id="${id}">${escapeHtml(code)}</code></pre></div>`;
}

/* ---------- rendering ---------- */
const thread = $("#thread");

function avatarFor(role) {
  return role === "user" ? "U" : "🚗";
}

function buildMetaHtml(meta) {
  if (!meta) return "";
  let html = "";
  if (meta.refined) {
    html += `<details class="detail"><summary>🔍 Refined question</summary>
      <div class="detail-body"><blockquote>${escapeHtml(meta.refined)}</blockquote></div></details>`;
  }
  if (meta.sql) {
    html += `<details class="detail"><summary>🗄️ SQL query</summary>
      <div class="detail-body">${codeBlockHtml(meta.sql, "sql")}</div></details>`;
  }
  if (meta.code) {
    html += `<details class="detail"><summary>🔧 Generated code</summary>
      <div class="detail-body">${codeBlockHtml(meta.code, "python")}</div></details>`;
  }
  for (const f of meta.files || []) {
    if (f.kind === "image") {
      html += `<div class="msg-image"><img src="${f.url}" alt="${escapeHtml(f.name)}" loading="lazy"/></div>`;
    } else {
      html += `<a class="file-link" href="${f.url}" download>📥 ${escapeHtml(f.name)}</a>`;
    }
  }
  return html;
}

function messageRowHtml(role, contentHtml, metaHtml, withActions) {
  const name = role === "user" ? "You" : "Renty Analytics";
  const actions = withActions
    ? `<div class="msg-actions">
         <button class="copy-msg" title="Copy">📋 Copy</button>
         ${role === "assistant" ? '<button class="regen-msg" title="Regenerate">↻ Regenerate</button>' : ""}
       </div>` : "";
  return `<div class="msg-inner">
      <div class="avatar">${avatarFor(role)}</div>
      <div class="msg-body">
        <div class="msg-name">${name}</div>
        <div class="msg-content">${contentHtml}</div>
        ${metaHtml || ""}
        ${actions}
      </div>
    </div>`;
}

function renderThread() {
  const conv = activeConv();
  thread.innerHTML = "";
  if (!conv.messages.length) {
    thread.innerHTML = welcomeHtml();
    wireSuggestions();
    return;
  }
  for (const m of conv.messages) {
    const row = document.createElement("div");
    row.className = "msg-row " + m.role;
    const contentHtml = m.role === "user" ? `<p>${escapeHtml(m.content).replace(/\n/g, "<br>")}</p>` : renderMarkdown(m.content);
    row.innerHTML = messageRowHtml(m.role, contentHtml, buildMetaHtml(m.meta), true);
    thread.appendChild(row);
  }
  wireMessageActions();
  scrollToBottom();
}

function welcomeHtml() {
  return `<div class="welcome">
    <div class="welcome-logo">🚗</div>
    <h1>Renty AI Analytics</h1>
    <p>Ask anything about the rental data — branches, contracts, bookings, demand, pricing, utilization.</p>
    <div class="suggestions">
      ${SUGGESTIONS.map(s => `<button class="suggestion" data-text="${escapeHtml(s.text)}">
        <div class="s-title">${escapeHtml(s.title)}</div>
        <div class="s-sub">${escapeHtml(s.text)}</div></button>`).join("")}
    </div></div>`;
}

function scrollToBottom() {
  thread.scrollTop = thread.scrollHeight;
}

/* ---------- sidebar ---------- */
function renderSidebar() {
  const list = $("#conversation-list");
  const ids = Object.keys(State.conversations).sort((a, b) => State.conversations[b].updated - State.conversations[a].updated);
  list.innerHTML = "";
  if (!ids.length) return;
  const label = document.createElement("div");
  label.className = "conv-group-label";
  label.textContent = "Chats";
  list.appendChild(label);
  for (const id of ids) {
    const c = State.conversations[id];
    const item = document.createElement("div");
    item.className = "conv-item" + (id === State.activeId ? " active" : "");
    item.innerHTML = `<span class="conv-title">${escapeHtml(c.title || "New chat")}</span>
      <button class="conv-del" title="Delete">
        <svg viewBox="0 0 24 24" width="15" height="15"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="M6 6l12 12M18 6L6 18"/></svg>
      </button>`;
    item.addEventListener("click", (e) => {
      if (e.target.closest(".conv-del")) return;
      State.activeId = id; saveStore(); renderSidebar(); renderThread();
    });
    item.querySelector(".conv-del").addEventListener("click", (e) => {
      e.stopPropagation();
      deleteConversation(id);
    });
    list.appendChild(item);
  }
}

/* ---------- streaming chat ---------- */
async function sendMessage(text) {
  if (State.streaming) return;
  text = text.trim();
  if (!text) return;

  const conv = activeConv();
  conv.messages.push({ role: "user", content: text });
  if (conv.title === "New chat") conv.title = text.slice(0, 40);
  conv.updated = Date.now();
  saveStore();
  renderSidebar();
  renderThread();

  // assistant placeholder row
  const row = document.createElement("div");
  row.className = "msg-row assistant";
  row.innerHTML = messageRowHtml("assistant",
    `<div class="status-line"><span class="dot-pulse"></span><span class="status-text">Thinking…</span></div>`,
    "", false);
  thread.appendChild(row);
  scrollToBottom();

  const contentEl = row.querySelector(".msg-content");
  const bodyEl = row.querySelector(".msg-body");

  const meta = { refined: "", sql: "", code: "", files: [] };
  let answer = "";
  let started = false;

  setStreaming(true);
  State.abort = new AbortController();

  // history excludes the just-added user message that we send separately
  const history = conv.messages.slice(0, -1).map(m => ({ role: m.role, content: m.content }));

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, history }),
      signal: State.abort.signal,
    });
    if (!res.ok || !res.body) throw new Error("Request failed (" + res.status + ")");

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    const setStatus = (t) => {
      const s = contentEl.querySelector(".status-text");
      if (s) s.textContent = t;
    };
    const ensureAnswerEl = () => {
      if (!started) {
        started = true;
        contentEl.innerHTML = `<span class="answer"></span><span class="cursor"></span>`;
      }
      return contentEl.querySelector(".answer");
    };

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split("\n\n");
      buffer = parts.pop();
      for (const part of parts) {
        const lineMatch = part.match(/^data:\s?(.*)$/s);
        if (!lineMatch) continue;
        let evt;
        try { evt = JSON.parse(lineMatch[1]); } catch { continue; }

        if (evt.type === "status") {
          if (!started) setStatus(evt.text);
        } else if (evt.type === "refined") {
          meta.refined = evt.text || "";
        } else if (evt.type === "code") {
          meta.code = evt.code || "";
          meta.sql = evt.sql || "";
          meta.files = evt.files || [];
        } else if (evt.type === "delta") {
          const a = ensureAnswerEl();
          answer += evt.text;
          a.innerHTML = renderMarkdown(answer);
          scrollToBottom();
        } else if (evt.type === "error") {
          const a = ensureAnswerEl();
          answer += (answer ? "\n\n" : "") + "⚠️ " + evt.text;
          a.innerHTML = renderMarkdown(answer);
        } else if (evt.type === "final" || evt.type === "done") {
          // handled after loop
        }
      }
    }
  } catch (err) {
    if (err.name === "AbortError") {
      answer += (answer ? "\n\n_(stopped)_" : "_(stopped)_");
    } else {
      answer += (answer ? "\n\n" : "") + "⚠️ " + err.message;
    }
  }

  // finalize: remove cursor, render full content + meta + actions
  if (!answer) answer = "_(no answer returned)_";
  conv.messages.push({ role: "assistant", content: answer, meta });
  conv.updated = Date.now();
  saveStore();
  setStreaming(false);
  State.abort = null;
  renderThread();
}

function setStreaming(on) {
  State.streaming = on;
  $("#send").style.display = on ? "none" : "flex";
  $("#stop").style.display = on ? "flex" : "none";
  $("#input").disabled = false;
}

/* ---------- message actions ---------- */
function wireMessageActions() {
  $$(".copy-code").forEach(b => b.addEventListener("click", () => {
    const el = document.getElementById(b.dataset.target);
    if (el) { navigator.clipboard.writeText(el.textContent); flash(b, "✓ Copied"); }
  }));
  $$(".msg-row").forEach((row, idx) => {
    const conv = activeConv();
    const copyBtn = row.querySelector(".copy-msg");
    if (copyBtn) copyBtn.addEventListener("click", () => {
      const m = conv.messages[idx];
      if (m) { navigator.clipboard.writeText(m.content); flash(copyBtn, "✓ Copied"); }
    });
    const regen = row.querySelector(".regen-msg");
    if (regen) regen.addEventListener("click", () => {
      // find the user message preceding this assistant message
      let userMsg = null;
      for (let j = idx - 1; j >= 0; j--) {
        if (conv.messages[j].role === "user") { userMsg = conv.messages[j].content; break; }
      }
      if (userMsg == null) return;
      // drop this assistant msg (and trailing) then resend
      conv.messages = conv.messages.slice(0, idx);
      // remove the trailing user msg too (sendMessage re-adds it)
      if (conv.messages.length && conv.messages[conv.messages.length - 1].role === "user") {
        conv.messages.pop();
      }
      saveStore(); renderThread();
      sendMessage(userMsg);
    });
  });
}
function flash(btn, text) {
  const old = btn.innerHTML; btn.textContent = text;
  setTimeout(() => { btn.innerHTML = old; }, 1200);
}

/* ---------- suggestions ---------- */
function wireSuggestions() {
  $$(".suggestion").forEach(s => s.addEventListener("click", () => {
    sendMessage(s.dataset.text);
  }));
}

/* ---------- composer ---------- */
const input = $("#input");
function autoGrow() {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 200) + "px";
}
input.addEventListener("input", autoGrow);
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    submit();
  }
});
function submit() {
  const text = input.value;
  if (!text.trim() || State.streaming) return;
  input.value = ""; autoGrow();
  sendMessage(text);
}
$("#composer").addEventListener("submit", (e) => { e.preventDefault(); submit(); });
$("#stop").addEventListener("click", () => { if (State.abort) State.abort.abort(); });

/* ---------- sidebar / topbar controls ---------- */
$("#new-chat").addEventListener("click", () => {
  newConversation(); renderSidebar(); renderThread(); input.focus();
});
$("#collapse-sidebar").addEventListener("click", () => {
  $("#app").classList.add("sidebar-hidden");
  $("#show-sidebar").style.display = "inline-flex";
});
$("#show-sidebar").addEventListener("click", () => {
  $("#app").classList.remove("sidebar-hidden");
  $("#show-sidebar").style.display = "none";
});

/* theme */
const THEME_KEY = "renty_theme";
function applyTheme(t) {
  document.documentElement.setAttribute("data-theme", t);
  localStorage.setItem(THEME_KEY, t);
}
$("#theme-toggle").addEventListener("click", () => {
  const cur = document.documentElement.getAttribute("data-theme");
  applyTheme(cur === "dark" ? "light" : "dark");
});
applyTheme(localStorage.getItem(THEME_KEY) || "dark");

/* lightbox for charts */
const lightbox = document.createElement("div");
lightbox.id = "lightbox";
lightbox.innerHTML = "<img/>";
document.body.appendChild(lightbox);
lightbox.addEventListener("click", () => lightbox.classList.remove("open"));
thread.addEventListener("click", (e) => {
  const img = e.target.closest(".msg-image img");
  if (img) { lightbox.querySelector("img").src = img.src; lightbox.classList.add("open"); }
});

/* ---------- db info ---------- */
async function loadInfo() {
  try {
    const res = await fetch("/api/info");
    const data = await res.json();
    if (data.model) $("#model-label").textContent = data.model.split("/").pop().replace(/-/g, " ");
    const stats = $("#db-stats");
    stats.innerHTML = "";
    for (const [k, v] of Object.entries(data.counts || {})) {
      const el = document.createElement("span");
      el.className = "db-stat";
      el.innerHTML = `<b>${v.toLocaleString()}</b> ${k}`;
      stats.appendChild(el);
    }
  } catch (e) { /* ignore */ }
}

/* ---------- boot ---------- */
loadStore();
if (!State.activeId || !State.conversations[State.activeId]) newConversation();
renderSidebar();
renderThread();
loadInfo();
input.focus();
