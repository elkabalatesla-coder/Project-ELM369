.PHONY: up down restart logs test clean lint

PY_FILES = elm369_security_engine.py elm369_robotics_core.py

up:
	@echo "[ELM369] Starting local containerized telemetry & monitoring stack..."
	docker compose up -d

down:
	@echo "[ELM369] Stopping telemetry stack..."
	docker compose down

restart: down up

logs:
	docker compose logs -f

test:
	@echo "[ELM369] Executing security and robotics test suites..."
	python3 elm369_security_engine.py
	@if [ -f elm369_robotics_core.py ]; then python3 elm369_robotics_core.py; else echo "[ELM369] Skipping elm369_robotics_core.py (not found)"; fi

lint:
	@echo "[ELM369] Running code quality checks with flake8..."
	flake8 $(PY_FILES) --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 $(PY_FILES) --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

clean:
	@echo "[ELM369] Cleaning up containers, volumes, and temporary files..."
	docker compose down -v
	rm -rf __pycache__ .pytest_cache .ruff_cache .mypy_cache build dist *.egg-info
