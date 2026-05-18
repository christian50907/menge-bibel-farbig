---
name: annotation-review
description: >
  Review-Skill für bestehende Annotationen im menge-bibel-farbig-Projekt.
  Aufgerufen vom Main Agent nach der Erstannotation eines Kapitels.
  Prüft Korrektheit, Vollständigkeit und Qualität der Annotationen
  aus einer unabhängigen Perspektive.
---

# Skill: Annotations-Review

## Rolle

Du bist ein Review-Agent. Der Main Agent hat ein Kapitel annotiert und übergibt
dir das Ergebnis zur unabhängigen Prüfung. Du prüfst aus deiner eigenen Perspektive
— nicht als Korrektiv, sondern als zweite Stimme.

---

## Was du bekommst (Input vom Main Agent)

1. **Die JSON-Datei des Kapitels** — das `markierungen`-Array mit allen Annotationen
2. **Geparste Verstexte** — ein Dictionary `{ Versnummer: bereinigter_Text }`,
   wobei "bereinigt" bedeutet: Fußnoten entfernt, Überschriften entfernt,
   Whitespace normalisiert. Positionen `von`/`bis` beziehen sich auf diese Texte.
3. **Liste bereits annotierter AT-Motive** in früheren Kapiteln desselben Buches
   (für den Wiederholungs-Check)

---

## Leitprinzip

**Alle Annotationsentscheidungen drehen sich um eine Frage:**

> Hätte ein engagierter jüdischer Leser des 1. Jahrhunderts diesen Bezug
> beim Lesen intuitiv erkannt — und verliert ein heutiger Leser ohne
> dieses Wissen einen bedeutenden Teil des Textverständnisses?

Der Maßstab ist ein Jude, der diesen NT-Text liest: jemand mit normaler
religiöser Einbettung in die jüdische Tradition — kein Bauer, aber auch nicht
zwingend ein Schriftgelehrter. Technische Rechtsbegriffe (wie Korban, Mk 7,11)
oder apokalyptische Terminologie können annotiert werden, wenn sie für das
Verständnis der Textstelle wesentlich sind.

---

## Checkliste

### A — Jesus-Span Check

Für jede `typ: "jesus"`-Annotation:
- Spricht an dieser Stelle wirklich Jesus? Nicht Erzähler, nicht Johannes der Täufer,
  nicht Pharisäer oder andere Personen.
- Stimmt der markierte Textbereich mit tatsächlicher Jesusrede überein?

Scan des Kapitels:
- Gibt es Guillemets `»...«`, die eindeutig Jesus-Worte sind, aber keine jesus-Annotation haben?

### B — Positions-Check

Für jede Annotation: Extrahiere `verstext[von:bis]` und prüfe ob der Ausschnitt
dem annotierten Inhalt entspricht. **Kein Ad-hoc-Python schreiben** — dafür gibt es
ein vorproduziertes Skript, das Unicode-sicher ist und alle Annotationen auf einmal prüft:

```bash
python ai-tools/skills/menge-bibel-farbig/scripts/check_positions.py \
  ai-tools/markus-roh.txt <kapitel> annotationen/markus/kapitel-<N>.json
```

⛔ **Rohtext niemals per WebFetch laden** — das lädt 117 KB in den Kontext und
verlangsamt alle nachfolgenden Schritte massiv. Der Rohtext liegt bereits lokal
unter `ai-tools/markus-roh.txt`; `check_positions.py` liest ihn direkt von Disk.

Das Skript gibt für jede Annotation den extrahierten Snippet aus und meldet:
- **FEHLER**: `von`/`bis` außerhalb der Verslänge, invertierter Span, fehlender Vers
- **Warnung**: `bis` == Verslänge (sollte `-1` sein), leerer Span

Prüfe für jeden Snippet: Entspricht der markierte Text tatsächlich dem, was annotiert
sein soll — beginnt und endet die Markierung an der richtigen Stelle?

Prüfe für jede Annotation:
- Entspricht der extrahierte Ausschnitt dem annotierten Inhalt?
- Ist `bis: -1` korrekt für Annotationen, die bis zum Versende reichen?
- Bei versübergreifenden Annotationen (`vers_von ≠ vers_bis`):
  `von` bezieht sich auf `vers_von`, `bis` auf `vers_bis`.

### C — AT-Qualitäts-Check (zu viel / aktiv → inaktiv?)

Für jede aktive AT-Annotation — prüfe anhand des Leitprinzips:

1. **Ist der Bezug load-bearing?**
   Eine Annotation ist berechtigt, wenn das Textverständnis ohne diesen AT-Hintergrund
   erheblich eingeschränkt ist. Eine thematische Parallele allein genügt nicht.

2. **Hat die spezifische Formulierung eine AT-Entsprechung?**
   Inhaltliche Verwandtschaft ≠ erkennbarer Bezug. Ein zeitgenössischer Jude hätte
   den Bezug bei dieser konkreten Formulierung erkennen müssen — nicht erst durch
   Nachschlagen. (Gegenbeispiel: „Ich bin nicht gekommen, Gerechte zu rufen" → Jes 61
   ist inhaltlich verwandt, aber die Formulierung hat keine direkte Vorlage.)

3. **Ist es evokative Bildsprache ohne Autorenabsicht?**
   Wenn der NT-Autor ein AT-Bild verwendet, ohne es zu zitieren oder explizit aufzurufen,
   und die Parallele nur durch das Bild entsteht (nicht durch Formulierung oder Struktur),
   → inaktiv mit Begründung. (Beispiel: „grüner Rasen" → Ps 23,2 nur evokativ, Mk 6,39.)

4. **Wiederholung eines bereits annotierten Motivs?**
   Wurde dieses AT-Motiv bereits in einem früheren Kapitel desselben Buches annotiert?
   → Inaktiv, außer der neue Kontext fügt eine eigenständige neue Dimension hinzu.

5. **Intra-Kapitel-Redundanz?**
   Deckt eine andere aktive Annotation im selben Kapitel bereits denselben Sachverhalt ab?
   → Inaktiv mit Begründung.

### D — AT-Vollständigkeits-Check (zu wenig / fehlt etwas?)

Prüfe jeden Vers auf übersehene Bezüge anhand des Leitprinzips. Kategorien,
in denen häufig Lücken entstehen:

- **Reinheits- und Ritualgesetze** (3. Mo, 4. Mo): Unreinheit durch Kontakt,
  Speisegebote, Zizit, Opferformeln
- **Prophetenhandlungen** (v.a. Mose/Elia/Elisa-Parallelen): strukturelle Parallelen
  in Wundererzählungen, Berufungsszenen, Rückzug in die Wüste
- **Theophanie-Formeln**: „Ich bin's" (ego eimi), „Vorübergehen Gottes",
  Wolke, Stimme vom Himmel
- **Heilsgeschichtliche Symbole**: 40 Tage/Jahre, 12 Stämme/Jünger,
  Exodusmotive, Wüstenmotiv
- **Technische Rechtsbegriffe**: Tempelrecht, Eherecht, Reinheitsrecht —
  wenn der Text einen Fachbegriff verwendet, der heute nicht mehr verstanden wird
- **Menge-Fußnoten haben Präzedenz ⚠️**: Wenn Menge selbst an einer Stelle eine
  AT-Referenz in einer Fußnote notiert hat, muss diese Stelle aktiv annotiert sein —
  unabhängig davon, ob sie sonst nach dem „allgemeines Vokabular"-Kriterium annotiert
  worden wäre. Fehlt die Annotation: als `NEU aktiv` melden.

### E — Formale Prüfung

- Haben alle `typ: "at"`-Einträge die Pflichtfelder `autor`, `status`, `begruendung`?
- Ist `vgl` korrekt gesetzt?
  - `false` = wörtliches Zitat (der Bibeltext ist erkennbar übernommen)
  - `true` = inhaltliche Anspielung
- Stimmen die Buchtitel in den URLs mit der Menge-Bibel-Schreibweise überein?
  Bekannte Abweichungen: **Hesekiel** (nie Ezechiel), **5. Mose** (nie Deuteronomium),
  **Joel hat 4 Kapitel** in deutschen Bibeln (Joel 4,13, nicht Joel 3,13)
- Sind Begründungen vollständig, aber kompakt? Keine unnötige Ausschmückung.
  Das Argument muss erkennbar sein, aber der Text erscheint als Tooltip.

---

## Output-Format

Berichte als Tabelle mit vier Spalten:

| # | Art | Beschreibung | Begründung (Website) |
|---|-----|-------------|----------------------|

**Spalte `Art`** — feste Tags (dieselben wie im Hauptskill):

| Tag | Bedeutung |
|-----|-----------|
| `NEU aktiv` | Fehlende Annotation vorschlagen |
| `NEU inaktiv` | Geprüft, abgelehnt — **expliziter Auftrag an den Main Agent**, als `"status": "inaktiv"` einzutragen |
| `FIX Position` | Positions-Korrektur (von/bis falsch) |
| `FIX Konvention` | Formale Korrektur (z.B. bis=Verslänge → bis=-1) |
| `BUG fehlender Span` | Span fehlt komplett |
| `BUG Jesus-Span` | Jesus-Span zu weit oder zu eng |
| `UPDATE Begründung` | Begründung inhaltlich überarbeiten |
| `UPDATE Referenz` | Andere AT-Stelle passt besser |
| `UPDATE Span` | Span ausdehnen oder einschränken |
| `BESTÄTIGT` | Korrekt, keine Änderung |
| `ERWÄGEN` | Offene Frage ohne klare Entscheidung |

**Spalte `Begründung (Website)`** — nur für `NEU aktiv` und `UPDATE Begründung`:
der Text, der als Tooltip auf der Website erscheint. Für `NEU inaktiv`:
*(nicht sichtbar)* + kurze inhaltliche Notiz. Für technische Korrekturen: `—`.

**Zu `NEU inaktiv` ⚠️:** Jede Stelle, die untersucht aber bewusst nicht annotiert
wird (Wiederholung, kein load-bearing Bezug, evokativ ohne Autorenabsicht), muss
explizit als `NEU inaktiv` gemeldet werden — mit dem Hinweis, dass der Main Agent
sie als `"status": "inaktiv"` in die JSON-Datei einträgt. Ohne diesen Schritt
entsteht eine stille Lücke, die beim nächsten Review erneut aufgegriffen wird.

Wenn keine Befunde: kurze Bestätigung genügt.
