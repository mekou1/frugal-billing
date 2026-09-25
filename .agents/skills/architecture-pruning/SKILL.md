---
name: architecture-pruning
description: "Protocole obligatoire avant tout code : Tournoi des 3 Architectures. Choisit toujours la plus simple, la plus courte, zéro dépendance externe."
---

# 🏛️ Architecture Pruning — Tournoi des 3 Architectures

> **Règle absolue** : Interdit de coder sans avoir documenté le Tournoi. L'Option C gagne toujours.

## Le Tournoi (Obligatoire Pré-Code)

| Critère | A — Standard Boursouflé | B — Sur-Ingénierie | **C — Noyau Frugal ✓** |
|---|---|---|---|
| Stack | Next.js, Prisma, Redux | Microservices, gRPC, Kafka | Python stdlib, PocketBase, HTMX |
| Lignes | 300–1 500 | 500–2 000 | **< 100 (max 150)** |
| Dépendances | 40–150 packages | 20 libs externes | **Zéro (stdlib pure)** |
| Boot | 5–30 s | 10–60 s | **< 5 ms** |
| Bugs | Élevé | Élevé | **Quasi-nul (FSM + fail-fast)** |

**Critère éliminatoire** : Choisir C — division par 3 du code, zéro dépendance.

## Échelle Ponytail (Karpathy)

1. **YAGNI ?** → Ne code jamais.
2. **Dans le repo ?** → Réutilise.
3. **Dans la stdlib ?** → Utilise (`collections`, `dataclasses`, `sqlite3`, `math`).
4. **En 1 ligne ?** → Fais-le en 1 ligne.
5. **Alors seulement** → Code minimal (< 100 lignes, McCabe ≤ 8).

## Mutation Gate (Obligatoire Post-Code)

- Zéro test "happy path" (`assert x is not None` interdit).
- Mutation Kill Rate = 100% : chaque mutant doit être tué par un test.
- Fail-Fast : circuit-breaker 2 essais → `git reset --hard HEAD`.
