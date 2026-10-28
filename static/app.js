const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("input");
const sendBtn = document.getElementById("send");
const resetBtn = document.getElementById("btnReset");
const welcomeEl = document.getElementById("welcome");

marked.setOptions({ breaks: true });

// Auto-resize textarea
function autoGrow() {
  inputEl.style.height = "auto";
  inputEl.style.height = Math.min(inputEl.scrollHeight, 180) + "px";
}
inputEl.addEventListener("input", autoGrow);

// Scroll to bottom
function scrollDown() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

// SVG avatars
const botAvatar = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v2M12 19v2M5 12H3M21 12h-2M18.4 5.6l-1.4 1.4M7 17l-1.4 1.4M18.4 18.4 17 17M7 7 5.6 5.6"/><circle cx="12" cy="12" r="4"/></svg>`;
const userAvatar = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`;

function addMessage(role, content, { markdown = false } = {}) {
  if (welcomeEl) welcomeEl.remove();

  const row = document.createElement("div");
  row.className = `msg ${role === "user" ? "user" : "bot"}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.innerHTML = role === "user" ? userAvatar : botAvatar;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  if (markdown) {
    bubble.innerHTML = DOMPurify.sanitize(marked.parse(content));
  } else {
    bubble.textContent = content;
  }

  row.appendChild(avatar);
  row.appendChild(bubble);
  messagesEl.appendChild(row);
  scrollDown();
  return bubble;
}

function addTyping() {
  if (welcomeEl) welcomeEl.remove();
  const row = document.createElement("div");
  row.className = "msg bot";
  row.id = "typing-row";
  row.innerHTML = `<div class="avatar">${botAvatar}</div>
    <div class="bubble"><div class="typing"><span></span><span></span><span></span></div></div>`;
  messagesEl.appendChild(row);
  scrollDown();
}

function removeTyping() {
  const el = document.getElementById("typing-row");
  if (el) el.remove();
}

let busy = false;

async function send() {
  const text = inputEl.value.trim();
  if (!text || busy) return;

  busy = true;
  sendBtn.disabled = true;

  addMessage("user", text);
  inputEl.value = "";
  autoGrow();
  addTyping();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    removeTyping();

    if (!res.ok) {
      addMessage("bot", "⚠️ " + (data.error || "Algo deu errado."));
    } else {
      addMessage("bot", data.reply || "(sem resposta)", { markdown: true });
    }
  } catch (err) {
    removeTyping();
    addMessage("bot", "⚠️ Não consegui falar com o servidor.");
  } finally {
    busy = false;
    sendBtn.disabled = false;
    inputEl.focus();
  }
}

sendBtn.addEventListener("click", send);

inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    send();
  }
});

// Suggestion chips
document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    inputEl.value = chip.textContent;
    send();
  });
});

// New conversation
resetBtn.addEventListener("click", async () => {
  await fetch("/api/reset", { method: "POST" });
  messagesEl.innerHTML = "";
  location.reload();
});
