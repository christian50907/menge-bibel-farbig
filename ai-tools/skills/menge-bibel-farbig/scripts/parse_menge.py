#!/usr/bin/env python3
"""parse_menge.py — Menge-Bibel Kapitel-Parser

Extrahiert die bereinigten Verstexte eines Kapitels aus dem Menge-Bibel-Markdown.

Verwendung:
    python parse_menge.py <markdown_datei> <kapitel_nummer>

Ausgabe (stdout):
    JSON-Objekt { "1": "Verstext...", "2": "...", ... }
    Positionen von/bis in Annotationen beziehen sich auf diese bereinigten Texte.
"""

import re
import json
import sys

FN_REGEX = re.compile(
    r'<sup\s+title=(["\'])([^"\']*)\1>\s*(?:&#x[\da-fA-F]+;|✲)\s*</sup>'
)
CHAPTER_MARKER = re.compile(r'^__(\d+)__\s*$')
HEADING_LINE = re.compile(r'^#{1,6}\s+')


def extract_chapter_block(lines: list, chapter: int) -> list:
    """Gibt die Zeilen zurück, die zum angegebenen Kapitel gehören.

    Vorgelagerte Überschriften (zwischen letztem Fließtext und __N__) werden
    dem neuen Kapitel zugerechnet. Nachgelagerte Überschriften (am Ende des
    Blocks) werden abgeschnitten, da sie zum nächsten Kapitel gehören.
    """
    block = []
    pending_headings = []
    in_chapter = False

    for line in lines:
        stripped = line.strip()
        m = CHAPTER_MARKER.match(stripped)

        if not in_chapter:
            if m:
                if int(m.group(1)) == chapter:
                    block.extend(pending_headings)
                    block.append(line)
                    in_chapter = True
                else:
                    pending_headings = []
            elif HEADING_LINE.match(stripped):
                pending_headings.append(line)
            elif stripped:
                pending_headings = []
        else:
            if m and int(m.group(1)) != chapter:
                break
            block.append(line)

    if not block:
        raise ValueError(f'Kapitel {chapter} nicht gefunden')

    # Nachgelagerte Überschriften und Leerzeilen abschneiden
    end = len(block) - 1
    while end >= 0:
        s = block[end].strip()
        if not s or HEADING_LINE.match(s):
            end -= 1
        else:
            break
    return block[:end + 1]


def parse_verses(block: list) -> dict:
    """Gibt {versnr: bereinigter_text} zurück.

    Bereinigt bedeutet: Fußnoten entfernt, Überschriften entfernt,
    Whitespace normalisiert. Positionen von/bis beziehen sich auf diese Texte.
    """
    raw = '\n'.join(block)

    # Fußnoten entfernen
    raw = FN_REGEX.sub('', raw)
    raw = re.sub(r'&#x[\da-fA-F]+;', '', raw)

    # Überschriftszeilen entfernen
    lines = [l for l in raw.split('\n') if not HEADING_LINE.match(l.strip())]
    raw = ' '.join(lines)
    raw = re.sub(r'\s+', ' ', raw).strip()

    # Nach Versmarkern aufteilen
    parts = re.split(r'<sup>(\d+)</sup>', raw)
    verses = {}
    for i in range(1, len(parts) - 1, 2):
        nr = int(parts[i])
        text = re.sub(r'\s+', ' ', parts[i + 1]).strip()
        if text:
            verses[nr] = text
    return verses


def main():
    if len(sys.argv) != 3:
        print(f'Verwendung: {sys.argv[0]} <markdown_datei> <kapitel_nummer>',
              file=sys.stderr)
        sys.exit(1)

    path, chapter_str = sys.argv[1], sys.argv[2]
    try:
        chapter = int(chapter_str)
    except ValueError:
        print('Fehler: Kapitelnummer muss eine ganze Zahl sein', file=sys.stderr)
        sys.exit(1)

    try:
        with open(path, encoding='utf-8') as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        print(f'Fehler: Datei "{path}" nicht gefunden', file=sys.stderr)
        sys.exit(1)

    try:
        block = extract_chapter_block(lines, chapter)
        verses = parse_verses(block)
    except ValueError as e:
        print(f'Fehler: {e}', file=sys.stderr)
        sys.exit(1)

    print(json.dumps(verses, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
