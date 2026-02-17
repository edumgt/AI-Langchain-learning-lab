.PHONY: up down demo

up:
	docker compose up --build

down:
	docker compose down

demo:
	@echo "Usage: make demo D=catalog/prompts/01_prompt_templates.py"
	@[ -n "$(D)" ] && docker compose run --rm lab python $(D) || true

run-api:
	docker compose up --build api

demo-cli:
	docker compose run --rm lab python -m app.cli "예산 3천만원으로 2주 관객개발 캠페인 실행 계획" --mode plan

