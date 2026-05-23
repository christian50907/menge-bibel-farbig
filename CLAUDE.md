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

## UI-Redesign — Beschlossene Korrekturen (feat/redesign/*)

Diese Punkte wurden auf `feat/redesign/warm-refined` erarbeitet und müssen in
**jedes weitere Design-Branch** übernommen werden:

### Layout & Struktur
- **2-spaltig**: Rechte TOC-Sidebar entfernt. Layout: `220px 1fr`, max-width 960px.
- **Kapitel-Navigation inline**: `.kapitel-nav-inline` direkt im Hauptinhalt, oben (nach Header) und unten (nach Bibeltext). Nicht in Sidebar.
- **Kein `border-bottom` auf `.kapitel-header`**: Die Nav-Linie darunter reicht.
- **„Übersetzt von Hermann Menge · Menge-Bibel (1926)"** aus `kapitel.html` entfernt — nur auf Startseite.
- **Buch-Grid**: `minmax(min(140px, 100%), 1fr)` — responsiv, kein festes `max-width`.
- **`min-width: 0`** auf `.index-content` (Grid-Overflow-Fix), `overflow-wrap: break-word`.

### Fußnoten
- **Marker**: Kein Badge. Stattdessen: `font-size: 0.72em; line-height: 0; vertical-align: 0.5em; color: var(--farbe-gold)` — unauffälliges Sternchen ohne Zeilenhöhen-Schaden.
- **Popup**: `.fn-wrap` (display: **inline-block** — wichtig für iOS-Positionierung) + `.fn-popup` mit `width: max-content; max-width: 240px`.

### Dark Mode
- Toggle: Button unten in linker Sidebar (Desktop) + Icon-Button im Header (Mobile, nur `@media (max-width: 900px)`).
- Dark-Mode-Button in Sidebar auf Mobile ausblenden (`.theme-toggle { display: none }` im Breakpoint).
- Korrekte Farbüberschreibungen für: Abschnittsüberschriften, Fließtext, Sidebar-Links, Hauptinhalt-Hintergrund.

### Mobile
- **Hamburger-Menü**: `☰`-Button im Header öffnet Sidebar als Overlay (`position: fixed; z-index: 50`). Klick auf Overlay schließt.
- Sidebar `.sidebar-nav.open` für Mobile-Overlay-Zustand.
- Dark-Mode-Button in Sidebar auf Mobile ausgeblendet (Header-Icon übernimmt).

### Tooltip-System (AT + Fußnoten)
- **Zweistufiges Tippen auf Mobile**: Erster Tap öffnet Tooltip (verhindert Navigation), zweiter Tap navigiert. Tap außerhalb schließt.
- **Viewport-Klemmung** (JS): `tooltipPositionPruefen()` berechnet `left`-Offset der Tooltip-Box so dass sie weder links noch rechts aus dem Fenster läuft.
- `alleTooltipsSchliessen()` setzt auch `tooltip.style.left = ''` zurück.
- AT- und Fußnoten-Tooltips schließen sich gegenseitig.
