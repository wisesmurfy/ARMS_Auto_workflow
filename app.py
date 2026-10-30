"""
app.py — Vercel 배포 입구 (ADR-0005). Vercel은 저장소 맨 위의 app.py에서 `app`을 찾는다

  Vercel ──► app.py ──► evidos.api.app (FastAPI: 화면 파일 + /api/propose)

실제 코드는 src/evidos/api.py에 있다. 이 파일은 그것을 Vercel이 찾는 자리에 가져다 놓기만 한다
환경변수(ANTHROPIC_API_KEY, EVIDOS_PASSWORD, EVIDOS_MODEL)는 Vercel 프로젝트 설정 화면에서 넣는다
"""

import logging
import sys
from pathlib import Path

# 파이썬이 우리 코드(src/evidos)를 찾을 수 있게 src 폴더를 찾아볼 곳에 추가한다
sys.path.insert(0, str(Path(__file__).parent / "src"))
logging.basicConfig(level=logging.INFO)  # 단계별 걸린 시간(pipeline.py)을 Vercel 로그에 남긴다

from evidos.api import app  # noqa: E402  (경로를 먼저 추가해야 import된다)

__all__ = ["app"]
