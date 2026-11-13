.PHONY: up down restart logs test clean lint demo

PYTHON ?= python3
# Security engine is required; robotics is optional until added to the repository.
OPTIONAL_PY_FILES := $(wildcard elm369_robotics_core.py)
PY_FILES := elm369_security_engine.py elm369_security_demo.py tests/test_elm369_security_engine.py $(OPTIONAL_PY_FILES)

up:
	@echo "[ELM369] Starting local containerized telemetry & monitoring stack..."
	docker compose up -d

down:
	@echo "[ELM369] Stopping telemetry stack..."
	docker compose down

restart:
	$(MAKE) down
	$(MAKE) up

logs:
	docker compose logs -f

test:
	@echo "[ELM369] Running security engine tests..."
	$(PYTHON) -m pytest -q tests/test_elm369_security_engine.py
	@if [ -f elm369_robotics_core.py ]; then \
		$(PYTHON) elm369_robotics_core.py; \
	else \
		echo "[ELM369] Skipping optional elm369_robotics_core.py (not found)"; \
	fi

demo:
	$(PYTHON) elm369_security_demo.py

lint:
	@echo "[ELM369] Running code quality checks with flake8..."
	@if [ ! -f elm369_robotics_core.py ]; then \
		echo "[ELM369] Skipping lint for optional elm369_robotics_core.py (not found)"; \
	fi
	$(PYTHON) -m flake8 $(PY_FILES) --count --max-complexity=10 --max-line-length=127 --show-source --statistics

clean:
	@echo "[ELM369] Cleaning up containers, volumes, and temporary files..."
	docker compose down -v
	rm -rf __pycache__ .pytest_cache .ruff_cache .mypy_cache build dist *.egg-info
