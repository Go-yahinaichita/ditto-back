.PHONY: check
check:
	uvx ruff@latest check src . --fix
	uvx ruff@latest format src .
	uv run pyright

.PHONY: run
run:
	uv run uvicorn src.main:app --reload