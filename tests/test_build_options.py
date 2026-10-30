"""
test_build_options.py — [A2] 공통 분석을 지시서에 제대로 채워 보내는지 확인한다 (실제 API 호출 없음)

  TopicFrame ──► build_options ──► (가짜) llm.ask_structured ──► 보낸 지시서·양식 기록

확인하는 것: 분석 칸이 모두 지시서에 들어가는가 · 빈 통념은 "None"으로 적지 않는가 ·
           지시서 파일이 프롬프트 규칙(XML 태그, {topic_frame} 자리)을 지키는가
"""

import pytest

from evidos.module_a import build_options as a2
from evidos.schemas import OptionSet, TopicFrame

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
        return "가짜 OptionSet"

    monkeypatch.setattr(a2.llm, "ask_structured", fake_ask)
    return calls


def test_every_frame_field_is_sent(sent):
    a2.build_options(FRAME)

    prompt, output_type = sent[0]
    assert output_type is OptionSet
    assert "{topic_frame}" not in prompt
    for value in FRAME.model_dump(exclude_none=True).values():
        assert value in prompt


def test_empty_common_belief_is_omitted_not_written_as_none():
    text = a2._describe(FRAME)  # common_belief 없음

    assert "common_belief" not in text
    assert "None" not in text
    assert len(text.splitlines()) == 7


def test_common_belief_is_included_when_present():
    frame = FRAME.model_copy(update={"common_belief": "호르몬을 보충하면 예방된다"})

    assert "(common_belief): 호르몬을 보충하면 예방된다" in a2._describe(frame)


def test_prompt_file_follows_prompt_rules():
    # .claude/rules/prompts.md: XML 태그로 구획, 입력 자리는 중괄호 변수
    text = a2.PROMPT_PATH.read_text(encoding="utf-8")
    for tag in ["role", "guideline", "input", "output_rules"]:
        assert f"<{tag}>" in text and f"</{tag}>" in text
    assert text.count("{topic_frame}") == 1
