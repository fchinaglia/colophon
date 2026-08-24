# SPDX-License-Identifier: MIT
"""render_pdf.py — the published PDF.

Two properties carry everything else. The gate, shared with render_md.py: the source is
hashed against the manifest before anything is rendered, because a signature over a PDF
says *this file is unaltered* and a reader will hear *this text is what was measured*.
And the converter's one rule: it wraps, it never rewrites.
"""
import hashlib
import importlib.util
import json
import os
import shutil
import sys

import pytest

from conftest import SCRIPTS, run

ONLY = {"record.py", "measure.py", "build_icon.py", "build_note.py", "build_block.py",
        "render_md.py", "render_pdf.py"}


def load(name):
    """Imported, not run: these are pure functions and the point is to mutate around
    them. Everything else in this suite still goes through a subprocess."""
    sys.path.insert(0, SCRIPTS)
    try:
        return importlib.import_module(name)
    finally:
        sys.path.pop(0)


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def seal_manifest(wd):
    covered = {}
    for base, dirs, files in os.walk(wd):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fn in sorted(files):
            rel = os.path.relpath(os.path.join(base, fn), wd)
            if rel != "events.jsonl" and not fn.startswith("."):
                covered[rel] = sha256(os.path.join(base, fn))
    event = {"type": "status", "actor": "system", "phase": "—", "meta": True,
             "payload": {"closing": "MANIFEST", "algorithm": "sha256", "sha256": covered}}
    assert run(wd, "record.py", json.dumps(event, ensure_ascii=False)).returncode == 0


@pytest.fixture
def manifested(workspace):
    wd = workspace("example", only=ONLY)
    assert run(wd, "build_icon.py").returncode == 0
    seal_manifest(wd)
    return wd


def source_of(wd):
    rows = [json.loads(l) for l in open(os.path.join(wd, "events.jsonl"),
                                        encoding="utf-8") if l.strip()]
    return next(k for k in rows[-1]["payload"]["sha256"] if k.startswith("versions/"))


def test_the_gate_is_the_same_one(manifested):
    with open(os.path.join(manifested, source_of(manifested)), "a", encoding="utf-8") as f:
        f.write("\nA sentence the measurement never saw.\n")
    r = run(manifested, "render_pdf.py", "--html-only")
    assert r.returncode != 0
    assert "not the file the manifest covers" in r.stdout + r.stderr


def test_unsupported_markdown_is_refused_by_line_number(workspace):
    """A converter that silently mangles a table publishes something the author did not
    write, under a signature saying they did, and it is invisible in the finished PDF."""
    wd = workspace("example", only=ONLY)
    assert run(wd, "build_icon.py").returncode == 0
    src = None
    for base, _, files in os.walk(os.path.join(wd, "versions")):
        for fn in files:
            src = os.path.join(base, fn)
    with open(src, "a", encoding="utf-8") as f:
        f.write("\n| a | b |\n|---|---|\n| 1 | 2 |\n")
    seal_manifest(wd)
    r = run(wd, "render_pdf.py", "--html-only")
    assert r.returncode != 0
    assert "a table" in r.stdout + r.stderr
    assert "line " in r.stdout + r.stderr


def test_the_converter_wraps_and_never_rewrites():
    m = load("render_pdf")
    src = ("# A heading\n\nA paragraph with **bold** and *italic* and `code`,\n"
           "and a [link](https://example.com) too.\n\n- one\n- two\n\n> quoted words\n")
    m.check_nothing_was_rewritten(src, m.to_html(src))


def test_a_converter_that_dropped_a_word_would_be_caught():
    """The invariant is only worth having if it fires."""
    m = load("render_pdf")
    src = "A paragraph with several plain words in it.\n"
    mangled = m.to_html(src).replace("several ", "")
    with pytest.raises(SystemExit) as e:
        m.check_nothing_was_rewritten(src, mangled)
    assert "changed the text" in str(e.value)


def test_the_disclosure_block_survives_as_raw_html():
    """build_block.py generated it; rewriting it here would defeat that."""
    m = load("render_pdf")
    out = m.to_html('text\n\n<table class="colophon">\n  <tr><td>x</td></tr>\n</table>\n')
    assert '<table class="colophon">' in out


def test_the_marker_goes_under_the_title(manifested):
    assert run(manifested, "render_pdf.py", "--html-only").returncode == 0
    doc = open(os.path.join(manifested, "document.html"), encoding="utf-8").read()
    assert doc.index("</h1>") < doc.index("class=\"marker\"")
    assert doc.index("class=\"marker\"") < doc.index('class="colophon"')


def test_it_never_claims_pdf_a(manifested):
    """An unbacked compliance claim, in the one artefact whose job is to be checkable."""
    r = run(manifested, "render_pdf.py", "--html-only")
    text = r.stdout + open(os.path.join(SCRIPTS, "render_pdf.py"), encoding="utf-8").read()
    assert "PDF/A" in text and "not PDF/A" in text
    doc = open(os.path.join(manifested, "document.html"), encoding="utf-8").read()
    assert "PDF/A" not in doc


@pytest.mark.skipif(not any(os.path.exists(c) or shutil.which(c)
                            for c in load("render_pdf").CHROMES),
                    reason="no Chrome or Chromium")
def test_it_prints_a_pdf(manifested):
    r = run(manifested, "render_pdf.py", "-o", "out.pdf")
    assert r.returncode == 0, r.stdout + r.stderr
    data = open(os.path.join(manifested, "out.pdf"), "rb").read()
    assert data.startswith(b"%PDF-") and len(data) > 1000
