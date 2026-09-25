---
name: frugal-python
description: "Règles Python frugal : stdlib first, @dataclass(frozen=True), Decimal, fonctions pures < 35 lignes, fuzzing en mémoire, Mutation Gate 100%."
---

# 🐍 Frugal Python

## Ponytail Ladder (Karpathy — Ordre Strict)

1. **YAGNI** : si pas indispensable aujourd'hui → ne code pas.
2. **Repo** : existe déjà → réutilise sans modifier.
3. **Stdlib** : `dataclasses`, `sqlite3`, `decimal`, `math`, `statistics`, `unittest`, `collections`.
4. **1 ligne** : faisable en 1 ligne → 1 ligne.
5. **Code minimal** : < 100 lignes, McCabe ≤ 8, fonctions < 35 lignes.

## Règles d'Implémentation

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)          # Immuabilité obligatoire
class Price:
    amount: Decimal              # Zéro float pour les valeurs monétaires
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError(f"Prix négatif interdit: {self.amount}")
```

- Fonctions pures et déterministes : même entrée → même sortie, toujours.
- Zéro exception silencieuse : fail-fast immédiat, pas de `try/except` vide.
- Zéro dépendance externe : si `pip install` → refuser et trouver l'équivalent stdlib.

## Mutation Gate (Obligatoire)

```bash
rtk pytest tests/ -q                    # 100% vert obligatoire
python -m mutmut run --paths-to-mutate core/  # Kill Rate = 100% exigé
```

- Fuzzing : 500 inputs aléatoires en mémoire, < 50 ms, dans chaque test file.
- Tester : zéro, négatif, NaN, MAX_INT, chaîne vide, liste vide.
