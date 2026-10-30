/*
  app.js — 화면 동작. api.py가 흘려보내는 줄을 받아 그리고, 사람이 고른 안을 내려받게 한다 (A3, ADR-0005)

  [구성안 만들기] ── POST /api/propose {topic} + X-Access-Password
     │ 한 줄 = JSON 1개 (NDJSON)
     ├─ {"step": "frame"}   → drawFrame: P·E/I·C·O 카드
     ├─ {"step": "options"} → drawOptions: 안 1~3 카드
     └─ {"step": "error"}   → 안내문 표시
  [이 안 선택] ── selected_option.json {topic, frame, option, selected_at} 내려받기 (서버 저장 없음)

  보안: Claude가 쓴 글은 textContent로만 넣는다 (innerHTML 금지 — 글 속 <script> 실행 방지, K22)
*/

const $ = (id) => document.getElementById(id);
const state = { topic: "", frame: null };

// 비밀번호는 이 탭을 닫으면 지워진다
try { $("password").value = sessionStorage.getItem("evidos-password") || ""; } catch {}

$("topic-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const password = $("password").value;
  state.topic = $("topic").value.trim();
  try { sessionStorage.setItem("evidos-password", password); } catch {}
  reset();

  const started = Date.now();
  const timer = setInterval(() => {
    $("elapsed").textContent = `경과 ${Math.round((Date.now() - started) / 1000)}초`;
  }, 1000);
  try {
    const response = await fetch("/api/propose", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Access-Password": password },
      body: JSON.stringify({ topic: state.topic }),
    });
    if (!response.ok) throw new Error(httpMessage(response.status));
    await readLines(response, handleLine);
  } catch (error) {
    showError(error.message);
  } finally {
    clearInterval(timer);
    $("submit").disabled = false;
  }
});

/** 응답 본문을 줄 단위로 끊어 onLine에 넘긴다. 줄이 조각나 도착해도 이어 붙인다. */
async function readLines(response, onLine) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    buffer += decoder.decode(value, { stream: !done });
    const lines = buffer.split("\n");
    buffer = lines.pop(); // 마지막 조각은 아직 덜 온 줄일 수 있다
    lines.filter((line) => line.trim()).forEach((line) => onLine(JSON.parse(line)));
    if (done) break;
  }
  if (buffer.trim()) onLine(JSON.parse(buffer));
}

function handleLine(line) {
  if (line.step === "frame") {
    state.frame = line.data;
    mark("step-a1", "done");
    mark("step-a2", "active");
    drawFrame(line.data);
  } else if (line.step === "options") {
    mark("step-a2", "done");
    drawOptions(line.data);
  } else if (line.step === "error") {
    showError(line.message);
  }
}

function drawFrame(frame) {
  const pico = [
    ["P", "대상", frame.population],
    ["E/I", "노출·중재", frame.exposure],
    ["C", "비교", frame.comparison],
    ["O", "결과", frame.outcome],
  ];
  $("pico").replaceChildren(...pico.map(([tag, label, text]) =>
    el("div", "pico-cell", [el("div", "tag", tag), el("div", "label", label), el("p", "", text)])));

  const details = [
    ["핵심 질문", frame.core_question],
    ["잠정 메시지", frame.provisional_message],
    ["예상 독자", frame.audience],
    ["통념", frame.common_belief],
  ].filter(([, text]) => text);
  $("frame-details").replaceChildren(...details.flatMap(([term, text]) => [el("dt", "", term), el("dd", "", text)]));
  $("frame").hidden = false;
}

function drawOptions(optionSet) {
  $("recommendation").textContent = `추천: 안 ${optionSet.recommended} — ${optionSet.recommendation_reason}`;
  $("shortfall").textContent = optionSet.shortfall_reason ? `구성안이 ${optionSet.options.length}개인 이유: ${optionSet.shortfall_reason}` : "";
  $("shortfall").hidden = !optionSet.shortfall_reason;

  const cards = optionSet.options.map((option, index) => {
    const number = index + 1;
    const card = el("article", number === optionSet.recommended ? "option recommended" : "option");
    if (number === optionSet.recommended) card.append(el("span", "badge", "추천"));
    card.append(el("h3", "", `안 ${number}. ${option.name}`), el("p", "flow", option.flow), el("p", "strength", option.strength));
    option.parts.forEach((part, i) => {
      const box = el("section", "part", [
        el("div", "num", `PART ${i + 1}`),
        el("h4", "", part.title),
        labeled("역할", part.role),
        labeled("선정 근거", part.rationale),
      ]);
      box.dataset.n = String(i + 1);
      card.append(box, el("div", "bridge", part.bridge_question));
    });
    const button = el("button", "", "이 안 선택");
    button.type = "button";
    button.addEventListener("click", () => choose(option, card));
    card.append(button);
    return card;
  });
  $("option-list").replaceChildren(...cards);
  $("options").hidden = false;
}

/** [A3] 사람이 고른 안을 표시하고 파일로 내려받게 한다. */
function choose(option, card) {
  document.querySelectorAll(".option.selected").forEach((c) => c.classList.remove("selected"));
  card.classList.add("selected");
  const record = { topic: state.topic, frame: state.frame, option, selected_at: new Date().toISOString() };
  const url = URL.createObjectURL(new Blob([JSON.stringify(record, null, 2)], { type: "application/json" }));
  const link = Object.assign(document.createElement("a"), { href: url, download: "selected_option.json" });
  link.click();
  URL.revokeObjectURL(url);
}

/** 요소를 만든다. 글은 textContent로만 넣는다 (보안: 맨 위 주석). */
function el(tag, className, content) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (Array.isArray(content)) node.append(...content);
  else if (content != null) node.textContent = content;
  return node;
}

function labeled(key, text) {
  const p = el("p");
  p.append(el("span", "key", `${key}: `), document.createTextNode(text));
  return p;
}

function reset() {
  $("submit").disabled = true;
  $("error").hidden = true;
  $("frame").hidden = true;
  $("options").hidden = true;
  $("progress").hidden = false;
  $("elapsed").textContent = "";
  mark("step-a1", "active");
  mark("step-a2", "");
}

function mark(id, status) { $(id).className = status; }

function showError(message) {
  $("error").textContent = message;
  $("error").hidden = false;
}

function httpMessage(status) {
  if (status === 401) return "비밀번호가 맞지 않습니다.";
  if (status === 503) return "서버에 비밀번호가 설정되지 않았습니다. 관리자에게 알려 주세요.";
  if (status === 422) return "주제를 입력해 주세요.";
  return `서버 오류가 났습니다 (${status}).`;
}
