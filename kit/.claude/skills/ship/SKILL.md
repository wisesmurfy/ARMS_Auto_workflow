---
name: ship
description: 로드맵 Step의 모든 리뷰 Unit이 승인된 뒤 실행. 린트·테스트 → 문서 확인 → 푸시 → PR 안내 → 사용자에게 완료 보고. "Step 끝났어", "ship", "올려줘"라고 할 때 사용
---

# /ship — Step 마무리

전제: 이번 Step의 모든 Unit이 사용자 "OK"로 승인되고 커밋되어 있다. 아니면 멈추고 남은 Unit을 알린다.

## 순서 (하나라도 실패하면 멈추고 보고한다. 커밋·푸시하지 않는다)
1. `uv run ruff check .` 와 `uv run ruff format --check .` 와 `uv run pytest`
   - 테스트가 아직 없어서 "collected 0 items"(exit 5)면 실패가 아니라 "테스트 없음"으로 보고한다
2. `/sync-docs` 로 문서 누락 확인. 고칠 게 있으면 `[docs]` Unit으로 리뷰를 받고 다시 1번부터
3. `git status` 로 커밋 안 된 변경이 없는지 확인
4. 현재 브랜치가 `step/*` 인지 확인하고 `git push -u origin <브랜치>`
5. PR
   - `gh` 가 있으면 `gh pr create` 로 만든다
   - 없으면 푸시 출력의 "Create a pull request" 링크를 전달한다

## 6. 보고 (이 형식 그대로, 쉬운 말로)
```
✅ Step N 완료: <한국어 요약>
커밋 n개: [타입] … / [타입] …
테스트: n passed (또는 "아직 없음") · 린트 통과
리뷰할 곳: <파일> (핵심), <파일>
PR: <링크>  ← 리뷰 후 merge 해주세요
```
이어서 붙여넣기용 코드 블록 4개를 준다 (형식: `.claude/rules/git.md` "PR 넘길 때"):
PR 제목 / PR 설명(무엇을·확인·리뷰 기록) / Merge 커밋 제목 / Merge 커밋 설명

## 하지 않는 것
- main에 푸시, force push, `--no-verify`
- merge (사용자가 GitHub에서 직접 한다)
