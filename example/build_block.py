#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
The disclosure block: the icon, the note and the technical line, as one object.

reference/disclosures.md specifies this block exactly — the icon on the left, the note
and the technical line stacked to its right, in a table, the icon in absolute units,
aligned to the top — and then nothing built it. It was assembled by hand from a
specification two hundred lines below the pointer that sent the reader there, and the
first render of case 001 came out full-width, body-size, stacked. The author's words:
*il disclaimer è enorme*. This script exists so that shape is not retyped.

It composes rather than reimplements. The category and the boundary margin come from
build_icon.py, the technical line from build_note.py — the same functions that produce
those parts elsewhere, so the block cannot disagree with the icon beside it or with the
page it links to.

Four of the five note lines are functions of kpi.json and are generated. The third is a
judgement about what the gap between the two axes means, so a default is generated from
its direction and --gap replaces it.

    python3 build_block.py                  an HTML fragment, styled, ready to paste
    python3 build_block.py --lang it        Italian wording
    python3 build_block.py --form svg       the whole block as one image
    python3 build_block.py --form text      plain lines, for a plain-text context
    python3 build_block.py --essential      the card form: drop the third and fifth lines
    python3 build_block.py --inline-icon    icon.svg inlined, for a fragment that travels
    python3 build_block.py -o block.html

THE QUADRANT NAME STAYS IN ENGLISH in every language: three of the four names are the
classes of LLM-DetectAIve, and a translated label stops pointing at the taxonomy it
quotes. Everything around it is in the language of the piece.

Usage: python3 build_block.py [--lang it|en] [--form html|svg|text] [-o OUT]
"""
import argparse
import json
import os
import sys

import build_icon
import build_note

GAP_MIN = 10.0          # below this the two axes say the same thing and line 3 is filler
EDGE = 5.0              # build_icon.py's own warning threshold

T = {
    "en": {
        "words": "words", "spans": "spans", "thousands": ",",
        "axes": "human words {x} · human ideas {y}",
        "gap_lex": "The model wrote more words than it brought ideas.",
        "gap_idea": "The ideas came from the model more than the words did.",
        "edge": ("the point is {m} points from the boundary: "
                 "read the point, not the label alone"),
        "stand": "I stand behind every statement in it.",
        "alt": "Provenance quadrant: {name}, human words {x}%, human ideas {y}%.",
    },
    "it": {
        "words": "parole", "spans": "span", "thousands": ".",
        "axes": "parole umane {x} · idee umane {y}",
        "gap_lex": "Il modello ha scritto più parole di quante idee abbia portato.",
        "gap_idea": "Le idee vengono dal modello più di quanto vengano le parole.",
        "edge": ("il punto è a {m} punti dal confine: "
                 "guardate il punto, non la sola etichetta"),
        "stand": "Di ogni affermazione rispondo io.",
        "alt": "Quadrante di provenienza: {name}, parole umane {x}%, idee umane {y}%.",
    },
}

CSS = """.colophon    { width: 100%; border-collapse: collapse; }
.colophon td { vertical-align: top; padding: 0; }
.colophon .icon { width: 56mm; padding-right: 8mm; }
.colophon .icon img { width: 54mm; }
.colophon .line { font-size: 9pt; line-height: 1.5; margin: 0 0 1.2mm; }
.colophon .line b { font-weight: 700; }
.colophon .technical { font-family: ui-monospace, monospace; font-size: 7pt;
               color: #7a7975; margin-top: 3.5mm; overflow-wrap: anywhere; }"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def note_lines(kpi, lang, gap=None, essential=False):
    """The five lines, in the order that is the argument: what this is, how much, what
    the gap means, how firm the classification is, who answers for it."""
    t = T[lang]
    xl = 100 - kpi["ai_lexical"]                       # human share of the words
    yi = 100 - kpi["ai_ideational"]                    # human share of the ideas
    name = " ".join(build_icon.NAMES[(1 if xl >= 50 else 0, 0 if yi >= 50 else 1)])

    # A thousands separator is not decoration: "1,096 parole" reads to an Italian
    # eye as one thousand and ninety-six thousandths. The word count is the first
    # number the reader meets, and it has to be the number the author means.
    def n(v):
        return f"{v:,}".replace(",", t["thousands"])

    head = f"{name} · {n(kpi['words'])} {t['words']}"
    if not essential:
        head += f" · {n(kpi['spans'])} {t['spans']}"
    lines = [(head, None),
             (t["axes"].format(x="\0", y="\1"), (f"{xl:.0f}", f"{yi:.0f}"))]

    if not essential:
        if gap is not None:
            if gap:
                lines.append((gap, None))
        elif abs(kpi["ai_lexical"] - kpi["ai_ideational"]) >= GAP_MIN:
            lines.append((t["gap_lex"] if kpi["ai_lexical"] > kpi["ai_ideational"]
                          else t["gap_idea"], None))

    margin = min(abs(xl - 50), abs(yi - 50))
    if margin < EDGE:
        lines.append((t["edge"].format(m=f"{margin:.0f}"), None))

    if not essential:
        lines.append((t["stand"], None))
    return lines, name, xl, yi


def render_line(text, bolds, bold_open, bold_close):
    """The two percentages are the only thing set in bold, in every form."""
    if not bolds:
        return esc(text)
    out = esc(text)
    for i, b in enumerate(bolds):
        out = out.replace(chr(i), bold_open + esc(b) + "%" + bold_close, 1)
    return out


def technical(log, lang, url, form, short_root):
    """build_note.py owns this line in every form: asking it, rather than reassembling
    it here, is what keeps the block from claiming a seal the line does not name."""
    return build_note.line(log=log, lang=lang, html=(form == "html"), url=url,
                           form="compact", short_root=short_root)


def as_html(lines, tech, icon_src, alt, style=True):
    body = "".join(
        f'      <p class="line">{render_line(txt, b, "<b>", "</b>")}</p>\n'
        for txt, b in lines)
    out = []
    if style:
        out.append(f"<style>\n{CSS}\n</style>\n")
    out.append('<table class="colophon">\n  <tr>\n'
               f'    <td class="icon">{icon_src}</td>\n'
               f'    <td class="body">\n{body}'
               f'      {tech}\n'
               '    </td>\n  </tr>\n</table>')
    return "".join(out)


def as_text(lines, tech):
    return "\n".join(render_line(t, b, "", "") for t, b in lines) + "\n" + tech


def as_svg(lines, tech, icon_svg, alt):
    """One image, for a post, a slide or a newsletter — anywhere that takes neither an
    HTML fragment nor an image and a caption that stay together."""
    x0, lead, top = 239, 17, 34
    inner = icon_svg.split(">", 1)[1].rsplit("</svg>", 1)[0]
    p = [f'<g transform="translate(0,0)">{inner}</g>']
    y = top
    for txt, bolds in lines:
        s = esc(txt)
        for i, b in enumerate(bolds or []):
            s = s.replace(chr(i), f'</tspan><tspan font-weight="700">{esc(b)}%</tspan>'
                                  f'<tspan>', 1)
        p.append(f'<text x="{x0}" y="{y}" font-size="12.5" fill="#16171a">'
                 f'<tspan>{s}</tspan></text>')
        y += lead
    y += 8
    for row in tech.split("\n"):
        p.append(f'<text x="{x0}" y="{y}" font-size="9" fill="#7a7975"'
                 f' font-family="ui-monospace,monospace">{esc(row)}</text>')
        y += 12
    # The root is sixty-four characters of monospace with nowhere to break, so the
    # canvas is measured against the longest row rather than guessed at: an SVG that
    # clips its own root prints a hash the reader cannot compare.
    note_w = max((len(t) for t, _ in lines), default=0) * 6.3
    tech_w = max((len(r) for r in tech.split("\n")), default=0) * 5.45
    w, h = int(x0 + max(note_w, tech_w) + 16), max(200, y + 6)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"'
            ' font-family="ui-sans-serif,-apple-system,sans-serif"'
            f' role="img" aria-label="{esc(alt)}">'
            f'<rect width="{w}" height="{h}" fill="#fcfcfb"/>'
            + "".join(p) + '</svg>')


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--kpi", default="kpi.json")
    p.add_argument("--log", default="events.jsonl")
    p.add_argument("--icon", default="icon.svg")
    p.add_argument("--lang", choices=sorted(T), default="en")
    p.add_argument("--form", choices=("html", "svg", "text"), default="html")
    p.add_argument("--essential", action="store_true",
                   help="the card form: the first two lines and the boundary warning")
    p.add_argument("--gap", default=None,
                   help="replace the sentence about the gap; empty string drops it")
    p.add_argument("--url", default=None, help="passed to build_note.py")
    p.add_argument("--short-root", action="store_true")
    p.add_argument("--inline-icon", action="store_true",
                   help="inline icon.svg, for a fragment that has to travel alone")
    p.add_argument("--no-style", action="store_true", help="emit the table without CSS")
    p.add_argument("-o", "--out", help="write here instead of stdout")
    a = p.parse_args(argv)

    if not os.path.exists(a.kpi):
        sys.exit(f"missing {a.kpi} — run measure.py first")
    kpi = json.load(open(a.kpi, encoding="utf-8"))
    build_icon.refuse_if_ungated(kpi, a.kpi)

    lines, name, xl, yi = note_lines(kpi, a.lang, a.gap, a.essential)
    alt = T[a.lang]["alt"].format(name=name, x=f"{xl:.0f}", y=f"{yi:.0f}")
    tech = technical(a.log, a.lang, a.url, a.form, a.short_root)

    if a.form == "svg":
        svg, _ = build_icon.icon(xl / 100, yi / 100)
        out = as_svg(lines, tech, svg, alt)
    elif a.form == "text":
        out = as_text(lines, tech)
    else:
        if a.inline_icon:
            src = open(a.icon, encoding="utf-8").read() if os.path.exists(a.icon) else ""
            if not src:
                sys.exit(f"missing {a.icon} — run build_icon.py first, "
                         f"or drop --inline-icon")
        else:
            src = f'<img src="{esc(a.icon)}" alt="{esc(alt)}">'
        out = as_html(lines, tech, src, alt, style=not a.no_style)

    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            f.write(out + "\n")
        print(f"{a.out} — {name}, {len(lines)} lines")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
