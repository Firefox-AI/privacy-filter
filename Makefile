PYTHON_VERSION=3.12
VENV=.venv
HOST?=0.0.0.0
PORT?=8080
IMAGE?=privacy-filter:local

.PHONY: all setup install lint test serve docker-build docker-run clean docs

all: setup

setup:
	uv venv --python $(PYTHON_VERSION)
	uv sync --all-groups
	uv run pre-commit install
	@echo ""
	@echo "Setup complete. To activate your environment, run:"
	@echo "   source $(VENV)/bin/activate"

install:
	uv pip install --no-cache-dir -e .

lint:
	uv run ruff check .
	uv run ty check

test:
	uv run pytest -v

serve:
	HOST=$(HOST) PORT=$(PORT) uv run privacy-filter

docker-build:
	docker build -t $(IMAGE) .

docker-run:
	docker run --rm -p $(PORT):8080 $(IMAGE)

clean:
	rm -rf __pycache__ .cache .pytest_cache .ruff_cache $(VENV)

docs:
	@NVM_DIR=$${NVM_DIR:-$$HOME/.nvm}; \
	if [ -s "$$NVM_DIR/nvm.sh" ]; then . "$$NVM_DIR/nvm.sh" && nvm use >/dev/null; fi; \
	want=$$(cat .nvmrc); have=$$(node -v | sed 's/v\([0-9]*\).*/\1/'); \
	if [ "$$have" != "$$want" ]; then \
		echo "make docs needs Node $$want (see .nvmrc); found Node $$have."; \
		echo "Switch with: nvm use  (or e.g. brew install node@$$want)"; \
		exit 1; \
	fi; \
	mkdir -p docs && \
	env -u VIRTUAL_ENV uv run python -c "from privacy_filter.core.service import app; import json; json.dump(app.openapi(), open('openapi.json', 'w'), indent=2)" && \
	npx --yes -p @redocly/cli@2.5.0 -p styled-components@6.4.3 redocly build-docs openapi.json -o docs/index.html && \
	rm -f openapi.json
