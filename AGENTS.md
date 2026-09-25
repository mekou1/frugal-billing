# AGENTS.md — Règles d'Ingénierie FrugalBilling

> Application Micro-SaaS de facturation récurrente et grand livre comptable.
> Développée selon les principes stricts du Frugal-Vibe Framework.

## 🛠️ Commandes de Validation
- Tests unitaires compacts : `./bin/frugal test` (via RTK)
- Contrôle qualité Garde-Fou : `./bin/frugal check core/` (150L, McCabe <= 8, zéro float)
- Diff Git ultra-condensé : `./bin/frugal diff`
- Métriques d'économie de tokens : `./bin/frugal gain`

## 🏛️ Invariants Non-Négociables
1. **Règle des 150 Lignes** : Aucun fichier source ne dépasse 150 lignes.
2. **Complexité Cyclomatique** : McCabe <= 8 par fonction.
3. **Zéro Float Monétaire** : `Decimal` à 4 décimales ou centimes entiers obligatoires. Tout `float` est rejeté par `frugal check`.
4. **Architecture Deep Module (3 fichiers)** : `__init__.py`, `core.py`, `test_*.py`.
5. **Crash-Only & ACID** : En cas d'incohérence, crash immédiat (*Fail-Fast*).
