"""Purple Pool task prioritization and simulated charity allocation ledger."""

import logging
import math
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from typing import Dict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [ELM369-PPPM]: %(message)s",
)
logger = logging.getLogger("PPPM_ELM369")


class PurplePoolScheduler:
    def __init__(
        self,
        primary_id: str = "JMR0824197846902",
        companion_id: str = "JMR08241978202646902",
    ):
        self.primary_id = primary_id
        self.companion_id = companion_id
        self.charity_targets = [
            "Shriners Hospitals for Children",
            "Cancer & Stroke Research Foundations",
            "Human Trafficking Prevention Initiatives",
        ]
        logger.info(
            "Initialized PurplePoolScheduler for IDs: %s, %s",
            self.primary_id,
            self.companion_id,
        )

    def calculate_priority(
        self, task_name: str, base_weight: float, is_purple_pool_aligned: bool
    ) -> float:
        """Return a task's priority, multiplying aligned tasks by 2.5."""
        if not math.isfinite(base_weight) or base_weight < 0:
            raise ValueError("base_weight must be a finite, non-negative number")

        multiplier = 2.5 if is_purple_pool_aligned else 1.0
        final_priority = round(base_weight * multiplier, 4)
        logger.info(
            "Task '%s' priority calculated: %s (Aligned: %s)",
            task_name,
            final_priority,
            is_purple_pool_aligned,
        )
        return final_priority

    def process_charity_allocation(self, simulated_value: float) -> Dict[str, float]:
        """Return a simulated 1% allocation split, without transferring funds."""
        if not math.isfinite(simulated_value) or simulated_value < 0:
            raise ValueError("simulated_value must be a finite, non-negative number")

        total = (Decimal(str(simulated_value)) * Decimal("0.01")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        total_cents = int(total * 100)
        base_cents, remainder = divmod(total_cents, len(self.charity_targets))
        allocations = {}
        for index, target in enumerate(self.charity_targets):
            cents = base_cents + (1 if index < remainder else 0)
            allocations[target] = float(
                (Decimal(cents) / Decimal(100)).quantize(
                    Decimal("0.01"), rounding=ROUND_DOWN
                )
            )

        logger.info(
            "[SIMULATED CHARITY LEDGER] Allocated 1%% total ($%.2f) across %d causes; "
            "no funds were transferred.",
            float(total),
            len(self.charity_targets),
        )
        return allocations
