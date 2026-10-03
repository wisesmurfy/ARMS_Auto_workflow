---
paths:
  - "src/evidos/prompts/**"
---

# 프롬프트 규칙 (앱 안의 OpenAI가 읽는 파일)

- 구조: `<role>`, `<guideline>`, `<input>`, `<output_rules>` XML 태그로 구획한다
- 의학 규칙은 docs/guideline-summary.md에서 가져오고 항 번호를 적는다 (예: 가이드라인 2항)
- 출력 형태는 schemas.py의 Pydantic 모델이 강제한다. 프롬프트에 JSON 예시를 길게 쓰지 않는다
- 입력 자리는 `{topic}`처럼 중괄호 변수로 둔다
- 프롬프트를 고치면 반드시 eval을 돌린다: `uv run python -m evals.run`
