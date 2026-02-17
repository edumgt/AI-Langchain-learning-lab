# Self-Query Retriever 노트 (카탈로그)

Self-Query Retriever는 "질문에서 메타데이터 조건을 추출"해
- 예: year=2026, type=policy 같은 조건으로 필터링 검색
을 할 수 있게 해줍니다.

다만, 아래가 준비되어야 합니다:
1) 문서에 의미 있는 metadata가 저장돼 있어야 함 (type, date, org 등)
2) VectorStore가 metadata 필터를 지원해야 함
3) LLM이 query+filter를 안정적으로 생성해야 함

이 레포의 v2에서는 개념/설계 노트를 제공하고,
필요하면 여러분의 문서 메타데이터 설계에 맞춘 실제 데모 파일로 확장하는 것을 권장합니다.
