---
name: chain-runner
description: "Exécution autonome séquentielle de tickets GitHub. claim → verify → commit → close. Circuit-breaker 2 échecs."
---

# ⚡ Chain Runner

Exécute les tickets GitHub sans surveillance, un par un, du plus prioritaire au moins bloqué.

## Protocole (par ticket)

1. `gh issue list --state open --label "frugal:ready"` → prend le 1er non-bloqué.
2. Lit le ticket, comprend le périmètre exact.
3. Code la solution minimale (Ponytail : YAGNI d'abord).
4. `rtk pytest` → si rouge : diagnostique, corrige, re-teste (max 2 essais).
5. `git add <files> && git commit -m "fix: #<n> <description>"`.
6. `gh issue close <n> --comment "Livré — tests verts"`.
7. Relance la boucle sur le ticket suivant.

## Circuit-Breaker

- 2 échecs successifs sur le même ticket → `git reset --hard HEAD` + `gh issue comment <n> --body "Bloqué — escalade humaine"` + STOP.
- Jamais de patch aveugle, jamais de `try/except` silencieux.

## Hygiène

- Contexte vierge par ticket (0 token de passif).
- Commit atomique par ticket fermé.
- `rtk git status` avant chaque commit.
