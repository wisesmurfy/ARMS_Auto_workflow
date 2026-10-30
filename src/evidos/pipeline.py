"""
pipeline.py — 모듈 A의 순서를 정하는 유일한 곳 (ADR-0001: LLM이 다음 단계를 고르지 않는다)

  topic: str
    │ [A1] analyze_topic   주제 → TopicFrame      ─► 1번째로 내보냄 (화면이 PICO 분석을 먼저 그린다)
    │ [A2] build_options   TopicFrame → OptionSet ─► 2번째로 내보냄 (화면이 구성안 카드를 그린다)
    │ [A2.5] 근거 등급화 자리 — v1은 하지 않음 (Part.grade = None, ADR-0002)
    ▼
  api.py가 받은 순서대로 웹 화면에 흘려보낸다
    │ [A3] 사람이 화면에서 1개 선택 (Gate, ADR-0005) — 서버가 아니라 브라우저에서 일어난다
    ▼
  Option → selected_option.json (브라우저 다운로드)
"""

import logging
import time
from collections.abc import Iterator

from evidos.module_a.analyze_topic import analyze_topic
from evidos.module_a.build_options import build_options
from evidos.schemas import OptionSet, TopicFrame

logger = logging.getLogger(__name__)


def propose(topic: str) -> Iterator[TopicFrame | OptionSet]:
    """주제 1개로 A1 → A2를 차례로 실행하고, 각 결과가 나오는 즉시 내보낸다.

    Args:
        topic: 사용자가 입력한 학술 주제 한 문장
    Returns:
        TopicFrame 1개, 이어서 OptionSet 1개를 차례로 내보내는 흐름
    Raises:
        ValueError: 주제가 비었거나 너무 길 때 (A1, API 호출 전)
        llm.LLMRefusalError, llm.LLMOutputError: Claude가 거절했거나 모양을 못 맞췄을 때
    """
    started = time.monotonic()
    frame = analyze_topic(topic)  # str → TopicFrame
    logger.info("A1 %.0f초", time.monotonic() - started)
    yield frame

    started = time.monotonic()
    option_set = build_options(frame)  # TopicFrame → OptionSet
    # 걸린 시간을 남긴다: 웹 배포(Vercel)의 실행 시간 제한과 비교하기 위해 (ADR-0005)
    logger.info("A2 %.0f초", time.monotonic() - started)
    yield option_set
