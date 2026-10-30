# 파이썬 문법 사전

리뷰 카드 8번에서 처음 나온 문법을 모은다. 두 번째부터는 "사전 #n"으로만 가리킨다.

| # | 문법 | 한 줄 뜻 | 처음 본 곳 | 다시 본 횟수 |
|---|------|---------|-----------|------------|
| 1 | `class 이름(BaseModel):` + `칸: 타입` | 데이터 모양(양식지) 정의. 칸마다 타입을 적으면 Pydantic이 값이 맞는지 검사한다 | schemas.py:36 | 0 |
| 2 | `str \| None` | "글자 또는 비어 있음". 없어도 되는 칸에 쓴다 | schemas.py:46 | 0 |
| 3 | `try:` … `except 오류종류:` | 실패할 수 있는 일을 시도하고, 그 오류가 나면 멈추지 않고 except 아래를 실행한다 | llm.py:89 | 0 |
| 4 | `def f[T: BaseModel](x: type[T]) -> T` | "넣은 모양 그대로 돌려준다"는 표시. TopicFrame을 넣으면 TopicFrame이 나온다 | llm.py:52 | 0 |
| 5 | `@pytest.fixture` (함수 위 `@이름`) | 아래 함수에 기능을 덧씌운다. fixture는 "테스트가 인자 이름으로 달라고 하면 pytest가 준비해 넘겨주는 도구" | tests/test_llm.py:60 | 0 |
| 6 | `def f(**request):` | 이름 붙은 인자(`model=...`, `max_tokens=...`)를 몽땅 사전(dict) 하나로 받는다 | tests/test_llm.py:55 | 0 |
| 7 | `Path(__file__).parent / "prompts"` | 파일 경로 다루기. `__file__`은 지금 파일 위치, `.parent`는 한 단계 위 폴더, `/`는 경로 잇기 | module_a/analyze_topic.py:21 | 0 |
| 8 | `raise 오류종류("메시지")` | 일부러 오류를 내서 실행을 멈추고 부른 쪽에 알린다 (#3 `except`로 받을 수 있다) | module_a/analyze_topic.py:38 | 0 |
| 9 | `f"- {이름}: {값}"` | f-문자열. 따옴표 앞 `f`가 있으면 `{ }` 안의 변수 값이 글자 속에 채워진다 | module_a/build_options.py:30 | 0 |
| 10 | `for 키, 값 in 사전.items():` | 사전(dict)의 (이름, 내용) 쌍을 하나씩 꺼내 두 변수에 나눠 담으며 반복한다 | module_a/build_options.py:27 | 0 |
