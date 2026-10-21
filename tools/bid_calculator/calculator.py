from decimal import Decimal, ROUND_HALF_UP


def calculate_bid(
    standard_rate: Decimal,
    competitor_bid: Decimal,
    stage: int,
) -> dict:
    """Calculate a proposed bid only; never submit or accept a contract."""
    standard_rate = Decimal(str(standard_rate))
    competitor_bid = Decimal(str(competitor_bid))

    if standard_rate <= 0 or competitor_bid <= 0:
        raise ValueError("Rates must be greater than zero.")

    if stage == 1:
        multiplier = Decimal("0.90")
    elif stage == 2:
        multiplier = Decimal("0.97")
    elif stage >= 3:
        return {
            "status": "WITHDRAW",
            "reason": "Further underbidding is not authorized.",
        }
    else:
        raise ValueError("Stage must be 1, 2, or 3.")

    proposed = (competitor_bid * multiplier).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    if proposed >= standard_rate:
        return {
            "status": "REVIEW_REQUIRED",
            "proposed_bid": str(proposed),
            "reason": "Revised bid does not beat the standard rate.",
        }

    return {
        "status": "AWAITING_JOSEPH_AUTHORIZATION",
        "proposed_bid": str(proposed),
        "authorization_required": True,
    }
