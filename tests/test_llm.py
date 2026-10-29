"""
test_llm.py — llm.ask_structured의 실패 처리 흐름을 가짜 Claude로 확인한다 (실제 API 호출 없음)

  FakeClient에 미리 준비한 응답 목록 ──► ask_structured ──► 반환값 / 오류 / 호출 횟수 확인
    응답 1개 = {stop_reason, content[text], usage.iterations, model}

확인하는 것: 정상 · 잘림 후 재시도 · 검사 실패 3번 · 거절 · 대신 답한 모델 로그 · 모델 선택
"""

import json
from types import SimpleNamespace

import pytest

from evidos import llm
from evidos.schemas import OptionSet, TopicFrame

TOPIC_FRAME = {
    "population": "중년 남녀",
    "exposure": "노화로 인한 성호르몬 감소",
    "comparison": "해당 없음",
    "outcome": "심혈관 대사질환",
    "core_question": "성호르몬 변화가 심혈관 대사질환 위험을 바꾸는가",
    "provisional_message": "성호르몬 감소는 위험 요인일 수 있다",
    "audience": "일반 독자 (추론)",
}
PART = {"title": "제목", "role": "역할", "rationale": "근거", "bridge_question": "질문"}


def _option_set(parts_per_option: int) -> dict:
    option = {"name": "안", "flow": "흐름", "strength": "강점", "parts": [PART] * parts_per_option}
    return {"options": [option] * 3, "recommended": 1, "recommendation_reason": "이유"}


def _response(text: str = "", stop_reason: str = "end_turn", fallback: bool = False):
    """Claude 응답 1개의 가짜. llm.py가 읽는 속성만 둔다."""
    iterations = [SimpleNamespace(type="fallback_message")] if fallback else None
    return SimpleNamespace(
        stop_reason=stop_reason,
        stop_details=None,
        content=[SimpleNamespace(type="text", text=text)],
        usage=SimpleNamespace(iterations=iterations),
        model="claude-fallback" if fallback else "claude-opus-5-5",
    )


class FakeClient:
    """client.beta.messages.create(...)를 흉내 낸다. 부를 때마다 준비한 응답을 하나씩 꺼낸다."""

    def __init__(self, responses: list):
        self.responses = list(responses)
        self.calls: list[dict] = []  # 보낸 요청 기록 (model, output_config 등)
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._create))

    def _create(self, **request):
        self.calls.append(request)
        return self.responses.pop(0)


@pytest.fixture
def use_fake(monkeypatch):
    """llm._client()가 FakeClient를 돌려주게 바꾸는 함수를 준다."""

    def install(*responses) -> FakeClient:
        fake = FakeClient(responses)
        monkeypatch.setattr(llm, "_client", lambda: fake)
        return fake

    return install


def test_valid_response_returns_model(use_fake):
    fake = use_fake(_response(json.dumps(TOPIC_FRAME, ensure_ascii=False)))

    result = llm.ask_structured("프롬프트", TopicFrame)

    assert isinstance(result, TopicFrame)
    assert result.comparison == "해당 없음"
    assert len(fake.calls) == 1


def test_grade_is_hidden_from_llm_schema(use_fake):
    # ADR-0002: LLM이 등급을 지어내지 못하게 grade 칸은 스키마에서 빠져야 한다
    fake = use_fake(_response(json.dumps(_option_set(3), ensure_ascii=False)))

    result = llm.ask_structured("프롬프트", OptionSet)

    sent_schema = json.dumps(fake.calls[0]["output_config"]["format"]["schema"])
    assert "grade" not in sent_schema
    assert all(part.grade is None for option in result.options for part in option.parts)


def test_truncated_response_is_retried(use_fake):
    valid = json.dumps(TOPIC_FRAME, ensure_ascii=False)
    fake = use_fake(_response('{"population": "중', "max_tokens"), _response(valid))

    assert isinstance(llm.ask_structured("프롬프트", TopicFrame), TopicFrame)
    assert len(fake.calls) == 2


def test_invalid_shape_every_time_raises_output_error(use_fake):
    two_parts = json.dumps(_option_set(2), ensure_ascii=False)  # Part 3개 규칙 위반
    fake = use_fake(*[_response(two_parts)] * llm.MAX_ATTEMPTS)

    with pytest.raises(llm.LLMOutputError):
        llm.ask_structured("프롬프트", OptionSet)
    assert len(fake.calls) == llm.MAX_ATTEMPTS


def test_refusal_raises_without_retry(use_fake):
    fake = use_fake(_response(stop_reason="refusal"))

    with pytest.raises(llm.LLMRefusalError):
        llm.ask_structured("프롬프트", TopicFrame)
    assert len(fake.calls) == 1


def test_fallback_model_is_logged(use_fake, caplog):
    use_fake(_response(json.dumps(TOPIC_FRAME, ensure_ascii=False), fallback=True))

    llm.ask_structured("프롬프트", TopicFrame)

    assert "claude-fallback" in caplog.text


@pytest.mark.parametrize(
    ("env_value", "expected"),
    [("claude-haiku-5-5", "claude-haiku-5-5"), ("", llm.DEFAULT_MODEL)],
)
def test_model_comes_from_env_or_default(use_fake, monkeypatch, env_value, expected):
    monkeypatch.setenv("EVIDOS_MODEL", env_value)
    fake = use_fake(_response(json.dumps(TOPIC_FRAME, ensure_ascii=False)))

    llm.ask_structured("프롬프트", TopicFrame)

    assert fake.calls[0]["model"] == expected
