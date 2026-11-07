# ARMS EvidOS

**의학 주제 한 줄을 3-Part 구성안 세 개로 설계하고, 최종 선택은 사람이 한다.**

[English](README.md)

ARMS EvidOS는 학술 원고를 위한 작고 의도적으로 단순한 LLM **워크플로**입니다.
*"노화로 인한 성호르몬 변화와 심혈관 대사질환"* 같은 주제를 넣으면, 주제를 **P·E/I·C·O**로 나누고
Part 1 → 2 → 3으로 된 **서로 실질적으로 다른 구성안을 최대 3개** 설계한 뒤 하나를 추천하고 멈춥니다.
**최종 선택은 사람이 합니다.**

모듈 A 전체는 파이썬 약 400줄과 지시서 파일 2개입니다.
단계의 순서는 모델이 아니라 코드가 정합니다.

> **상태** — 모듈 A(주제 → 구성안 → 사람 선택)는 v1으로 완성되어 비밀번호로 보호된 웹 앱으로 동작합니다.
> 모듈 B~D(PubMed 검색, 논문 선별, 원고 초안)는 예정입니다.

---

## 하는 일

```
 [주제]
    │
    ▼
 ┌─────────────────────────────────────────────┐
 │ A. 질문 구조화와 구성안 선택                 │  ✅ v1
 │    A1 PICO 분석 → A2 구성안 3개              │
 │    → (A2.5 근거 등급화, 예정)                │
 │    → A3 사람 선택                            │
 └─────────────────────────────────────────────┘
    │  selected_option.json
    ▼
 ┌─────────────────────────────────────────────┐
 │ B. PubMed 검색 (E-utilities API)             │  🔜
 └─────────────────────────────────────────────┘
    │  records.json
    ▼
 ┌─────────────────────────────────────────────┐
 │ C. 논문 선별                                 │  🔜
 │    관련성 → 근거 수준 → 최신성 → 저널 품질   │
 └─────────────────────────────────────────────┘
    │  selected_studies.json
    ▼
 ┌─────────────────────────────────────────────┐
 │ D. 문헌 요약과 원고 초안 (Word)              │  🔜
 └─────────────────────────────────────────────┘
```

| 모듈 | 하는 일 | 넣는 것 | 나오는 것 | 상태 |
|---|---|---|---|---|
| **A** | 주제를 P·E/I·C·O로 분해하고 구성안을 최대 3개 설계, 사람이 1개 선택 | 주제 문장 | `selected_option.json` | ✅ v1 |
| **B** | 선택된 구성안의 Part별로 PubMed 검색 | `selected_option.json` | `records.json` | 🔜 |
| **C** | 관련성 → 근거 수준 → 최신성 → 저널 품질 순으로 선별 | `records.json` | `selected_studies.json` | 🔜 |
| **D** | 문헌 요약과 원고 초안(Word) 작성 | `selected_studies.json` | 원고 초안 | 🔜 |

## 예시

주제: **노화로 인한 성호르몬 변화와 심혈관 대사질환**

**A1 · 공통 분석** (약 10초)

| P | E/I | C | O |
|---|---|---|---|
| 40세 이상 중·노년 남녀 (폐경 전후 여성, 테스토스테론이 감소하는 남성) | 노화에 따른 에스트로겐·테스토스테론 감소 | 같은 연령대에서 호르몬 수치가 유지된 사람 | 심혈관 대사질환 (관상동맥질환, 뇌졸중, 제2형 당뇨병, 대사증후군) |

**A2 · 구성안 3개** (약 1분)

| | 안 1 ⭐ *기전–연관–대응 표준형* | 안 2 *여성·남성 병렬 비교형* | 안 3 *통념 검증형* |
|---|---|---|---|
| Part 1 | 성호르몬은 심장과 대사에 어떤 일을 하는가 | 여성: 폐경 이행기 에스트로겐 감소와 심장·대사 변화 | '갱년기 이후 성인병은 호르몬 탓'이라는 믿음은 어디서 왔나 |
| Part 2 | 무엇이 관찰되었고 무엇이 불확실한가 | 남성: 연령 관련 테스토스테론 감소의 영향 | 노화와 호르몬을 나눌 수 있는가, 보충은 질환을 줄이는가 |
| Part 3 | 중년 이후 심장·대사 건강을 지키는 방법 | 남녀 비교와 통합: 공통 원칙과 성별 맞춤 주의점 | 근거에 맞는 대응 |

모델은 연관성과 인과를 구분하고, 대리지표 개선을 질환 감소로 바꿔 쓰지 않으며,
**논문·PMID·수치를 지어내지 않도록** 지시받습니다. 이 단계에서는 아직 문헌을 검색하지 않았기 때문입니다.

## 빠른 시작

Python 3.12 이상과 [uv](https://docs.astral.sh/uv/)가 필요합니다.

```bash
git clone https://github.com/wisesmurfy/ARMS_Auto_workflow.git
cd ARMS_Auto_workflow
uv sync
cp .env.example .env        # ANTHROPIC_API_KEY와 EVIDOS_PASSWORD를 채운다
uv run uvicorn evidos.api:app --reload
```

<http://127.0.0.1:8000>을 열고 비밀번호와 주제를 입력합니다.
공통 분석이 먼저 나오고, 약 1분 뒤 구성안이 나옵니다. **이 안 선택**을 누르면 `selected_option.json`이 내려받아집니다.

```bash
uv run pytest               # API 호출 없음, 무료
uv run ruff check .         # 린트
```

배포: `main`에 merge하면 Vercel에 배포됩니다(입구: [`app.py`](app.py)). `ANTHROPIC_API_KEY`와 `EVIDOS_PASSWORD`는 Vercel 프로젝트 설정에 넣습니다.

## 모듈 A의 동작

```
topic: str
  │  [A1] module_a/analyze_topic.py  + prompts/a1_analyze_topic.md
  ▼
TopicFrame   {population, exposure, comparison, outcome,
              core_question, provisional_message, audience, common_belief?}
  │  [A2] module_a/build_options.py  + prompts/a2_build_options.md
  ▼
OptionSet    {options: Option ×1~3, recommended, recommendation_reason, shortfall_reason?}
              Option = {name, flow, strength, parts: Part ×3}
              Part   = {title, role, rationale, bridge_question, grade}
  │  [A2.5] 근거 등급화 자리 — v1은 grade = None, LLM에게는 숨김
  ▼
  │  [A3] 사람이 브라우저에서 1개 선택 (Gate)
  ▼
selected_option.json  {topic, frame, option, selected_at}
```

대부분의 일을 해내는 선택 몇 가지:

- **에이전트가 아니라 워크플로.** [`pipeline.py`](src/evidos/pipeline.py)가 A1 → A2 순서를 고정합니다. 모델은 칸을 채울 뿐, 다음에 무엇을 할지 정하지 않습니다.
- **모델로 가는 문은 하나.** 모든 LLM 호출은 [`llm.py`](src/evidos/llm.py)를 지납니다. Pydantic 스키마로 구조화 출력을 받고, *거절 → 즉시 중단*, *잘림·모양 오류 → 재시도(최대 3번)*. API가 강제하지 못하는 제약(Part 정확히 3개 등)은 받은 뒤 다시 검사합니다.
- **스키마가 계약서.** [`schemas.py`](src/evidos/schemas.py)가 단계 사이 데이터의 단일 출처입니다. `grade` 칸은 있지만 LLM 스키마에서 빠져 있어 모델이 등급을 지어낼 수 없습니다.
- **지시서는 파일.** 도메인 지시는 [`prompts/`](src/evidos/prompts/)에만 두고, 파이썬 문자열에 쓰지 않습니다. 의학 규칙은 [`docs/guideline-summary.md`](docs/guideline-summary.md) 한곳에 있습니다.
- **기다리지 말고 흘려보내기.** [`api.py`](src/evidos/api.py)가 결과를 NDJSON 줄로 보내서, A2가 도는 동안 브라우저가 PICO 분석을 먼저 그립니다.
- **외부 글은 데이터로만.** 주제와 모델 출력은 실행되지 않습니다. 지시서는 입력 안의 지시를 무시하라고 명시하고, 화면은 모델 글을 `textContent`로만 넣습니다.

## 저장소 구조

```
app.py                     Vercel 입구 (evidos.api.app을 연결)
src/evidos/
  pipeline.py              단계 순서 — 순서를 정하는 유일한 곳
  llm.py                   LLM을 부르는 유일한 곳
  schemas.py               단계 사이 데이터 모양
  api.py                   웹 입구: 비밀번호 확인 + NDJSON 스트림
  module_a/                파일 1개 = 변환 1개 (A1, A2)
  prompts/                 앱 안의 LLM이 읽는 지시서
  web/                     HTML · CSS · JS (A3가 여기서 일어남)
tests/                     API 없는 테스트 (문서-코드 일치 테스트 포함)
docs/
  ARCHITECTURE.md          모듈 지도, 데이터 흐름, 파일 역할
  guideline-summary.md     의학 규칙 (단일 출처)
  decisions/               ADR — 왜 이렇게 만들었는지
```

## 설계 결정

| ADR | 결정 |
|---|---|
| [0001](docs/decisions/0001-workflow-not-agent.md) | 에이전트가 아니라 워크플로로 만든다 |
| [0002](docs/decisions/0002-grading-before-selection.md) | 근거 등급화는 사람이 고르기 *전에* 둔다 (A2.5) |
| [0003](docs/decisions/0003-pubmed-only-v1.md) | v1의 문헌 검색은 PubMed만 쓴다 |
| [0004](docs/decisions/0004-claude-as-llm-provider.md) | 앱 안의 LLM은 Claude API를 쓴다 |
| [0005](docs/decisions/0005-web-ui-on-vercel.md) | 모듈 A를 웹 앱으로 제공한다 (FastAPI + HTML, Vercel) |

## 검증

- **코드 테스트** (`uv run pytest`, 무료): LLM을 가짜로 바꿔 동작을 확인합니다 — 재시도·거절 처리, 단계 순서, 비밀번호 관문, `grade`가 모델에 전달되지 않는지, 화면이 `innerHTML`을 쓰지 않는지, 문서가 코드와 맞는지.
- **품질 평가** (유료, 예정): 가이드라인의 주제 예시를 정답지로 삼아 코드 검사 → LLM 판정 → 사람 검토 순으로 채점합니다. 예시는 지시서에 넣지 않아 평가가 공정하게 유지됩니다.

## 로드맵

- [x] A1 공통 분석 · A2 구성안 3개 · A3 사람 선택 · 웹 화면
- [ ] 모듈 A 품질 평가
- [ ] A2.5 근거 등급화 (A / B / C / 판정 보류), PubMed 일치율 기반
- [ ] B · PubMed 검색 (E-utilities)
- [ ] C · 논문 선별
- [ ] D · 문헌 요약과 Word 원고 초안

## 고지

학술팀의 원고 작성을 돕는 도구이며, **의료 조언이 아니고 체계적 문헌고찰도 아닙니다.**
구성안은 제안이며, 사람이 고르고 검증합니다. 3-Part 구조와 A/B/C 등급은 ARMS 내부 운영 규칙으로 외부에서 검증된 척도가 아니며, GRADE의 근거 확실성 등급과도 다릅니다.

## 만든 사람

- **기획·방법론** — ARMS 학술팀 (「3-Part 구조화 가이드라인」)
- **아키텍처 설계 및 개발** — ARMS 학술팀원 [@wisesmurfy](https://github.com/wisesmurfy) 단독 개발
- 방법론 참고문헌(Cochrane Handbook, PRISMA-ScR, GRADE, AMSTAR 2, AGREE II)은 [`docs/guideline-summary.md`](docs/guideline-summary.md)에 있습니다

## 라이선스

아직 정하지 않았습니다.
