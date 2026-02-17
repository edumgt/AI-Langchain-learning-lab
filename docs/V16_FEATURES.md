# v16 [1][2] 각주 표기 + 부록 근거 매핑 + Eval 11

## 1) 본문 각주 변환
- 본문에서 `SOURCE 1/2` 마커를 `[1]` / `[2]`로 변환합니다.
- 인라인 형태 `(SOURCE 1)`도 `[1]`로 통일합니다.

## 2) 부록(근거) 매핑 자동 생성
- `used_docs`(RAG 상위 2개 스니펫)을 사용해 부록에 아래를 삽입합니다:
  - `[1] <SOURCE 1 스니펫>`
  - `[2] <SOURCE 2 스니펫>`

구현:
- `app/server/proposal_footnotes.py`

API 응답:
- `footnote_report` 추가

## 3) Eval 11 — 각주 매핑/사용 평가
pass 조건:
- 본문에 `[1]`과 `[2]`가 존재
- 부록에 `[1]`, `[2]` 매핑 라인이 존재

실행:
```bash
docker compose run --rm lab python catalog/eval/11_footnote_mapping.py
# 또는
docker compose run --rm lab python catalog/eval/05_eval_suite_runner.py
```
