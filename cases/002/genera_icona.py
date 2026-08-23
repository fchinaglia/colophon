#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
Icona di provenienza: il quadrante con il testo classificato.

Legge misura_kpi.json e produce icona.svg. Nessuna dipendenza esterna:
scrive SVG a mano, così gira ovunque giri python3.

Due assi, ciascuno da AI a Me:
    orizzontale  quota umana delle parole      (100 - ai_lessicale)
    verticale    quota umana delle idee        (100 - ai_ideativa)

Il quadrante in cui cade il punto dà il nome:
    human written      parole mie, idee mie
    machine polished   idee mie, parole dell'AI
    human edited       idee dell'AI, parole mie
    machine generated  parole e idee dell'AI

Il punto resta visibile sopra il quadrante acceso: la classificazione
arrotonda al 50%, il punto mostra quanto si è vicini al bordo.

Uso: python3 genera_icona.py [misura_kpi.json] [icona.svg]
"""
import json
import os
import sys

S, D = 124, 16                     # lato del quadrato, distanza delle etichette
X0, Y0 = 46, 32                    # angolo in alto a sinistra
XT, YT = 200, 16                   # punte delle due frecce
TINTA, PUNTO = "#2a78d6", "#e34948"
GRIGIO, NERO, LINEA = "#7a7975", "#16171a", "#8f9196"

NOMI = {(0, 0): ("machine", "polished"), (1, 0): ("human", "written"),
        (0, 1): ("machine", "generated"), (1, 1): ("human", "edited")}


def icona(x, y):
    """x, y = quote umane di parole e idee, in 0..1."""
    c = S / 2
    xr, yb = X0 + S, Y0 + S
    att = (1 if x >= .5 else 0, 0 if y >= .5 else 1)
    ax, ay = X0 + att[0] * c, Y0 + att[1] * c
    px, py = X0 + S * x, Y0 + S * (1 - y)

    p = ['<defs><marker id="f" markerWidth="8" markerHeight="8" refX="6.5" refY="4"'
         f' orient="auto"><path d="M0 0.5 L8 4 L0 7.5 z" fill="{LINEA}"/></marker></defs>',
         f'<rect x="{X0}" y="{Y0}" width="{S}" height="{S}" fill="#fcfcfb"/>',
         f'<rect x="{ax}" y="{ay}" width="{c}" height="{c}" fill="{TINTA}" fill-opacity=".13"/>',
         f'<path d="M{X0+c} {Y0} V{yb} M{X0} {Y0+c} H{xr} M{xr} {Y0} V{yb} M{X0} {Y0} H{xr}"'
         f' stroke="#d2d3d7" stroke-width="1.6" fill="none"/>',
         f'<line x1="{X0}" y1="{yb}" x2="{X0}" y2="{YT}" stroke="{LINEA}" stroke-width="2"'
         f' marker-end="url(#f)"/>',
         f'<line x1="{X0}" y1="{yb}" x2="{XT}" y2="{yb}" stroke="{LINEA}" stroke-width="2"'
         f' marker-end="url(#f)"/>']

    for k, (a, b) in NOMI.items():
        cx, cy = X0 + k[0] * c, Y0 + k[1] * c
        on = k == att
        col, pes = (NERO, "700") if on else ("#9b9ca0", "500")
        base = cy + c - 22
        p.append(f'<text x="{cx+c/2}" y="{base}" text-anchor="middle" font-size="10.5"'
                 f' font-weight="{pes}" fill="{col}" letter-spacing="-.1">{a}</text>'
                 f'<text x="{cx+c/2}" y="{base+12}" text-anchor="middle" font-size="10.5"'
                 f' font-weight="{pes}" fill="{col}" letter-spacing="-.1">{b}</text>')

    p.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="6.5" fill="{PUNTO}" fill-opacity=".72"/>'
             f'<circle cx="{px:.1f}" cy="{py:.1f}" r="6.5" fill="none" stroke="{PUNTO}"'
             f' stroke-width="1.4" stroke-opacity=".9"/>')

    g = f'font-size="11.5" fill="{GRIGIO}" letter-spacing=".06em"'
    n = f'font-size="11.5" font-weight="700" fill="{NERO}"'
    p += [f'<text x="{X0+S/2}" y="{yb+D+4}" text-anchor="middle" {g}>words</text>',
          f'<text x="{X0-D}" y="{Y0+S/2}" text-anchor="middle" {g}'
          f' transform="rotate(-90 {X0-D} {Y0+S/2})">ideas</text>',
          f'<text x="{X0-D}" y="{yb+D+4}" text-anchor="middle" {n}>AI</text>',
          f'<text x="{XT-2}" y="{yb+D+4}" text-anchor="middle" {n}>Me</text>',
          f'<text x="{X0-D}" y="{YT+4}" text-anchor="middle" {n}>Me</text>']

    nome = " ".join(NOMI[att])
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 215 200"'
            ' font-family="ui-sans-serif,-apple-system,sans-serif"'
            f' role="img" aria-label="Provenienza: {nome}. Parole umane {100*x:.0f}%,'
            f' idee umane {100*y:.0f}%.">' + "".join(p) + '</svg>'), nome


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "misura_kpi.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "icona.svg"
    if not os.path.exists(src):
        sys.exit(f"manca {src} — esegui prima misura.py")
    k = json.load(open(src, encoding="utf-8"))
    x = 1 - k["ai_lessicale"] / 100
    y = 1 - k["ai_ideativa"] / 100
    svg, nome = icona(x, y)
    open(out, "w", encoding="utf-8").write(svg)

    print(f"{out} — {nome}")
    print(f"parole umane {100*x:.1f}%  ·  idee umane {100*y:.1f}%")
    margine = min(abs(x - .5), abs(y - .5)) * 100
    if margine < 5:
        print(f"  ! il punto dista {margine:.1f} punti dal bordo del quadrante: "
              f"la classificazione è fragile, pubblica l'icona con il punto e non "
              f"il solo nome della categoria")


if __name__ == "__main__":
    main()
