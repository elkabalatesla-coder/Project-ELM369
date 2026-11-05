"""FastAPI calculation interface for Project ELM369."""

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from elm369_matrix_engine import influence_weight, optimal_route, transaction_ledger

app = FastAPI(title="ELM369 Matrix API")


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    return JSONResponse(status_code=422, content={
        "detail": [
            {"loc": error["loc"], "msg": error["msg"], "type": error["type"]}
            for error in exc.errors()
        ]
    })


class NumericRequest(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)


class InfluenceRequest(NumericRequest):
    reach: float
    viral_velocity: float
    sentiment_delta: float


class LogisticsRequest(BaseModel):
    origin: str = Field(min_length=1)
    destination: str = Field(min_length=1)


class TransactionRequest(NumericRequest):
    base_amount: float
    supply_volatility: float
    demand_flux: float


@app.get("/health")
def health_check():
    return {"status": "operational", "system": "ELM369 Matrix API"}


@app.post("/influence")
def calculate_influence(payload: InfluenceRequest):
    try:
        weight = influence_weight(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "success", "influence_weight": weight}


@app.post("/logistics")
def calculate_logistics(payload: LogisticsRequest):
    try:
        route = optimal_route(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "success", **route}


@app.post("/transaction")
def calculate_transaction(payload: TransactionRequest):
    try:
        ledger = transaction_ledger(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "success", "ledger": ledger}
