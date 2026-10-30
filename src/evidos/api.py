"""
api.py — 웹 입구(FastAPI). 화면과 Claude 사이에서 API 키를 숨긴 채 pipeline을 대신 부른다 (ADR-0005)

  브라우저 ── POST /api/propose  {"topic": "..."}  + 헤더 X-Access-Password
     │  ① 비밀번호 확인 (틀리면 401, 서버에 비밀번호가 설정 안 됐으면 503)
     ▼
  pipeline.propose(topic) ── 나오는 대로 한 줄씩 흘려보낸다 (NDJSON: 한 줄 = JSON 1개)
     {"step": "frame",   "data": TopicFrame}     ← A1 끝 (약 10초)
     {"step": "options", "data": OptionSet}      ← A2 끝 (약 1분)
     {"step": "error",   "message": "..."}       ← 중간에 실패하면 이 줄로 끝난다

환경변수: EVIDOS_PASSWORD (화면 접속 비밀번호). 저장소는 붙이지 않는다 (선택 결과는 브라우저가 받음)
로컬 실행: uv run uvicorn evidos.api:app --reload
"""

import json
import logging
import os
import secrets
from collections.abc import Iterator

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from evidos import llm
from evidos.pipeline import propose
from evidos.schemas import TopicFrame

load_dotenv()  # .env → 환경변수 (EVIDOS_PASSWORD, ANTHROPIC_API_KEY)
logger = logging.getLogger(__name__)
app = FastAPI(title="ARMS EvidOS")


class TopicRequest(BaseModel):
    """화면이 보내는 요청 본문."""

    topic: str


def _check_password(given: str | None) -> None:
    expected = os.getenv("EVIDOS_PASSWORD")
    if not expected:  # 비밀번호 없이 공개되는 일을 막는다: 설정이 없으면 아무도 못 쓴다
        raise HTTPException(503, "서버에 EVIDOS_PASSWORD가 설정되지 않았습니다")
    if given is None or not secrets.compare_digest(given.encode(), expected.encode()):
        raise HTTPException(401, "비밀번호가 맞지 않습니다")


def _stream(topic: str) -> Iterator[str]:
    """pipeline 결과를 NDJSON 줄로 바꾼다. 오류는 사용자에게 보여 줄 짧은 문장으로만 알린다."""
    try:
        for result in propose(topic):
            step = "frame" if isinstance(result, TopicFrame) else "options"
            line = {"step": step, "data": result.model_dump(mode="json")}  # 모델 → JSON 1줄
            yield json.dumps(line, ensure_ascii=False) + "\n"
    except Exception as error:
        logger.exception("propose 실패: %s", topic)
        yield json.dumps({"step": "error", "message": _user_message(error)}, ensure_ascii=False)


def _user_message(error: Exception) -> str:
    """오류 → 화면 안내문. 내부 사정(키, 서버 주소 등)은 화면에 내보내지 않는다."""
    if isinstance(error, ValueError):
        return str(error)  # 주제가 비었거나 너무 길다 (A1 입력 검사)
    if isinstance(error, llm.LLMRefusalError):
        return "이 주제는 처리할 수 없습니다. 표현을 바꿔 다시 시도해 주세요."
    if isinstance(error, llm.LLMOutputError):
        return "구성안을 만들지 못했습니다. 다시 시도해 주세요."
    if isinstance(error, anthropic.APIError):
        return "Claude API 연결에 문제가 있습니다. 잠시 후 다시 시도해 주세요."
    return "알 수 없는 오류가 났습니다."


@app.post("/api/propose")
def propose_endpoint(
    request: TopicRequest, x_access_password: str | None = Header(default=None)
) -> StreamingResponse:
    """주제를 받아 A1 → A2 결과를 차례로 흘려보낸다."""
    _check_password(x_access_password)
    return StreamingResponse(_stream(request.topic), media_type="application/x-ndjson")
