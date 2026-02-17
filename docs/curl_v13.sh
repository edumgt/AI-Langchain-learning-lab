#!/usr/bin/env bash
set -euo pipefail
BASE="${BASE:-http://localhost:8000}"

echo "== get template =="
curl -s "$BASE/artbiz/proposal/template" | jq -r '.template' | head -n 40

echo "== create proposal (normalize) =="
curl -s "$BASE/artbiz/proposal" -H "Content-Type: application/json" -d '{
  "sponsor_name":"ACME",
  "campaign_title":"도시 커뮤니티 예술 캠페인",
  "budget_total_krw":30000000,
  "weeks":2,
  "org_type":"festival",
  "auto_approve":true,
  "save":true,
  "format":"both",
  "normalize":true
}' | jq .

echo "== check structure =="
curl -s "$BASE/artbiz/proposal/check" -H "Content-Type: application/json" -d '{"markdown":"## 1. 요약(Executive Summary)\n..."}' | jq .
