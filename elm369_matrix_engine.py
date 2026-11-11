"""Project ELM369 calculation demos (JMR0824197846902 / JMR08241978202646902)."""

from decimal import Decimal, DecimalException, ROUND_HALF_EVEN
import json
import math

import networkx as nx


def influence_weight(reach: float, viral_velocity: float, sentiment_delta: float) -> float:
    if not all(math.isfinite(value) for value in (reach, viral_velocity, sentiment_delta)):
        raise ValueError("Influence inputs must be finite")
    if reach < 0 or viral_velocity < 0 or sentiment_delta < -1:
        raise ValueError("Reach and velocity must be nonnegative; sentiment must be at least -1")
    weight = reach * viral_velocity * (1 + sentiment_delta)
    if not math.isfinite(weight):
        raise ValueError("Influence result is out of range")
    return weight


def optimal_route(origin: str, destination: str) -> dict:
    graph = nx.Graph()
    graph.add_weighted_edges_from([
        ("Kokomo_Hub", "Regional_Hub", 2.0),
        ("Regional_Hub", "Fulfillment_Node_7", 3.0),
        ("Kokomo_Hub", "Fulfillment_Node_7", 8.0),
    ])
    try:
        cost, path = nx.single_source_dijkstra(graph, origin, destination)
    except (nx.NodeNotFound, nx.NetworkXNoPath) as exc:
        raise ValueError("Unknown logistics node or unavailable route") from exc
    return {"optimal_path": path, "cost_index": float(cost)}


def transaction_ledger(base_amount: float, supply_volatility: float, demand_flux: float) -> dict:
    values = (base_amount, supply_volatility, demand_flux)
    if not all(math.isfinite(value) for value in values) or base_amount < 0:
        raise ValueError("Transaction inputs must be finite and base amount nonnegative")
    base, supply, demand = (Decimal(str(value)) for value in values)
    factor = Decimal(1) + supply + demand
    if factor < 0:
        raise ValueError("Transaction adjustment must not produce a negative gross amount")
    try:
        gross = (base * factor).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
        charity = (gross * Decimal("0.01")).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
        share = (charity / 3).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
        return {
            "executed_gross_amount": float(gross),
            "charity_allocation_total": float(charity),
            "shriners_hospitals": float(share),
            "charity_shares": [float(share)] * 3,
            "charity_rounding_adjustment": float(charity - share * 3),
            "net_treasury_settlement": float(gross - charity),
        }
    except DecimalException as exc:
        raise ValueError("Transaction result is out of range") from exc


def main() -> None:
    print(json.dumps({
        "influence_weight": influence_weight(1000000.0, 7.5, 0.25),
        "logistics": optimal_route("Kokomo_Hub", "Fulfillment_Node_7"),
        "ledger": transaction_ledger(50000.0, 0.01, 0.015),
    }, indent=2))


if __name__ == "__main__":
    main()
