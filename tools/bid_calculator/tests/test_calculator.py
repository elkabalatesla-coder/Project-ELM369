import unittest
from decimal import Decimal

from tools.bid_calculator import calculate_bid


class CalculateBidTests(unittest.TestCase):
    def test_stage_one_rounds_half_up_and_requires_authorization(self):
        result = calculate_bid(Decimal("2.00"), Decimal("1.05"), 1)

        self.assertEqual(result["status"], "AWAITING_JOSEPH_AUTHORIZATION")
        self.assertEqual(result["proposed_bid"], "0.95")
        self.assertTrue(result["authorization_required"])

    def test_stage_two_uses_its_multiplier(self):
        result = calculate_bid(Decimal("100.00"), Decimal("100.00"), 2)

        self.assertEqual(result["proposed_bid"], "97.00")
        self.assertEqual(result["status"], "AWAITING_JOSEPH_AUTHORIZATION")

    def test_bid_at_standard_rate_requires_review(self):
        result = calculate_bid(Decimal("90.00"), Decimal("100.00"), 1)

        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertEqual(result["proposed_bid"], "90.00")
        self.assertEqual(
            result["reason"],
            "Revised bid does not beat the standard rate.",
        )

    def test_stage_three_or_later_withdraws(self):
        result = calculate_bid(Decimal("100.00"), Decimal("100.00"), 3)

        self.assertEqual(result["status"], "WITHDRAW")
        self.assertNotIn("proposed_bid", result)

    def test_nonpositive_rates_are_rejected(self):
        for standard_rate, competitor_bid in (
            (Decimal("0"), Decimal("10")),
            (Decimal("10"), Decimal("-1")),
        ):
            with self.subTest(standard_rate=standard_rate, competitor_bid=competitor_bid):
                with self.assertRaisesRegex(ValueError, "Rates must be greater than zero"):
                    calculate_bid(standard_rate, competitor_bid, 1)

    def test_unsupported_stages_are_rejected(self):
        for stage in (0, -1):
            with self.subTest(stage=stage):
                with self.assertRaisesRegex(ValueError, "Stage must be 1, 2, or 3"):
                    calculate_bid(Decimal("10"), Decimal("10"), stage)


if __name__ == "__main__":
    unittest.main()
