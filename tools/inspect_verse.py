#!/usr/bin/env python3
"""inspect_verse.py — Verstext anzeigen und Zeichenposition finden

Liest die Menge-Bibel-Markdown-Datei direkt — kein Zwischenschritt nötig.

Verwendung:
    python inspect_verse.py <markdown_datei> <kapitel> <vers> [suchstring]

Argumente:
    markdown_datei  Pfad zur Menge-Bibel-Markdown-Datei (z.B. "01 - Matthäus.md")
    kapitel         Kapitelnummer
    vers            Versnummer
    suchstring      Optional: Substring, dessen von/bis-Position gesucht wird

Ausgabe:
    Verstext mit Länge; bei Suchstring zusätzlich Position und Kontext.

Beispiel:
    python tools/inspect_verse.py pfad/zu/Matthäus.md 1 5
    python tools/inspect_verse.py pfad/zu/Matthäus.md 1 5 "Rahab"
"""

import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_menge import extract_chapter_block, parse_verses


def main():
    args = sys.argv[1:]
    if len(args) < 3:
        print(
            f'Verwendung: {sys.argv[0]} <markdown_datei> <kapitel> <vers> [suchstring]',
            file=sys.stderr,
        )
        sys.exit(1)

    markdown_path = args[0]
    kapitel_str   = args[1]
    vers_str      = args[2]
    suchstring    = ' '.join(args[3:]) if len(args) >= 4 else None

    try:
        kapitel = int(kapitel_str)
    except ValueError:
        print('Fehler: Kapitelnummer muss eine ganze Zahl sein', file=sys.stderr)
        sys.exit(1)

    try:
        with open(markdown_path, encoding='utf-8') as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        print(f'Fehler: Datei "{markdown_path}" nicht gefunden', file=sys.stderr)
        sys.exit(1)

    try:
        block  = extract_chapter_block(lines, kapitel)
        verses = {str(k): v for k, v in parse_verses(block).items()}
    except ValueError as e:
        print(f'Fehler: {e}', file=sys.stderr)
        sys.exit(1)

    if vers_str not in verses:
        available = ', '.join(sorted(verses.keys(), key=int))
        print(
            f'Fehler: Vers {vers_str} nicht in Kapitel {kapitel_str}.\n'
            f'Verfügbare Verse: {available}',
            file=sys.stderr,
        )
        sys.exit(1)

    text = verses[vers_str]
    print(f'V{vers_str} [len={len(text)}]:\n{repr(text)}\n')

    if suchstring is None:
        return

    pos = text.find(suchstring)
    if pos == -1:
        print(f'Suchstring nicht gefunden: {repr(suchstring)}')
        sys.exit(1)

    end = pos + len(suchstring)
    at_vers_end = end == len(text)

    ctx_l = max(0, pos - 15)
    ctx_r = min(len(text), end + 15)
    prefix = '...' if ctx_l > 0 else ''
    suffix = '...' if ctx_r < len(text) else ''
    context = text[ctx_l:ctx_r]

    print(f'Gefunden: von={pos}, bis={end if not at_vers_end else -1}')
    if at_vers_end:
        print('(Suchstring geht bis Versende → bis=-1 empfohlen)')
    print(f'Kontext:  {prefix}{repr(context)}{suffix}')


if __name__ == '__main__':
    main()
