---
name: invariants-fsm
description: "Machines à états finis, lois de conservation et oracles de non-régression. États invalides impossibles par typage. Crash-Only, SQLite WAL."
---

# 🔒 Invariants & FSM

> Zéro état invalide possible. Zéro float monétaire. Crash-Only : laisser crasher, SQLite WAL restaure en 2 ms.

## Structure FSM Obligatoire

```python
from enum import Enum, auto
from dataclasses import dataclass
from decimal import Decimal

class OrderState(Enum):
    DRAFT = auto()
    CONFIRMED = auto()
    SHIPPED = auto()
    CANCELLED = auto()

# Transitions valides (toute autre transition → ValueError immédiat)
TRANSITIONS = {
    OrderState.DRAFT: {OrderState.CONFIRMED, OrderState.CANCELLED},
    OrderState.CONFIRMED: {OrderState.SHIPPED, OrderState.CANCELLED},
}

def transition(current: OrderState, next_: OrderState) -> OrderState:
    if next_ not in TRANSITIONS.get(current, set()):
        raise ValueError(f"Transition illégale: {current} → {next_}")
    return next_
```

## Lois de Conservation (Mathématiques Obligatoires)

- Somme des entrées == Somme des sorties (comptabilité, stock, tokens).
- Vérifié par assertion après chaque transition : `assert total_in == total_out`.
- `Decimal` partout pour les montants — zéro `float` IEEE-754.

## Philosophie Crash-Only

- Une anomalie → crash immédiat (jamais de fallback silencieux).
- SQLite en mode WAL : rollback automatique en < 2 ms.
- Tests adversariaux : injecter une transition illégale → `pytest.raises(ValueError)`.
