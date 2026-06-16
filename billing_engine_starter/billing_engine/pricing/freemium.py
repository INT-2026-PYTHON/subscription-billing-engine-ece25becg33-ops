"""
Freemium — first N units are free, overage delegated to another strategy.

This is a great example of COMPOSITION: Freemium HAS-A inner PricingStrategy
rather than IS-A specific kind of pricing.

Example: 1000 free API calls per month, then ₹0.50 per call (UsageBased).
"""

from billing_engine.money import Money
from billing_engine.pricing.base import PricingStrategy


class Freemium(PricingStrategy):
    """Returns 0 for quantity <= free_quota, else delegates overage to inner strategy."""

    def __init__(self, free_quota: int, overage_strategy: PricingStrategy) -> None:
        # TODO Day 1
        self.free_quota = free_quota
        self.overage_strategy = overage_strategy

    def calculate(self, quantity: int) -> Money:
        # TODO Day 1
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")

        if quantity <= self.free_quota:
            currency = getattr(
                self.overage_strategy,
                "unit_price",
                Money.zero("INR")
            ).currency

            return Money.zero(currency)

        overage = quantity - self.free_quota
        return self.overage_strategy.calculate(overage)
