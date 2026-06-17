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
    def __init__(self, results: list[PaymentResult]) -> None:
        self.results = results

    def charge(self, invoice: Invoice) -> PaymentResult:
        if not self.results:
            return PaymentResult(False, "NO_MORE_RESULTS")
        return self.results.pop(0)

    
# ----------------------------------------------------------------
# Fake-random — for the CLI demo
# ----------------------------------------------------------------
       import random

class FakeRandomGateway(PaymentGateway):
    def __init__(self, success_rate: float = 0.7, seed: Optional[int] = None) -> None:
        self.success_rate = success_rate
        self.random = random.Random(seed)

    def charge(self, invoice: Invoice) -> PaymentResult:
        if self.random.random() < self.success_rate:
            return PaymentResult(True)
        return PaymentResult(False, "PAYMENT_FAILED")
        
       
