# v10 운영 모드 확장

## 1) 재인덱싱 큐(배치/증분)
- `POST /ops/queue-reindex` 로 재인덱싱 작업을 큐에 적재합니다.
- `GET /ops/queue` 로 큐 상태 확인
- 워커 실행:
```bash
docker compose run --rm lab python catalog/ops/01_index_worker.py
```
> 학습용 구현은 jsonl 파일 큐이며, 운영에서는 Redis/SQS 등으로 확장하세요.

## 2) 제안서 저장(MD/PDF) + 버전 관리
- `/artbiz/proposal` 호출 시 옵션:
  - `save=true`
  - `format=md|pdf|both` (기본 both)
- 저장 위치:
  - `/app/storage/proposals/<timestamp>_<sponsor>_<campaign>/proposal.md`
  - `/app/storage/proposals/.../proposal.pdf`
- 버전 목록:
  - `GET /artbiz/proposals`

## 3) 평가: 인용 준수율
- `catalog/eval/07_citation_compliance.py`
- suite runner에 포함되어 함께 실행 가능:
```bash
docker compose run --rm lab python catalog/eval/05_eval_suite_runner.py
```
