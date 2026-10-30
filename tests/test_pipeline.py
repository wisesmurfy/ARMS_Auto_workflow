"""
test_pipeline.py — pipeline.propose가 A1 → A2 순서를 지키는지 확인한다 (실제 API 호출 없음)

  주제 ──► propose ──► (가짜) analyze_topic ──► 1번째로 TopicFrame
                   ──► (가짜) build_options ──► 2번째로 OptionSet

확인하는 것: 순서 · A1 결과가 A2에 그대로 넘어가는가 · A1이 실패하면 A2를 부르지 않는가
"""

import pytest

from evidos import pipeline


@pytest.fixture
def calls(monkeypatch) -> list:
    """A1·A2를 가짜로 바꾸고, 불린 순서를 기록할 목록을 준다."""
    record: list = []

    def fake_a1(topic):
        record.append(("A1", topic))
        if not topic:
            raise ValueError("주제가 비어 있다")
        return "가짜 TopicFrame"

    def fake_a2(frame):
        record.append(("A2", frame))
        return "가짜 OptionSet"

    monkeypatch.setattr(pipeline, "analyze_topic", fake_a1)
    monkeypatch.setattr(pipeline, "build_options", fake_a2)
    return record


def test_yields_a1_then_a2(calls):
    results = list(pipeline.propose("주제"))

    assert results == ["가짜 TopicFrame", "가짜 OptionSet"]
    assert calls == [("A1", "주제"), ("A2", "가짜 TopicFrame")]  # A1 결과가 A2 입력


def test_a1_result_is_available_before_a2_runs(calls):
    flow = pipeline.propose("주제")

    assert next(flow) == "가짜 TopicFrame"
    assert [name for name, _ in calls] == ["A1"]  # 화면이 A1을 그리는 동안 A2는 아직


def test_a1_failure_stops_before_a2(calls):
    with pytest.raises(ValueError):
        list(pipeline.propose(""))
    assert [name for name, _ in calls] == ["A1"]
