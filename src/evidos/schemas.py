"""
schemas.py — 모듈 A의 단계 사이를 오가는 데이터 모양 (단일 출처)

  topic: str
    │ [A1]
    ▼
  TopicFrame        공통 분석: P·E/I·C·O, 핵심 질문, 잠정 메시지, 예상 독자, (통념)
    │ [A2]
    ▼
  OptionSet         구성안 1~3개 + 추천 + (3개 미만이면) 부족 사유
    └─ Option       이름·전개·강점 + Part 3개
         └─ Part    제목·역할·선정 근거·연결 질문·(등급: v1은 None)
    │ [A3] 사람이 1개 선택
    ▼
  Option

LLM 출력은 llm.py에서 이 모델들로 검사된다. 칸이 비거나 모양이 틀리면 여기서 걸린다.
필드 description은 칸 이름표만 적는다. 작성 규칙은 prompts/*.md에 둔다.
근거: 가이드라인 2항(공통 분석·Part 역할), 5항(출력 항목), ADR-0002(등급 자리)
"""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.json_schema import SkipJsonSchema

Grade = Literal["A", "B", "C", "판정 보류"]  # 가이드라인 3항


class _Schema(BaseModel):
    """모든 모델의 공통 규칙: 빈 문자열 금지, 정의되지 않은 칸 금지."""

    model_config = ConfigDict(str_min_length=1, extra="forbid")


class TopicFrame(_Schema):
    """[A1 출력] 주제의 공통 분석. 가이드라인 2항."""

    population: str = Field(description="P: 연구 대상")
    exposure: str = Field(description="E/I: 노출 또는 중재")
    comparison: str = Field(description="C: 비교")
    outcome: str = Field(description="O: 결과")
    core_question: str = Field(description="핵심 질문")
    provisional_message: str = Field(description="잠정 메시지")
    audience: str = Field(description="예상 독자")
    common_belief: str | None = Field(default=None, description="통념")


class Part(_Schema):
    """구성안의 Part 1개. 몇 번째 Part인지는 Option.parts 안의 위치로 정한다."""

    title: str = Field(description="Part 제목")
    role: str = Field(description="역할과 범위")
    rationale: str = Field(description="선정 근거")
    bridge_question: str = Field(description="연결 질문")
    # LLM에게 보내는 스키마에서 빼서, LLM이 등급을 지어낼 수 없게 한다 (ADR-0002, 가이드라인 3항)
    grade: SkipJsonSchema[Grade | None] = None


class Option(_Schema):
    """[A3에서 고르는 단위] 구성안 1개. 가이드라인 5항."""

    name: str = Field(description="구성안 이름")  # 예) "남녀 비교형"
    flow: str = Field(description="전개")  # 예) "남성 → 여성 → 통합 관리"
    strength: str = Field(description="이 안의 강점")
    parts: list[Part] = Field(min_length=3, max_length=3)  # [Part 1, Part 2, Part 3]


class OptionSet(_Schema):
    """[A2 출력] 구성안 묶음과 추천. 가이드라인 4·5항."""

    options: list[Option] = Field(min_length=1, max_length=3)
    recommended: int = Field(ge=1, description="우선 추천하는 구성안 번호")  # 1부터 센다
    recommendation_reason: str = Field(description="추천 이유와 구성안 간 차이")
    shortfall_reason: str | None = Field(default=None, description="구성안이 3개 미만인 이유")

    @model_validator(mode="after")
    def _check_consistency(self) -> Self:
        if self.recommended > len(self.options):
            raise ValueError(f"recommended={self.recommended}인데 구성안은 {len(self.options)}개다")
        # 억지로 3개를 채우지 않되, 부족하면 이유를 남긴다 (가이드라인 5항)
        if len(self.options) < 3 and self.shortfall_reason is None:
            raise ValueError("구성안이 3개 미만이면 shortfall_reason이 필요하다")
        return self
