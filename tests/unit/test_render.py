# SPDX-License-Identifier: MIT
"""render_md.py — the published document.

The gate is the point of this file. A document rendered from a file the measurement
never saw carries percentages about a different text, and once a signature is over it
the reader will read *this file is unaltered* as *this text is the text measured*.
"""
import hashlib
import json
import os

import pytest

from conftest import run

ONLY = {"record.py", "measure.py", "build_icon.py", "build_note.py", "build_block.py",
        "render_md.py"}


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


@pytest.fixture
def manifested(workspace):
    """example/ carried to a closing manifest, so there is a covered source to render.
    Not signed: render_md.py warns about that and still renders, and the block says so
    to the reader in its own words."""
    wd = workspace("example", only=ONLY)
    assert run(wd, "build_icon.py").returncode == 0
    covered = {}
    for base, dirs, files in os.walk(wd):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fn in sorted(files):
            rel = os.path.relpath(os.path.join(base, fn), wd)
            if rel != "events.jsonl" and not fn.startswith("."):
                covered[rel] = sha256(os.path.join(base, fn))
    event = {"type": "status", "actor": "system", "phase": "—", "meta": True,
             "payload": {"closing": "MANIFEST", "algorithm": "sha256", "sha256": covered}}
    r = run(wd, "record.py", json.dumps(event, ensure_ascii=False))
    assert r.returncode == 0, r.stdout + r.stderr
    return wd


def source_of(wd):
    rows = [json.loads(l) for l in open(os.path.join(wd, "events.jsonl"),
                                        encoding="utf-8") if l.strip()]
    m = rows[-1]["payload"]["sha256"]
    return next(k for k in m if k.startswith("versions/"))


def test_the_body_is_the_covered_source_byte_for_byte(manifested):
    src = os.path.join(manifested, source_of(manifested))
    r = run(manifested, "render_md.py", "-o", "doc.md")
    assert r.returncode == 0, r.stdout + r.stderr
    doc = open(os.path.join(manifested, "doc.md"), encoding="utf-8").read()
    for line in open(src, encoding="utf-8").read().rstrip("\n").split("\n"):
        assert line in doc, f"the renderer changed a line of the source: {line!r}"


def test_it_refuses_a_source_the_manifest_does_not_cover(manifested):
    """Either restore the file, or reopen the case: a new event saying why, a new
    manifest, a new seal."""
    src = os.path.join(manifested, source_of(manifested))
    with open(src, "a", encoding="utf-8") as f:
        f.write("\nA sentence the measurement never saw.\n")
    r = run(manifested, "render_md.py", "-o", "doc.md")
    assert r.returncode != 0
    assert "not the file the manifest covers" in r.stdout + r.stderr
    assert not os.path.exists(os.path.join(manifested, "doc.md")), \
        "a refused render must leave no document behind"


def test_there_is_no_flag_that_skips_the_gate(manifested):
    r = run(manifested, "render_md.py", "--help")
    for flag in ("--force", "--no-check", "--skip"):
        assert flag not in r.stdout, f"{flag} would make the gate optional"


def test_it_refuses_a_case_with_no_manifest(workspace):
    wd = workspace("example", only=ONLY)
    r = run(wd, "render_md.py", "-o", "doc.md")
    assert r.returncode != 0
    assert "no closing manifest" in r.stdout + r.stderr


def test_the_icon_is_inlined_so_the_document_can_travel_alone(manifested):
    """`<img src="icon.svg">` breaks the moment the file leaves its folder, which is
    what publishing a document is."""
    assert run(manifested, "render_md.py", "-o", "doc.md").returncode == 0
    doc = open(os.path.join(manifested, "doc.md"), encoding="utf-8").read()
    assert "<svg" in doc and 'src="icon.svg"' not in doc


def test_the_marker_goes_under_the_title_not_above_it(manifested):
    """Never above the thing the reader came for."""
    assert run(manifested, "render_md.py", "-o", "doc.md").returncode == 0
    doc = open(os.path.join(manifested, "doc.md"), encoding="utf-8").read()
    lines = doc.split("\n")
    title = next(i for i, l in enumerate(lines) if l.startswith("# "))
    marker = next(i for i, l in enumerate(lines) if "assistance of a language model" in l)
    assert marker > title


def test_the_note_lines_do_not_collapse_into_one_paragraph_in_markdown(manifested):
    """Consecutive lines are one paragraph in markdown: the five would arrive as a
    single run-on sentence."""
    assert run(manifested, "render_md.py", "--block", "md", "-o", "doc.md").returncode == 0
    doc = open(os.path.join(manifested, "doc.md"), encoding="utf-8").read()
    assert doc.count("  \n") >= 3, "the note lines carry no hard breaks"


def test_it_says_so_when_the_register_is_not_signed(manifested):
    """Seal first and render after: a document rendered before the seal carries the root
    of the event preceding the manifest."""
    r = run(manifested, "render_md.py", "-o", "doc.md")
    assert r.returncode == 0
    assert "is missing" in r.stderr and "unsigned register" in r.stderr
