---
name: menge-bibel-farbig
description: >
  Projektwissen für das GitHub-Repo christian50907/menge-bibel-farbig —
  eine statische Website zur farbkodierten Darstellung der Menge-Bibel.
  Verwende diesen Skill immer wenn es um dieses Projekt geht: Markdown-Parser,
  Annotationen erstellen oder bearbeiten, kapitel.html oder style.css anpassen,
  neue Bücher/Kapitel hinzufügen, manifest.json pflegen, oder Bugs im Rendering beheben.
---

# Skill: menge-bibel-farbig Projekt

Dieses Dokument fasst alles zusammen, was Claude über das Projekt
`christian50907/menge-bibel-farbig` wissen muss, um in einem neuen Chat
sofort produktiv zu sein — ohne erneutes Debugging.

---

## Projektübersicht

Eine statische GitHub-Pages-Website, die Bibelkapitel aus der gemeinfreien
Menge-Bibel farbkodiert darstellt:

- **Rot** — direkte Worte Jesu (`<span class="jesus">`)
- **Grün** — alttestamentliche Zitate und Bezüge (`<span class="at">`), mit klickbaren Links zu bibleserver.com/MENG
- **Goldenes `*`** — Fußnoten aus dem Quell-Repo, als Hover-Tooltip (`<span class="fn" title="...">`)

Quelldaten: `renehamburger/Menge-Bibel` (Markdown)  
Annotationen: eigene JSON-Dateien im Repo unter `annotationen/<buch>/kapitel-N.json`  
Live-URL: `https://christian50907.github.io/menge-bibel-farbig/`

---

## Dateistruktur

```
index.html                          Startseite (dynamisch aus manifest.json)
kapitel.html                        Kapitelanzeige (dynamisch per JS)
style.css                           Zentrales Stylesheet (gilt für beide Seiten)
annotationen/
  manifest.json                     ← zentrale Wahrheitsquelle für Bücher/Kapitel
  markus/
    kapitel-1.json
    kapitel-2.json
```

---

## manifest.json — zentrale Wahrheitsquelle ⚠️

`annotationen/manifest.json` ist die **einzige Stelle**, an der Bücher und
Kapitel registriert werden. Beide Seiten laden diese Datei relativ.

```json
{
  "buecher": [
    {
      "id":        "markus",
      "name":      "Markus",
      "quellpfad": "Bibel/Neues%20Testament/02%20-%20Markus.md",
      "kapitel":   [1, 2]
    }
  ]
}
```

### Felder

- `id` — URL-Parameter (`?buch=markus`), entspricht dem Unterordner-Namen unter `annotationen/`
- `name` — Anzeigename in Sidebar, Grid, Seitentitel
- `quellpfad` — Pfad im Repo `renehamburger/Menge-Bibel` (URL-encoded)
- `kapitel` — Array der verfügbaren Kapitel-Nummern; **Reihenfolge = Navigationsreihenfolge**

### Workflow: neues Kapitel hinzufügen

1. `annotationen/<buch>/kapitel-N.json` erstellen
2. In `manifest.json` die Kapitel-Nummer ins `kapitel`-Array eintragen
3. Fertig — Sidebar, TOC-Navigation und Index-Grid aktualisieren sich automatisch

### Workflow: neues Buch hinzufügen

1. Unterordner `annotationen/<buch-id>/` anlegen
2. Ersten `kapitel-1.json` erstellen
3. Neuen Eintrag in `manifest.json` hinzufügen — **Position im Array = Anzeigereihenfolge**
4. Fertig

### Reihenfolge-Prinzip

Die Reihenfolge der Bücher im `buecher`-Array bestimmt die Anzeigereihenfolge
**überall**: Sidebar auf `kapitel.html`, Buch-Grid auf `index.html`.
Das Array folgt der kanonischen NT-Reihenfolge, wird aber manuell gepflegt.
Bücher, die noch nicht im Manifest stehen, erscheinen im Grid als
„In Vorbereitung" — ihre Reihenfolge kommt aus der `NT_KANON`-Liste in `index.html`.

---

## index.html — dynamisch

`index.html` lädt `annotationen/manifest.json` und rendert daraus:

- **Sidebar** (`#sidebar-nav`): Nur verfügbare Bücher, mit Link auf ihr erstes Kapitel
- **Buch-Grid** (`#buch-grid`): Verfügbare Bücher als klickbare Karten (Manifest-Reihenfolge),
  dann alle NT-Bücher ohne Manifest-Eintrag als graue „In Vorbereitung"-Karten

Der statische HTML-Inhalt (Projektbeschreibung, Textgrundlage) bleibt in der Seite —
nur Grid und Sidebar werden per JS befüllt.

---

## kapitel.html — dynamisch

Lädt beim Start `annotationen/manifest.json`, daraus:
- `info = manifest.buecher.find(b => b.id === buch)` — Buchinfo inkl. `quellpfad` + `kapitel`-Array
- Sidebar mit allen verfügbaren Büchern (Manifest-Reihenfolge), aktiver Eintrag hervorgehoben
- Kapitelnavigation (← / →) aus `info.kapitel`-Array

Das **`BUECHER`-Objekt existiert nicht mehr** — `manifest.json` hat es vollständig ersetzt.

---

## Markdown-Format der Menge-Bibel (empirisch geprüft)

```
# BUCHTITEL

## Hauptabschnitt

### Unterabschnitt

__1__
<sup>1</sup>Erster Vers des ersten Kapitels.
<sup>2</sup>Zweiter Vers<sup title="Fußnote">&#x2732;</sup>.
<sup>3</sup>Dritter Vers — gleicher Absatz (keine Leerzeile).

<sup>4</sup>Vierter Vers — neuer Absatz (Leerzeile davor).

### Nächster Unterabschnitt

<sup>9</sup>Vers 9 — noch Kapitel 1.

## Nächster Hauptabschnitt

### Erster Unterabschnitt des nächsten Kapitels

__2__
<sup>1</sup>Erster Vers des zweiten Kapitels.
```

**Schlüsselregeln:**
- Kapitelmarkierung: `__N__` (Underscores), **nicht** `**N**`
- Versnummern: `<sup>N</sup>` als HTML-Tag im Fließtext
- Fußnoten: `<sup title="TEXT">&#x2732;</sup>` — Zeichen kann auch als UTF-8 `✲` vorkommen, title-Attribut mit einfachen oder doppelten Anführungszeichen
- Überschriften (`#`, `##`, `###`) sind Abschnittsstruktur, kein Bibeltext
- Leerzeilen im Markdown = Absatzgrenzen, die im HTML erhalten bleiben

---

## Parser-Algorithmus (JavaScript, getestet)

### Schritt 1 — Vorgelagerte Überschriften sammeln

Überschriften zwischen letztem Fließtext des Vorgängerkapitels und `__N__`
gehören zum **neuen** Kapitel. Reset bei: anderem `__M__` oder Fließtext-Zeile.

### Schritt 2 — Kapitelblock isolieren

Zeilen ab `__N__` bis zum nächsten `__M__` sammeln.

### Schritt 3 — Trailing Überschriften abschneiden ⚠️

Überschriften am Ende des Blocks gehören zum nächsten Kapitel.
Einen einzigen rückwärtslaufenden Index verwenden (nicht mehrere while-Loops),
weil Leerzeilen zwischen Überschriften vorkommen:

```javascript
let ende = blockLines.length - 1;
while (ende >= 0) {
  const s = blockLines[ende].trim();
  if (s === '' || /^#{1,6}\s+/.test(s)) ende--;
  else break;
}
blockLines.length = ende + 1;
```

### Schritt 4 — Absatzweise verarbeiten, Fußnoten extrahieren ⚠️

Fußnoten müssen **vor** der Annotation-Anwendung extrahiert werden,
weil die JSON-Annotationen (von/bis) auf dem **bereinigten Text ohne Fußnoten**
basieren. Die Positionen werden für spätere Einfügung gemerkt.

```javascript
const fnRegex = /<sup\s+title=(["'])([^"']*)\1>\s*(?:&#x[\da-fA-F]+;|✲)\s*<\/sup>/g;
const fnMap = [];
let bereinigt = '';
let fnCursor = 0, fnMatch;
while ((fnMatch = fnRegex.exec(block)) !== null) {
  bereinigt += block.slice(fnCursor, fnMatch.index);
  fnMap.push({ pos: bereinigt.length, title: fnMatch[2] });
  fnCursor = fnMatch.index + fnMatch[0].length;
}
bereinigt += block.slice(fnCursor);
bereinigt = bereinigt.replace(/&#x[\da-fA-F]+;/g, '').replace(/\s+/g, ' ').trim();
```

Verse extrahieren, und `fnMap` auf Verse aufteilen (Positionen relativ zum Versanfang):

```javascript
const parts = bereinigt.split(/<sup>(\d+)<\/sup>/);
let versOffset = 0;
for (let i = 1; i < parts.length - 1; i += 2) {
  const nr = parseInt(parts[i]);
  const text = parts[i + 1].trim();
  if (text) {
    const versStart = bereinigt.indexOf(text, versOffset);
    const versEnde  = versStart + text.length;
    const fnInVers  = fnMap
      .filter(f => f.pos >= versStart && f.pos <= versEnde)
      .map(f => ({ pos: f.pos - versStart, title: f.title }));
    verseImAbsatz.push({ nr, text, fn: fnInVers });
    versOffset = versEnde;
  }
}
```

### Schritt 5 — Rückgabe

```
{ typ: 'heading', level: 2, text: '...' }
{ typ: 'absatz',  verse: [ { nr, text, fn: [{pos, title}, ...] }, ... ] }
```

---

## Annotationen + Fußnoten rendern ⚠️

**Kritisch:** Fußnoten werden **zusammen mit Annotationen** als Events direkt
auf dem bereinigten Bibeltext platziert — NICHT nachträglich im annotierten HTML.

**Warum:** Nachträgliches Einfügen durch Zeichenzählung im HTML würde den Text
in `<a>…</a>`-Links mitzählen, was alle nachfolgenden Fußnoten-Positionen verschiebt.

```javascript
// Fußnoten als fnEvents — nach closeEvents, vor openEvents
const fnEvents = {};
for (const fn of (fussnoten || [])) {
  if (!fnEvents[fn.pos]) fnEvents[fn.pos] = [];
  const title = fn.title.replace(/"/g, '&quot;');
  fnEvents[fn.pos].push(`<span class="fn" title="${title}">*</span>`);
}

let result = '';
for (let i = 0; i <= n; i++) {
  if (closeEvents[i]) result += closeEvents[i].join('');
  if (fnEvents[i])    result += fnEvents[i].join('');  // nach close, vor open
  if (openEvents[i])  result += openEvents[i].join('');
  if (i < n) result += versText[i];
}
```

---

## Annotations-Span-Bug und Fix

Wenn Jesus-Span und AT-Span **dieselbe Endposition** haben (beide `bis: -1`),
landet der AT-Link sonst zwischen den `</span>`-Tags → Browser rendert ihn blau.

**Fix:** Getrennte open/close Event-Listen, close mit `unshift` (innerste zuerst):

```javascript
const openEvents  = {}; // append — äußere zuerst
const closeEvents = {}; // unshift — innerste zuerst

// Ausgabe: erst closeEvents, dann fnEvents, dann openEvents
```

---

## CSS-Klassen (style.css)

| Klasse | Verwendung |
|--------|------------|
| `.abschnitt-kopf` | H2-Überschriften — auch auf `index.html` direkt als `<div>` |
| `.abschnitt-titel` | H3+-Überschriften |
| `.jesus` | Rote Jesusworte |
| `.at` | Grüne AT-Bezüge (enthält Links) |
| `.vn` | Versnummer (hochgestellt, grau) |
| `.fn` | Fußnoten-Sternchen (hochgestellt, gold, `cursor:help`) |

**Wichtig:** `index.html` verwendet `<div class="abschnitt-kopf">` direkt,
nicht `<h2>`. Kein separater `.index-content h2`-Style nötig.

---

## AT-Annotationsstrategie

### Grundziel

AT-Annotationen sollen für einen heutigen Leser sichtbar machen, wo NT-Texte auf
der Lebens- und Glaubensrealität der damaligen Juden aufbauen. Ein jüdischer Zeitgenosse
Jesu kannte das AT auswendig und verstand intuitiv, was heute oft verloren ist.
Die Annotationen sollen dieses Wissen zurückbringen — nicht primär theologisch kommentieren.

### Annotieren wenn mindestens eines dieser Kriterien zutrifft

1. **Kulturelle Fremdheit** — etwas, das heute befremdlich wirkt, aber im AT eine
   selbstverständliche Grundlage hat (Speisegebote, Reinheitsvorschriften, Rituale,
   Alltagsgesten). Beispiel: Heuschrecken als Speise → 3. Mo 11,22.

2. **Verlorenes Hintergrundwissen** — ein Bild, eine Metapher oder eine Handlung,
   die ein damaliger Jude sofort als Bezug auf eine konkrete AT-Stelle erkannt hätte,
   die heute aber nicht mehr präsent ist. Beispiel: der Weltbaum mit nistenden Vögeln
   → Dan 4,9; Hes 17,23.

3. **Theologische Pointe** — wo der NT-Text eine AT-Stelle bewusst aufnimmt und
   weiterdreht, sodass der Bezug zur eigentlichen Aussage gehört. Beispiel: Jesus
   als „Stärkerer" gegenüber dem Starken → Jes 49,24f.

4. **Erstmalige oder ungewöhnliche Verwendung** — wenn etwas im NT auftaucht, das
   zwar AT-Grundlage hat, aber für damalige Juden trotzdem überraschend war. Beispiel:
   Jesus spricht Gott als „Vater" in einer Intimität an, die im AT so nicht vorkommt
   → beim ersten Auftreten im jeweiligen Buch annotieren.

### Nicht annotieren wenn

- Der Begriff so allgemein im jüdischen Sprachgebrauch war, dass kein Jude dabei
  an eine bestimmte Textstelle gedacht hätte (z.B. jede einzelne Erwähnung von
  „Vater", „Geist", „Sohn", „Auferstehung" nach der ersten annotierten Stelle)
- Der Bezug nur durch moderne theologische Gelehrsamkeit konstruiert ist und nicht
  durch das Alltagswissen eines damaligen Lesers erschließbar wäre

### Wiederholungen ⚠️

Zentrale theologische Begriffe und Motive (Vater, Sohn, Geist, Auferstehung,
Reich Gottes u.a.) werden **nur beim ersten Auftreten im jeweiligen Buch** annotiert,
es sei denn, der spätere Kontext gibt dem Bezug eine eigenständige neue Dimension.
Sonst entsteht Über-Annotation.

### Geltungsbereich

AT-Bezüge werden sowohl in **Jesu direkter Rede** als auch im **Erzählertext**
annotiert — und später auch in den Briefen.

### Mehrere Referenzen an einer Stelle

Mehrere `urls`-Einträge sind angebracht, wenn die Bezüge **konzeptionell unterschiedliche
Dimensionen** beleuchten — nicht nur wenn mehrere Bücher dieselbe Aussage belegen.
Beispiel Mk 4,32: Hes 17,23 (der erhabene Baum als Heilsort) und Dan 4,9 (der
Weltbaum als Bild für ein Reich) tragen je eine eigene Aussage → beide annotieren.

---

## Annotationsstrategie AT-Bezüge

### Grundziel

AT-Annotationen sollen für heutige Leser sichtbar machen, wo NT-Texte auf der
Lebens- und Glaubensrealität der damaligen Juden aufbauen. Ein damaliger jüdischer
Leser kannte das AT sehr gut und verstand viele Anspielungen intuitiv — dieses
Wissen ist heute oft verloren. Die Annotationen stellen es wieder her.

Die Leitfrage ist nicht primär „Welche theologische Tiefenaussage steckt hier?",
sondern breiter: **„Gab es dafür im Leben eines damaligen Juden eine AT-Grundlage,
die ihm sofort verständlich war — und die einem heutigen Leser fehlt?"**

### Wann annotieren

Annotieren wenn **mindestens eines** dieser Kriterien zutrifft:

1. **Kulturelle Fremdheit** — etwas, das heute befremdlich wirkt, aber im AT
   eine selbstverständliche Grundlage hat (Speisegebote, Reinheitsvorschriften,
   Rituale, Gesten). Beispiel: Heuschrecken als Nahrung → 3. Mo 11,22.

2. **Verlorenes Hintergrundwissen** — ein Bild, eine Metapher oder Handlung,
   die ein damaliger Jude sofort als Bezug auf eine konkrete AT-Stelle erkannt
   hätte, die heute aber nicht mehr präsent ist. Beispiel: der Weltbaum mit
   nistenden Vögeln → Dan 4,9/18; Hes 17,23.

3. **Theologische Pointe** — der NT-Text nimmt eine AT-Stelle bewusst auf und
   dreht sie weiter, sodass der Bezug zur eigentlichen Aussage gehört.
   Beispiel: Jesus als „Stärkerer" gegenüber dem Starken → Jes 49,24f.

4. **Erstmalige oder ungewöhnliche Verwendung** — etwas hat zwar AT-Grundlage,
   war aber für damalige Juden trotzdem überraschend. Beispiel: Jesus spricht
   Gott als „Vater" in einer Intimität an, die im AT so nicht vorkommt —
   beim **ersten Auftreten** im jeweiligen Buch annotieren.

### Wann nicht annotieren

- Begriffe oder Wendungen, die so allgemein im jüdischen Sprachgebrauch waren,
  dass kein Jude dabei an eine bestimmte Textstelle gedacht hätte (z.B. jede
  Erwähnung von „Vater", „Sohn", „Geist", „Auferstehung" nach der ersten)
- Bezüge, die nur durch moderne theologische Gelehrsamkeit konstruiert sind
  und nicht durch das Alltagswissen eines damaligen Lesers erschließbar wären
- Allgemeines Lobesvokabular und geläufige Frömmigkeitssprache, auch wenn ein
  AT-Buch dieses Motiv besonders schön entfaltet. Beispiel: „wie Großes der Herr
  getan und wie er sich erbarmt hat" klingt nach Ps 103, aber die Wendungen waren
  so allgegenwärtig im jüdischen Gebet und Lobpreis, dass ein damaliger Jude dabei
  nicht an eine bestimmte Stelle dachte — ähnlich wie „Gott sei Dank" heute keinen
  Bezug zu einem konkreten Bibelvers herstellt. Solche Stellen nicht annotieren.

### Wiederholungen (wichtig!)

Zentrale theologische Begriffe und Bezüge werden **nur beim ersten Auftreten
im jeweiligen Buch** annotiert — nicht bei jeder weiteren Erwähnung.
Betrifft insbesondere: Vater, Sohn, Geist, Auferstehung, und andere
Schlüsselbegriffe des NT.

### Mehrere Referenzen

Mehrere `urls`-Einträge sind angebracht, wenn die Bezüge **konzeptionell
unterschiedliche Dimensionen** beleuchten — nicht nur wenn dieselbe Aussage
an mehreren AT-Stellen belegt ist. Beispiel Mk 4,32: Hes 17,23 zeigt den
Baum als Bild für Israels Wiederherstellung; Dan 4,9/18 zeigt den Weltbaum
als Bild für ein Weltreich — beide Dimensionen zusammen machen die Pointe
des Senfkorn-Gleichnisses erst vollständig sichtbar.

### Erzählertext vs. Jesus-Worte

AT-Bezüge werden sowohl in **direkten Jesus-Worten** als auch im
**Erzählertext** annotiert — und später auch in den Briefen.

## Annotationsformat (JSON)

### Feldreihenfolge

Die Felder werden in dieser Reihenfolge geschrieben — für bessere Lesbarkeit:
`vers_von` → `von` → `vers_bis` → `bis` → `typ` → (AT-Felder) → (Metadaten)

### Jesus-Einträge

Schlank — nur rendering-relevante Felder, keine Metadaten nötig:

```json
{ "vers_von": 15, "von": 16, "vers_bis": 15, "bis": -1, "typ": "jesus" }
```

### AT-Einträge

Mit vollständigen Metadaten — `autor`, `status` und `begruendung` sind Pflicht:

```json
{
  "vers_von": 2, "von": 45, "vers_bis": 2, "bis": 121, "typ": "at",
  "referenz": "Mal 3,1", "vgl": false,
  "url": "https://www.bibleserver.com/MENG/Maleachi3,1",
  "autor": "AI",
  "status": "aktiv",
  "begruendung": "Wörtliches Zitat: Der Bote, der den Weg bereiten soll..."
}
```

Für mehrere Referenzen an einer Stelle `urls` (Plural) statt `url`:

```json
{
  "vers_von": 32, "von": 109, "vers_bis": 32, "bis": -1, "typ": "at",
  "autor": "AI",
  "status": "aktiv",
  "urls": [
    { "label": "Hes 17,23", "url": "https://www.bibleserver.com/MENG/Hesekiel17,23" },
    { "label": "Dan 4,9",   "url": "https://www.bibleserver.com/MENG/Daniel4,9" }
  ],
  "begruendung": "Vögel nisten im Schatten des großen Baumes — zwei AT-Dimensionen..."
}
```

Inaktive Stellen (geprüft, aber bewusst nicht dargestellt):

```json
{
  "vers_von": 19, "von": 124, "vers_bis": 19, "bis": -1, "typ": "at",
  "referenz": "Ps 126,3", "vgl": true,
  "url": "...",
  "autor": "AI",
  "status": "inaktiv",
  "begruendung": "Zu allgemeines Lobesvokabular — kein spezifischer Textverweis."
}
```

### Felder im Überblick

**Rendering-Felder** (beide Typen):
- `vers_von` / `vers_bis`: Versnummern-Bereich (beide inklusiv). **Immer `vers_von`/`vers_bis` verwenden**, nicht das alte `vers`-Feld (einversig, veraltet)
- `von`: Zeichenposition im **bereinigten Text von `vers_von`** (ohne Fußnoten)
- `bis`: Zeichenposition im **bereinigten Text von `vers_bis`** — oder `-1` für Versende
- `typ`: `"jesus"` oder `"at"`
- `url` / `urls`: AT-Link(s) zu bibleserver.com/MENG
- `referenz`: Anzeige-Label der AT-Stelle, z.B. `"Mal 3,1"`
- `vgl`: `true` = inhaltliche Anspielung, `false` = wörtliches Zitat

**Metadaten-Felder** (nur `typ: "at"`):
- `autor`: `"AI"` oder `"Mensch"`
- `status`: `"aktiv"` (wird dargestellt) oder `"inaktiv"` (geprüft, nicht dargestellt) — **immer explizit angeben**
- `begruendung`: Erklärung warum annotiert oder warum inaktiv

### Status-Filter im Renderer

`kapitel.html` filtert vor dem Rendering:
```javascript
const aktiveMarkierungen = anno.markierungen.filter(m => (m.status || 'aktiv') === 'aktiv');
```
Fehlendes `status`-Feld gilt als aktiv (Rückwärtskompatibilität) — bei neuen AT-Einträgen aber immer explizit angeben.

### Versübergreifende Spans ⚠️

Wenn eine Markierung über mehrere Verse geht:
- `von` bezieht sich auf den bereinigten Text von `vers_von`
- `bis` bezieht sich auf den bereinigten Text von `vers_bis` (oder `-1`)
- AT-Spans innerhalb eines versübergreifenden Jesus-Spans werden normal
  einversig annotiert — der Renderer schachtelt sie korrekt

Beispiel (Jesus-Rede V25–26, AT-Bezug nur in V26):
```json
{ "vers_von": 25, "von": 21, "vers_bis": 26, "bis": -1, "typ": "jesus" },
{ "vers_von": 26, "von": 71, "vers_bis": 26, "bis": 137, "typ": "at",
  "referenz": "1. Sam 21,2–7", "vgl": false, "url": "...",
  "autor": "AI", "status": "aktiv", "begruendung": "..." }
```

### AT-Referenzen verifizieren ⚠️

Beim Annotieren von AT-Bezügen **immer** die tatsächliche Kapitel- und Versstruktur
des jeweiligen AT-Buches prüfen, bevor eine Referenz eingetragen wird.

Konkret bekannter Fehlerfall: **Joel** hat in deutschen Bibeln **4 Kapitel**
(in der englischen/hebräischen Zählung nur 3 — Kapitel 3 der englischen Zählung
entspricht Kapitel 4 der deutschen). Der Vers „Schwingt die Sichel, denn die Ernte
ist reif" steht in deutschen Bibeln in **Joel 4,13**, nicht in Joel 3,13.

Allgemeine Regel: Bücher mit abweichender Kapitelzählung zwischen hebräischer/
englischer und deutscher Tradition (betrifft u.a. Joel, Maleachi, manche Psalmen-
Abschnitte) immer gegen die deutsche Zählung auf bibleserver.com/MENG prüfen.

**Buchnamen in der Menge-Bibel:** Die Menge-Bibel verwendet eigene Schreibweisen,
die von anderen Übersetzungen abweichen können. Bekannte Fälle:
- **Hesekiel** (niemals Ezechiel) — Abkürzung `Hes`, URL-Segment `Hesekiel`
  → korrekt: `"referenz": "Hes 17,23"`, `"url": ".../Hesekiel17,23"`
- Immer die exakte Schreibweise auf bibleserver.com/MENG prüfen, bevor eine
  Referenz eingetragen wird — auch für weniger bekannte Bücher.

---

## Deployment & Feature-Branches ⚠️

Alle projekt-eigenen Ressourcen werden **relativ** geladen:

```javascript
// manifest.json
const manifestRes = await fetch("annotationen/manifest.json");

// Annotationsdatei
const annoUrl = `annotationen/${buch}/kapitel-${kapitel}.json`;
```

Das bedeutet: GitHub Pages liefert alle Dateien immer aus dem Branch, der gerade
deployed ist — Feature-Branches funktionieren dadurch autonom korrekt.

**Nicht** so laden (hardcodierter Branch bricht Feature-Branches):
```javascript
// FALSCH — kommt immer aus main, egal welcher Branch deployed ist:
const url = `https://raw.githubusercontent.com/.../main/annotationen/...`;
```

Der Bibeltext-Fetch bleibt weiterhin absolut (fremdes Repo, kein relativer Pfad möglich).

---

## Raw-Text fetchen

`raw.githubusercontent.com` ist über `web_fetch` blockiert.

**Workaround:** Zuerst `https://github.com/renehamburger/Menge-Bibel` fetchen —
dadurch werden alle Datei-URLs bekannt. Alternativ: Nutzer fügt Rohtext in den Chat ein.

---

## Empfohlener Workflow für neue Annotationen

1. Nutzer gibt Buch + Kapitel an
2. Markdown-Text laden (via Repo-Einstiegsseite oder Nutzer-Input)
3. Parser in **Python testen** (Sandbox), dann 1:1 nach JS übersetzen
4. `von`/`bis`-Positionen immer auf dem **bereinigten Text** (ohne Fußnoten) berechnen
5. JSON-Annotationsdatei erstellen unter `annotationen/<buch>/kapitel-N.json`
6. Kapitel-Nummer in `annotationen/manifest.json` ins `kapitel`-Array eintragen

## Suchstrings niemals aus dem Gedächtnis ⚠️

Beim Berechnen von `von`/`bis`-Positionen **niemals** den Suchstring aus dem Gedächtnis
tippen. Bereits ein einzelnes abweichendes Wort (z.B. `»Was versucht«` statt des
tatsächlichen `»Warum versucht«`) gibt `-1` zurück und erzeugt einen ungültigen Eintrag,
der im Renderer zu einem fehlerhaften oder fehlenden Span führt.

**Korrekter Ablauf:**
1. Zuerst den tatsächlichen Verstext ausgeben: `print(v[nr])`
2. Den gesuchten Substring **direkt aus der Ausgabe kopieren**
3. Erst dann `v[nr].find(substring)` aufrufen

```python
# FALSCH — aus dem Gedächtnis:
von = v[15].find('»Was versucht')   # gibt -1 wenn Text abweicht!

# RICHTIG — erst ausgeben, dann kopieren:
print(v[15])
# → '»Warum versucht ihr mich? Reicht mir einen Denar...'
von = v[15].find('»Warum versucht')  # korrekt
```

Diese Regel gilt auch für AT-Zitate mit ›...‹ — immer zuerst den tatsächlichen
Unicode-Zeichenbestand prüfen (U+203A = `›`, U+2039 = `‹`), da die schließenden
Zeichen leicht verwechselt werden.
