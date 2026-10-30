"""
build_options.py — [A2] 공통 분석(TopicFrame)으로 3-Part 구성안 묶음(OptionSet)을 만든다

  TopicFrame {population, exposure, ..., audience, common_belief?}
    │  칸마다 "- 이름표 (칸): 값" 한 줄로 풀어 prompts/a2_build_options.md의 {topic_frame}에 끼움
    ▼
  llm.ask_structured(지시문, OptionSet)
    ▼
  OptionSet {options: Option ×1~3, recommended, recommendation_reason, shortfall_reason?}
             Option = {name, flow, strength, parts: Part ×3}   Part.grade는 v1에서 항상 None

다음 단계: A3에서 사람이 Option 1개를 고른다 (Step 5~6, ADR-0005)
근거: 가이드라인 2·4·5항, ADR-0002(등급 자리)
"""

from pathlib import Path

from evidos import llm
from evidos.schemas import OptionSet, TopicFrame

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "a2_build_options.md"


def _describe(frame: TopicFrame) -> str:
    """TopicFrame → 지시서에 넣을 글 (칸마다 한 줄). 비어 있는 칸(예: 통념)은 줄을 생략한다."""
    lines = []
    for name, field in TopicFrame.model_fields.items():
        value = getattr(frame, name)
        if value is not None:  # 예) - P: 연구 대상 (population): 중년 남녀
            lines.append(f"- {field.description} ({name}): {value}")
    return "\n".join(lines)


def build_options(frame: TopicFrame) -> OptionSet:
    """공통 분석을 받아 구성안 1~3개와 추천을 만든다.

    Args:
        frame: A1 analyze_topic이 돌려준 공통 분석
    Returns:
        검사를 통과한 OptionSet (Part 3개 규칙, 추천 번호, 부족 사유는 schemas.py가 검사)
    Raises:
        llm.LLMRefusalError, llm.LLMOutputError: llm.ask_structured의 실패를 그대로 올린다
    """
    prompt = PROMPT_PATH.read_text(encoding="utf-8").replace("{topic_frame}", _describe(frame))
    return llm.ask_structured(prompt, OptionSet)  # 지시문 str → OptionSet
