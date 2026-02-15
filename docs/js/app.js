import { getUser, getConfig } from "./storage.js";
import { loadQuestions } from "./questions.js";
import {
  setAppData,
  updateUserInfo,
  renderSetup,
  renderHome,
  renderCategorySelect,
  renderQuiz,
  renderResult,
  renderHistory,
  renderSettings,
} from "./ui.js";

function isConfigured() {
  return !!getUser();
}

async function route() {
  const hash = location.hash || "#home";

  if (!isConfigured() && hash !== "#setup") {
    location.hash = "#setup";
    return;
  }

  updateUserInfo();

  switch (hash) {
    case "#setup":
      renderSetup();
      break;
    case "#home":
      renderHome();
      break;
    case "#category":
      renderCategorySelect();
      break;
    case "#quiz":
      renderQuiz();
      break;
    case "#result":
      await renderResult();
      break;
    case "#history":
      renderHistory();
      break;
    case "#settings":
      renderSettings();
      break;
    default:
      renderHome();
  }
}

async function init() {
  try {
    const data = await loadQuestions();
    setAppData(data);
  } catch (err) {
    document.querySelector("#app").innerHTML = `
      <div class="card" style="text-align:center;color:var(--danger)">
        <p>問題データの読み込みに失敗しました。</p>
        <p style="font-size:0.85rem;color:var(--text-light)">make site を実行してデータをビルドしてください。</p>
      </div>`;
    return;
  }

  window.addEventListener("hashchange", route);
  route();
}

init();
