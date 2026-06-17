"""
PaymentGateway — abstract + two mock implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import random

from billing_engine.models import Invoice


# ================================================================
# Payment Result
# ================================================================
@dataclass(frozen=True)
class PaymentResult:
    success: bool
    failure_reason: Optional[str] = None


# ================================================================
# Abstract Gateway
# ================================================================
class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, invoice: Invoice) -> PaymentResult:
        raise NotImplementedError


# ================================================================
# Scripted Gateway (USED BY TESTS)
# ================================================================
class ScriptedGateway(PaymentGateway):
    """
    Deterministic gateway used in tests.
    Returns predefined results in order.
    """

    def __init__(self, results: list[PaymentResult]) -> None:
        self.results = results
        self.index = 0  # keeps track of next result to return

    def charge(self, invoice: Invoice) -> PaymentResult:
        # If no predefined results, always succeed
        if not self.results:
            return PaymentResult(success=True)

        # Return next scripted result
        if self.index < len(self.results):
            result = self.results[self.index]
            self.index += 1
            return result

        # If exhausted, keep returning last result (safe fallback)
        return self.results[-1]


# ================================================================
# Fake Random Gateway (USED FOR DEMO)
# ================================================================
class FakeRandomGateway(PaymentGateway):
    """
    Randomized gateway for CLI/demo use.
    Seeded for reproducibility.
    """

    def __init__(self, success_rate: float = 0.7, seed: Optional[int] = None) -> None:
        if not (0 <= success_rate <= 1):
            raise ValueError("success_rate must be between 0 and 1")

        self.success_rate = success_rate
        self.random = random.Random(seed)

    def charge(self, invoice: Invoice) -> PaymentResult:
        value = self.random.random()

        if value < self.success_rate:
            return PaymentResult(success=True)

        return PaymentResult(success=False, failure_reason="RANDOM_FAILURE")
