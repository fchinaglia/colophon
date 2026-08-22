#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
Misura del contributo umano/AI su un testo annotato span per span.

Legge annotazione.json (mai annotazione dentro il codice) e produce
misura_span.json e misura_kpi.json.

Due attribuzioni indipendenti per span:
  lex  = chi ha scritto le parole che si leggono nel testo finale
  idea = da chi viene il contenuto che quelle parole esprimono
valori: U (umano), A (ai), UA (misto inscindibile)

Due controlli obbligatori:
  1. ricostruzione — la concatenazione degli span riproduce il testo
  2. copertura     — ogni modifica dichiarata nel registro ha uno span

Uso: python3 misura.py [annotazione.json]
"""
import json
import os
import re
import sys
import unicodedata

ANN_FILE = sys.argv[1] if len(sys.argv) > 1 else "annotazione.json"
LOG = "eventi.jsonl"

FASI = ["ricerca", "struttura", "prima_stesura",
        "revisione_contenuto", "revisione_forma", "titolazione"]
ORIG = ["U", "UA", "A"]


def norm(s):
    """Normalizza per il confronto: apostrofi, accenti tipografici, spazi."""
    for a, b in (("’", "'"), ("“", '"'), ("”", '"'),
                 ("—", "-"), ("«", '"'), ("»", '"')):
        s = s.replace(a, b)
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip().lower()


def trova(blocco, marcatore):
    """Posizione del marcatore nel blocco, tollerante ad accenti e apostrofi."""
    nb, nm = norm(blocco), norm(marcatore)
    pos = nb.find(nm)
    if pos < 0:
        return None
    # rimappa la posizione normalizzata su quella originale
    conta, i = 0, 0
    while i < len(blocco):
        if norm(blocco[:i + 1]) and len(norm(blocco[:i + 1])) > pos:
            break
        i += 1
    # fallback robusto: ricerca parola per parola
    parole = marcatore.split()[:4]
    pat = r"\s+".join(re.escape(p).replace("'", "['’]") for p in parole)
    pat = (pat.replace("e", "[eèé]").replace("E", "[EÈ]")
              .replace("a", "[aà]").replace("o", "[oò]")
              .replace("u", "[uù]").replace("i", "[iì]"))
    m = re.search(pat, blocco, re.IGNORECASE)
    return m.start() if m else i


def main():
    if not os.path.exists(ANN_FILE):
        sys.exit(f"manca {ANN_FILE}")
    ann = json.load(open(ANN_FILE, encoding="utf-8"))
    src = ann["sorgente"]
    esclusi = set(ann.get("esclusi", []))
    mappa = {int(k): v for k, v in ann["blocchi"].items()}

    testo = open(src, encoding="utf-8").read()
    blocks = [b.strip() for b in testo.split("\n\n") if b.strip()]
    spans, errori = [], []

    for i, b in enumerate(blocks):
        if i in esclusi:
            continue
        a = mappa.get(i)
        if a is None:
            errori.append(f"blocco {i} non annotato")
            continue
        pezzi = []
        if isinstance(a, dict):
            pezzi.append((b, a))
        else:
            tagli = []
            for m in a[1:]:
                p = trova(b, m["da"])
                if p is None:
                    errori.append(f"blocco {i}: marcatore non trovato «{m['da'][:40]}»")
                else:
                    tagli.append(p)
            bordi = [0] + tagli + [len(b)]
            for k in range(len(bordi) - 1):
                seg = b[bordi[k]:bordi[k + 1]].strip()
                if seg:
                    pezzi.append((seg, a[k]))
        for seg, meta in pezzi:
            spans.append({
                "blocco": i, "testo": seg, "parole": len(seg.split()),
                "lex": meta["lex"], "idea": meta["idea"], "fase": meta["fase"],
                "evento": meta.get("evento"), "nota": meta.get("nota", ""),
                "heading": b.startswith("#")})

    # --- controllo 1: ricostruzione ---
    ric = norm(" ".join(s["testo"] for s in spans))
    orig = norm(" ".join(b for i, b in enumerate(blocks) if i not in esclusi))
    ok = ric == orig

    # --- controllo 2: copertura ---
    orfane = []
    if os.path.exists(LOG):
        dich = set()
        for r in open(LOG, encoding="utf-8"):
            if r.strip():
                d = json.loads(r).get("payload", {}).get("modifica")
                if d:
                    dich.add(d)
        pres = {s["evento"] for s in spans if s["evento"]}
        orfane = sorted(dich - pres)

    json.dump(spans, open("misura_span.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    tot = sum(s["parole"] for s in spans) or 1

    def quota(chiave, sel=None):
        ss = [s for s in spans if sel is None or sel(s)]
        t = sum(s["parole"] for s in ss) or 1
        return {k: sum(s["parole"] for s in ss if s[chiave] == k) / t for k in ORIG}, t

    lex_q, _ = quota("lex")
    idea_q, _ = quota("idea")
    ai_lex = lex_q["A"] + lex_q["UA"] / 2
    ai_idea = idea_q["A"] + idea_q["UA"] / 2

    print(f"ricostruzione: {'OK' if ok else 'FALLITA'}")
    for e in errori:
        print("  !", e)
    if orfane:
        print(f"  copertura: {len(orfane)} modifiche dichiarate senza span "
              f"(verifica che siano state sostituite o diffuse): {', '.join(orfane)}")
    print(f"span {len(spans)} · parole {tot}\n")
    print(f"AI lessicale  {100*ai_lex:5.1f}%   (A {100*lex_q['A']:.1f} · "
          f"UA {100*lex_q['UA']:.1f} · U {100*lex_q['U']:.1f})")
    print(f"AI ideativa   {100*ai_idea:5.1f}%   (A {100*idea_q['A']:.1f} · "
          f"UA {100*idea_q['UA']:.1f} · U {100*idea_q['U']:.1f})\n")

    print(f"{'fase':22}{'parole':>8}{'quota AI':>10}")
    per_fase = {}
    for f in FASI:
        q, t = quota("lex", lambda s, ff=f: s["fase"] == ff)
        if t and any(s["fase"] == f for s in spans):
            v = q["A"] + q["UA"] / 2
            per_fase[f] = {"parole": t, "ai": round(100 * v, 1)}
            print(f"{f:22}{t:>8}{100*v:>9.1f}%")

    json.dump({"parole": tot, "span": len(spans), "integrita": ok,
               "orfane": orfane,
               "ai_lessicale": round(100 * ai_lex, 1),
               "ai_ideativa": round(100 * ai_idea, 1),
               "lessicale": {k: round(100 * v, 1) for k, v in lex_q.items()},
               "ideativa": {k: round(100 * v, 1) for k, v in idea_q.items()},
               "per_fase": per_fase},
              open("misura_kpi.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
