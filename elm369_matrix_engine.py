"""Deterministic simulation functions used by the ELM369 API."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import heapq
import math


_CENT = Decimal("0.01")
_MAX_BASE_AMOUNT = 1_000_000_000_000
_ROUTES = {
    "Kokomo": (("Indianapolis", 1.0), ("Chicago", 3.0)),
    "Indianapolis": (("Kokomo", 1.0), ("Chicago", 3.5), ("Cincinnati", 2.0)),
    "Chicago": (("Kokomo", 3.0), ("Indianapolis", 3.5), ("Detroit", 4.0)),
    "Detroit": (("Chicago", 4.0), ("Cincinnati", 5.0)),
    "Cincinnati": (("Indianapolis", 2.0), ("Detroit", 5.0)),
}


def _finite_number(value: float, name: str) -> float:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return value


def calculate_influence_weight(
    reach: float, viral_velocity: float, sentiment_delta: float
) -> float:
    """Calculate a simulation score: reach × velocity × (1 + sentiment)."""
    reach = _finite_number(reach, "reach")
    viral_velocity = _finite_number(viral_velocity, "viral_velocity")
    sentiment_delta = _finite_number(sentiment_delta, "sentiment_delta")
    if reach < 0 or viral_velocity < 0:
        raise ValueError("reach and viral_velocity must be non-negative")
    if not -1 <= sentiment_delta <= 1:
        raise ValueError("sentiment_delta must be between -1 and 1")
    weight = reach * viral_velocity * (1 + sentiment_delta)
    if not math.isfinite(weight):
        raise ValueError("calculated influence weight is too large")
    return weight


def initialize_logistics_network() -> dict[str, tuple[tuple[str, float], ...]]:
    """Return the illustrative, weighted regional network used by this simulator."""
    return _ROUTES.copy()


def optimize_logistics_route(
    network: dict[str, tuple[tuple[str, float], ...]], origin: str, destination: str
) -> tuple[list[str], float]:
    """Return the least-cost path and summed cost in the illustrative network."""
    if origin not in network or destination not in network:
        unknown_node = origin if origin not in network else destination
        raise ValueError(f"Unknown logistics node: {unknown_node}")
    if origin == destination:
        return [origin], 0.0

    pending = [(0.0, origin, [origin])]
    best_cost = {origin: 0.0}
    while pending:
        cost, node, path = heapq.heappop(pending)
        if node == destination:
            return path, cost
        if cost > best_cost.get(node, math.inf):
            continue
        for neighbor, edge_cost in network[node]:
            next_cost = cost + edge_cost
            if next_cost < best_cost.get(neighbor, math.inf):
                best_cost[neighbor] = next_cost
                heapq.heappush(pending, (next_cost, neighbor, path + [neighbor]))
    raise ValueError(f"No route from {origin} to {destination}")


@dataclass(frozen=True)
class FinancialTransactionConfig:
    base_amount: float
    supply_volatility: float
    demand_flux: float


def process_financial_simulation(config: FinancialTransactionConfig) -> dict[str, float]:
    """Simulate a settlement with two bounded adjustment factors and a 1% allocation."""
    amount = _finite_number(config.base_amount, "base_amount")
    volatility = _finite_number(config.supply_volatility, "supply_volatility")
    demand = _finite_number(config.demand_flux, "demand_flux")
    if not 0 < amount <= _MAX_BASE_AMOUNT:
        raise ValueError("base_amount must be greater than zero and at most 1e12")
    if not -1 <= volatility <= 1:
        raise ValueError("supply_volatility must be between -1 and 1")
    if not -1 <= demand <= 1:
        raise ValueError("demand_flux must be between -1 and 1")

    base = Decimal(str(amount))
    adjusted = (base * Decimal(str(1 + volatility)) * Decimal(str(1 + demand))).quantize(
        _CENT, rounding=ROUND_HALF_UP
    )
    charity = (adjusted * Decimal("0.01")).quantize(_CENT, rounding=ROUND_HALF_UP)
    settlement = adjusted - charity
    return {
        "base_amount": float(base.quantize(_CENT, rounding=ROUND_HALF_UP)),
        "adjusted_amount": float(adjusted),
        "charity_allocation": float(charity),
        "settlement_amount": float(settlement),
    }
