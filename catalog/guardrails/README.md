# Guardrails (실습 관점)

LangChain 자체가 '강제 안전장치'를 제공한다기보다는,
- Structured Output / Parsers
- 정책 체크 노드(전/후처리)
- Context-only RAG 프롬프트
같은 패턴으로 "가드레일을 설계"합니다.

실행:
- `catalog/guardrails/01_schema_guard.py`
- `catalog/guardrails/02_context_only_rag_guard.py`
- `catalog/guardrails/03_policy_checks.py`
