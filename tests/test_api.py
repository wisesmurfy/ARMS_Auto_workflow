"""
test_api.py — 웹 입구가 비밀번호를 지키고 결과·오류를 줄 단위로 보내는지 확인 (실제 API 호출 없음)

  요청(주제 + 비밀번호) ──► api ──► (가짜) pipeline.propose ──► NDJSON 줄 확인

확인하는 것: 비밀번호 없음·틀림·서버 미설정 거절 · 정상 2줄 · 중간 실패 시 error 줄 ·
           오류 안내문에 내부 정보가 나가지 않는가
"""

import json

import pytest
from fastapi.testclient import TestClient

from evidos import api, llm
from evidos.schemas import OptionSet, TopicFrame

FRAME = TopicFrame(
    population="p",
    exposure="e",
    comparison="해당 없음",
    outcome="o",
    core_question="q",
    provisional_message="m",
    audience="a",
)
PART = {"title": "t", "role": "r", "rationale": "근거", "bridge_question": "b"}
OPTIONS = OptionSet(
    options=[{"name": "안", "flow": "f", "strength": "s", "parts": [PART] * 3}] * 3,
    recommended=1,
    recommendation_reason="이유",
)
PASSWORD = {"X-Access-Password": "test-pw"}


@pytest.fixture
def client(monkeypatch) -> TestClient:
    monkeypatch.setenv("EVIDOS_PASSWORD", "test-pw")
    return TestClient(api.app)


def _fake_propose(monkeypatch, *steps):
    """pipeline.propose를 가짜로 바꾼다. steps의 값은 차례로 내보내고, 예외면 그 자리에서 낸다."""

    def fake(topic):
        for step in steps:
            if isinstance(step, Exception):
                raise step
            yield step

    monkeypatch.setattr(api, "propose", fake)


def _lines(response) -> list[dict]:
    return [json.loads(line) for line in response.text.splitlines()]


@pytest.mark.parametrize("headers", [{}, {"X-Access-Password": "wrong"}])
def test_wrong_or_missing_password_is_rejected(client, monkeypatch, headers):
    _fake_propose(monkeypatch, FRAME)

    assert client.post("/api/propose", json={"topic": "주제"}, headers=headers).status_code == 401


def test_unset_server_password_rejects_everyone(client, monkeypatch):
    monkeypatch.delenv("EVIDOS_PASSWORD")

    assert client.post("/api/propose", json={"topic": "주제"}, headers=PASSWORD).status_code == 503


def test_streams_frame_then_options(client, monkeypatch):
    _fake_propose(monkeypatch, FRAME, OPTIONS)

    lines = _lines(client.post("/api/propose", json={"topic": "주제"}, headers=PASSWORD))

    assert [line["step"] for line in lines] == ["frame", "options"]
    assert lines[0]["data"]["comparison"] == "해당 없음"
    assert lines[1]["data"]["options"][0]["parts"][0]["grade"] is None  # ADR-0002


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (ValueError("주제가 비어 있다"), "주제가 비어 있다"),
        (llm.LLMRefusalError("내부 상세"), "처리할 수 없습니다"),
        (llm.LLMOutputError("내부 상세"), "만들지 못했습니다"),
        (RuntimeError("sk-ant-비밀"), "알 수 없는 오류"),
    ],
)
def test_failure_becomes_short_error_line(client, monkeypatch, error, expected):
    _fake_propose(monkeypatch, FRAME, error)

    lines = _lines(client.post("/api/propose", json={"topic": "주제"}, headers=PASSWORD))

    assert [line["step"] for line in lines] == ["frame", "error"]
    assert expected in lines[1]["message"]
    assert "내부 상세" not in lines[1]["message"] and "sk-ant" not in lines[1]["message"]


def test_web_page_is_served(client):
    page = client.get("/")

    assert page.status_code == 200
    assert "ARMS EvidOS" in page.text
    assert client.get("/app.js").status_code == 200


def test_web_script_never_uses_inner_html():
    # Claude가 쓴 글이 HTML로 해석되면 글 속 <script>가 실행될 수 있다 (K22)
    script = (api.WEB_DIR / "app.js").read_text(encoding="utf-8")
    assert "innerHTML" not in script.replace("innerHTML 금지", "")
