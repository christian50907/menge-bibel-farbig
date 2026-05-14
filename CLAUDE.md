# CLAUDE.md — Projektregeln für Claude Code

## Hard Rules

- **NEVER push to `main` branch** without explicit user approval in the current session.
- All development goes to feature branches (e.g. `feat/...`, `fix/...`, `claude/...`).
- Before any `git push`, state the target branch explicitly. Only push if the user
  has approved it in this session.
- Before merging anything into `main`, always ask the user first.

## Projekt-Kontext

Dieses Repo enthält eine statische Website zur farbkodierten Darstellung der Menge-Bibel.
Projekt-Skill (Annotations-Workflow): `.claude/skills/menge-bibel-farbig/` → `/menge-bibel-farbig`

Aktueller Entwicklungsbranch: `feat/reasoning-for-references`
