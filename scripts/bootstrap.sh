#!/usr/bin/env bash
set -euo pipefail
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "[OK] .env created"
fi
docker compose up --build
