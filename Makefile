.PHONY: up down restart logs test clean lint

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
	python3 elm369_robotics_core.py

lint:
	@echo "[ELM369] Running code quality checks with flake8..."
	flake8 elm369_security_engine.py --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 elm369_security_engine.py --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

clean:
	@echo "[ELM369] Cleaning up containers, volumes, and temporary files..."
	docker compose down -v
	rm -rf __pycache__ .pytest_cache
