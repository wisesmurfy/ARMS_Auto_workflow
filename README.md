# ARMS EvidOS

**Turn one medical topic into three evidence-ready 3-Part outlines — and let a human pick.**

[한국어](README.ko.md)

ARMS EvidOS is a small, deliberately boring LLM *workflow* for academic writing.
You type a topic such as *"age-related sex hormone changes and cardiometabolic disease"*;
it decomposes the topic into **P·E/I·C·O**, designs up to **three structurally different outlines**
(each with Part 1 → 2 → 3), recommends one, and stops. **A human makes the final choice.**

The whole of Module A is ~400 lines of Python plus two prompt files.
The order of steps lives in code, not in the model.

> **Status** — Module A (topic → outlines → human selection) is complete as v1 and runs as a password-protected web app.
> Modules B–D (PubMed search, study selection, manuscript draft) are planned.

---

## What it does

```
 [Topic]
    │
    ▼
 ┌─────────────────────────────────────────────┐
 │ A. Question structuring & option selection  │  ✅ v1
 │    A1 PICO analysis → A2 3 options          │
 │    → (A2.5 evidence grading, planned)       │
 │    → A3 human selection                     │
 └─────────────────────────────────────────────┘
    │  selected_option.json
    ▼
 ┌─────────────────────────────────────────────┐
 │ B. PubMed search (E-utilities API)          │  🔜
 └─────────────────────────────────────────────┘
    │  records.json
    ▼
 ┌─────────────────────────────────────────────┐
 │ C. Study selection                          │  🔜
 │    Relevance → Evidence level → Recency     │
 │    → Journal quality                        │
 └─────────────────────────────────────────────┘
    │  selected_studies.json
    ▼
 ┌─────────────────────────────────────────────┐
 │ D. Summaries & manuscript draft (Word)      │  🔜
 └─────────────────────────────────────────────┘
```

| Module | What it does | Input | Output | Status |
|---|---|---|---|---|
| **A** | Decompose the topic into P·E/I·C·O, design up to 3 outlines, human picks one | topic sentence | `selected_option.json` | ✅ v1 |
| **B** | Search PubMed for each Part of the selected outline | `selected_option.json` | `records.json` | 🔜 |
| **C** | Select studies by relevance → evidence level → recency → journal quality | `records.json` | `selected_studies.json` | 🔜 |
| **D** | Summarize studies and draft the manuscript (Word) | `selected_studies.json` | draft | 🔜 |

## Example

Topic: **노화로 인한 성호르몬 변화와 심혈관 대사질환** (age-related sex hormone changes and cardiometabolic disease)

**A1 · Topic frame** (≈10 s)

| P | E/I | C | O |
|---|---|---|---|
| Adults 40+ (peri/post-menopausal women, men with age-related testosterone decline) | Age-related decline in estrogen / testosterone | Same-age peers with preserved hormone levels | Cardiometabolic disease (CAD, stroke, T2D, metabolic syndrome) |

**A2 · Three outlines** (≈1 min)

| | Option 1 ⭐ *Mechanism → Association → Action* | Option 2 *Women vs. Men* | Option 3 *Myth check* |
|---|---|---|---|
| Part 1 | What do sex hormones do to the heart and metabolism? | Women: menopause and cardiometabolic change | Where does "it's all hormones" come from? |
| Part 2 | What is observed — and what is still uncertain? | Men: testosterone decline and its effects | Can aging be separated from hormones? Does replacement help? |
| Part 3 | Protecting cardiometabolic health after midlife | Comparison and sex-specific management | Evidence-based response |

The model is instructed to keep association ≠ causation, never to promote surrogate markers to hard outcomes,
and **never to invent papers, PMIDs, or numbers** — no literature has been searched at this stage.

## Quickstart

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/wisesmurfy/ARMS_Auto_workflow.git
cd ARMS_Auto_workflow
uv sync
cp .env.example .env        # fill in ANTHROPIC_API_KEY and EVIDOS_PASSWORD
uv run uvicorn evidos.api:app --reload
```

Open <http://127.0.0.1:8000>, enter the password and a topic.
The topic frame appears first, the outlines about a minute later. Click **이 안 선택** (*choose this option*) to download `selected_option.json`.

```bash
uv run pytest               # no API calls, free
uv run ruff check .         # lint
```

Deployment: merging to `main` deploys to Vercel (entrypoint: [`app.py`](app.py)). Set `ANTHROPIC_API_KEY` and `EVIDOS_PASSWORD` in the Vercel project settings.

## How Module A works

```
topic: str
  │  [A1] module_a/analyze_topic.py  + prompts/a1_analyze_topic.md
  ▼
TopicFrame   {population, exposure, comparison, outcome,
              core_question, provisional_message, audience, common_belief?}
  │  [A2] module_a/build_options.py  + prompts/a2_build_options.md
  ▼
OptionSet    {options: Option ×1–3, recommended, recommendation_reason, shortfall_reason?}
              Option = {name, flow, strength, parts: Part ×3}
              Part   = {title, role, rationale, bridge_question, grade}
  │  [A2.5] evidence grading slot — v1 keeps grade = None, hidden from the LLM
  ▼
  │  [A3] a human picks one in the browser (the Gate)
  ▼
selected_option.json  {topic, frame, option, selected_at}
```

A few choices that do most of the work:

- **Workflow, not agent.** [`pipeline.py`](src/evidos/pipeline.py) fixes the order A1 → A2. The model fills in each box; it never decides what happens next.
- **One door to the model.** Every LLM call goes through [`llm.py`](src/evidos/llm.py): structured output against a Pydantic schema, then *refusal → stop*, *truncation or invalid shape → retry (max 3)*. Constraints the API cannot enforce (e.g. exactly 3 Parts) are re-checked client-side.
- **Schemas are the contract.** [`schemas.py`](src/evidos/schemas.py) is the single source of truth for every hand-off. `grade` exists but is excluded from the LLM schema, so the model cannot fabricate one.
- **Prompts are files.** Domain instructions live in [`prompts/`](src/evidos/prompts/), never in Python strings. Medical rules live in one place: [`docs/guideline-summary.md`](docs/guideline-summary.md).
- **Stream, don't wait.** [`api.py`](src/evidos/api.py) sends results as NDJSON lines, so the browser renders the PICO frame while A2 is still running.
- **Untrusted text stays data.** Topics and model output are never executed: prompts tell the model to ignore instructions inside the input, and the UI renders model text with `textContent` only.

## Repository layout

```
app.py                     Vercel entrypoint (re-exports evidos.api.app)
src/evidos/
  pipeline.py              order of steps — the only place that decides it
  llm.py                   the only place that calls the LLM
  schemas.py               data shapes between steps
  api.py                   web entry: password check + NDJSON stream
  module_a/                one transformation per file (A1, A2)
  prompts/                 instructions the in-app LLM reads
  web/                     HTML · CSS · JS (A3 happens here)
tests/                     no-API tests, including a docs-vs-code sync test
docs/
  ARCHITECTURE.md          module map, data flow, file roles
  guideline-summary.md     the medical rules (single source)
  decisions/               ADRs — why things are the way they are
```

## Design decisions

| ADR | Decision |
|---|---|
| [0001](docs/decisions/0001-workflow-not-agent.md) | Build a workflow, not an agent |
| [0002](docs/decisions/0002-grading-before-selection.md) | Grade evidence *before* the human chooses (A2.5) |
| [0003](docs/decisions/0003-pubmed-only-v1.md) | Use PubMed only for literature search in v1 |
| [0004](docs/decisions/0004-claude-as-llm-provider.md) | Use the Claude API as the in-app LLM |
| [0005](docs/decisions/0005-web-ui-on-vercel.md) | Ship Module A as a web app (FastAPI + HTML on Vercel) |

## Evaluation

- **Code tests** (`uv run pytest`, free): the LLM is replaced by a fake, so the tests check behavior — retry and refusal handling, step order, password gate, that `grade` never reaches the model, that the UI never uses `innerHTML`, and that the docs still match the code.
- **Quality evals** (paid, planned): example topics from the guideline become the answer key; outputs are checked by code first, then by an LLM judge, then by a human. Examples are kept *out* of the prompts so the eval stays honest.

## Roadmap

- [x] A1 topic frame · A2 three outlines · A3 human selection · web UI
- [ ] Quality evals for Module A
- [ ] A2.5 evidence grading (A / B / C / pending) from PubMed hit rates
- [ ] B · PubMed search (E-utilities)
- [ ] C · study selection
- [ ] D · summaries and Word manuscript draft

## Disclaimer

This is a drafting aid for an academic writing team, **not medical advice** and **not a systematic review**.
Outlines are proposals; a human chooses and verifies. The 3-Part structure and the A/B/C grades are internal ARMS conventions, not externally validated scales, and are distinct from GRADE certainty ratings.

## Credits

- **Planning & methodology** — ARMS Academic Team (*3-Part Structuring Guideline*)
- **Architecture design & development** — solo project by [@wisesmurfy](https://github.com/wisesmurfy), a member of the ARMS Academic Team
- Methodological references (Cochrane Handbook, PRISMA-ScR, GRADE, AMSTAR 2, AGREE II) are listed in [`docs/guideline-summary.md`](docs/guideline-summary.md)

## License

Not yet specified.
