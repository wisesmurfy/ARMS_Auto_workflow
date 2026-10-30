"""
test_analyze_topic.py — [A1] 지시서를 제대로 채워 보내는지 확인한다 (실제 API 호출 없음)

  주제 ──► analyze_topic ──► (가짜) llm.ask_structured ──► 보낸 지시서·양식 기록, TopicFrame 반환

확인하는 것: 주제가 {topic} 자리에 들어가는가 · 빈/긴 주제는 Claude를 부르기 전에 막는가 ·
           지시서 파일이 프롬프트 규칙(XML 태그, {topic} 자리)을 지키는가
"""

import pytest

from evidos.module_a import analyze_topic as a1
from evidos.schemas import TopicFrame

FRAME = TopicFrame(
    population="중년 남녀",
    exposure="성호르몬 감소",
    comparison="해당 없음",
    outcome="심혈관 대사질환",
    core_question="성호르몬 감소는 심혈관 대사질환 위험과 연관되는가?",
    provisional_message="연관될 가능성이 있다",
    audience="일반 대중(추론)",
)


@pytest.fixture
def sent(monkeypatch) -> list:
    """llm.ask_structured를 가짜로 바꾸고, 보낸 (지시서, 양식)을 담을 목록을 준다."""
    calls: list = []

    def fake_ask(prompt, output_type):
        calls.append((prompt, output_type))
        return FRAME

    monkeypatch.setattr(a1.llm, "ask_structured", fake_ask)
    return calls


def test_topic_is_inserted_into_prompt(sent):
    result = a1.analyze_topic("  노화와 {특수} 심혈관 질환  ")

    prompt, output_type = sent[0]
    assert result is FRAME
    assert output_type is TopicFrame
    assert "노화와 {특수} 심혈관 질환" in prompt  # 앞뒤 공백 제거, 중괄호도 그대로
    assert "{topic}" not in prompt


@pytest.mark.parametrize("topic", ["", "   ", "가" * (a1.MAX_TOPIC_LENGTH + 1)])
def test_invalid_topic_is_rejected_before_calling_claude(sent, topic):
    with pytest.raises(ValueError):
        a1.analyze_topic(topic)
    assert sent == []  # Claude를 부르지 않았다 = 크레딧을 쓰지 않았다


def test_prompt_file_follows_prompt_rules():
    # .claude/rules/prompts.md: XML 태그로 구획, 입력 자리는 {topic}
    text = a1.PROMPT_PATH.read_text(encoding="utf-8")
    for tag in ["role", "guideline", "input", "output_rules"]:
        assert f"<{tag}>" in text and f"</{tag}>" in text
    assert text.count("{topic}") == 1
