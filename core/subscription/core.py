"""
core/subscription/core.py — FSM d'Abonnement et Moteur de Prorata 100% Decimal.
"""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Dict, Set

class SubscriptionState(str, Enum):
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    CANCELED = "canceled"

VALID_TRANSITIONS: Dict[SubscriptionState, Set[SubscriptionState]] = {
    SubscriptionState.TRIALING: {SubscriptionState.ACTIVE, SubscriptionState.CANCELED},
    SubscriptionState.ACTIVE: {SubscriptionState.PAST_DUE, SubscriptionState.CANCELED},
    SubscriptionState.PAST_DUE: {SubscriptionState.ACTIVE, SubscriptionState.UNPAID, SubscriptionState.CANCELED},
    SubscriptionState.UNPAID: {SubscriptionState.ACTIVE, SubscriptionState.CANCELED},
    SubscriptionState.CANCELED: set(),
}

class InvalidTransitionError(Exception):
    pass

class ProrationError(Exception):
    pass

def calculate_proration(base_amount: Decimal, active_days: int, total_days: int = 30) -> Decimal:
    """Calcule le prorata temporis exact sans flottant IEEE-754."""
    if total_days <= 0:
        raise ProrationError(f"Le nombre total de jours doit être strictement positif: {total_days}")
    if active_days < 0 or active_days > total_days:
        raise ProrationError(f"Jours actifs invalides: {active_days} (hors de [0, {total_days}])")

    ratio = Decimal(active_days) / Decimal(total_days)
    prorated = base_amount * ratio
    return prorated.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

@dataclass
class Subscription:
    sub_id: str
    customer_id: str
    monthly_amount: Decimal
    state: SubscriptionState = SubscriptionState.TRIALING

    def transition_to(self, new_state: SubscriptionState) -> None:
        """Applique une transition d'état FSM sécurisée."""
        allowed = VALID_TRANSITIONS.get(self.state, set())
        if new_state not in allowed:
            raise InvalidTransitionError(
                f"Transition interdite : {self.state.value} -> {new_state.value}"
            )
        self.state = new_state
