import { getUser, getConfig } from "./storage.js";

const API_BASE = "https://api.github.com";

function getRepoInfo() {
  const hostname = location.hostname;
  const pathname = location.pathname;
  if (hostname.endsWith(".github.io")) {
    const owner = hostname.replace(".github.io", "");
    const repo = pathname.split("/").filter(Boolean)[0] || "";
    return { owner, repo };
  }
  return null;
}

export function isGitHubPages() {
  return getRepoInfo() !== null;
}

function headers() {
  const config = getConfig();
  return {
    Authorization: `token ${config.token}`,
    Accept: "application/vnd.github.v3+json",
    "Content-Type": "application/json",
  };
}

function repoPath() {
  const info = getRepoInfo();
  if (!info) throw new Error("GitHub Pages 環境外では自動コミットできません");
  return `${API_BASE}/repos/${info.owner}/${info.repo}/contents`;
}

function csvPath() {
  const user = getUser();
  return `data/answers/${user}.csv`;
}

const CSV_HEADER = "question_id,category,field,user_answer,correct_answer,is_correct,answered_at";

function answersToCSVRows(answers) {
  return answers
    .map((a) => {
      const cat = a.category.includes(",") ? `"${a.category}"` : a.category;
      return `${a.question_id},${cat},${a.field},${a.user_answer},${a.correct_answer},${a.is_correct},${a.answered_at}`;
    })
    .join("\n");
}

export async function commitAnswers(newAnswers) {
  const config = getConfig();
  if (!config || !config.token) {
    throw new Error("GitHub設定が未完了です");
  }

  const filePath = csvPath();
  const url = `${repoPath()}/${filePath}`;

  // Try to get existing file
  let existingContent = "";
  let sha = null;

  try {
    const res = await fetch(url, { headers: headers() });
    if (res.ok) {
      const data = await res.json();
      sha = data.sha;
      existingContent = atob(data.content.replace(/\n/g, ""));
    }
  } catch {
    // File doesn't exist yet, will create new
  }

  // Build new CSV content
  let csvContent;
  if (existingContent) {
    const newRows = answersToCSVRows(newAnswers);
    csvContent = existingContent.trimEnd() + "\n" + newRows + "\n";
  } else {
    const newRows = answersToCSVRows(newAnswers);
    csvContent = CSV_HEADER + "\n" + newRows + "\n";
  }

  // Commit
  const user = getUser();
  const date = new Date().toISOString().split("T")[0];
  const body = {
    message: `Add ${newAnswers.length} answers for ${user} (${date})`,
    content: btoa(unescape(encodeURIComponent(csvContent))),
  };
  if (sha) {
    body.sha = sha;
  }

  const putRes = await fetch(url, {
    method: "PUT",
    headers: headers(),
    body: JSON.stringify(body),
  });

  if (!putRes.ok) {
    const err = await putRes.json();
    throw new Error(err.message || `GitHub API error: ${putRes.status}`);
  }

  return await putRes.json();
}
