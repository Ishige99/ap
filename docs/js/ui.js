import { getUser, getConfig, setUser, setConfig, saveAnswers, getStats, clearHistory } from "./storage.js";
import { getCategories, filterByCategory, pickQuestions } from "./questions.js";
import { commitAnswers } from "./github.js";

const FIELD_NAMES = { T: "テクノロジ", M: "マネジメント", S: "ストラテジ" };
const COUNT_OPTIONS = [5, 10, 25, 50, 0]; // 0 = all
const $ = (sel) => document.querySelector(sel);

let appData = null;
let quizState = null;
let selectedCount = 10;

export function setAppData(data) {
  appData = data;
}

export function updateUserInfo() {
  const el = $("#user-info");
  const user = getUser();
  if (!user) {
    el.innerHTML = "";
    return;
  }
  el.innerHTML = `
    <span class="username">${esc(user)}</span>
    <button onclick="location.hash='#settings'">設定</button>
  `;
}

// --- Setup ---
export function renderSetup() {
  const app = $("#app");
  const config = getConfig() || {};
  app.innerHTML = `
    <div class="card">
      <h2 style="margin-bottom:16px">初期設定</h2>
      <div class="form-group">
        <label>ユーザー名</label>
        <input type="text" id="setup-user" value="${esc(getUser())}" placeholder="例: taro">
      </div>
      <div class="form-group">
        <label>GitHub Personal Access Token</label>
        <div class="hint">Fine-grained PAT: 対象リポジトリの Contents 権限 (Read and write) が必要です。このトークンはこのブラウザの localStorage にのみ保存されます。</div>
        <input type="password" id="setup-token" value="${esc(config.token || "")}" placeholder="github_pat_...">
      </div>
      <div class="form-group">
        <label>リポジトリオーナー</label>
        <input type="text" id="setup-owner" value="${esc(config.owner || "")}" placeholder="例: ishige">
      </div>
      <div class="form-group">
        <label>リポジトリ名</label>
        <input type="text" id="setup-repo" value="${esc(config.repo || "")}" placeholder="例: ap">
      </div>
      <div class="form-actions">
        <button class="btn btn-primary btn-block" id="setup-save">保存して始める</button>
      </div>
    </div>
  `;
  $("#setup-save").addEventListener("click", () => {
    const user = $("#setup-user").value.trim();
    const token = $("#setup-token").value.trim();
    const owner = $("#setup-owner").value.trim();
    const repo = $("#setup-repo").value.trim();
    if (!user) return alert("ユーザー名を入力してください");
    if (!token) return alert("GitHub PAT を入力してください");
    if (!owner || !repo) return alert("リポジトリ情報を入力してください");
    setUser(user);
    setConfig({ token, owner, repo });
    location.hash = "#home";
  });
}

// --- Home ---
export function renderHome() {
  if (!appData) return;
  const app = $("#app");
  const total = appData.questions.length;
  app.innerHTML = `
    <div class="card">
      <div class="home-title">応用情報 過去問道場</div>
      <div class="home-subtitle">${total} 問収録</div>
      <div class="count-select">
        <label>出題数</label>
        <div class="count-options" id="count-options"></div>
      </div>
      <div class="mode-buttons">
        <button class="btn btn-primary btn-lg" id="btn-random">ランダム出題</button>
        <button class="btn btn-outline btn-lg" id="btn-category">カテゴリ別出題</button>
      </div>
      <button class="btn btn-outline btn-block" onclick="location.hash='#history'">学習履歴</button>
    </div>
  `;

  const countEl = $("#count-options");
  for (const c of COUNT_OPTIONS) {
    const label = c === 0 ? "全問" : `${c}問`;
    const btn = document.createElement("button");
    btn.textContent = label;
    if (c === selectedCount) btn.classList.add("active");
    btn.addEventListener("click", () => {
      selectedCount = c;
      countEl.querySelectorAll("button").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
    });
    countEl.appendChild(btn);
  }

  $("#btn-random").addEventListener("click", () => {
    startQuiz(appData.questions, selectedCount);
  });
  $("#btn-category").addEventListener("click", () => {
    location.hash = "#category";
  });
}

// --- Category Select ---
export function renderCategorySelect() {
  if (!appData) return;
  const app = $("#app");
  const categories = getCategories(appData);

  const fields = ["T", "M", "S"];
  let html = '<a href="#home" class="back-link">< トップに戻る</a>';

  for (const f of fields) {
    const cats = Object.entries(categories).filter(([, v]) => v.field === f);
    if (cats.length === 0) continue;
    cats.sort((a, b) => b[1].count - a[1].count);

    html += `<div class="field-section">
      <div class="field-title">${FIELD_NAMES[f]}</div>
      <div class="category-list">`;

    for (const [name, info] of cats) {
      html += `<div class="category-item" data-category="${esc(name)}">
        <span>${esc(name)}</span>
        <span class="count">${info.count}問</span>
      </div>`;
    }
    html += `</div></div>`;
  }

  app.innerHTML = html;

  app.querySelectorAll(".category-item").forEach((el) => {
    el.addEventListener("click", () => {
      const cat = el.dataset.category;
      const questions = filterByCategory(appData, cat);
      startQuiz(questions, selectedCount);
    });
  });
}

// --- Quiz ---
function startQuiz(questions, count) {
  const picked = pickQuestions(questions, count);
  quizState = {
    questions: picked,
    current: 0,
    answers: [],
    selected: null,
  };
  location.hash = "#quiz";
}

export function renderQuiz() {
  if (!quizState) {
    location.hash = "#home";
    return;
  }
  const app = $("#app");
  const { questions, current, selected } = quizState;
  const q = questions[current];
  const total = questions.length;
  const progress = ((current) / total) * 100;

  let html = `
    <div class="progress-bar">
      <span>${current + 1}</span>
      <div class="progress-track"><div class="progress-fill" style="width:${progress}%"></div></div>
      <span>${total}問</span>
    </div>
    <div class="card">
      <div class="question-meta">${esc(q.exam_name)} 問${q.question_number}</div>
      <div class="question-text">${esc(q.question_text)}</div>`;

  if (q.image_path) {
    html += `<img src="${esc(q.image_path)}" alt="問題画像" class="question-image">`;
  }

  html += `<div class="choices">`;
  for (const [key, text] of Object.entries(q.choices)) {
    const selectedClass = selected === key ? " selected" : "";
    html += `<button class="choice-btn${selectedClass}" data-choice="${key}">
      <span class="choice-label">${key}</span>
      <span>${esc(text)}</span>
    </button>`;
  }
  html += `</div>`;

  if (selected) {
    html += `<div class="submit-area">
      <button class="btn btn-primary btn-lg" id="btn-submit">解答する</button>
    </div>`;
  }
  html += `</div>`;

  app.innerHTML = html;

  app.querySelectorAll(".choice-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      quizState.selected = btn.dataset.choice;
      renderQuiz();
    });
  });

  const submitBtn = $("#btn-submit");
  if (submitBtn) {
    submitBtn.addEventListener("click", () => {
      const q = quizState.questions[quizState.current];
      const isCorrect = quizState.selected === q.correct_answer;
      quizState.answers.push({
        question_id: q.id,
        category: q.category,
        field: q.field,
        user_answer: quizState.selected,
        correct_answer: q.correct_answer,
        is_correct: isCorrect,
        answered_at: new Date().toISOString(),
      });
      renderAnswer(isCorrect);
    });
  }
}

function renderAnswer(isCorrect) {
  const app = $("#app");
  const { questions, current, answers } = quizState;
  const q = questions[current];
  const userAnswer = answers[answers.length - 1].user_answer;
  const isLast = current >= questions.length - 1;

  let html = `<div class="card">
    <div class="result-icon">${isCorrect ? "\u2B55" : "\u274C"}</div>
    <div class="result-text ${isCorrect ? "correct" : "incorrect"}">
      ${isCorrect ? "正解!" : `不正解 (正解: ${q.correct_answer})`}
    </div>`;

  // Show choices with correct/incorrect highlighting
  html += `<div class="choices">`;
  for (const [key, text] of Object.entries(q.choices)) {
    let cls = "";
    if (key === q.correct_answer) cls = " correct";
    else if (key === userAnswer && !isCorrect) cls = " incorrect";
    html += `<button class="choice-btn${cls}" disabled>
      <span class="choice-label">${key}</span>
      <span>${esc(text)}</span>
    </button>`;
  }
  html += `</div>`;

  if (q.explanation) {
    html += `<div class="explanation">${esc(q.explanation)}</div>`;
  }

  if (isLast) {
    html += `<button class="btn btn-primary btn-block btn-lg" id="btn-finish">結果を見る</button>`;
  } else {
    html += `<button class="btn btn-primary btn-block btn-lg" id="btn-next">次の問題へ</button>`;
  }
  html += `</div>`;

  app.innerHTML = html;

  const nextBtn = $("#btn-next");
  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      quizState.current++;
      quizState.selected = null;
      renderQuiz();
    });
  }

  const finishBtn = $("#btn-finish");
  if (finishBtn) {
    finishBtn.addEventListener("click", () => {
      location.hash = "#result";
    });
  }
}

// --- Session Result ---
export async function renderResult() {
  if (!quizState || quizState.answers.length === 0) {
    location.hash = "#home";
    return;
  }
  const app = $("#app");
  const { questions, answers } = quizState;
  const correct = answers.filter((a) => a.is_correct).length;
  const total = answers.length;
  const rate = Math.round((correct / total) * 100);

  let html = `
    <div class="card">
      <div class="session-score">
        <div class="score-number">${rate}%</div>
        <div class="score-label">${correct} / ${total} 正解</div>
      </div>
    </div>
    <div class="card">
      <table class="session-list">
        <thead><tr><th>#</th><th>カテゴリ</th><th>結果</th></tr></thead>
        <tbody>`;

  for (let i = 0; i < answers.length; i++) {
    const a = answers[i];
    const icon = a.is_correct ? "\u2B55" : "\u274C";
    html += `<tr>
      <td>${i + 1}</td>
      <td>${esc(a.category)}</td>
      <td>${icon}</td>
    </tr>`;
  }

  html += `</tbody></table></div>
    <div id="commit-status" class="commit-status saving">回答データを保存中...</div>
    <button class="btn btn-outline btn-block" onclick="location.hash='#home'" style="margin-top:12px">トップに戻る</button>`;

  app.innerHTML = html;

  // Save to localStorage
  saveAnswers(answers);

  // Commit to GitHub
  const statusEl = $("#commit-status");
  try {
    await commitAnswers(answers);
    statusEl.className = "commit-status saved";
    statusEl.textContent = "回答データを GitHub に保存しました";
  } catch (err) {
    statusEl.className = "commit-status error";
    statusEl.textContent = `保存に失敗しました: ${err.message}`;
  }

  quizState = null;
}

// --- History ---
export function renderHistory() {
  const app = $("#app");
  const stats = getStats();

  if (stats.total === 0) {
    app.innerHTML = `
      <a href="#home" class="back-link">< トップに戻る</a>
      <div class="card">
        <p style="text-align:center;color:var(--text-light)">まだ回答データがありません</p>
      </div>`;
    return;
  }

  let html = `<a href="#home" class="back-link">< トップに戻る</a>`;

  // Overview
  html += `<div class="stats-overview">
    <div class="stat-card">
      <div class="stat-value">${stats.total}</div>
      <div class="stat-label">回答数</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">${stats.correct}</div>
      <div class="stat-label">正解数</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">${stats.rate}%</div>
      <div class="stat-label">正答率</div>
    </div>
  </div>`;

  // Field stats
  html += `<div class="card"><h3 style="margin-bottom:12px">分野別</h3>
    <table class="stats-table"><thead><tr><th>分野</th><th>正答率</th><th>回答数</th></tr></thead><tbody>`;
  for (const [f, label] of Object.entries(FIELD_NAMES)) {
    const s = stats.byField[f];
    if (!s) continue;
    const r = Math.round((s.correct / s.total) * 100);
    const color = r >= 70 ? "var(--success)" : r >= 50 ? "#eab308" : "var(--danger)";
    html += `<tr>
      <td>${label}</td>
      <td><span class="accuracy-bar"><span class="accuracy-fill" style="width:${r}%;background:${color}"></span></span>${r}%</td>
      <td>${s.total}</td>
    </tr>`;
  }
  html += `</tbody></table></div>`;

  // Category stats (sorted by accuracy ascending = weakest first)
  const catEntries = Object.entries(stats.byCategory).map(([name, s]) => ({
    name,
    field: s.field,
    total: s.total,
    correct: s.correct,
    rate: Math.round((s.correct / s.total) * 100),
  }));
  catEntries.sort((a, b) => a.rate - b.rate);

  html += `<div class="card"><h3 style="margin-bottom:12px">カテゴリ別 (苦手順)</h3>
    <table class="stats-table"><thead><tr><th>カテゴリ</th><th>正答率</th><th>回答数</th></tr></thead><tbody>`;
  for (const c of catEntries) {
    const color = c.rate >= 70 ? "var(--success)" : c.rate >= 50 ? "#eab308" : "var(--danger)";
    html += `<tr>
      <td>${esc(c.name)}</td>
      <td><span class="accuracy-bar"><span class="accuracy-fill" style="width:${c.rate}%;background:${color}"></span></span>${c.rate}%</td>
      <td>${c.total}</td>
    </tr>`;
  }
  html += `</tbody></table></div>`;

  html += `<button class="btn btn-danger btn-block" id="btn-clear" style="margin-top:12px">履歴をクリア</button>`;

  app.innerHTML = html;

  $("#btn-clear").addEventListener("click", () => {
    if (confirm("本当に回答履歴を削除しますか?")) {
      clearHistory();
      renderHistory();
    }
  });
}

// --- Settings ---
export function renderSettings() {
  const app = $("#app");
  const config = getConfig() || {};
  app.innerHTML = `
    <a href="#home" class="back-link">< トップに戻る</a>
    <div class="card">
      <h2 style="margin-bottom:16px">設定</h2>
      <div class="form-group">
        <label>ユーザー名</label>
        <input type="text" id="settings-user" value="${esc(getUser())}">
      </div>
      <div class="form-group">
        <label>GitHub Personal Access Token</label>
        <div class="hint">このトークンはこのブラウザの localStorage にのみ保存されます。</div>
        <input type="password" id="settings-token" value="${esc(config.token || "")}">
      </div>
      <div class="form-group">
        <label>リポジトリオーナー</label>
        <input type="text" id="settings-owner" value="${esc(config.owner || "")}">
      </div>
      <div class="form-group">
        <label>リポジトリ名</label>
        <input type="text" id="settings-repo" value="${esc(config.repo || "")}">
      </div>
      <div class="form-actions">
        <button class="btn btn-primary" id="settings-save">保存</button>
        <a href="#home" class="btn btn-outline">キャンセル</a>
      </div>
    </div>
  `;
  $("#settings-save").addEventListener("click", () => {
    const user = $("#settings-user").value.trim();
    const token = $("#settings-token").value.trim();
    const owner = $("#settings-owner").value.trim();
    const repo = $("#settings-repo").value.trim();
    if (!user) return alert("ユーザー名を入力してください");
    setUser(user);
    setConfig({ token, owner, repo });
    location.hash = "#home";
  });
}

// --- Util ---
function esc(str) {
  if (!str) return "";
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
