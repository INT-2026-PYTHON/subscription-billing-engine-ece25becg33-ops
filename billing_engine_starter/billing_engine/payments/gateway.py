"""
PaymentGateway — abstract + two mock implementations.

In real life this would talk to Stripe / Razorpay / Adyen. For the project
we use mocks so tests are deterministic and the demo never hits the network.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from billing_engine.models import Invoice


@dataclass(frozen=True)
class PaymentResult:
    success: bool
    failure_reason: Optional[str] = None


class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, invoice: Invoice) -> PaymentResult:
        raise NotImplementedError


# ----------------------------------------------------------------
# Scripted — for deterministic tests
# ----------------------------------------------------------------
class ScriptedGateway(PaymentGateway):
    """Returns pre-set results from a queue. Used in tests.

    Example:
        gateway = ScriptedGateway([
            PaymentResult(False, "INSUFFICIENT_FUNDS"),
            PaymentResult(False, "INSUFFICIENT_FUNDS"),
            PaymentResult(True),
        ])
    """

    def __init__(self, results: list[PaymentResult]) -> None:
        
       

    def charge(self, invoice: Invoice) -> PaymentResult:
        
        

# ----------------------------------------------------------------
# Fake-random — for the CLI demo
# ----------------------------------------------------------------
       class FakeRandomGateway(PaymentGateway):
    """
    Simulates payment success/failure.
    """

    def __init__(
        self,
        success_rate: float = 0.7,
        seed: Optional[int] = None,
    ) -> None:
        
    def charge(self, invoice: Invoice) -> PaymentResult:
        
       
