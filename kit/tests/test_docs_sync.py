"""
test_docs_sync.py — 코드를 바꾸고 문서를 안 고치면 실패하는 테스트 (CLAUDE.md Definition of Done)

  코드 (단일 출처)                       문서
  schemas.py의 공개 모델·필드     ──► ARCHITECTURE.md "데이터 흐름"에 모두 있는가
  src/<패키지>/*.py 파일          ──► ARCHITECTURE.md "파일 역할" 표에 모두 있는가
  ARCHITECTURE.md의 ADR 링크      ──► docs/decisions/에 실제 파일이 있는가

패키지는 src/ 아래 __init__.py가 있는 폴더 1개로 자동으로 찾는다. 아직 없으면 건너뛴다
"""

import importlib
import re
from pathlib import Path

import pytest
from pydantic import BaseModel

ROOT = Path(__file__).parent.parent
ARCHITECTURE = (ROOT / "docs" / "ARCHITECTURE.md").read_text(encoding="utf-8")
PACKAGES = [p.parent for p in (ROOT / "src").glob("*/__init__.py")]
PACKAGE = PACKAGES[0] if len(PACKAGES) == 1 else None
needs_package = pytest.mark.skipif(PACKAGE is None, reason="src/<패키지> 없음 (BOOTSTRAP 전)")


def _section(heading: str) -> str:
    """ARCHITECTURE.md에서 '## heading'부터 다음 '## '까지의 글."""
    start = ARCHITECTURE.index(f"## {heading}")
    end = ARCHITECTURE.find("\n## ", start + 1)
    return ARCHITECTURE[start:] if end == -1 else ARCHITECTURE[start:end]


def _schema_models() -> list[type[BaseModel]]:
    if PACKAGE is None or not (PACKAGE / "schemas.py").exists():
        return []
    module = importlib.import_module(f"{PACKAGE.name}.schemas")
    return [
        obj
        for name, obj in vars(module).items()
        if isinstance(obj, type)
        and issubclass(obj, BaseModel)
        and obj.__module__ == module.__name__
        and not name.startswith("_")
    ]


@pytest.mark.parametrize("model", _schema_models(), ids=lambda m: m.__name__)
def test_data_flow_lists_every_schema_field(model: type[BaseModel]):
    data_flow = _section("데이터 흐름")
    assert model.__name__ in data_flow
    missing = [name for name in model.model_fields if not re.search(rf"\b{name}\b", data_flow)]
    assert not missing, f"ARCHITECTURE.md 데이터 흐름에 {model.__name__}의 칸이 없음: {missing}"


@needs_package
def test_file_roles_list_every_python_file():
    file_roles = _section("파일 역할")
    files = [p.name for p in PACKAGE.glob("*.py") if p.name != "__init__.py"]
    missing = [name for name in files if f"`{name}`" not in file_roles]
    assert not missing, f"ARCHITECTURE.md 파일 역할 표에 없음: {missing}"


def test_adr_links_point_to_existing_files():
    links = re.findall(r"\(decisions/([^)]+\.md)\)", ARCHITECTURE)
    links = [name for name in links if "{{" not in name]  # 아직 안 채운 틀 칸은 건너뛴다
    missing = [name for name in links if not (ROOT / "docs" / "decisions" / name).exists()]
    assert not missing, f"ARCHITECTURE.md가 없는 ADR을 가리킴: {missing}"
