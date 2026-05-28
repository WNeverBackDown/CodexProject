const state = {
  config: { settings: {}, rules: [] },
  alerts: [],
  notified: false,
};

const $ = (selector) => document.querySelector(selector);

function splitWords(value) {
  return String(value || "")
    .split(/[,，\n]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function joinWords(value) {
  return (value || []).join(", ");
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  const data = await response.json();
  if (!response.ok || data.ok === false) {
    throw new Error(data.error || "请求失败");
  }
  return data;
}

async function loadState() {
  const data = await api("/api/state");
  state.config = data.config;
  state.alerts = data.alerts || [];
  state.notified = "Notification" in window && Notification.permission === "granted";
  $("#notifyBtn").textContent = state.notified ? "通知已开启" : "开启通知";
  $("#inboxPath").textContent = data.inbox_path;
  renderRules();
  renderAlerts();
  setStatus("运行中");
}

function renderAlerts() {
  const alerts = $("#alerts");
  $("#alertCount").textContent = state.alerts.length;
  if (!state.alerts.length) {
    alerts.innerHTML = '<div class="empty">暂无提醒</div>';
    return;
  }
  alerts.innerHTML = state.alerts
    .map((alert) => {
      const message = alert.message || {};
      const terms = (alert.matched_terms || []).map((term) => `<span class="chip">${escapeHtml(term)}</span>`).join("");
      const url = message.url ? `<a href="${escapeAttr(message.url)}" target="_blank" rel="noreferrer">打开链接</a>` : "";
      return `
        <article class="alert">
          <div class="alert-top">
            <div>
              <div class="alert-title">${escapeHtml(alert.rule_name)}</div>
              <div class="muted">${escapeHtml(message.room || "")}${message.sender ? " · " + escapeHtml(message.sender) : ""}</div>
            </div>
            <time class="alert-time">${formatTime(alert.created_at)}</time>
          </div>
          <div class="alert-content">${escapeHtml(message.content || "")}</div>
          <div class="chips">${terms}${url ? `<span class="chip">${url}</span>` : ""}</div>
        </article>
      `;
    })
    .join("");
}

function renderRules() {
  const list = $("#rulesList");
  const template = $("#ruleTemplate");
  list.innerHTML = "";
  $("#dedupeMinutes").value = state.config.settings.dedupe_minutes || 30;
  state.config.rules.forEach((rule) => {
    const node = template.content.firstElementChild.cloneNode(true);
    node.dataset.id = rule.id;
    node.querySelector('[data-field="enabled"]').checked = rule.enabled !== false;
    node.querySelector('[data-field="name"]').value = rule.name || "";
    node.querySelector('[data-field="terms"]').value = joinWords(rule.terms);
    node.querySelector('[data-field="exclude"]').value = joinWords(rule.exclude);
    node.querySelector(".remove-rule").addEventListener("click", () => {
      state.config.rules = state.config.rules.filter((item) => item.id !== rule.id);
      renderRules();
    });
    list.appendChild(node);
  });
}

function collectRules() {
  const rules = [...document.querySelectorAll(".rule")].map((node, index) => {
    const id = node.dataset.id || `rule-${Date.now()}-${index}`;
    return {
      id,
      enabled: node.querySelector('[data-field="enabled"]').checked,
      name: node.querySelector('[data-field="name"]').value.trim() || id,
      terms: splitWords(node.querySelector('[data-field="terms"]').value),
      exclude: splitWords(node.querySelector('[data-field="exclude"]').value),
    };
  });
  return {
    settings: {
      ...state.config.settings,
      dedupe_minutes: Number($("#dedupeMinutes").value || 0),
    },
    rules,
  };
}

function connectEvents() {
  const events = new EventSource("/api/events");
  events.onopen = () => {
    setStatus("运行中");
  };
  events.onerror = () => {
    setStatus("重连中");
  };
  events.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "alert") {
      state.alerts.unshift(data.payload);
      renderAlerts();
      notify(data.payload);
      beep();
    }
    if (data.type === "config") {
      state.config = data.payload.config;
      renderRules();
    }
    if (data.type === "alerts-cleared") {
      state.alerts = [];
      renderAlerts();
    }
  };
}

async function notify(alert) {
  if (!state.notified || !("Notification" in window) || Notification.permission !== "granted") return;
  const message = alert.message || {};
  new Notification(`CatBaby: ${alert.rule_name}`, {
    body: message.content || "命中关键词",
    tag: alert.id,
  });
}

function beep() {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    const context = new AudioContext();
    const oscillator = context.createOscillator();
    const gain = context.createGain();
    oscillator.frequency.value = 880;
    gain.gain.value = 0.05;
    oscillator.connect(gain);
    gain.connect(context.destination);
    oscillator.start();
    setTimeout(() => {
      oscillator.stop();
      context.close();
    }, 140);
  } catch (error) {
    // Browser audio can be blocked until the first user gesture.
  }
}

function formatTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[char];
  });
}

function escapeAttr(value) {
  return escapeHtml(value).replace(/`/g, "&#096;");
}

$("#messageForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const form = new FormData(event.currentTarget);
    await api("/api/messages", {
      method: "POST",
      body: JSON.stringify({
        source: "manual-test",
        room: form.get("room"),
        sender: form.get("sender"),
        content: form.get("content"),
      }),
    });
    setStatus("测试消息已发送");
  } catch (error) {
    setStatus(error.message);
  }
});

$("#rulesForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const config = collectRules();
    const data = await api("/api/rules", {
      method: "POST",
      body: JSON.stringify(config),
    });
    state.config = data.config;
    renderRules();
    setStatus("规则已保存");
  } catch (error) {
    setStatus(error.message);
  }
});

$("#addRuleBtn").addEventListener("click", () => {
  state.config.rules.push({
    id: `rule-${Date.now()}`,
    name: "新规则",
    enabled: true,
    terms: ["猫咪"],
    exclude: ["已结束"],
  });
  renderRules();
});

$("#clearAlertsBtn").addEventListener("click", async () => {
  await api("/api/alerts/clear", { method: "POST", body: "{}" });
  setStatus("提醒已清空");
});

$("#notifyBtn").addEventListener("click", async () => {
  if (!("Notification" in window)) return;
  const permission = await Notification.requestPermission();
  state.notified = permission === "granted";
  $("#notifyBtn").textContent = state.notified ? "通知已开启" : "开启通知";
  beep();
});

loadState().then(connectEvents).catch((error) => {
  setStatus(error.message);
});

function setStatus(value) {
  $("#statusText").textContent = value;
}
