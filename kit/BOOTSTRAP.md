# BOOTSTRAP — 새 프로젝트 시작 절차 (Claude가 따르는 문서)

사용자가 "BOOTSTRAP 따라 시작해줘"라고 하면 Claude는 아래 순서를 지킨다.
각 단계 끝에서 멈추고 사용자 확인("OK")을 받는다. 마지막에 이 파일은 사용자 승인 후 지운다.

## 1. 질문 (한 번에 하나씩, 쉬운 말로. 선택지와 추천을 함께 준다)
1. 무엇을 만드나: 누가 쓰고, 무엇을 넣으면 무엇이 나오나
2. **Workflow인가 Agent인가**
   - Workflow: 단계 순서가 정해져 있다 (예: 분석 → 생성 → 사람 선택)
   - Agent: 대화 흐름이나 다음 행동을 LLM이 정한다 (예: 인터뷰 질문 고르기)
   - 섞인 경우: 어디까지 LLM에게 맡기고, 어디서 사람이 확인하나(Gate)
3. 어떤 LLM을 쓰나 (기본 추천: Claude API, 최신 모델)
4. 어디서 돌리나: 웹, 메신저 봇(카카오톡 등), CLI. **응답 시간 제한**이 있는지 공식 문서로 확인한다
5. 지켜야 할 도메인 규칙·원문 문서가 있나. 개인정보를 다루나

## 2. 채우기 (답을 바탕으로)
- `CLAUDE.md`의 `{{ }}` 칸을 모두 채운다
- `pyproject.toml`의 이름과 설명을 채우고 `src/<패키지>/__init__.py`를 만든다
- `.claude/rules/review.md`의 🔴 정독 목록을 실제 파일 이름으로 바꾼다
- `docs/domain-rules.md`를 원문 요약으로 채운다 (실명·원문 예시 제외)
- `docs/ARCHITECTURE.md`의 그림과 표를 채운다
- `docs/decisions/0001-*.md`: 2번 질문(Workflow/Agent)의 결정을 ADR로 쓴다. 이후 큰 결정(LLM 선택, 배포 방식)도 ADR로

## 3. 설치와 확인
- `uv sync` → `uv run ruff check .` → `uv run pytest` 통과 확인
- `.env.example`을 `.env`로 복사하는 법을 알려 준다. Claude는 `.env`를 읽지 않는다

## 4. 로드맵
- Step 1~N을 표로 제안한다. 각 Step = 브랜치 1개 = PR 1개
- LLM 호출이 필요하면 `patterns/llm.py`를 `src/<패키지>/llm.py`로 복사해 Step 2쯤에서 리뷰 Unit으로 다룬다
- 메신저 봇처럼 응답 시간 제한이 짧으면, 오래 걸리는 LLM 호출을 어떻게 나눌지(먼저 응답하고 나중에 보내기 등)를 로드맵 초기에 정한다

## 5. 첫 커밋
- `[chore] 프로젝트 틀 설정` (설정·규칙) / `[docs] 아키텍처와 첫 ADR` 처럼 나눠 커밋한다
- 이 BOOTSTRAP.md 삭제도 승인 후 커밋에 포함한다

## 이 키트에 들어 있는 공통 장치
| 장치 | 파일 |
|---|---|
| 보안 약속 + 기계 차단 | `.claude/rules/security.md`, `.claude/settings.json` |
| 리뷰 카드·목줄 레벨 | `.claude/rules/review.md` |
| 브랜치·커밋·PR 형식 | `.claude/rules/git.md`, `.claude/skills/ship` |
| 주석 규칙 | `.claude/rules/python.md` |
| 지시서·평가 규칙 | `.claude/rules/prompts.md`, `evals.md` |
| 문서-코드 일치 | `.claude/skills/sync-docs`, `tests/test_docs_sync.py` |
| 결정 기록 | `docs/decisions/0000-template.md` |
| 문법 사전 | `docs/learning/python-glossary.md` |
| LLM 호출 견본 | `patterns/llm.py` (거절·잘림·검사·재시도) |
