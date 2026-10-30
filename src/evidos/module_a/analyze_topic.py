"""
analyze_topic.py — [A1] 주제 1개를 공통 분석(TopicFrame)으로 바꾼다

  topic: str  "노화로 인한 성호르몬 변화와 심혈관 대사질환"
    │  prompts/a1_analyze_topic.md의 {topic} 자리에 끼워 넣음
    ▼
  llm.ask_structured(지시문, TopicFrame)
    ▼
  TopicFrame {population, exposure, comparison, outcome,
              core_question, provisional_message, audience, common_belief?}

다음 단계: A2 build_options.py가 이 TopicFrame으로 구성안을 만든다
근거: 가이드라인 2항(주제 분해), ADR-0001(순서는 pipeline.py가 정함)
"""

from pathlib import Path

from evidos import llm
from evidos.schemas import TopicFrame

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "a1_analyze_topic.md"
MAX_TOPIC_LENGTH = 500  # 웹 입력 주제 길이 상한. 긴 글이 통째로 들어와 비용이 커지는 것을 막는다


def analyze_topic(topic: str) -> TopicFrame:
    """주제 문장을 P·E/I·C·O와 핵심 질문 등으로 분석한다.

    Args:
        topic: 사용자가 입력한 학술 주제 한 문장
    Returns:
        검사를 통과한 TopicFrame
    Raises:
        ValueError: 주제가 비었거나 MAX_TOPIC_LENGTH보다 길 때 (API를 부르기 전에 막는다)
        llm.LLMRefusalError, llm.LLMOutputError: llm.ask_structured의 실패를 그대로 올린다
    """
    topic = topic.strip()
    if not topic:
        raise ValueError("주제가 비어 있다")
    if len(topic) > MAX_TOPIC_LENGTH:
        raise ValueError(f"주제는 {MAX_TOPIC_LENGTH}자 이하여야 한다 (지금 {len(topic)}자)")

    # str.format 대신 replace: 지시문이나 주제에 있는 다른 중괄호를 건드리지 않는다
    prompt = PROMPT_PATH.read_text(encoding="utf-8").replace("{topic}", topic)
    return llm.ask_structured(prompt, TopicFrame)  # 지시문 str → TopicFrame
