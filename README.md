# 💳 FrugalBilling

> **Micro-SaaS de facturation récurrente, abonnements et grand livre comptable à double entrée.**
> Conçu et validé de bout en bout avec le **Frugal-Vibe Framework**.

## 🚀 Fonctionnalités Clés
- **FSM d'Abonnement Stricte** : `trialing` → `active` → `past_due` → `canceled` → `unpaid`.
- **Moteur de Prorata 100% Decimal** : Calculs d'arrondis sans aucune dérive IEEE-754.
- **Grand Livre à Double Entrée (AlphaLedger)** : Conservation comptable absolue ($\sum \text{debits} - \sum \text{credits} == 0$).
- **Persistance ACID** : SQLite WAL ultra-légère sans ORM lourd.
- **Visual Cockpit** : Dashboard Vanilla HTML/CSS/JS (zéro build step npm).

## 🧪 Validation Frugale
```bash
./bin/frugal test      # Tests unitaires via RTK (ultra-frugaux)
./bin/frugal check     # Linter statique AST (150L, McCabe <= 8, zéro float)
./bin/frugal gain      # Économies de tokens mesurées
```
