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
import time

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


def test_attached_without_embed_is_refused(manifested):
    """A PDF that says `drop colophon-<uid>.tar on verify.html` and carries no attachment
    is the failure the technical line exists to remove, wearing the costume of the fix.
    The two flags were independent — --attached wrote the line, --embed put the file in —
    so forgetting the second produced a document that lied, silently, and two were made
    that way before anyone noticed.

    Not a hard rule: `enclosed` means *travels with the document*, and a PDF mailed
    together with its tar is honestly described by it. That case has to be said out loud.
    """
    r = run(manifested, "render_pdf.py", "--attached")
    assert r.returncode != 0, "a PDF promising an enclosure it does not carry"
    out = r.stdout + r.stderr
    assert "--embed" in out and "--beside" in out, out

    # The honest side-by-side route must stay open. It still has to satisfy the older
    # check that the tar it names is real — the example carries neither a case_uid nor a
    # bundle, so both are put there first.
    cj = os.path.join(manifested, "case.json")
    case = json.load(open(cj, encoding="utf-8"))
    case["case_uid"] = "beside"
    json.dump(case, open(cj, "w", encoding="utf-8"), ensure_ascii=False)
    open(os.path.join(manifested, "colophon-beside.tar"), "wb").write(b"x" * 512)
    r = run(manifested, "render_pdf.py", "--attached", "--beside", "--html-only")
    assert r.returncode == 0, r.stdout + r.stderr


def test_embed_without_attached_warns(manifested):
    """The mirror failure under-claims instead of over-claiming, so it is a warning: the
    document carries the record and its own disclosure says it does not."""
    r = run(manifested, "render_pdf.py", "--embed", "--html-only")
    assert "--attached" in r.stdout + r.stderr


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
    after = m.embed_bundle(pdf, [(str(tar), "d")])
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
    merged = m.embed_bundle(pdf, [(str(tar), "the record")])
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
    merged = m.embed_bundle(pdf, [(str(tar), "d")])
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
        m.embed_bundle(pdf, [(str(tar), "d")])
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
        m.embed_bundle(pdf, [(str(tar), "d")])
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
    merged = m.embed_bundle(pdf, [(str(tar), "d")])
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
        m.embed_bundle(pdf, [(str(tar), "d")])
    assert "ASCII" in str(e.value)


def test_two_attachments_both_arrive(tmp_path):
    """The record and the tool that reads it are two things. A reader who saves only the
    bundle finds the tool inside it, which works and reads like a riddle."""
    if not shutil.which("pdfdetach"):
        pytest.skip("no poppler")
    m = load("render_pdf")
    pdf = a_pdf(tmp_path)
    tar, tool = tmp_path / "colophon-x.tar", tmp_path / "verify.html"
    tar.write_bytes(os.urandom(9000))
    tool.write_text("<html>the verifier</html>", encoding="utf-8")
    merged = m.embed_bundle(pdf, [(str(tar), "the record"), (str(tool), "the tool")])
    open(pdf, "wb").write(merged)

    listing = subprocess.run(["pdfdetach", "-list", pdf], capture_output=True, text=True)
    assert "2 embedded files" in listing.stdout, listing.stdout
    d = tmp_path / "out"
    d.mkdir()
    subprocess.run(["pdfdetach", "-saveall", pdf], cwd=d, check=True, capture_output=True)
    assert (d / "colophon-x.tar").read_bytes() == tar.read_bytes()
    assert (d / "verify.html").read_text(encoding="utf-8") == tool.read_text(encoding="utf-8")


def test_the_name_tree_keys_are_sorted(tmp_path):
    """A reader that binary-searches the tree finds nothing if they are not."""
    m = load("render_pdf")
    pdf = a_pdf(tmp_path)
    a, b = tmp_path / "zz.tar", tmp_path / "aa.html"
    a.write_bytes(b"x")
    b.write_bytes(b"y")
    appended = m.embed_bundle(pdf, [(str(a), "z"), (str(b), "a")])[len(open(pdf, "rb").read()):]
    names = re.search(rb"/Names\s*\[(.*?)\]", appended, re.S).group(1).decode("latin-1")
    assert names.index("aa.html") < names.index("zz.tar")


def test_a_plain_first_line_becomes_the_title_when_case_json_says_so(tmp_path):
    """A source written before the deliverable was markdown carries its title as an
    ordinary paragraph, and the renderer set it at body size with the marker above it —
    the one placement disclosures.md forbids."""
    m = load("render_pdf")
    body = m.to_html("How it was written\n\nThe first paragraph.\n")
    assert body.startswith("<p>")
    out = m.promote_title(body, "How it was written")
    assert out.startswith("<h1>How it was written</h1>")
    assert "The first paragraph." in out


def test_it_promotes_nothing_when_the_title_does_not_match(tmp_path):
    """A fact check, not a guess: when they differ, nothing happens."""
    m = load("render_pdf")
    body = m.to_html("Some opening line\n\nBody.\n")
    assert m.promote_title(body, "A completely different title") == body
    assert m.promote_title(body, None) == body


def test_the_source_disclosure_is_not_printed_twice(manifested):
    """disclosures.md defines `excluded` as the blocks of the disclosure, and both
    renderers generate the marker and the block themselves. A source carrying its own —
    every case sealed before that was true — printed the level-1 marker once from the
    renderer and once from the text, and a paragraph note the generated block had already
    superseded."""
    src = os.path.join(manifested, source_of(manifested))
    text = open(src, encoding="utf-8").read()
    # A hand-typed disclosure, as every case sealed before the renderers generated one.
    typed = "Written by hand with the assistance of a language model, ZZQX."
    open(src, "w", encoding="utf-8").write(text.rstrip("\n") + "\n\n" + typed + "\n")
    ann = os.path.join(manifested, "annotation.json")
    a = json.loads(open(ann, encoding="utf-8").read())
    n = len([b for b in open(src, encoding="utf-8").read().split("\n\n") if b.strip()])
    a["excluded"] = [n - 1]
    open(ann, "w", encoding="utf-8").write(json.dumps(a))
    seal_manifest(manifested)

    r = run(manifested, "render_pdf.py", "--html-only")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "dropped" in r.stdout, "the excluded block was rendered anyway"
    doc = open(os.path.join(manifested, "document.html"), encoding="utf-8").read()
    assert "ZZQX" not in doc, "the hand-typed disclosure was printed as well"
    generated = load("render_md").MARKER["en"].strip("*")[:40]
    assert doc.count(generated) == 1, "the generated marker is not there exactly once"


def test_nothing_is_dropped_when_the_annotation_excludes_nothing(manifested):
    r = run(manifested, "render_pdf.py", "--html-only")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "dropped" not in r.stdout


def test_a_bare_name_is_never_answered_by_the_working_directory(tmp_path, monkeypatch):
    """Issue #39. Every candidate used to be tried with os.path.exists() first, and for a
    bare name that asks about the current directory: a file called `google-chrome` beside
    a case was handed to subprocess.run as a browser."""
    m = load("render_pdf")
    (tmp_path / "google-chrome").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    (tmp_path / "chromium").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(m, "CHROME_PATHS", ())
    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)
    assert m.find_chrome() is None, "a decoy in the working directory was returned"


def test_googles_own_linux_package_name_is_looked_for(tmp_path, monkeypatch):
    """`google-chrome-stable` is what Google's .deb and .rpm install. Without it a Linux
    machine with Chrome reported having none, at the last step of a sealed case."""
    m = load("render_pdf")
    assert "google-chrome-stable" in m.CHROME_NAMES
    monkeypatch.setattr(m, "CHROME_PATHS", ())
    monkeypatch.setattr(shutil, "which",
                        lambda n, *a, **k: "/usr/bin/" + n if n == "google-chrome-stable" else None)
    assert m.find_chrome() == "/usr/bin/google-chrome-stable"


def test_the_snap_and_flatpak_launchers_are_paths_not_names():
    """They live where a PATH lookup will not reach, so they belong in the path list."""
    m = load("render_pdf")
    joined = " ".join(m.CHROME_PATHS)
    assert "/snap/bin/chromium" in joined and "flatpak" in joined
    assert not any(os.sep not in c for c in m.CHROME_PATHS), \
        "a bare name in the path list is the fault this split exists to remove"


# --------------------------------------------------- issue #44: a stall is not a slow render

def stub_chrome(tmp_path, name, body):
    """A stand-in that behaves the way a stalled Chrome behaves: it never exits.

    A real stall cannot be provoked on demand — it depends on a profile lock or a
    crashpad handler — so the stall is supplied and the question asked of `render_pdf.py`
    is the one that matters either way: what does it do while a Chrome does not come back.
    """
    path = os.path.join(str(tmp_path), name)
    with open(path, "w") as f:
        f.write(body)
    os.chmod(path, 0o755)
    return path


def stalled(monkeypatch, manifested, tmp_path, body, seconds=3):
    rp = load("render_pdf")
    monkeypatch.setattr(rp, "find_chrome",
                        lambda: stub_chrome(tmp_path, "chrome-stub", body))
    monkeypatch.setattr(rp, "CHROME_SECONDS", seconds)
    monkeypatch.chdir(manifested)
    return rp, rp.main(["-o", "out.pdf"])


def test_a_chrome_that_never_exits_is_stopped_rather_than_waited_on(
        monkeypatch, manifested, tmp_path, capsys):
    """Issue #44. `subprocess.run` with no `timeout=` waits forever, and this call runs
    during closing — so an author sees a program that printed its progress and stopped,
    with nothing to tell a hopeless wait from a slow one.

    The deadline is asserted by the clock as well as the return code: a test that only
    checked the message would pass just as well against the unbounded call, since the
    message would arrive eventually. What is being fixed is *when*."""
    started = time.time()
    _, code = stalled(monkeypatch, manifested, tmp_path, "#!/bin/sh\nsleep 60\n")
    spent = time.time() - started
    assert code == 1, "a stalled rendering has to fail, not return success"
    assert spent < 30, (
        "issue #44: the call waited %.0fs on a Chrome that never exits; the deadline is "
        "what the fix is" % spent)
    said = capsys.readouterr().err
    assert "did not finish within 3 seconds" in said, said
    assert "--html-only" in said, (
        "the refusal has to leave the author somewhere to go: the HTML is complete and "
        "printable by hand. It said: %r" % said)


def test_the_html_survives_a_stalled_rendering(monkeypatch, manifested, tmp_path):
    """The rendering is not lost when Chrome is. The HTML is written before Chrome is
    ever started, and the refusal says so — which is only worth saying if it is true."""
    stalled(monkeypatch, manifested, tmp_path, "#!/bin/sh\nsleep 60\n")
    html = os.path.join(manifested, "out.html")
    assert os.path.exists(html) and os.path.getsize(html) > 0
    assert "<html" in open(html, encoding="utf-8").read().lower()


def test_a_half_written_pdf_does_not_outlive_the_stall(
        monkeypatch, manifested, tmp_path, capsys):
    """The one that matters most. Chrome may create the file and then stall part-way
    through it, and a truncated PDF sitting beside a finished HTML is the artefact that
    gets picked up later and believed — a signature over it would say *this file is
    unaltered* about a document that stops mid-sentence."""
    body = ('#!/bin/sh\n'
            'printf "%%PDF-1.4 truncated" > "${4#--print-to-pdf=}"\n'
            'sleep 60\n')
    _, code = stalled(monkeypatch, manifested, tmp_path, body)
    assert code == 1
    pdf = os.path.join(manifested, "out.pdf")
    assert not os.path.exists(pdf), (
        "issue #44: a partly written %r was left behind" % pdf)
    assert "was removed" in capsys.readouterr().err


def test_the_deadline_is_named_where_it_is_spent():
    """`CHROME_SECONDS` is a named constant and the call carries it. A number written
    inline at the call site is a number nobody finds when a slow machine needs it
    raised, and this is the kind of value someone will need to raise."""
    rp = load("render_pdf")
    assert isinstance(rp.CHROME_SECONDS, int) and rp.CHROME_SECONDS > 0
    src = open(os.path.join(SCRIPTS, "render_pdf.py"), encoding="utf-8").read()
    call = src[src.index('"--print-to-pdf='):]
    assert "timeout=CHROME_SECONDS" in call[:400], (
        "issue #44: the Chrome call does not carry the deadline")
