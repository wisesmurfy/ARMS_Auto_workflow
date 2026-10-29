---
name: sync-docs
description: 코드와 문서가 어긋난 곳을 찾아 고친다. 모듈·입출력·실행 명령을 바꾼 뒤, 또는 /ship 전에 사용. "문서 맞춰줘", "sync docs"라고 할 때 사용
---

# /sync-docs — 코드 ↔ 문서 맞추기

기준은 항상 **코드**다. 문서를 코드에 맞춘다. 코드가 틀려 보이면 고치지 말고 사용자에게 묻는다.

## 확인 목록 (코드 → 맞춰야 할 문서)
| 코드에서 볼 것 | 맞춰야 할 문서 |
|---|---|
| `src/evidos/module_*` 폴더 목록과 상태 | README.md·README.ko.md 모듈 그림·표, docs/ARCHITECTURE.md |
| `src/evidos/schemas.py` 모델과 필드 | docs/ARCHITECTURE.md 데이터 흐름 |
| `pyproject.toml` 의 실행 명령·의존성 | CLAUDE.md Commands, README Quickstart |
| 파일 맨 위 "지도" 주석과 함수 Args/Returns | 실제 함수 시그니처 |
| `docs/decisions/` ADR 목록 | README "Design decisions" 링크 |

## 순서
1. 위 표를 한 줄씩 비교하고 어긋난 곳을 목록으로 만든다 (파일:줄, 무엇이 다른가)
2. 없으면 "문서 일치"라고 보고하고 끝낸다
3. 있으면 고친 뒤 `[docs]` Unit 리뷰 카드를 준다. "OK" 전에는 커밋하지 않는다
4. `uv run pytest` (문서-코드 일치 테스트 포함)

## 하지 않는 것
- `docs/design/` 수정 (승인된 스냅샷)
- 기존 ADR 내용 수정 (바뀌면 새 ADR + 기존 것에 "Superseded" 표시, 사용자 확인)
- 아직 없는 파일(README 등)을 이 skill에서 새로 만들기 — 로드맵 Step에서 만든다
