const LANG_NAMES = { bn: "Bengali", en: "English", zh: "Chinese" };
const DIRS = [
  ["en", "bn"],
  ["en", "zh"],
  ["bn", "en"],
  ["bn", "zh"],
  ["zh", "en"],
  ["zh", "bn"],
];

let current = null;

const $ = (id) => document.getElementById(id);

function setDirection(from, to) {
  $("direction").textContent = `${LANG_NAMES[from]} → ${LANG_NAMES[to]}`;
}

async function loadCard() {
  const [from, to] = DIRS[Math.floor(Math.random() * DIRS.length)];
  setDirection(from, to);
  const res = await fetch(`/api/cards?from=${from}&to=${to}`);
  if (!res.ok) {
    $("prompt").textContent = "No words yet. Add some below.";
    return;
  }
  current = await res.json();
  $("prompt").textContent = current.prompt;
  $("answer-input").value = "";
  $("feedback").textContent = "";
  $("answer-input").focus();
}

async function checkAnswer(e) {
  e.preventDefault();
  if (!current) return;
  const guess = $("answer-input").value.trim().toLowerCase();
  const answer = current.answer.trim().toLowerCase();
  const correct = guess === answer;
  const res = await fetch("/api/answer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ word_id: current.id, correct }),
  });
  const stats = await res.json();
  const fb = $("feedback");
  if (correct) {
    fb.textContent = "Correct.";
    fb.className = "feedback ok";
  } else {
    fb.textContent = `Not quite. Answer: ${current.answer}`;
    fb.className = "feedback no";
  }
  const pct = stats.total ? Math.round((stats.correct / stats.total) * 100) : 0;
  $("stats").textContent = `Answered ${stats.total} · Correct ${stats.correct} · ${pct}%`;
}

async function addWord(e) {
  e.preventDefault();
  const payload = {
    bn: $("add-bn").value.trim(),
    en: $("add-en").value.trim(),
    zh: $("add-zh").value.trim(),
  };
  if (!payload.bn || !payload.en || !payload.zh) return;
  const res = await fetch("/api/cards", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  $("add-msg").textContent = res.ok
    ? "Added. It can show up in the deck now."
    : "Could not add the word.";
  ["add-bn", "add-en", "add-zh"].forEach((id) => {
    $(id).value = "";
  });
}

$("answer-form").addEventListener("submit", checkAnswer);
$("next-btn").addEventListener("click", loadCard);
$("add-form").addEventListener("submit", addWord);
loadCard();
