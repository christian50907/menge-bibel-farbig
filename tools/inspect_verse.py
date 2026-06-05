#!/usr/bin/env python3
"""inspect_verse.py — Verstext anzeigen und Zeichenposition finden

Verwendung:
    python inspect_verse.py <kapitel> <vers> [suchstring]

Argumente:
    kapitel     Kapitelnummer (lädt ai-tools/kap<N>_verses.json)
    vers        Versnummer
    suchstring  Optional: Substring, dessen von/bis-Position gesucht wird

Ausgabe:
    Verstext mit Länge; bei Suchstring zusätzlich Position und Kontext.

Beispiel:
    python .claude/skills/menge-bibel-farbig/scripts/inspect_verse.py 12 15
    python .claude/skills/menge-bibel-farbig/scripts/inspect_verse.py 12 15 "Herr unser Gott"
"""

import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print(
            f'Verwendung: {sys.argv[0]} <kapitel> <vers> [suchstring]',
            file=sys.stderr,
        )
        sys.exit(1)

    kapitel_str = args[0]
    vers_str = args[1]
    suchstring = ' '.join(args[2:]) if len(args) >= 3 else None

    json_path = f'ai-tools/kap{kapitel_str}_verses.json'

    try:
        raw = open(json_path, 'rb').read()
        for enc in ('utf-8-sig', 'utf-16', 'utf-8', 'cp1252'):
            try:
                verses = json.loads(raw.decode(enc))
                break
            except (UnicodeDecodeError, ValueError):
                continue
        else:
            print(f'Fehler: {json_path} konnte nicht gelesen werden', file=sys.stderr)
            sys.exit(1)
    except FileNotFoundError:
        print(
            f'Fehler: {json_path} nicht gefunden — zuerst parse_menge.py ausführen',
            file=sys.stderr,
        )
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
