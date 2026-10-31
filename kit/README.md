# Agent Dev Kit

LLM 앱(에이전트·챗봇·워크플로)을 Claude Code와 바이브코딩으로 만들 때 쓰는 **공통 개발 프로토콜** 템플릿.
보안 규칙, 리뷰 카드, 브랜치·커밋·PR 형식, 문서화(아키텍처·결정 기록), 문서-코드 일치 테스트가 들어 있다.

## 새 프로젝트 시작
1. GitHub에서 이 저장소의 **Use this template → Create a new repository**
2. 새 저장소를 내 컴퓨터에 받는다 (`git clone ...`)
3. 그 폴더에서 Claude Code를 열고: **"BOOTSTRAP.md 따라 시작해줘"**
4. Claude의 질문(무엇을 만드나, Workflow/Agent, 어디서 돌리나 …)에 답하면 틀이 채워진다

## 들어 있는 것
- `CLAUDE.md` — 프로젝트 규칙 틀 (`{{ }}` 칸을 BOOTSTRAP에서 채움)
- `.claude/` — 규칙 6개, 스킬 2개(/ship, /sync-docs), 권한 설정
- `docs/` — 아키텍처 틀, 도메인 규칙 틀, ADR 템플릿, 문법 사전
- `tests/test_docs_sync.py` — 문서와 코드가 어긋나면 실패
- `patterns/llm.py` — LLM 호출 견본

## 규칙을 고치고 싶을 때
- 이 템플릿을 고치면 **앞으로 만드는** 프로젝트에만 반영된다. 이미 만든 프로젝트는 각자 고친다
