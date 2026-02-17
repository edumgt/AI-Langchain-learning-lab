#!/usr/bin/env bash
set -euo pipefail
BASE="${BASE:-http://localhost:8000}"

echo "== enqueue reindex job =="
curl -s "$BASE/ops/queue-reindex" -H "Content-Type: application/json" -d '{"mode":"full"}' | jq .

echo "== list queue =="
curl -s "$BASE/ops/queue" | jq .

echo "== proposal with save(md+pdf) =="
curl -s "$BASE/artbiz/proposal" -H "Content-Type: application/json" -d '{
  "sponsor_name":"ACME",
  "campaign_title":"도시 커뮤니티 예술 캠페인",
  "budget_total_krw":30000000,
  "weeks":2,
  "org_type":"festival",
  "auto_approve":true,
  "save":true,
  "format":"both",
  "tags":["festival","ACME"],
  "template_version":"v11"
}' | jq .

echo "== proposal versions =="
curl -s "$BASE/artbiz/proposals" | jq .
