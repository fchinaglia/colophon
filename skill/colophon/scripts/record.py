#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
Append-only event register with a hash chain.

Every event is one JSON line. The chain binds each event to the previous one:
    h(n) = sha256( h(n-1) || canonical(event_n) )
Altering a past event invalidates every hash that follows it.

An event may hold strings, integers within +/-(2**53 - 1), booleans, null, lists and
objects with ASCII keys. Not floats. See violations() for why, and spec/canonical.md
for the rule in full.

THE RED LIST warns and does not refuse. See redlist_violations(): what may not be
recorded about a third party is a judgement, and the only part of it a machine can
decide is whether a string the author named in advance is present. That check is
machine-local — it depends on a file outside the case — so it lives outside
violations(), which spec/canonical.md §4 makes normative and a second implementation
has to reproduce exactly.

THE EVENT COMES FROM A FILE, and the file is written by the assistant's own file
tool — never by a shell heredoc. A JSON object on a command line puts the sequence
`{"` in it, and Claude Code's command analysis rejects that shape as `Contains brace
with quote character (expansion obfuscation)`. Measured: braces alone pass, quotes
alone pass, the two together do not, and it makes no difference whether they sit in
an argument or in the body of a heredoc. An event is recorded for every substantial
exchange, so the form that puts JSON on the command line earns a security warning
for every event of every case — and a warning that fires that often is one nobody
reads any more.

    python3 record.py --file ../.colophon-event.json

The path is outside the case folder, and this refuses one that is not. The closing
manifest covers the case folder: a scratch file left inside it is a file no manifest
covers, which `build_bundle.py` then withholds, and which sits in a sealed case as
the remains of the last event recorded.

`'<event json>'` still works. A sealed case carries its own copy of this script and
must keep behaving as it did on the day it was sealed.

Usage:
    python3 record.py --file <path>      the event, from a file outside the case
    python3 record.py '<event json>'     the same, on the command line
    python3 record.py --verify
    python3 record.py --root
"""
import hashlib
import json
import os
import re
import sys
import unicodedata
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(BASE, "events.jsonl")

GENESIS = "0" * 64


def canonical(obj) -> bytes:
    """Deterministic serialization: sorted keys, no whitespace, UTF-8."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


MAX_INT = 2 ** 53 - 1


def violations(obj, path="event") -> list:
    """What an event may not contain. An empty list means it can be recorded.

    The chain is checked by whoever reads it, and a reader outside Python cannot
    reproduce these bytes. After a JavaScript JSON.parse, 94.0 and 94 are the same
    value: the distinction is destroyed by parsing and cannot be recovered, so a
    register carrying one cannot be verified in a browser at all. Integers past
    2**53 are worse — JavaScript loses precision silently and returns a different
    number without saying so.

    None of this is repairable after the fact: the register is append-only, and
    reopening a case adds events rather than rewriting them. So the check belongs
    here, at the door, and it refuses rather than warning. The values that provoke
    it are descriptive payload — nothing reads them as numbers, the measurement of
    record is kpi.json — so write them as strings and nothing is lost.
    """
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not isinstance(k, str) or any(ord(c) > 0x7F for c in k):
                out.append(f"{path}: key {k!r} is not ASCII")
            out += violations(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += violations(v, f"{path}[{i}]")
    elif isinstance(obj, bool):
        pass                            # bool before int: it is a subclass of it
    elif isinstance(obj, float):
        out.append(f"{path}: {obj!r} is not an integer — write it as a string")
    elif isinstance(obj, int) and abs(obj) > MAX_INT:
        out.append(f"{path}: {obj} is beyond 2**53-1")
    return out


def redlist_path(case_dir=BASE):
    """Beside author.json, never in the case folder.

    A list of the names an author is protecting must not be committed, and .gitignore
    covers no such name; both case folders in this repository are committed, and
    cli/colophon.py writes .nojekyll precisely so that dot-paths are served. So it
    lives in the config directory, per case, named after case_uid — which is a public
    name, because the bundle is called after it.
    """
    uid = None
    for fn in ("case.json", "caso.json"):
        try:
            uid = json.load(open(os.path.join(case_dir, fn),
                                 encoding="utf-8")).get("case_uid")
        except (OSError, ValueError):
            continue
        if uid:
            break
    if not uid:
        return None
    home = os.environ.get("XDG_CONFIG_HOME") or os.path.join(
        os.path.expanduser("~"), ".config")
    return os.path.join(home, "colophon", "redlists", f"{uid}.txt")


def fold(s: str) -> str:
    """NFD, combining marks dropped, casefolded, whitespace collapsed.

    So that Peròtti matches Perotti and MARIO ROSSI matches Mario Rossi. It does not
    make `il Rossi` match `Mario Rossi`, and nothing here will: the variants are the
    author's knowledge, and getting them into the list is a conversation.
    """
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s.casefold())


def redlist(case_dir=BASE) -> list:
    p = redlist_path(case_dir)
    if not p or not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip() and not l.startswith("#")]


def redlist_violations(obj, entries, path="event") -> list:
    """Where a declared string appears in a payload. Warns; never refuses.

    Word-bounded, so that an entry `Rossi` does not fire on `Rossini`. The cost of the
    boundary is that `M.R.` and a misspelling are unreachable, and the cost of not
    having one is an author who learns to delete events to get past a false positive.

    The caller must never print what matched. Printing the name is the harm arriving
    through the guard.
    """
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            out += redlist_violations(v, entries, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += redlist_violations(v, entries, f"{path}[{i}]")
    elif isinstance(obj, str) and entries:
        hay = fold(obj)
        for e in entries:
            needle = fold(e)
            if needle and re.search(rf"(?<!\w){re.escape(needle)}(?!\w)", hay):
                out.append(path)
                break
    return out


def link(prev_hash: str, body: dict) -> str:
    return hashlib.sha256(prev_hash.encode("ascii") + canonical(body)).hexdigest()


def read() -> list:
    if not os.path.exists(LOG):
        return []
    with open(LOG, encoding="utf-8") as f:
        return [json.loads(r) for r in f if r.strip()]


def last_hash() -> str:
    rows = read()
    return rows[-1]["hash"] if rows else GENESIS


def append(event: dict) -> dict:
    bad = violations(event)
    if bad:
        raise ValueError("this event cannot be recorded:\n  " + "\n  ".join(bad))
    rows = read()
    body = dict(event)
    body["seq"] = len(rows)
    body.setdefault("ts", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    body["prev"] = last_hash()
    row = {**body, "hash": link(body["prev"], body)}
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return row


def verify() -> bool:
    prev = GENESIS
    rows = read()
    for i, r in enumerate(rows):
        body = {k: v for k, v in r.items() if k != "hash"}
        if body.get("prev") != prev:
            print(f"BROKEN at event {i}: prev does not match")
            return False
        if link(prev, body) != r["hash"]:
            print(f"BROKEN at event {i}: hash does not match")
            return False
        prev = r["hash"]
    print(f"chain intact — {len(rows)} events — root {prev[:16]}...")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "--verify":
        sys.exit(0 if verify() else 1)
    if sys.argv[1] == "--root":
        print(last_hash())
        sys.exit(0)
    if sys.argv[1] == "--file":
        if len(sys.argv) < 3:
            sys.exit("usage: python3 record.py --file <path outside the case folder>")
        src = os.path.abspath(sys.argv[2])
        try:
            inside = os.path.commonpath([src, BASE]) == BASE
        except ValueError:          # different drives on Windows: not inside
            inside = False
        if inside:
            sys.exit(f"not recorded — {sys.argv[2]} is inside the case folder, which "
                     "the closing manifest covers.\nA scratch file left there is a file "
                     "no manifest covers: build_bundle.py withholds\nit, and it stays in "
                     "the sealed case as the remains of the last event.\nWrite it beside "
                     "the folder instead — ../.colophon-event.json.")
        try:
            with open(src, encoding="utf-8") as f:
                event = json.load(f)
        except (OSError, ValueError) as exc:
            sys.exit(f"not recorded — {exc}")
    else:
        event = sys.argv[1]
    try:
        row = append(json.loads(event) if isinstance(event, str) else event)
    except ValueError as exc:
        print(f"not recorded — {exc}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(row, ensure_ascii=False))

    # After the write, on stderr, and naming nothing. The row above goes to stdout and
    # a caller may be consuming it; and this is a courtesy at the moment of the write,
    # not the guard. The guard is the review before the manifest, where every one of
    # these comes back — because a warning printed into a conversation while somebody
    # is writing an article is a warning nobody reads.
    # One line, however many fields matched — case 002's seq 68 has five, and five
    # lines of warning about one event is an interruption in a conversation where
    # somebody is writing an article. And a seq, not a JSON path: the path is not
    # actionable here by construction, because the whole design is that the decision
    # happens at the review; the seq is what that review prints back.
    if redlist_violations(row.get("payload") or {}, redlist(), "event.payload"):
        print(f"noted at seq {row['seq']} — something on your list is in what I just "
              f"recorded.\nNothing is blocked and nothing is lost. This comes back at "
              f"the last read\nbefore sealing, and can still be changed then.",
              file=sys.stderr)
