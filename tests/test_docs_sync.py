"""
test_docs_sync.py — 코드를 바꾸고 문서를 안 고치면 실패하는 테스트 (CLAUDE.md Definition of Done)

  코드 (단일 출처)                     문서
  schemas.py의 모델·필드      ──► ARCHITECTURE.md "모듈 A 데이터 흐름" 그림에 모두 있는가
  src/evidos/*.py 파일        ──► ARCHITECTURE.md "파일 역할" 표에 모두 있는가
  src/evidos/module_* 폴더    ──► ARCHITECTURE.md 모듈 표에서 "예정"이 아닌가
  ARCHITECTURE.md의 ADR 링크  ──► docs/decisions/에 실제 파일이 있는가

README.md는 Step 9에서 만든다. 생기면 같은 검사를 README에도 추가한다.
"""

import re
from pathlib import Path

import pytest
from pydantic import BaseModel

from evidos import schemas

ROOT = Path(__file__).parent.parent
PACKAGE = ROOT / "src" / "evidos"
ARCHITECTURE = (ROOT / "docs" / "ARCHITECTURE.md").read_text(encoding="utf-8")


def _section(heading: str) -> str:
    """ARCHITECTURE.md에서 '## heading'부터 다음 '## '까지의 글."""
    start = ARCHITECTURE.index(f"## {heading}")
    end = ARCHITECTURE.find("\n## ", start + 1)
    return ARCHITECTURE[start:] if end == -1 else ARCHITECTURE[start:end]


SCHEMA_MODELS = [schemas.TopicFrame, schemas.OptionSet, schemas.Option, schemas.Part]


@pytest.mark.parametrize("model", SCHEMA_MODELS, ids=lambda m: m.__name__)
def test_data_flow_lists_every_schema_field(model: type[BaseModel]):
    data_flow = _section("모듈 A 데이터 흐름")
    assert model.__name__ in data_flow
    missing = [name for name in model.model_fields if not re.search(rf"\b{name}\b", data_flow)]
    assert not missing, f"ARCHITECTURE.md 데이터 흐름에 {model.__name__}의 칸이 없음: {missing}"


def test_file_roles_list_every_python_file():
    file_roles = _section("파일 역할")
    files = [p.name for p in PACKAGE.glob("*.py") if p.name != "__init__.py"]
    missing = [name for name in files if f"`{name}`" not in file_roles]
    assert not missing, f"ARCHITECTURE.md 파일 역할 표에 없음: {missing}"


def test_existing_modules_are_not_marked_planned():
    module_table = _section("모듈 A~D")
    for folder in PACKAGE.glob("module_*"):
        letter = folder.name.removeprefix("module_").upper()  # module_a → A
        row = re.search(rf"^\| {letter} \|.*$", module_table, re.MULTILINE)
        assert row, f"{folder.name} 폴더가 있는데 모듈 표에 {letter} 줄이 없음"
        assert "예정" not in row.group(), f"{folder.name} 폴더가 있는데 상태가 '예정'"


def test_adr_links_point_to_existing_files():
    links = re.findall(r"\(decisions/([^)]+\.md)\)", ARCHITECTURE)
    assert links
    missing = [name for name in links if not (ROOT / "docs" / "decisions" / name).exists()]
    assert not missing, f"ARCHITECTURE.md가 없는 ADR을 가리킴: {missing}"
