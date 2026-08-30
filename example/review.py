#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
The last read, before the register is sealed.

A case travels as one file, handed to whoever the author hands it to. An embedded
record cannot be withdrawn, corrected, or told that it has been superseded, and the
register travels inside it whole. This is the moment — the only one — at which
anything in it can still be taken back for free.

It shows three lists, and they are not the same kind of thing:

  told        places the red list matched and the event was recorded anyway. Not
              "worth a look": things the author was already told about once.
  supplied    every human_contribution event, whole, and only that type. protocol.md
              marks the author's primary material U/U.
  repeated    every payload string that reproduces 30 or more characters of a draft.
              This is the register preserving what the text removed, and it is where
              three of the four events case 002 had to redact actually were.

Nothing else. A register carries five to six hundred strings and nobody reads that;
these three are thirty to forty-five lines and a person does.

NOT THE BRIEF, AND THAT IS A DECISION. This said for a long time that the second list
was "where a brief and a real case live", and it never was: the filter is on the event
type and a brief is its own type. The line is corrected rather than the filter widened,
and the reasons are worth having in one place.

The brief is not invisible here. The lists either side of it run over every non-meta
event, so a red-list match or a repeated draft passage inside a brief is raised exactly
like any other — only the "what you told me" list skips it.

What that list is for is the material that arrives one exchange at a time, once the case
is under way and nobody is deciding anything about disclosure any more. The brief is the
opposite: it is recorded at the one moment the question has just been put. Under
confidential nothing the author said is quoted anywhere in the case at all
(reference/people.md 1 and 2), so there is no verbatim brief to reread; under open the
words travel by a decision the author made minutes before it was written down. And it is
usually the longest single string in the register — putting it in the one list whose
whole value is being short enough to read is how thirty lines become a hundred and stop
being read at all.

    python3 review.py                       the three lists
    python3 review.py --set 37 payload.rimossi[0] "4 identifying details, removed"
    python3 review.py --keep 12 payload.note        accepted; stop raising it
    python3 review.py --done                        record that the review happened

WHERE IT SITS: after measure.py passes, before build_page.py. Not earlier — a failed
gate sends the author back to the register and makes any earlier read stale. Not
later — build_page.py prints the root into a manifest-covered page, and a rebuild
changes it. Not after the manifest, which is the last event: rebuilding then changes
the hash of the manifest itself. Not after the seal: the signature regenerates, the
timestamp does not.

WHAT A REWRITE COSTS: nothing that is measured. measure.py reads exactly one thing
from the register — payload.change — so a rewritten value leaves the coverage check
bit-identical. Every original timestamp survives, because record.py takes ts as given
when it is there. Events are never deleted, only their values rewritten: the count is
printed into a page the manifest covers.

Usage: python3 review.py [--set SEQ PATH TEXT | --keep SEQ PATH | --done] [--lang it]
"""
import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata

import record

SHINGLE = 30          # characters of a draft a payload string may repeat unremarked

T = {
 "en": {
  # One of these is not an offer. Three headers of equal weight say the three are the
  # same kind of thing, and two are "worth a look" while the first is a thing the author
  # was already told once. The typography is the difference between an alarm and an
  # invitation, and it is the only part of it a reader takes in before reading.
  "told": "YOU ASKED ME TO KEEP THESE OUT, AND THEY ARE STILL IN",
  "supplied": "what you told me, in your words, as the register has them",
  "repeated": "what the register still says and the article no longer does",
  "rest": "{n} more strings in this register are not shown: they are the method "
          "talking\n  about itself. These three lists are a filter, not the register.",
  "head": "  This is the last moment at which anything here can be taken out for free.\n"
          "  After the file is handed over, not at all.",
  "clean": "Nothing to change.",
  "none": "nothing was removed",
  "review": "The author read what this register says about people other than themselves, and about the text, before it was sealed.",
  "not_recorded": "which events, how many, or what kind of thing was removed. Naming them would narrow what a reader has to guess.",
  "some": "text was removed from some events and replaced with a statement of what "
          "the change did",
 },
 "it": {
  "told": "AVEVI CHIESTO DI TENERLI FUORI, E SONO ANCORA QUI",
  "supplied": "quello che mi hai detto, con le tue parole, come le tiene il registro",
  "repeated": "quello che il registro dice ancora e l'articolo non dice più",
  "rest": "Altre {n} stringhe di questo registro non sono mostrate: sono il metodo che "
          "parla\n  di sé. Questi tre elenchi sono un filtro, non il registro.",
  "head": "  Questo è l'ultimo momento in cui qualcosa può essere tolto senza costi.\n"
          "  Dopo che il file è stato consegnato, non più.",
  "clean": "Niente da cambiare.",
  "none": "non è stato tolto niente",
  "review": "L'autore ha letto quello che questo registro dice di persone diverse da sé, e del testo, prima che venisse sigillato.",
  "not_recorded": "quali eventi, quanti, o di che tipo fosse ciò che è stato tolto. Nominarli restringerebbe quello che un lettore deve indovinare.",
  "some": "del testo è stato tolto da alcuni eventi e sostituito con una dichiarazione "
          "di cosa la modifica ha fatto",
 },
}


def fold(s):
    return record.fold(s)


def strings(o, path):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from strings(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from strings(v, f"{path}[{i}]")
    elif isinstance(o, str):
        yield path, o


def draft_shingles(base):
    """Every window of the drafts, so a payload string can be tested against all of
    them at once. The drafts are on disk while the case is open; that is what makes
    this decidable at all."""
    d = os.path.join(base, "versions")
    if not os.path.isdir(d):
        return set()
    text = fold(" ".join(open(os.path.join(d, f), encoding="utf-8").read()
                         for f in sorted(os.listdir(d))
                         if os.path.isfile(os.path.join(d, f))))
    return {text[i:i + SHINGLE] for i in range(max(0, len(text) - SHINGLE + 1))}


def repeats_a_draft(s, shingles):
    n = fold(s)
    return len(n) >= SHINGLE and any(n[i:i + SHINGLE] in shingles
                                     for i in range(len(n) - SHINGLE + 1))


def marker_path(base):
    """That a rewrite happened, held outside the case and outside the register.

    In the register it would be an event before the one that reports it; in the case
    folder collect() might pack it. Here it is one empty file, read and removed by
    --done, so the author never has to remember what they did an hour ago.
    """
    p = record.redlist_path(base)
    return p[:-4] + ".changed" if p and p.endswith(".txt") else None


def kept_path(base):
    p = record.redlist_path(base)
    return p[:-4] + ".kept" if p and p.endswith(".txt") else None


def kept(base):
    p = kept_path(base)
    if not p or not os.path.exists(p):
        return set()
    with open(p, encoding="utf-8") as f:
        return {tuple(l.rstrip("\n").split("\t")) for l in f if l.strip()}


def digest(v):
    return hashlib.sha256(json.dumps(v, ensure_ascii=False,
                                     sort_keys=True).encode()).hexdigest()[:16]


def walk_get(obj, path):
    """`payload.rimossi[0]` -> the value. The path shape the lists print."""
    cur = obj
    for part in re.findall(r"[^.\[\]]+|\[\d+\]", path):
        cur = cur[int(part[1:-1])] if part.startswith("[") else cur[part]
    return cur


def walk_set(obj, path, value):
    parts = re.findall(r"[^.\[\]]+|\[\d+\]", path)
    cur = obj
    for part in parts[:-1]:
        cur = cur[int(part[1:-1])] if part.startswith("[") else cur[part]
    last = parts[-1]
    if last.startswith("["):
        cur[int(last[1:-1])] = value
    else:
        cur[last] = value


def rebuild(rows, base):
    """Re-record every event in order. record.py reassigns seq from position, takes ts
    as given, and recomputes prev and hash — so the dates survive, the numbering
    reproduces, and the chain closes over the new values."""
    open(record.LOG, "w", encoding="utf-8").close()
    for r in rows:
        record.append({k: v for k, v in r.items() if k not in ("seq", "prev", "hash")})


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--lang", choices=sorted(T), default="en")
    p.add_argument("--set", nargs=3, metavar=("SEQ", "PATH", "TEXT"),
                   help="replace one value and rebuild the chain")
    p.add_argument("--keep", nargs=2, metavar=("SEQ", "PATH"),
                   help="a red-list hit the author read and accepted")
    p.add_argument("--done", action="store_true",
                   help="record that the review happened, and what it did")
    a = p.parse_args(argv)
    base = record.BASE
    t = T[a.lang]

    if not os.path.exists(record.LOG):
        sys.exit(f"missing {record.LOG}")
    rows = record.read()
    if rows and record.is_manifest(rows[-1]):
        print("! the closing manifest is already recorded. Rebuilding the chain now\n"
              "  would change the hash of the manifest event itself. Reopen the case\n"
              "  instead, or run this before the manifest.", file=sys.stderr)
        return 1

    if a.keep:
        seq, path = int(a.keep[0]), a.keep[1]
        row = next((r for r in rows if r["seq"] == seq), None)
        if row is None:
            sys.exit(f"no event with seq {seq}")
        kp = kept_path(base)
        if not kp:
            sys.exit("this case has no case_uid, so it has no red list")
        os.makedirs(os.path.dirname(kp), mode=0o700, exist_ok=True)
        os.chmod(os.path.dirname(kp), 0o700)
        fd = os.open(kp, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(fd, "a", encoding="utf-8") as f:
            f.write(f"{seq}\t{path}\t{digest(walk_get(row, path))}\n")
        print(f"  accepted at seq {seq}. It will not be raised again unless the value "
              f"changes.")
        return 0

    if a.set:
        seq, path, text = int(a.set[0]), a.set[1], a.set[2]
        row = next((r for r in rows if r["seq"] == seq), None)
        if row is None:
            sys.exit(f"no event with seq {seq}")
        before = walk_get(row, path)
        if not isinstance(before, str):
            sys.exit(f"{path} is not a string — this rewrites values, it does not "
                     f"restructure events")
        walk_set(row, path, text)
        rebuild(rows, base)
        m = marker_path(base)
        if m:
            os.makedirs(os.path.dirname(m), mode=0o700, exist_ok=True)
            os.chmod(os.path.dirname(m), 0o700)
            os.close(os.open(m, os.O_WRONLY | os.O_CREAT, 0o600))
        print(f"  seq {seq} · {path} rewritten, {len(before)} characters replaced by "
              f"{len(text)}")
        print(f"  chain rebuilt from seq {seq} — new root {record.last_hash()}")
        print("  the measurement did not move: measure.py reads payload.change and "
              "nothing else")
        return 0

    if a.done:
        # Whether anything changed is not something the author should have to remember
        # and not something the register may hold before this event: --set leaves a
        # marker beside the red list, outside the case, and this reads it and removes it.
        m = marker_path(base)
        changed = bool(m and os.path.exists(m))
        # Recorded whether or not anything was removed, and in both regimes: if it were
        # conditional, its presence would itself be the leak.
        record.append({"type": "register_note", "actor": "system", "phase": "—",
                       "meta": True, "payload": {
                           "review": t["review"],
                           "outcome": t["some"] if changed else t["none"],
                           "not_recorded": t["not_recorded"]}})
        if changed:
            os.remove(m)
        print(f"  recorded. root {record.last_hash()}")
        return 0

    # ---- the three lists
    entries = record.redlist(base)
    accepted = kept(base)
    shingles = draft_shingles(base)
    told, supplied, repeated = [], [], []
    total = 0
    for r in rows:
        if r.get("meta"):
            continue
        pay = r.get("payload") or {}
        for path, s in strings(pay, "payload"):
            total += 1
        for path in record.redlist_violations(pay, entries, "payload"):
            if (str(r["seq"]), path, digest(walk_get(r, path))) not in accepted:
                told.append((r["seq"], r.get("ts", "")[:10], path))
        if r.get("type") == "human_contribution":
            supplied.append(r)
        for path, s in strings(pay, "payload"):
            if repeats_a_draft(s, shingles):
                repeated.append((r["seq"], path, s))

    shown = len(told) + len(repeated) + sum(
        1 for r in supplied for _ in strings(r.get("payload") or {}, "payload"))
    # Numbered across all three, contiguously. The author says "3 and 7"; finding the
    # path is the model's job, not theirs — SKILL.md's rule that they are never asked to
    # edit a file, applied to the review.
    n = 0
    print()
    print(t["head"])
    if told:
        print(f"\n{t['told']}\n")
        for seq, ts, path in told:
            n += 1
            print(f"  {n:>3}.  seq {seq:>3}  {ts}  {path}")
    if supplied:
        print(f"\n{t['supplied']}\n")
        for r in supplied:
            for path, s in strings(r.get("payload") or {}, "payload"):
                n += 1
                print(f"  {n:>3}.  seq {r['seq']:>3}  {path}: "
                      f"{s[:140]}{'…' if len(s) > 140 else ''}")
    if repeated:
        print(f"\n{t['repeated']}\n")
        for seq, path, s in repeated:
            n += 1
            print(f"  {n:>3}.  seq {seq:>3}  {path}: "
                  f"{s[:140]}{'…' if len(s) > 140 else ''}")
    if not (told or supplied or repeated):
        print(f"\n  {t['clean']}")
    print(f"\n  " + t["rest"].format(n=total - shown))
    return 0


if __name__ == "__main__":
    sys.exit(main())
