"""
llm.py — Claude API 호출을 모은 유일한 곳 (ADR-0004)

  prompt: str ─────┐
  output_type ─────┴─► Claude API  (응답 모양을 output_type의 JSON 스키마로 제한)
                          │
                          ▼  ① 거절? ② 잘림? ③ Pydantic 검사
                       output_type 객체   예) TopicFrame, OptionSet (schemas.py)

  실패 처리
    - 안전 정책 거절      → 다시 묻지 않고 LLMRefusalError (서버가 다른 모델로 한 번 더 시도한 뒤)
    - 응답 잘림·검사 실패 → 최대 MAX_ATTEMPTS번 다시 묻고, 그래도 안 되면 LLMOutputError
    - 네트워크·429·5xx    → SDK가 자동 재시도. 그래도 실패하면 anthropic.APIError를 그대로 올린다

환경변수(.env): ANTHROPIC_API_KEY (SDK가 직접 읽음), EVIDOS_MODEL (비우면 DEFAULT_MODEL)
"""

import logging
import os
from functools import cache

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-opus-5-5"
EFFORT = "medium"  # 생각의 깊이: low < medium < high. Opus 5.5의 기본값이지만 명시해 둔다
MAX_TOKENS = 16000  # 생각 + 답변 합계 상한. 넘으면 JSON이 중간에 잘린다
MAX_ATTEMPTS = 3


class LLMOutputError(Exception):
    """여러 번 다시 물어도 응답이 스키마에 맞지 않을 때."""


class LLMRefusalError(Exception):
    """Claude가 안전 정책으로 답을 거절했을 때."""


@cache
def _client() -> anthropic.Anthropic:
    load_dotenv()  # .env → 환경변수
    return anthropic.Anthropic()


def _model() -> str:
    return os.getenv("EVIDOS_MODEL") or DEFAULT_MODEL


def ask_structured[T: BaseModel](prompt: str, output_type: type[T]) -> T:
    """프롬프트를 보내고, 답을 output_type 모양으로 받는다.

    Args:
        prompt: 완성된 지시문 (prompts/*.md에 주제 등을 채운 것)
        output_type: 받고 싶은 모양. schemas.py의 모델 클래스
    Returns:
        검사를 통과한 output_type 객체
    Raises:
        LLMRefusalError: 안전 정책으로 거절됐을 때
        LLMOutputError: MAX_ATTEMPTS번 모두 모양이 맞지 않았을 때
        anthropic.APIError: 네트워크·인증·요금 한도 등 API 자체 오류
    """
    schema = anthropic.transform_schema(output_type)  # 모델 → JSON 스키마 (grade 칸은 빠짐)

    for attempt in range(1, MAX_ATTEMPTS + 1):
        response = _client().beta.messages.create(
            model=_model(),
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
            output_config={
                "effort": EFFORT,
                "format": {"type": "json_schema", "schema": schema},
            },
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",  # 거절되면 서버가 다른 모델로 한 번 더 시도한다
        )

        if response.stop_reason == "refusal":  # 다시 물어도 같은 결과라 바로 멈춘다
            raise LLMRefusalError(f"안전 정책으로 거절됨: {response.stop_details}")
        if any(it.type == "fallback_message" for it in response.usage.iterations or []):
            logger.warning("요청 모델 %s가 거절해 %s가 대신 답함", _model(), response.model)
        if response.stop_reason == "max_tokens":
            logger.warning("시도 %d/%d: 응답이 MAX_TOKENS에서 잘림", attempt, MAX_ATTEMPTS)
            continue

        text = "".join(block.text for block in response.content if block.type == "text")
        try:
            return output_type.model_validate_json(text)  # JSON str → T (개수·빈칸·추천 번호 검사)
        except ValidationError as error:
            logger.warning("시도 %d/%d: 스키마 검사 실패 %s", attempt, MAX_ATTEMPTS, error)

    raise LLMOutputError(f"{MAX_ATTEMPTS}번 시도했지만 {output_type.__name__} 모양으로 받지 못함")
