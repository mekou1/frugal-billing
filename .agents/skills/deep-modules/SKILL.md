---
name: deep-modules
description: "Architecture Deep Modules (Ousterhout) : surface publique minimale, logique interne riche. 3 fichiers purs, 150 lignes max, McCabe ≤ 8."
---

# 🏛️ Deep Modules

> Surface publique minimale (2–4 fonctions) qui cache une logique interne riche.

## Structure Obligatoire (3 Fichiers)

```
composant/
├── __init__.py     # Expose uniquement __all__ = ["nom_public"]
├── logic.py        # Cœur pur : zéro I/O, zéro side-effect, < 150 lignes
└── test_logic.py   # Tests adversariaux : fuzzing, cas limites, mutations
```

## Règles Strictes

| Règle | Seuil |
|---|---|
| Lignes par fichier | ≤ 150 |
| Complexité McCabe | ≤ 8 |
| Fonctions | < 35 lignes, pures |
| Imbrication | max 2 niveaux |
| I/O dans `logic.py` | ❌ Interdit |

## Interfaces (Séparation Shell/Core)

- **Functional Core** (`logic.py`) : calculs purs, déterministes, testables en mémoire.
- **Imperative Shell** (`__init__.py`) : orchestre les effets (I/O, DB, réseau).
- Dépendances injectées, jamais importées en dur dans le core.

## Test Adversarial (Obligatoire)

```python
# Exemple : tester les cas limites réels, pas le happy-path
def test_edge_cases():
    assert compute(0) raises ValueError      # zéro
    assert compute(-1) raises ValueError     # négatif
    assert compute(MAX_INT) == expected      # débordement
# Fuzzing 500 inputs aléatoires en < 50 ms
```
