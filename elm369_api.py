"""FastAPI telemetry and transaction API for Project ELM369."""

from __future__ import annotations

from collections import Counter, defaultdict
from threading import Lock
from time import perf_counter

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field

from elm369_db import init_database, persist_transaction
from elm369_matrix_engine import (
    FinancialTransactionConfig,
    calculate_influence_weight,
    initialize_logistics_network,
    optimize_logistics_route,
    process_financial_simulation,
)

app = FastAPI(
    title="Project ELM369 Matrix API",
    version="1.0.0",
    description="Simulation telemetry and transaction routing API for Project ELM369.",
)

_metrics_lock = Lock()
_request_counts: Counter[tuple[str, str, int]] = Counter()
_request_duration: defaultdict[tuple[str, str], float] = defaultdict(float)


@app.on_event("startup")
def startup_event() -> None:
    init_database()


class RequestModel(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)


class InfluenceRequest(RequestModel):
    reach: float = Field(ge=0)
    viral_velocity: float = Field(ge=0)
    sentiment_delta: float = Field(ge=-1, le=1)


class LogisticsRequest(RequestModel):
    origin: str = Field(min_length=1, max_length=100)
    destination: str = Field(min_length=1, max_length=100)


class TransactionRequest(RequestModel):
    base_amount: float = Field(gt=0, le=1_000_000_000_000)
    supply_volatility: float = Field(ge=-1, le=1)
    demand_flux: float = Field(ge=-1, le=1)


@app.middleware("http")
async def collect_request_metrics(request: Request, call_next):
    started = perf_counter()
    response = await call_next(request)
    elapsed = perf_counter() - started
    if request.url.path != "/metrics":
        route = request.scope.get("route")
        path = getattr(route, "path", "unmatched")
        key = (request.method, path)
        with _metrics_lock:
            _request_counts[(*key, response.status_code)] += 1
            _request_duration[key] += elapsed
    return response


@app.post("/influence")
def api_influence(data: InfluenceRequest) -> dict[str, object]:
    """Calculate the influence simulation score."""
    try:
        weight = calculate_influence_weight(
            data.reach, data.viral_velocity, data.sentiment_delta
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "success", "influence_weight": weight}


@app.post("/logistics")
def api_logistics(data: LogisticsRequest) -> dict[str, object]:
    """Compute the least-cost route through the illustrative regional network."""
    try:
        path, cost = optimize_logistics_route(
            initialize_logistics_network(), data.origin, data.destination
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "success", "optimal_path": path, "cost_index": cost}


@app.post("/transaction")
def api_transaction(data: TransactionRequest) -> dict[str, object]:
    """Simulate a transaction, allocate 1% to charity, and persist its ledger."""
    try:
        ledger = process_financial_simulation(
            FinancialTransactionConfig(
                base_amount=data.base_amount,
                supply_volatility=data.supply_volatility,
                demand_flux=data.demand_flux,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    transaction_id = persist_transaction(ledger)
    return {"status": "success", "transaction_id": transaction_id, "ledger": ledger}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "operational",
        "system": "ELM369 Matrix API",
        "identifiers": "JMR0824197846902 / JMR08241978202646902",
    }


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    """Expose request counters in Prometheus text exposition format."""
    with _metrics_lock:
        counts = sorted(_request_counts.items())
        durations = sorted(_request_duration.items())
    lines = [
        "# HELP elm369_http_requests_total Total HTTP requests, excluding metrics scrapes.",
        "# TYPE elm369_http_requests_total counter",
    ]
    lines.extend(
        f'elm369_http_requests_total{{method="{method}",path="{path}",status="{status}"}} {count}'
        for (method, path, status), count in counts
    )
    lines.extend(
        [
            "# HELP elm369_http_request_duration_seconds_sum Cumulative request duration in seconds.",
            "# TYPE elm369_http_request_duration_seconds_sum counter",
        ]
    )
    lines.extend(
        f'elm369_http_request_duration_seconds_sum{{method="{method}",path="{path}"}} {total:.9f}'
        for (method, path), total in durations
    )
    return Response("\n".join(lines) + "\n", media_type="text/plain; version=0.0.4")
