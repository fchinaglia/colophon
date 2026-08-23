#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
Provenance icon: the quadrant with the classified text.

Reads kpi.json and writes icon.svg. No external dependencies: it writes the
SVG by hand, so it runs anywhere python3 runs.

Two axes, each running from AI to Me:
    horizontal  human share of the words   (100 - ai_lexical)
    vertical    human share of the ideas   (100 - ai_ideational)

The quadrant the point falls into gives it a name:
    human written      my words, my ideas
    machine polished   my ideas, the AI's words
    human edited       the AI's ideas, my words
    machine generated  the AI's words and ideas

Labels are English in every language, and there is deliberately no option to change
that: three of the four names are the classes of LLM-DetectAIve, and a translated
label stops pointing at the taxonomy it is quoting. build_note.py takes --lang, this
does not.

The point stays visible on top of the lit quadrant: the classification rounds
at 50%, the point shows how close to the boundary the text actually is.

Usage: python3 build_icon.py [kpi.json] [icon.svg]
"""
import json
import os
import sys

S, D = 124, 16                     # square side, label offset
X0, Y0 = 46, 32                    # top-left corner
XT, YT = 200, 16                   # tips of the two arrows
TINT, DOT = "#2a78d6", "#e34948"
GREY, BLACK, LINE = "#7a7975", "#16171a", "#8f9196"

NAMES = {(0, 0): ("machine", "polished"), (1, 0): ("human", "written"),
        (0, 1): ("machine", "generated"), (1, 1): ("human", "edited")}

# A halo in the page colour, painted under the glyphs: it keeps a label legible where
# the point passes close to it, which moving the label alone cannot always prevent.
HALO = 'paint-order="stroke" stroke="#fcfcfb" stroke-width="3" stroke-linejoin="round"'



def refuse_if_ungated(kpi, path="kpi.json"):
    """A caller that ignores an exit status must not get past this.

    measure.py refuses to write a measurement that failed its checks, so a kpi.json
    saying otherwise means someone kept an old one, or edited it. Publishing from it
    would put numbers on a page that the checks never passed.
    """
    if kpi.get("unexplained"):
        sys.exit(f"{path}: {len(kpi['unexplained'])} declared changes with no span and "
                 f"no reason ({', '.join(kpi['unexplained'])}) — run measure.py first")
    if kpi.get("integrity") is False:
        sys.exit(f"{path}: the reconstruction check failed — run measure.py first")


def icon(x, y):
    """x, y = human shares of words and ideas, in 0..1."""
    c = S / 2
    xr, yb = X0 + S, Y0 + S
    att = (1 if x >= .5 else 0, 0 if y >= .5 else 1)
    ax, ay = X0 + att[0] * c, Y0 + att[1] * c
    px, py = X0 + S * x, Y0 + S * (1 - y)

    p = ['<defs><marker id="f" markerWidth="8" markerHeight="8" refX="6.5" refY="4"'
         f' orient="auto"><path d="M0 0.5 L8 4 L0 7.5 z" fill="{LINE}"/></marker></defs>',
         f'<rect x="{X0}" y="{Y0}" width="{S}" height="{S}" fill="#fcfcfb"/>',
         f'<rect x="{ax}" y="{ay}" width="{c}" height="{c}" fill="{TINT}" fill-opacity=".13"/>',
         f'<path d="M{X0+c} {Y0} V{yb} M{X0} {Y0+c} H{xr} M{xr} {Y0} V{yb} M{X0} {Y0} H{xr}"'
         f' stroke="#d2d3d7" stroke-width="1.6" fill="none"/>',
         f'<line x1="{X0}" y1="{yb}" x2="{X0}" y2="{YT}" stroke="{LINE}" stroke-width="2"'
         f' marker-end="url(#f)"/>',
         f'<line x1="{X0}" y1="{yb}" x2="{XT}" y2="{yb}" stroke="{LINE}" stroke-width="2"'
         f' marker-end="url(#f)"/>']

    for k, (a, b) in NAMES.items():
        cx, cy = X0 + k[0] * c, Y0 + k[1] * c
        on = k == att
        col, pes = (BLACK, "700") if on else ("#9b9ca0", "500")
        # The label sits low in its cell, except in the lit one when the point would
        # land on it: then it moves to the top. The point is drawn last and cannot be
        # moved — it is the datum — so the label is what gives way. A text with a dot
        # through it reads as neither.
        base = cy + c - 22
        if on and py > cy + c / 2:
            base = cy + 18
        p.append(f'<text x="{cx+c/2}" y="{base}" text-anchor="middle" font-size="10.5"'
                 f' font-weight="{pes}" fill="{col}" letter-spacing="-.1" {HALO}>{a}</text>'
                 f'<text x="{cx+c/2}" y="{base+12}" text-anchor="middle" font-size="10.5"'
                 f' font-weight="{pes}" fill="{col}" letter-spacing="-.1" {HALO}>{b}</text>')

    p.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="6.5" fill="{DOT}" fill-opacity=".72"/>'
             f'<circle cx="{px:.1f}" cy="{py:.1f}" r="6.5" fill="none" stroke="{DOT}"'
             f' stroke-width="1.4" stroke-opacity=".9"/>')

    g = f'font-size="11.5" fill="{GREY}" letter-spacing=".06em"'
    n = f'font-size="11.5" font-weight="700" fill="{BLACK}"'
    p += [f'<text x="{X0+S/2}" y="{yb+D+4}" text-anchor="middle" {g}>words</text>',
          f'<text x="{X0-D}" y="{Y0+S/2}" text-anchor="middle" {g}'
          f' transform="rotate(-90 {X0-D} {Y0+S/2})">ideas</text>',
          f'<text x="{X0-D}" y="{yb+D+4}" text-anchor="middle" {n}>AI</text>',
          f'<text x="{XT-2}" y="{yb+D+4}" text-anchor="middle" {n}>Me</text>',
          f'<text x="{X0-D}" y="{YT+4}" text-anchor="middle" {n}>Me</text>']

    name = " ".join(NAMES[att])
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 215 200"'
            ' font-family="ui-sans-serif,-apple-system,sans-serif"'
            f' role="img" aria-label="Provenance: {name}. Human words {100*x:.0f}%,'
            f' human ideas {100*y:.0f}%.">' + "".join(p) + '</svg>'), name


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "kpi.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "icon.svg"
    if not os.path.exists(src):
        sys.exit(f"missing {src} — run measure.py first")
    k = json.load(open(src, encoding="utf-8"))
    refuse_if_ungated(k, src)
    x = 1 - k["ai_lexical"] / 100
    y = 1 - k["ai_ideational"] / 100
    svg, name = icon(x, y)
    open(out, "w", encoding="utf-8").write(svg)

    print(f"{out} — {name}")
    print(f"human words {100*x:.1f}%  ·  human ideas {100*y:.1f}%")
    margin = min(abs(x - .5), abs(y - .5)) * 100
    if margin < 5:
        print(f"  ! the point is {margin:.1f} points from the quadrant boundary: "
              f"the classification is fragile — publish the icon with the dot, "
              f"not the category name on its own")


if __name__ == "__main__":
    main()
