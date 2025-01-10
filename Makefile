.PHONY: check
check:
	uvx ruff@latest check app . --fix
	uvx ruff@latest format app .
	uv run pyright

.PHONY: run
run:
	uv run uvicorn app.main:app --reload

.PHONY: migrate
migrate:
	uv run alembic autogenerate -m "create table"

.PHONY: upgrade
upgrade:
	uv run alembic upgrade head

.PHONY: downgrade
downgrade:
	uv run alembic downgrade -1