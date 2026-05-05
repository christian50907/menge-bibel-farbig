# Übergabe: Annotationen-Review Markus (Stand 2026-05-05)

Dieses Dokument ermöglicht einer neuen Claude-Session, die laufende Arbeit
am Branch `feat/reasoning-for-references` ohne Kontext-Verlust fortzusetzen.

---

## Aktueller Status

**Branch:** `feat/reasoning-for-references`
**Letzter Commit:** `843871a` — *Review Mk 1-3: add missing AT refs, fix speculative Begruendung, add CLAUDE.md*

### Was in diesem Sprint abgeschlossen wurde (Mk 1–3)

| # | Datei | Änderung |
|---|-------|----------|
| 1 | `annotationen/markus/kapitel-1.json` | V13: neue AT-Annotation hinzugefügt (Dtn 8,2 + 1. Kön 19,8) für „vierzig Tage in der Wüste" |
| 2 | `annotationen/markus/kapitel-1.json` | V44: AT-Annotation `"bis": 191` → `"bis": -1` korrigiert (Versende-Fehler) |
| 3 | `annotationen/markus/kapitel-2.json` | V17: Jes 61,1-Annotation auf `"status": "inaktiv"` gesetzt + Begründung überarbeitet |
| 4 | `annotationen/markus/kapitel-3.json` | V22: neue AT-Annotation für „Beelzebul" → 2. Kön 1,2 hinzugefügt |
| 5 | `CLAUDE.md` | Projekt-Root: Hard Rule „nie auf main pushen" eingerichtet |

**Kapitel 3 V29:** Bestehende Jesus-Annotation `"bis": 150` wurde geprüft und ist **korrekt** —
sie endet absichtlich vor dem Erzähler-Gedankenstrich `–` an Position 151.

---

## Offene Arbeit: Kapitel 4–16

Alle Kapitel ab 4 wurden noch **nicht** inhaltlich reviewed. Die Annotationsdateien
existieren bereits (bis Kap 16), aber das Review nach den unten beschriebenen Kriterien
fehlt noch.

**Nächster Schritt:** Mit Kap 4 beginnen (`annotationen/markus/kapitel-4.json`).

---

## Methodik (unbedingt lesen vor Fortsetzung)

Vollständige Richtlinien: `ai-tools/skills/menge-bibel-farbig/SKILL.MD`

### Review-Kriterien für AT-Annotationen

Eine AT-Annotation ist **gerechtfertigt**, wenn einer der folgenden Fälle zutrifft:

**Kategorie 1 — Kulturelle Fremdheit:**
Ein Wort, Name oder Brauch, das/den ein heutiger Leser nicht versteht, aber ein
1. Jh.-Jude sofort eingeordnet hätte. Beispiel: „Beelzebul" → heidnischer Götze.

**Kategorie 2 — Verlorenes Hintergrundwissen:**
Eine Formulierung, bei der ein zeitgenössischer Jude sofort eine konkrete AT-Stelle
vor Augen gehabt hätte, heute aber kein Leser mehr. Beispiel: „40 Tage Wüste" →
Dtn 8,2 + 1. Kön 19,8.

**Kategorie 3 — Wörtliches Zitat:**
Jesus oder der Erzähler zitieren nachweislich einen AT-Text. Immer annotieren.

**NICHT annotieren**, wenn:
- Die Verbindung eine theologische Spekulation ist (Bsp.: „Jesus versteht sich als…")
- Nur inhaltliche Ähnlichkeit, kein erkennbarer Textzusammenhang für Zeitgenossen
- Allgemeines Frömmigkeitsvokabular ohne konkrete AT-Vorlage

### Review-Kriterien für Jesus-Annotationen

- `typ: "jesus"` markiert Jesusrede im bereinigten Vers-Text
- `von` und `bis` sind Zeichenpositionen im **bereinigten** Text (Fußnoten entfernt)
- `bis: -1` bedeutet Versende
- Prüfen: Endet die Annotation wirklich am Ende der Jesusrede?
  Insbesondere `bis`-Werte ≠ `-1` am Ende von Versen verifizieren.

### Wie Zeichenpositionen berechnet werden

```python
import re
fn_regex = re.compile(r'<sup\s+title=(["\'])([^"\']*)\1>\s*(?:&#x[\da-fA-F]+;|✲)\s*</sup>')

def clean(raw_vers_text):
    return fn_regex.sub('', raw_vers_text).strip()

vers = clean(raw_text)
von = vers.find("gesuchter Textausschnitt")
bis = von + len("gesuchter Textausschnitt")
```

Der Raw-Text der Menge-Bibel ist fetchbar über:
`https://raw.githubusercontent.com/renehamburger/Menge-Bibel/master/Bibel/Neues%20Testament/02%20-%20Markus.md`
(gemeinfrei, 1926 veröffentlicht; beim `WebFetch`-Aufruf ggf. Copyright-Kontext mitgeben)

---

## JSON-Dateistruktur (Erinnerung)

```json
{
  "buch": "Markus",
  "kapitel": 4,
  "markierungen": [
    {
      "vers_von": 12,
      "von": 0,
      "vers_bis": 12,
      "bis": -1,
      "typ": "at",
      "referenz": "Jes 6,9f",
      "vgl": false,
      "url": "https://www.bibleserver.com/MENG/Jesaja6,9",
      "autor": "AI",
      "begruendung": "...",
      "status": "aktiv"
    }
  ]
}
```

Mehrere Referenzen: statt `url` das `urls`-Array verwenden:
```json
"urls": [
  { "label": "Dtn 8,2", "url": "https://www.bibleserver.com/MENG/5.Mose8,2" },
  { "label": "1. Kön 19,8", "url": "https://www.bibleserver.com/MENG/1.Koenige19,8" }
]
```

---

## Git-Workflow (Hard Rules)

- **NIEMALS auf `main` pushen** ohne explizite Zustimmung in der aktuellen Session
- Alle Commits auf `feat/reasoning-for-references`
- Vor jedem Push: Ziel-Branch explizit nennen

```bash
git checkout feat/reasoning-for-references
git pull origin feat/reasoning-for-references
# ... Änderungen ...
git add annotationen/markus/kapitel-X.json
git commit -m "Review Mk X: ..."
git push -u origin feat/reasoning-for-references
```
