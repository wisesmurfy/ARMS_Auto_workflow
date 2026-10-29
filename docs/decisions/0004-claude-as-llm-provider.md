# ADR-0004: 앱 안의 LLM은 Claude API(Anthropic)를 쓴다

- 상태: Accepted
- 날짜: 2026-10-29

## 배경
- EvidOS는 각 단계에서 LLM을 호출하고, 출력을 Pydantic 모델(구조화 출력)로 받아야 한다
- 개발을 돕는 AI(Claude Code)와 앱 안에서 호출되는 AI(Claude API)는 역할이 다르다. 같은 회사 모델이어도 서로 별개다
- 승인된 설계(`docs/design/v1-plan.md`)는 OpenAI API를 가정했다
- 사용자에게 Claude API 무료 크레딧이 있다
- Anthropic Python SDK(`anthropic`)도 구조화 출력을 지원한다. Pydantic 모델을 넘기면 검사된 객체를 돌려준다
  (정확한 사용법은 Step 2에서 공식 문서로 확인한다)

## 결정
- 앱 안의 LLM 공급자는 Claude API다. 설계 문서의 OpenAI 부분은 이 ADR로 대체한다
- API 키는 `.env`의 `ANTHROPIC_API_KEY`로 읽는다
- 모델 이름은 코드에 박지 않고 `.env`의 `EVIDOS_MODEL`로 지정한다. 기본값은 Step 2에서 정한다
- Claude API 호출은 `src/evidos/llm.py` 한 곳에서만 한다

## 결과
- 좋은 점: 무료 크레딧 안에서 eval을 돌릴 수 있다. 공급자를 바꿀 때 `llm.py`·`.env`·의존성만 고치면 된다
- 감수할 점: 크레딧이 끝나면 사용료가 든다. 그래서 테스트는 가짜 LLM으로, 실제 호출은 eval에서만 한다
- 설계 스냅샷은 수정하지 않으므로 `v1-plan.md`에는 OpenAI가 남아 있다. 둘이 다르면 이 ADR이 우선한다
- 바꾸려면: `llm.py`의 호출부 교체 → `pyproject.toml` 의존성 교체 → 이 ADR을 Superseded로 표시하고 새 ADR 작성
- 다시 볼 조건: 크레딧이 끝나 비용을 비교해야 할 때, 또는 eval에서 구조화 출력 실패가 반복될 때
