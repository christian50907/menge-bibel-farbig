#!/usr/bin/env python3
"""check_positions.py — Annotationspositions-Prüfung für menge-bibel-farbig

Extrahiert Verstexte aus dem Menge-Bibel-Rohtext und prüft alle von/bis-Positionen
einer Annotationsdatei. Gibt Snippets und Warnungen aus.

Verwendung:
    python check_positions.py <rohtext_datei> <kapitel_nr> <kapitel_json> [--verses]

Optionen:
    --verses    Alle Verstexte mit Längen ausgeben — nützlich zum Auffinden neuer
                Positionen, bevor die JSON-Datei existiert.

Beispiel:
    python ai-tools/skills/menge-bibel-farbig/scripts/check_positions.py \\
      ai-tools/markus-roh.txt 9 annotationen/markus/kapitel-9.json

Exit-Code:
    0  — kein Fehler
    1  — mindestens ein Positions-Fehler gefunden (Warnungen zählen nicht)
"""

import sys
import os
import json

sys.stdout.reconfigure(encoding='utf-8')

# parse_menge im gleichen Verzeichnis importieren
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_menge import extract_chapter_block, parse_verses


def load_verses(rohtext_path: str, kapitel: int) -> dict:
    with open(rohtext_path, encoding='utf-8') as f:
        lines = f.read().splitlines()
    block = extract_chapter_block(lines, kapitel)
    raw = parse_verses(block)
    return {str(k): v for k, v in raw.items()}


def fmt_snippet(text: str, maxlen: int = 72) -> str:
    """Repr-Darstellung, bei langen Texten abgekürzt."""
    if len(text) <= maxlen:
        return repr(text)
    return repr(text[:maxlen - 3]) + '...'


def check_positions(kapitel_json_path: str, verses: dict) -> int:
    with open(kapitel_json_path, encoding='utf-8') as f:
        anno = json.load(f)

    markierungen = anno.get('markierungen', [])
    n_jesus = sum(1 for m in markierungen if m.get('typ') == 'jesus')
    n_at    = sum(1 for m in markierungen if m.get('typ') == 'at')
    total   = len(markierungen)

    print(
        f"=== Kapitel {anno.get('kapitel', '?')} — "
        f"Positions-Check ({total} Annotationen: {n_jesus} jesus, {n_at} at) ===\n"
    )

    n_errors   = 0
    n_warnings = 0

    for typ_label, typ_key in [('JESUS-SPANS', 'jesus'), ('AT-SPANS', 'at')]:
        gruppe = [m for m in markierungen if m.get('typ') == typ_key]
        if not gruppe:
            continue

        print(f"{typ_label}:")

        for m in gruppe:
            vv  = str(m.get('vers_von', '?'))
            vb  = str(m.get('vers_bis', '?'))
            von = m.get('von', 0)
            bis = m.get('bis', -1)

            vers_label = f"V{vv}" if vv == vb else f"V{vv}-{vb}"

            # Referenz-Label für AT
            ref = ''
            if typ_key == 'at':
                if 'referenz' in m:
                    ref = f"  ({m['referenz']})"
                elif 'urls' in m:
                    labels = [u.get('label', '') for u in m['urls']]
                    ref = f"  ({', '.join(labels)})"

            status = m.get('status', 'aktiv')
            status_tag = '' if status == 'aktiv' else f'  [{status}]'

            # Startvers vorhanden?
            if vv not in verses:
                print(f"  {vers_label:12}  FEHLER: V{vv} nicht in geparsten Versen!")
                n_errors += 1
                continue

            t_start  = verses[vv]
            len_start = len(t_start)

            issues = []

            # von validieren
            if von < 0:
                issues.append(f"FEHLER: von={von} ist negativ")
                n_errors += 1
            elif von > len_start:
                issues.append(f"FEHLER: von={von} > Verslänge V{vv} ({len_start})")
                n_errors += 1

            if vv == vb:
                # --- einversige Annotation ---
                span_label = f"[{von}:{bis}]"

                if bis == -1:
                    snippet = t_start[von:] if 0 <= von <= len_start else ''
                elif 0 <= von <= len_start and 0 <= bis <= len_start:
                    snippet = t_start[von:bis]
                else:
                    snippet = ''

                # bis validieren
                if bis != -1:
                    if bis > len_start:
                        issues.append(f"FEHLER: bis={bis} > Verslänge V{vv} ({len_start})")
                        n_errors += 1
                    elif bis == len_start:
                        issues.append(f"Warnung: bis={bis} == Verslänge ({len_start}), besser bis=-1")
                        n_warnings += 1
                    elif bis < von:
                        issues.append(f"FEHLER: bis={bis} < von={von}, invertierter Span")
                        n_errors += 1
                    elif bis == von:
                        issues.append(f"Warnung: bis={bis} == von={von}, leerer Span")
                        n_warnings += 1

                print(f"  {vers_label:12}  {span_label:14}  {fmt_snippet(snippet)}{ref}{status_tag}")

            else:
                # --- versübergreifende Annotation ---
                # Startvers-Ende
                snippet_start = t_start[von:] if 0 <= von <= len_start else ''
                disp_start = fmt_snippet(snippet_start, 55)

                # Endvers
                if vb not in verses:
                    print(f"  {vers_label:12}  V{vv}[{von}:] = {disp_start}")
                    print(f"  {'':12}  FEHLER: V{vb} nicht in geparsten Versen!")
                    n_errors += 1
                else:
                    t_end   = verses[vb]
                    len_end = len(t_end)

                    if bis == -1:
                        snippet_end = t_end
                    elif bis <= len_end:
                        snippet_end = t_end[:bis]
                    else:
                        snippet_end = ''
                        issues.append(f"FEHLER: bis={bis} > Verslänge V{vb} ({len_end})")
                        n_errors += 1

                    if bis != -1 and bis == len_end and not issues:
                        issues.append(f"Warnung: bis={bis} == Verslänge V{vb} ({len_end}), besser bis=-1")
                        n_warnings += 1

                    disp_end = fmt_snippet(snippet_end, 55)
                    print(f"  {vers_label:12}  V{vv}[{von}:]  = {disp_start}")
                    print(f"  {'':12}  V{vb}[:{bis}] = {disp_end}{ref}{status_tag}")

            for issue in issues:
                tag = 'FEHLER  ' if issue.startswith('FEHLER') else 'Warnung '
                print(f"    {tag}: {issue}")

        print()

    # Zusammenfassung
    if n_errors == 0 and n_warnings == 0:
        print("=== OK: Keine Fehler, keine Warnungen ===")
    else:
        print(f"=== Zusammenfassung: {n_errors} Fehler, {n_warnings} Warnungen ===")

    return n_errors


def print_verses(verses: dict):
    print("=== ALLE VERSTEXTE (repr, mit Länge) — für Positions-Suche ===\n")
    for nr in sorted(verses.keys(), key=int):
        t = verses[nr]
        display = repr(t) if len(t) <= 100 else repr(t[:97]) + '...'
        print(f"V{int(nr):3}  [len={len(t):4}]:  {display}")
    print()


def main():
    show_verses = '--verses' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('--')]

    if len(args) != 3:
        print(
            f'Verwendung: {sys.argv[0]} <rohtext_datei> <kapitel_nr> <kapitel_json> [--verses]',
            file=sys.stderr
        )
        sys.exit(1)

    rohtext_path, kapitel_str, json_path = args

    try:
        kapitel = int(kapitel_str)
    except ValueError:
        print('Fehler: Kapitelnummer muss eine ganze Zahl sein', file=sys.stderr)
        sys.exit(1)

    try:
        verses = load_verses(rohtext_path, kapitel)
    except FileNotFoundError as e:
        print(f'Fehler: {e}', file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f'Fehler: {e}', file=sys.stderr)
        sys.exit(1)

    if show_verses:
        print_verses(verses)

    if not os.path.exists(json_path):
        if show_verses:
            print(f'(JSON-Datei {json_path} existiert noch nicht — nur --verses ausgegeben)')
            sys.exit(0)
        print(f'Fehler: JSON-Datei "{json_path}" nicht gefunden', file=sys.stderr)
        sys.exit(1)

    try:
        n_errors = check_positions(json_path, verses)
    except FileNotFoundError as e:
        print(f'Fehler: {e}', file=sys.stderr)
        sys.exit(1)

    sys.exit(1 if n_errors > 0 else 0)


if __name__ == '__main__':
    main()
