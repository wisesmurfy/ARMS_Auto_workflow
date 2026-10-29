---
paths:
  - "evals/**"
---

# Eval 규칙 (실제 Claude API 호출, 비용 발생)

- 케이스는 YAML 파일 1개 = 주제 1개 (`evals/cases/*.yaml`)
- 정답지는 출처를 적는다 (예: 가이드라인 3~4쪽 예시)
- 판정 순서: 코드 검사(빈 칸, Part 개수) 먼저 → 애매한 것만 LLM-judge → 마지막은 사람 검토
- 프롬프트를 바꿨을 때만 돌린다. 평소 확인은 무료인 `uv run pytest`로 한다
