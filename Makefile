# Project ELM369 — JMR0824197846902 / JMR08241978202646902
PYTHON = python3

.PHONY: install run api test clean

install:
	@echo "Installing dependencies..."
	$(PYTHON) -m pip install -r requirements-api.txt

run:
	@echo "Executing Project ELM369 Master Pipeline..."
	$(PYTHON) elm369_matrix_engine.py

api:
	@echo "Starting FastAPI Telemetry Server..."
	$(PYTHON) -m uvicorn elm369_api:app --host 0.0.0.0 --port 8000 --reload

test:
	@echo "Running Full Pytest Integration Suite..."
	$(PYTHON) -m pytest -v

clean:
	@echo "Cleaning up Python caches..."
	find . -type d \( -name __pycache__ -o -name .pytest_cache \) -prune -exec rm -rf {} +
