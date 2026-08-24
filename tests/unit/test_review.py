# SPDX-License-Identifier: MIT
"""review.py — the last read before the register is sealed.

The register travels whole inside a bundle handed to other people, and a copy cannot be
withdrawn. This is the only moment at which anything in it can still be taken back for
free, and every assertion here defends either that the moment works or that it costs
nothing when there is nothing to take back.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

import pytest

from conftest import ROOT, SCRIPTS, run

ONLY = {"record.py", "review.py", "measure.py", "build_icon.py"}


@pytest.fixture
def case(workspace, tmp_path):
    wd = workspace("example", only=ONLY)
    c = json.loads((wd / "case.json").read_text(encoding="utf-8"))
    c["case_uid"] = "a-case"
    (wd / "case.json").write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")
    return wd


def cfg(tmp_path, *entries):
    d = tmp_path / "cfg" / "colophon" / "redlists"
    d.mkdir(parents=True, exist_ok=True)
    if entries:
        (d / "a-case.txt").write_text("\n".join(entries), encoding="utf-8")
    return {"XDG_CONFIG_HOME": str(tmp_path / "cfg")}


def note(wd, text, env=None, typ="register_note"):
    return run(wd, "record.py", json.dumps(
        {"type": typ, "actor": "ai", "phase": "—", "payload": {"note": text}},
        ensure_ascii=False), env=env)


def test_it_shows_what_the_author_supplied_and_what_repeats_the_article(case, tmp_path):
    """Two of the three lists. The third needs a red list."""
    src = (case / "versions" / "post.md").read_text(encoding="utf-8")
    piece = " ".join(src.split()[8:20])
    assert note(case, piece, typ="human_contribution").returncode == 0
    r = run(case, "review.py", env=cfg(tmp_path))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "what you told me, in your words" in r.stdout
    assert "the article no longer does" in r.stdout
    assert piece[:40] in r.stdout


def test_the_told_list_never_prints_what_matched(case, tmp_path):
    """It is the list the red list feeds, and printing the name is the harm arriving
    through the guard — twice over, since it already went into the register."""
    env = cfg(tmp_path, "Mario Rossi")
    assert note(case, "parlato con Mario Rossi", env=env).returncode == 0
    r = run(case, "review.py", env=env)
    assert "YOU ASKED ME TO KEEP THESE OUT" in r.stdout
    assert "payload.note" in r.stdout
    assert "Mario Rossi" not in r.stdout.split("what the register still says")[0]


def test_a_rewrite_moves_no_number_and_loses_no_date(case, tmp_path):
    """measure.py reads payload.change and nothing else, so a rewritten value leaves the
    coverage check bit-identical. And record.py takes ts as given when it is there."""
    env = cfg(tmp_path)
    assert note(case, "una nota qualunque").returncode == 0
    before_rows = [json.loads(l) for l in
                   (case / "events.jsonl").read_text(encoding="utf-8").splitlines() if l]
    assert run(case, "measure.py").returncode == 0
    kpi_before = (case / "kpi.json").read_text(encoding="utf-8")

    seq = before_rows[-1]["seq"]
    r = run(case, "review.py", "--set", str(seq), "payload.note", "sostituita", env=env)
    assert r.returncode == 0, r.stdout + r.stderr

    after_rows = [json.loads(l) for l in
                  (case / "events.jsonl").read_text(encoding="utf-8").splitlines() if l]
    assert len(after_rows) == len(before_rows), "an event was deleted"
    assert [x["seq"] for x in after_rows] == [x["seq"] for x in before_rows]
    assert [x["ts"] for x in after_rows] == [x["ts"] for x in before_rows], "a date moved"
    assert after_rows[-1]["payload"]["note"] == "sostituita"
    assert run(case, "record.py", "--verify").returncode == 0

    assert run(case, "measure.py").returncode == 0
    assert (case / "kpi.json").read_text(encoding="utf-8") == kpi_before, \
        "the measurement moved"


def test_it_refuses_once_the_manifest_is_recorded(case, tmp_path):
    """The manifest is the last event. Rebuilding after it changes the hash of the
    manifest event itself, and the seal after that attests bytes that are gone."""
    ev = {"type": "status", "actor": "system", "phase": "—", "meta": True,
          "payload": {"closing": "MANIFEST", "algorithm": "sha256", "sha256": {"a": "b"}}}
    assert run(case, "record.py", json.dumps(ev)).returncode == 0
    r = run(case, "review.py", env=cfg(tmp_path))
    assert r.returncode == 1
    assert "already recorded" in r.stderr and "Reopen the case" in r.stderr


def test_done_records_always_and_names_nothing(case, tmp_path):
    """If the event were conditional its presence would itself be the leak. And case 002
    recorded which events it had redacted, which is a map for whoever wants to guess."""
    env = cfg(tmp_path)
    assert run(case, "review.py", "--done", env=env).returncode == 0
    last = json.loads((case / "events.jsonl").read_text(encoding="utf-8").splitlines()[-1])
    p = last["payload"]
    assert last["meta"] is True and "review" in p
    assert p["outcome"].startswith("nothing was removed")
    assert "not_recorded" in p
    blob = json.dumps(last, ensure_ascii=False)
    for leak in ("seq", "events", "root", "sha256"):
        assert f'"{leak}":' not in blob.replace('"seq":', "", 1), \
            f"the review event names {leak}"


def test_done_says_so_when_something_was_removed(case, tmp_path):
    env = cfg(tmp_path)
    assert note(case, "da riscrivere").returncode == 0
    seq = json.loads((case / "events.jsonl").read_text(encoding="utf-8")
                     .splitlines()[-1])["seq"]
    assert run(case, "review.py", "--set", str(seq), "payload.note", "x", env=env).returncode == 0
    assert run(case, "review.py", "--done", env=env).returncode == 0
    last = json.loads((case / "events.jsonl").read_text(encoding="utf-8").splitlines()[-1])
    assert last["payload"]["outcome"].startswith("text was removed")


def test_a_kept_hit_stops_being_raised_and_lapses_when_the_value_changes(case, tmp_path):
    env = cfg(tmp_path, "Rossi")
    assert note(case, "una nota su Rossi", env=env).returncode == 0
    seq = json.loads((case / "events.jsonl").read_text(encoding="utf-8")
                     .splitlines()[-1])["seq"]
    assert "YOU ASKED ME TO KEEP THESE OUT" in run(case, "review.py", env=env).stdout

    assert run(case, "review.py", "--keep", str(seq), "payload.note", env=env).returncode == 0
    kept = tmp_path / "cfg" / "colophon" / "redlists" / "a-case.kept"
    assert kept.exists() and oct(kept.stat().st_mode)[-3:] == "600"
    assert oct(kept.parent.stat().st_mode)[-3:] == "700"
    assert "YOU ASKED ME TO KEEP THESE OUT" not in run(case, "review.py", env=env).stdout

    assert run(case, "review.py", "--set", str(seq), "payload.note",
               "un'altra nota su Rossi", env=env).returncode == 0
    assert "YOU ASKED ME TO KEEP THESE OUT" in run(case, "review.py", env=env).stdout, \
        "the acceptance survived a change to the value it accepted"


def test_a_clean_case_costs_one_line(tmp_path):
    """The whole feature, on a case with nothing to take back. Built from nothing rather
    than from example/, whose register does carry a human_contribution — which the
    review surfaces, correctly, and which is why example/ is not the fixture here."""
    wd = tmp_path / "clean"
    wd.mkdir()
    for name in ("record.py", "review.py"):
        shutil.copy2(os.path.join(SCRIPTS, name), wd / name)
    (wd / "case.json").write_text(json.dumps({"title": "t", "case_uid": "a-case"}),
                                  encoding="utf-8")
    for text in ("case opened", "sealed nothing yet"):
        assert run(wd, "record.py", json.dumps(
            {"type": "status", "actor": "system", "phase": "—",
             "payload": {"note": text}})).returncode == 0
    r = run(wd, "review.py", env=cfg(tmp_path))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "Nothing to change." in r.stdout
    assert len(r.stdout.strip().splitlines()) <= 8


def test_one_list_shouts_and_the_other_two_do_not(case, tmp_path):
    """Two of the three are worth a look; the first is a thing the author was already
    told once. Three headers of equal weight say the three are the same kind of thing,
    and the typography is the only part a reader takes in before reading."""
    env = cfg(tmp_path, "Rossi")
    assert note(case, "una nota su Rossi", env=env).returncode == 0
    src = (case / "versions" / "post.md").read_text(encoding="utf-8")
    assert note(case, " ".join(src.split()[8:20]), typ="human_contribution").returncode == 0
    out = run(case, "review.py", env=env).stdout
    heads = [l.strip() for l in out.splitlines()
             if l.strip() and not l.startswith(" ") and not l.startswith("This")]
    shouting = [h for h in heads if h.isupper()]
    assert len(shouting) == 1, f"expected one shout, got {heads}"
    assert out.index(shouting[0]) < out.index("what you told me"), \
        "the one that is not an offer comes first"


def test_the_entries_are_numbered_contiguously(case, tmp_path):
    """The author says "3 and 7". Finding the path is the model's job — SKILL.md's rule
    that they are never asked to edit a file, applied to the review."""
    import re as _re
    env = cfg(tmp_path, "Rossi")
    assert note(case, "una nota su Rossi", env=env).returncode == 0
    src = (case / "versions" / "post.md").read_text(encoding="utf-8")
    assert note(case, " ".join(src.split()[8:20]), typ="human_contribution").returncode == 0
    out = run(case, "review.py", env=env).stdout
    nums = [int(m) for m in _re.findall(r"^\s*(\d+)\.\s+seq ", out, _re.M)]
    assert nums, "nothing is numbered"
    assert nums == list(range(1, len(nums) + 1)), f"not contiguous: {nums}"
