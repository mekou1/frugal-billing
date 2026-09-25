"""
tests/test_subscription.py — Tests miroir FSM d'abonnement et prorata Decimal.
"""
from decimal import Decimal
import pytest
from core.subscription import (
    Subscription,
    SubscriptionState,
    calculate_proration,
    InvalidTransitionError,
    ProrationError,
)

def test_subscription_initial_and_valid_transitions():
    sub = Subscription("sub_1", "cust_1", Decimal("99.00"))
    assert sub.state == SubscriptionState.TRIALING

    sub.transition_to(SubscriptionState.ACTIVE)
    assert sub.state == SubscriptionState.ACTIVE

    sub.transition_to(SubscriptionState.PAST_DUE)
    assert sub.state == SubscriptionState.PAST_DUE

    sub.transition_to(SubscriptionState.CANCELED)
    assert sub.state == SubscriptionState.CANCELED

def test_subscription_invalid_transitions():
    sub = Subscription("sub_2", "cust_2", Decimal("49.00"))
    with pytest.raises(InvalidTransitionError):
        sub.transition_to(SubscriptionState.UNPAID)

    sub.state = SubscriptionState.CANCELED
    with pytest.raises(InvalidTransitionError):
        sub.transition_to(SubscriptionState.ACTIVE)

def test_calculate_proration_nominal():
    # 15 jours sur 30 pour 100€ -> 50.00€
    res = calculate_proration(Decimal("100.00"), 15, 30)
    assert res == Decimal("50.00")

    # 10 jours sur 30 pour 29.99€ -> 10.00€
    res2 = calculate_proration(Decimal("29.99"), 10, 30)
    assert res2 == Decimal("10.00")

    # Frontières : 0 jours -> 0.00€, 30 jours -> montant total
    assert calculate_proration(Decimal("50.00"), 0, 30) == Decimal("0.00")
    assert calculate_proration(Decimal("50.00"), 30, 30) == Decimal("50.00")

def test_calculate_proration_invalid_inputs():
    with pytest.raises(ProrationError):
        calculate_proration(Decimal("100.00"), -1, 30)
    with pytest.raises(ProrationError):
        calculate_proration(Decimal("100.00"), 35, 30)
    with pytest.raises(ProrationError):
        calculate_proration(Decimal("100.00"), 15, 0)
