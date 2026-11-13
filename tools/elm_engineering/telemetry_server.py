"""Loopback-only refreshed simulation API; no hardware telemetry or payments."""

import asyncio
import json
import random
from datetime import datetime, timezone

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse

from .efficiency import ELM369EfficiencyEngine
from .engine import ELM369EngineeringCore
from .productivity import ELM369ProductivityEngine
from .quality import ELM369QualityInspectionEngine


PROJECT_ID = "JMR0824197846902"
COMPANION_ID = "JMR08241978202646902"
CHARITY_FEE_RATE = 0.01
QEP_SEQUENCE = ("PRODUCTIVITY", "QUALITY", "EFFICIENCY")
ALLOWED_HOSTS = {"127.0.0.1:8000", "localhost:8000"}
ALLOWED_ORIGINS = {"http://" + host for host in ALLOWED_HOSTS}
MAX_TICKS = 100
TICK_SECONDS = 1.5
MAX_STREAMS = 4


class SimulationEngine:
    def __init__(self):
        self.simulation_tick = 0
        self.active_streams = 0

    def qep_state(self):
        return {
            "active_mode": QEP_SEQUENCE[0],
            "shuffling_sequence": list(QEP_SEQUENCE),
            "is_read_only": True,
            "automatic_shuffling": False,
        }

    def charity_ledger(self):
        allocation = ELM369EngineeringCore().evaluate_project_resource_allocation(50000.0)
        return {
            "fee_rate": CHARITY_FEE_RATE,
            "gross_value_usd": allocation["gross_value"],
            "total_charity_allocated_usd": allocation["charity_allocation"],
            "net_retained_usd": allocation["net_retained_resource"],
            "charity_targets": allocation["charity_targets"],
            "allocations": {
                "shriners_hospitals_usd": 200.0,
                "cancer_stroke_research_usd": 200.0,
                "human_trafficking_prevention_usd": 100.0,
            },
            "basis": "Fixed scenario baseline, not a cumulative transaction ledger. 40/40/20 split is illustrative, not an approved pledge.",
            "simulation_only": True,
            "funds_transferred": False,
            "purple_pool_logged": False,
        }

    def get_snapshot(self):
        measured = round(2 + random.uniform(-0.0012, 0.0012), 5)
        inspection = ELM369QualityInspectionEngine().audit_dimensional_tolerances(
            2, measured, 0.001, -0.001
        )
        fleet = ELM369ProductivityEngine().execute_fleet_synchronization(
            10, round(random.uniform(94, 98.5), 1)
        )
        energy = ELM369EfficiencyEngine().optimize_energy_and_power_consumption(
            45, round(45 - random.uniform(10.5, 14.2), 2), 200, 0.12
        )
        material = ELM369EfficiencyEngine().execute_material_waste_audit(100, 84.5)
        self.simulation_tick += 1
        return {
            "metadata": {
                "project_id": PROJECT_ID, "companion_id": COMPANION_ID,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tick": self.simulation_tick, "data_type": "SIMULATION_REFRESH_ONLY",
                "hardware_connected": False, "production_release_authorized": False,
            },
            "qep_state": self.qep_state(),
            "domains": {
                "cnc_machining": {
                    "inspection": inspection,
                    "hitl_status": "PENDING_HUMAN_REVIEW" if inspection["within_tolerance"] else "HOLD_REQUIRES_REWORK_OR_SCRAP",
                    "limitations": "Scalar dimensional check, not full GD&T or zero-defect certification.",
                },
                "agricultural_fleet": fleet,
                "additive_fabrication": {
                    "energy": energy, "material": material,
                    "inputs": {"base_power_kw": 45, "operating_hours": 200, "cost_per_kwh": 0.12,
                               "gross_material_weight_lbs": 100, "net_part_weight_lbs": 84.5},
                },
                "medical": {
                    "status": "PLANNED_NOT_IMPLEMENTED", "patient_data_ingested": False,
                    "clinical_validation_performed": False,
                },
            },
            "charity_ledger": self.charity_ledger(),
        }


engine = SimulationEngine()
app = FastAPI(
    title="ELM369 Localhost Simulation API",
    description="Refreshed simulation snapshots, not live physical telemetry.",
    version="2026.10", docs_url=None, redoc_url=None, openapi_url=None,
)


@app.middleware("http")
async def loopback_access(request: Request, call_next):
    # CORS is not access control. Ignore forwarded headers and reject browser origins.
    if (
        request.client is None or request.client.host != "127.0.0.1"
        or request.headers.get("host") not in ALLOWED_HOSTS
        or (request.headers.get("origin") is not None
            and request.headers["origin"] not in ALLOWED_ORIGINS)
        or request.headers.get("sec-fetch-site") == "cross-site"
    ):
        return JSONResponse({"error": "Loopback client and approved local Host/Origin required."}, status_code=403)
    if request.method != "GET":
        return JSONResponse({"error": "Read-only API: GET required."}, status_code=405, headers={"Allow": "GET"})
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/api/status")
async def get_status():
    return {
        "status": "SIMULATION_SERVICE_READY",
        "project_id": PROJECT_ID, "companion_id": COMPANION_ID,
        "simulation_only": True, "access_control": "LOOPBACK_ONLY_NO_PROXY",
        "qep_state": engine.qep_state(), "simulation_ticks_generated": engine.simulation_tick,
        "charity_ledger": engine.charity_ledger(),
        "active_streams": engine.active_streams,
    }


@app.get("/api/qep-mode")
async def get_qep_mode():
    return engine.qep_state()


@app.get("/api/telemetry")
async def get_telemetry():
    return engine.get_snapshot()


async def simulation_events(request, ticks):
    for index in range(ticks):
        if await request.is_disconnected():
            break
        payload = json.dumps(engine.get_snapshot(), allow_nan=False)
        yield f"event: simulation\ndata: {payload}\n\n"
        if index + 1 < ticks:
            await asyncio.sleep(TICK_SECONDS)


class BoundedSimulationResponse(StreamingResponse):
    async def __call__(self, scope, receive, send):
        state = engine
        if state.active_streams >= MAX_STREAMS:
            response = JSONResponse({"error": "Simulation stream capacity reached."}, status_code=429)
            await response(scope, receive, send)
            return
        state.active_streams += 1
        try:
            await super().__call__(scope, receive, send)
        finally:
            state.active_streams -= 1


@app.get("/api/simulation/stream")
async def stream_simulation(request: Request, ticks: int = Query(default=MAX_TICKS, ge=1, le=MAX_TICKS)):
    return BoundedSimulationResponse(
        simulation_events(request, ticks), media_type="text/event-stream",
        headers={"Cache-Control": "no-store", "X-ELM369-Stream": "Bounded-Simulation",
                 "X-Accel-Buffering": "no"},
    )


def main():
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, proxy_headers=False, log_level="info")


if __name__ == "__main__":
    main()
