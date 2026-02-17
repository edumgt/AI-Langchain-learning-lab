#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-http://localhost:8000}"

echo "== health =="
curl -s "$BASE/health" | jq .

echo "== chat (rag) =="
curl -s "$BASE/chat" -H "Content-Type: application/json" -d '{"q":"후원 패키지 혜택 3개 요약","mode":"rag"}' | jq .

echo "== tools/budget-split =="
curl -s "$BASE/tools/budget-split" -H "Content-Type: application/json" -d '{"total_krw":30000000}' | jq .

echo "== tools/sponsorship-package =="
curl -s "$BASE/tools/sponsorship-package" -H "Content-Type: application/json" -d '{"tier_count":3,"total_target_krw":30000000,"org_type":"festival"}' | jq .
