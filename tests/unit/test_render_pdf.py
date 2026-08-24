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
import re
import shutil
import subprocess
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


# ------------------------------------------------------------------ embedding, --embed

def a_pdf(tmp_path):
    """A real one, from Chrome, because the point is the shape Chrome writes."""
    m = load("render_pdf")
    chrome = next((c for c in m.CHROMES if os.path.exists(c) or shutil.which(c)), None)
    if not chrome:
        pytest.skip("no Chrome or Chromium")
    src = tmp_path / "p.html"
    src.write_text("<h1>Title</h1><p>Body.</p>", encoding="utf-8")
    out = tmp_path / "p.pdf"
    subprocess.run([chrome if os.path.exists(chrome) else shutil.which(chrome),
                    "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out}", str(src)], check=True, capture_output=True)
    return str(out)


def test_the_original_bytes_are_never_touched(tmp_path):
    """That is what an incremental update is, and it is why a PAdES signature added
    afterwards covers this revision instead of contradicting it."""
    m = load("render_pdf")
    pdf = a_pdf(tmp_path)
    tar = tmp_path / "colophon-x.tar"
    tar.write_bytes(os.urandom(4096))
    before = open(pdf, "rb").read()
    after = m.embed_bundle(pdf, str(tar), "d")
    assert after[:len(before)] == before
    assert len(after) > len(before)


def test_an_independent_reader_gets_the_bundle_back_byte_for_byte(tmp_path):
    """Our writer and our reader agreeing proves nothing. poppler is somebody else's."""
    if not shutil.which("pdfdetach"):
        pytest.skip("no poppler")
    m = load("render_pdf")
    pdf = a_pdf(tmp_path)
    payload = os.urandom(20000)
    tar = tmp_path / "colophon-x.tar"
    tar.write_bytes(payload)
    merged = m.embed_bundle(pdf, str(tar), "the record")
    open(pdf, "wb").write(merged)

    listing = subprocess.run(["pdfdetach", "-list", pdf], capture_output=True, text=True)
    assert "colophon-x.tar" in listing.stdout, listing.stdout
    d = tmp_path / "out"
    d.mkdir()
    subprocess.run(["pdfdetach", "-saveall", pdf], cwd=d, check=True, capture_output=True)
    assert (d / "colophon-x.tar").read_bytes() == payload


def test_the_document_still_reads_afterwards(tmp_path):
    if not shutil.which("pdftotext"):
        pytest.skip("no poppler")
    m = load("render_pdf")
    pdf = a_pdf(tmp_path)
    tar = tmp_path / "colophon-x.tar"
    tar.write_bytes(b"x" * 1000)
    merged = m.embed_bundle(pdf, str(tar), "d")
    open(pdf, "wb").write(merged)
    r = subprocess.run(["pdftotext", pdf, "-"], capture_output=True, text=True)
    assert "Title" in r.stdout and "Body." in r.stdout


@pytest.mark.parametrize("marker,why", [
    (b"/Encrypt 9 0 R", "encrypted"),
    (b"/Type /XRef", "cross-reference stream"),
    (b"/ObjStm", "object streams"),
])
def test_it_refuses_shapes_it_does_not_implement(tmp_path, marker, why):
    """A malformed incremental update opens in some readers and not others, silently.
    Guessing is the one thing this must not do."""
    m = load("render_pdf")
    pdf = a_pdf(tmp_path)
    data = open(pdf, "rb").read()
    open(pdf, "wb").write(data[:100] + marker + data[100:])
    tar = tmp_path / "colophon-x.tar"
    tar.write_bytes(b"x")
    with pytest.raises(SystemExit) as e:
        m.embed_bundle(pdf, str(tar), "d")
    assert "cannot be updated" in str(e.value)


def test_it_refuses_a_catalog_that_already_has_names(tmp_path):
    """Merging one in blindly would break whatever is already there."""
    m = load("render_pdf")
    pdf = a_pdf(tmp_path)
    data = open(pdf, "rb").read()
    root = int(re.search(rb"/Root\s+(\d+)", data).group(1))
    k = re.search(rb"(?m)^%d\s+0\s+obj\b" % root, data).end()
    j = data.index(b"<<", k)
    open(pdf, "wb").write(data[:j + 2] + b" /Names 1 0 R" + data[j + 2:])
    tar = tmp_path / "colophon-x.tar"
    tar.write_bytes(b"x")
    with pytest.raises(SystemExit) as e:
        m.embed_bundle(pdf, str(tar), "d")
    assert "already carries" in str(e.value)


def test_the_dictionary_scanner_counts_rather_than_matching(tmp_path):
    """A regex cannot count, and the catalog is the one object that has to be rewritten
    correctly or the file has no root."""
    m = load("render_pdf")
    buf = rb"<< /A << /B 1 >> /C (a \) string with >> inside) /D 2 >>tail"
    assert buf[:m._balanced_dict(buf, 0)].endswith(b">>")
    assert buf[m._balanced_dict(buf, 0):] == b"tail"


def test_the_file_name_strings_stay_literal(tmp_path):
    """The literal form is what the ASCII guard below is written for: a literal string
    round-trips an ASCII name exactly, and the two have to stay consistent. Switching to
    the UTF-16BE form the specification prefers is defensible, but then the guard is
    pointless and should go with it — this asserts they do not drift apart."""
    m = load("render_pdf")
    pdf = a_pdf(tmp_path)
    tar = tmp_path / "colophon-x.tar"
    tar.write_bytes(b"payload")
    merged = m.embed_bundle(pdf, str(tar), "d")
    appended = merged[len(open(pdf, "rb").read()):]
    assert re.search(rb"/UF\s*\(", appended), "/UF must be a literal string"
    assert re.search(rb"/Names\s*\[\s*\(", appended), "the name-tree key must be literal"
    assert b"<feff" not in appended.lower()


def test_it_refuses_a_non_ascii_bundle_name(tmp_path):
    """The literal-string form cannot carry one with confidence, and a mangled name is
    how an attachment becomes unfindable in a file that otherwise looks correct."""
    m = load("render_pdf")
    pdf = a_pdf(tmp_path)
    tar = tmp_path / "colophon-però.tar"
    tar.write_bytes(b"x")
    with pytest.raises(SystemExit) as e:
        m.embed_bundle(pdf, str(tar), "d")
    assert "ASCII" in str(e.value)
