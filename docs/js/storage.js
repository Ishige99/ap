const KEYS = {
  user: "ap_current_user",
  config: "ap_config",
  historyPrefix: "ap_history_",
};

export function getUser() {
  return localStorage.getItem(KEYS.user) || "";
}

export function setUser(name) {
  localStorage.setItem(KEYS.user, name);
}

export function getConfig() {
  const raw = localStorage.getItem(KEYS.config);
  if (!raw) return null;
  return JSON.parse(raw);
}

export function setConfig(config) {
  localStorage.setItem(KEYS.config, JSON.stringify(config));
}

function historyKey() {
  return KEYS.historyPrefix + getUser();
}

export function saveAnswers(records) {
  const history = getHistory();
  history.push(...records);
  localStorage.setItem(historyKey(), JSON.stringify(history));
}

export function getHistory() {
  const raw = localStorage.getItem(historyKey());
  if (!raw) return [];
  return JSON.parse(raw);
}

export function getStats() {
  const history = getHistory();
  if (history.length === 0) return { total: 0, correct: 0, rate: 0, byCategory: {}, byField: {} };

  const total = history.length;
  const correct = history.filter((r) => r.is_correct).length;
  const rate = total > 0 ? Math.round((correct / total) * 100) : 0;

  const byCategory = {};
  const byField = {};

  for (const r of history) {
    // Category stats
    if (!byCategory[r.category]) {
      byCategory[r.category] = { total: 0, correct: 0, field: r.field };
    }
    byCategory[r.category].total++;
    if (r.is_correct) byCategory[r.category].correct++;

    // Field stats
    if (!byField[r.field]) {
      byField[r.field] = { total: 0, correct: 0 };
    }
    byField[r.field].total++;
    if (r.is_correct) byField[r.field].correct++;
  }

  return { total, correct, rate, byCategory, byField };
}

export function clearHistory() {
  localStorage.removeItem(historyKey());
}
