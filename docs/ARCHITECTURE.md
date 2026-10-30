# ARCHITECTURE

ARMS EvidOS는 **Workflow**다. 순서는 코드(`pipeline.py`)가 정하고, LLM은 각 단계의 칸만 채운다 ([ADR-0001](decisions/0001-workflow-not-agent.md)).

## 모듈 A~D

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

| 모듈 | 하는 일 | 넣는 것 | 나오는 것 | 상태 |
|---|---|---|---|---|
| A | 주제를 P·E/I·C·O로 분해하고 3-Part 구성안 3개 중 사람이 1개 선택 | 주제 문장 | `selected_option.json` | v1 개발 중 |
| B | 선택된 구성안으로 PubMed 검색 | `selected_option.json` | `records.json` | 예정 |
| C | 관련성 → 근거 수준 → 최신성 → 저널 품질 순으로 선별 | `records.json` | `selected_studies.json` | 예정 |
| D | 문헌 요약과 원고 초안(Word) 작성 | `selected_studies.json` | 원고 초안 | 예정 |

B·C·D 폴더는 구현할 때 만든다. 빈 폴더를 미리 두지 않는다.

## 모듈 A 데이터 흐름

```
topic: str
  │  [A1] module_a/analyze_topic.py   + prompts/a1_analyze_topic.md
  ▼
TopicFrame  {population, exposure, comparison, outcome,
             core_question, provisional_message, audience, common_belief?}
  │  [A2] module_a/build_options.py   + prompts/a2_build_options.md
  ▼
OptionSet   {options: Option ×1~3, recommended, recommendation_reason, shortfall_reason?}
             Option = {name, flow, strength, parts: Part ×3}
             Part   = {title, role, rationale, bridge_question, grade}
  │  [A2.5] 근거 등급화 자리 — v1은 grade: None, LLM 스키마에서 제외 (ADR-0002)
  ▼
  │  [A3] 웹 화면에서 사람이 1개 선택 (Gate, ADR-0005)
  ▼
Option  →  selected_option.json {topic, frame, option, selected_at} (브라우저 다운로드, 서버 저장 없음)
```

- 스키마의 정확한 필드는 `src/evidos/schemas.py`가 단일 출처다. `?`는 비어 있을 수 있는 칸이다.
- 구성안이 3개 미만이면 `shortfall_reason`이 필수다 (가이드라인 5항: 억지로 3개를 채우지 않는다).
- 의학 규칙(PICO, Part 역할)은 [guideline-summary.md](guideline-summary.md)가 단일 출처다.

## 파일 역할

| 파일 | 역할 |
|---|---|
| `pipeline.py` | A1 → A2 → (A2.5) → A3 순서만 담당 |
| `llm.py` | Claude API 호출을 모은 유일한 곳. 구조화 출력으로 Pydantic 모델을 받는다 ([ADR-0004](decisions/0004-claude-as-llm-provider.md)) |
| `schemas.py` | 단계 사이를 오가는 데이터 모양 |
| `module_a/*.py` | 단계별 변환 1개씩: `analyze_topic.py`(A1, Step 3), `build_options.py`(A2, Step 4) |
| `prompts/*.md` | 앱 안의 LLM이 읽는 지시문. 코드와 분리 |
| `api.py` | 웹 입구(FastAPI): 비밀번호 확인 후 pipeline을 부르고, A1·A2 결과를 나오는 대로 한 줄씩(NDJSON) 흘려보낸다 (Step 5, [ADR-0005](decisions/0005-web-ui-on-vercel.md)) |
| `app.py` (저장소 맨 위) | Vercel 배포 입구. `evidos.api.app`을 Vercel이 찾는 자리에 가져다 놓기만 한다 (Step 7) |
| `web/` | 화면(HTML·CSS·JS): 공통 분석과 구성안 3개를 보여 주고 선택받는다. api.py가 `/`에서 내보낸다 (Step 6) |
| `tests/` | API 호출 없는 코드 테스트 (무료) |
| `evals/` | 실제 API를 부르는 품질 평가 (유료, 프롬프트 변경 시) |
