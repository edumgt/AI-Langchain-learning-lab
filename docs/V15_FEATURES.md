# v15 섹션별 인용(각주) 자동 삽입 + 인용 위치/빈도 Eval

## 1) 섹션별 인용 자동 삽입(Deterministic)
- LLM이 인라인 인용을 빼먹어도, 서버가 섹션별로 최소 1회 이상
  `SOURCE 1/2` 마커가 들어가도록 보정합니다.
- 방식: 각 섹션 끝에 짧게 `근거: SOURCE 1, SOURCE 2` 라인을 삽입(footnote-like)

구현:
- `app/server/proposal_citation_enforcer.py`

응답에 포함:
- `citation_enforce_report`
- `citation_placement_report`

## 2) Eval 10 — 인용 위치/빈도 평가
pass 조건(score=1):
- 모든 필수 섹션에 SOURCE 마커 >= 1
- 전체 SOURCE 마커 >= 6
- appendix 외 섹션에 SOURCE 마커 >= 3 (근거가 부록에만 몰리지 않도록)

실행:
```bash
docker compose run --rm lab python catalog/eval/10_citation_placement.py
# 또는
docker compose run --rm lab python catalog/eval/05_eval_suite_runner.py
```
