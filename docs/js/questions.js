let cachedData = null;

export async function loadQuestions() {
  if (cachedData) return cachedData;
  const res = await fetch("data/ap_questions.json");
  cachedData = await res.json();
  return cachedData;
}

export function getCategories(data) {
  const categories = {};
  for (const q of data.questions) {
    if (!categories[q.category]) {
      categories[q.category] = { field: q.field, count: 0 };
    }
    categories[q.category].count++;
  }
  return categories;
}

export function filterByCategory(data, category) {
  return data.questions.filter((q) => q.category === category);
}

export function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export function pickQuestions(questions, count) {
  const shuffled = shuffle(questions);
  if (count <= 0 || count >= shuffled.length) return shuffled;
  return shuffled.slice(0, count);
}
