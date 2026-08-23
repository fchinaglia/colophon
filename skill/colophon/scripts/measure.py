#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
Measure the human and AI contribution over a span-annotated text.

Reads annotation.json (never an annotation buried in the code) and writes
spans.json and kpi.json.

Two independent attributions per span:
  lex  = who wrote the words that appear in the final text
  idea = whose content those words express
values: U (human), A (ai), UA (indivisible mixed)

Two mandatory checks:
  1. reconstruction — concatenating the spans reproduces the text
  2. coverage       — every change declared in the register has a span

Usage: python3 measure.py [annotation.json]
"""
import json
import os
import re
import sys
import unicodedata

ANN_FILE = sys.argv[1] if len(sys.argv) > 1 else "annotation.json"
LOG = "events.jsonl"

PHASES = ["research", "outline", "first_draft",
          "content_revision", "copy_revision", "titling"]
ORIGINS = ["U", "UA", "A"]


def norm(s):
    """Normalize for comparison: apostrophes, typographic accents, whitespace."""
    for a, b in (("’", "'"), ("“", '"'), ("”", '"'),
                 ("—", "-"), ("«", '"'), ("»", '"')):
        s = s.replace(a, b)
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip().lower()


def find(block, marker):
    """Position of the marker in the block, tolerant of accents and apostrophes."""
    nb, nm = norm(block), norm(marker)
    pos = nb.find(nm)
    if pos < 0:
        return None
    i = 0
    while i < len(block):
        if norm(block[:i + 1]) and len(norm(block[:i + 1])) > pos:
            break
        i += 1
    words = marker.split()[:4]
    pat = r"\s+".join(re.escape(w).replace("'", "['’]") for w in words)
    m = re.search(pat, block, re.IGNORECASE)
    return m.start() if m else i


def main():
    if not os.path.exists(ANN_FILE):
        sys.exit(f"missing {ANN_FILE}")
    ann = json.load(open(ANN_FILE, encoding="utf-8"))
    src = ann["source"]
    excluded = set(ann.get("excluded", []))
    # Declared exceptions to the coverage check: {"R12": "superseded by R19"}. A
    # legitimate orphan is common — the protocol tells you to record a diffuse
    # intervention as an event and leave the attributions alone, which produces one by
    # design — so the check cannot be a blind gate. What it can require is that the
    # author say which ones they mean, in the annotated file, where a reader sees it.
    explained = {str(k): v for k, v in (ann.get("explained") or {}).items()}
    mapping = {int(k): v for k, v in ann["blocks"].items()}

    text = open(src, encoding="utf-8").read()
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    spans, errors = [], []

    for i, b in enumerate(blocks):
        if i in excluded:
            continue
        a = mapping.get(i)
        if a is None:
            errors.append(f"block {i} not annotated")
            continue
        pieces = []
        if isinstance(a, dict):
            pieces.append((b, a))
        else:
            cuts = []
            for m in a[1:]:
                p = find(b, m["from"])
                if p is None:
                    errors.append(f"block {i}: marker not found: {m['from'][:40]}")
                    continue
                # A marker that occurs more than once silently moves the span
                # boundary when the text is edited, producing a wrong span that
                # still passes both checks. Refuse it instead.
                if norm(b).count(norm(m["from"])) > 1:
                    errors.append(
                        f"block {i}: marker is ambiguous, it occurs "
                        f"{norm(b).count(norm(m['from']))} times: {m['from'][:40]}")
                    continue
                cuts.append(p)
            if cuts != sorted(cuts):
                errors.append(f"block {i}: markers are out of order, spans would overlap")
                cuts = sorted(cuts)
            edges = [0] + cuts + [len(b)]
            for k in range(len(edges) - 1):
                seg = b[edges[k]:edges[k + 1]].strip()
                if seg:
                    pieces.append((seg, a[k]))
        for seg, meta in pieces:
            spans.append({
                "block": i, "text": seg, "words": len(seg.split()),
                "lex": meta["lex"], "idea": meta["idea"], "phase": meta["phase"],
                "event": meta.get("event"), "note": meta.get("note", ""),
                "events": ([meta["event"]] if isinstance(meta.get("event"), str)
                           else list(meta.get("event") or [])),
                "heading": b.startswith("#")})

    # --- check 1: reconstruction ---
    rebuilt = norm(" ".join(s["text"] for s in spans))
    original = norm(" ".join(b for i, b in enumerate(blocks) if i not in excluded))
    ok = rebuilt == original
    # An empty span set must never pass. Comparing nothing with nothing is not
    # evidence of anything, and it is exactly what happens when the source file
    # has been truncated: the check would report OK on a destroyed text.
    if not spans or not original:
        ok = False
        errors.append("nothing to reconstruct: the span set or the source text is empty")

    # --- check 2: coverage ---
    orphans = []
    if os.path.exists(LOG):
        declared = set()
        for r in open(LOG, encoding="utf-8"):
            if r.strip():
                d = json.loads(r).get("payload", {}).get("change")
                if d:
                    declared.add(d)
        present = {e for s in spans for e in s["events"]}
        orphans = sorted(declared - present)
    unexplained = [o for o in orphans if not explained.get(o)]
    # An explanation for something that is not an orphan is stale: it points at an
    # edit that has since been annotated, and a stale exception hides the next one.
    stale = sorted(k for k in explained if k not in orphans)

    json.dump(spans, open("spans.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    tot = sum(s["words"] for s in spans) or 1

    def share(key, sel=None):
        ss = [s for s in spans if sel is None or sel(s)]
        t = sum(s["words"] for s in ss) or 1
        return {k: sum(s["words"] for s in ss if s[key] == k) / t for k in ORIGINS}, t

    lex_q, _ = share("lex")
    idea_q, _ = share("idea")
    ai_lex = lex_q["A"] + lex_q["UA"] / 2
    ai_idea = idea_q["A"] + idea_q["UA"] / 2

    print(f"reconstruction: {'OK' if ok else 'FAILED'}")
    for e in errors:
        print("  !", e)
    if orphans:
        done = len(orphans) - len(unexplained)
        print(f"  coverage: {len(orphans)} declared changes without a span, "
              f"{done} explained, {len(unexplained)} not")
    for k in stale:
        print(f"  ! stale exception: {k} is not an unmatched change — it has a span, "
              f"or the register never declared it. Remove it from \"explained\"")
    if unexplained:
        print(f"  ! no span and no explanation: {', '.join(unexplained)}")
        print('    annotate them, or say why in "explained" in ' + ANN_FILE +
              ': {"R12": "superseded by R19"}')
    print(f"spans {len(spans)} · words {tot}\n")
    print(f"AI lexical    {100*ai_lex:5.1f}%   (A {100*lex_q['A']:.1f} · "
          f"UA {100*lex_q['UA']:.1f} · U {100*lex_q['U']:.1f})")
    print(f"AI ideational {100*ai_idea:5.1f}%   (A {100*idea_q['A']:.1f} · "
          f"UA {100*idea_q['UA']:.1f} · U {100*idea_q['U']:.1f})\n")

    print(f"{'phase':22}{'words':>8}{'AI share':>10}")
    by_phase = {}
    for f in PHASES:
        q, t = share("lex", lambda s, ff=f: s["phase"] == ff)
        if t and any(s["phase"] == f for s in spans):
            v = q["A"] + q["UA"] / 2
            by_phase[f] = {"words": t, "ai": round(100 * v, 1)}
            print(f"{f:22}{t:>8}{100*v:>9.1f}%")

    json.dump({"words": tot, "spans": len(spans), "integrity": ok,
               "orphans": orphans,
               "explained": {k: v for k, v in explained.items() if k in orphans},
               "unexplained": unexplained,
               "ai_lexical": round(100 * ai_lex, 1),
               "ai_ideational": round(100 * ai_idea, 1),
               "lexical": {k: round(100 * v, 1) for k, v in lex_q.items()},
               "ideational": {k: round(100 * v, 1) for k, v in idea_q.items()},
               "by_phase": by_phase},
              open("kpi.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # Both checks gate the numbers, which is what the skill and the paper have always
    # said and what the script did not do: an unexplained orphan is the signature of
    # the incident this check was written for — an annotation that fell behind while
    # the reconstruction stayed green.
    if not ok or unexplained or stale:
        sys.exit(1)


if __name__ == "__main__":
    main()
