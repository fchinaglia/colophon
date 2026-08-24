# SPDX-License-Identifier: MIT
"""build_attestation.py — the page an author signs by hand.

The design is one line: the digest lines are flush-left in `sha256sum` checkfile format,
so the legally signed document IS the checkfile the reader runs. Everything here defends
that property, and the paragraph that says what the signature does not claim.
"""
import hashlib
import json
import os
import re
import subprocess

import pytest

from conftest import run

ONLY = {"record.py", "measure.py", "build_icon.py", "build_attestation.py",
        "build_bundle.py", "seal.sh"}
CHECKLINE = re.compile(r"^[0-9a-f]{64}  (.+)$", re.M)


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


@pytest.fixture
def manifested(workspace):
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
    assert run(wd, "record.py", json.dumps(event, ensure_ascii=False)).returncode == 0
    return wd


def attest(wd, *argv):
    r = run(wd, "build_attestation.py", *argv)
    assert r.returncode == 0, r.stdout + r.stderr
    name = "attestazione.txt" if "it" in argv else "attestation.txt"
    return open(os.path.join(wd, name), encoding="utf-8").read()


def test_the_signed_page_is_the_checkfile(manifested):
    """`grep -E '^[0-9a-f]{64}  ' attestation.txt | shasum -a 256 -c -` — no PDF, no PKI,
    no browser. If this breaks, the artefact is just prose."""
    text = attest(manifested)
    lines = "\n".join(m.group(0) for m in CHECKLINE.finditer(text))
    r = subprocess.run(["shasum", "-a", "256", "-c", "-"], input=lines, text=True,
                       capture_output=True, cwd=manifested)
    assert r.returncode == 0, r.stdout + r.stderr
    assert " FAILED" not in r.stdout


def test_a_tampered_file_fails_the_check(manifested):
    text = attest(manifested)
    with open(os.path.join(manifested, "kpi.json"), "a", encoding="utf-8") as f:
        f.write(" ")
    lines = "\n".join(m.group(0) for m in CHECKLINE.finditer(text))
    r = subprocess.run(["shasum", "-a", "256", "-c", "-"], input=lines, text=True,
                       capture_output=True, cwd=manifested)
    assert r.returncode != 0 and "kpi.json: FAILED" in r.stdout


def test_the_register_itself_is_in_the_checkfile(manifested):
    """A `-c` run that checks everything except the file the page is about would be a
    strange thing to have signed."""
    names = CHECKLINE.findall(attest(manifested))
    assert "events.jsonl" in names


def test_prose_never_lands_in_the_checkfile(manifested):
    """Every flush-left digest line is a file that exists; nothing else may match."""
    wd = manifested
    for name in CHECKLINE.findall(attest(wd)):
        assert os.path.exists(os.path.join(wd, name)), f"{name!r} is not a file"


def test_it_states_what_the_signature_does_not_claim(manifested):
    """A reader who sees a legal name will merge 'this file is unaltered' with 'this text
    is the text that was measured'. The page has to separate them itself."""
    text = attest(manifested)
    assert "complete" in text and "compiled by the language model about itself" in text
    assert "is the text that was measured" in text


def test_the_ots_is_named_but_not_hashed(manifested):
    """`ots upgrade` rewrites the file when the Bitcoin attestation confirms, so any
    digest of it goes stale by design."""
    open(os.path.join(manifested, "events.jsonl.ots"), "wb").write(b"pending")
    text = attest(manifested)
    assert "events.jsonl.ots" in text
    assert "events.jsonl.ots" not in CHECKLINE.findall(text)


def test_it_refuses_a_case_with_no_manifest(workspace):
    wd = workspace("example", only=ONLY)
    r = run(wd, "build_attestation.py")
    assert r.returncode != 0
    assert "no closing manifest" in r.stdout + r.stderr


def test_it_stops_when_a_covered_file_is_not_here(manifested):
    """The checkfile a reader runs would fail on them, and the failure would look like
    tampering rather than like attesting from the wrong folder."""
    os.remove(os.path.join(manifested, "kpi.json"))
    r = run(manifested, "build_attestation.py")
    assert r.returncode == 1
    assert "not in this folder" in r.stdout


def test_the_italian_form_names_the_verify_file_that_exists(manifested):
    """An Italian case may carry VERIFY.md and an English one VERIFICA.md; naming the
    wrong one sends the reader to a 404 in the paragraph explaining what this is worth."""
    text = attest(manifested, "--lang", "it")
    assert "ATTESTAZIONE" in text
    named = re.search(r"scritto in (VERIF\S+), accanto", text).group(1)
    assert os.path.exists(os.path.join(manifested, named)) or named == "VERIFY.md"


def test_the_attestation_travels_in_the_bundle(manifested, tmp_path):
    """The one file in the bundle carrying a legal name must not be the one withheld for
    not being covered — it cannot be covered, it carries the root."""
    import tarfile
    attest(manifested)
    open(os.path.join(manifested, "attestation.txt.p7m"), "wb").write(b"\x30\x82fake")
    open(os.path.join(manifested, "events.jsonl.sig"), "w").write("x")
    r = run(manifested, "build_bundle.py", ".", "-o", str(tmp_path / "out"),
            "--verifier", os.path.join(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))), "verifier", "verify.html"),
            "--uid", "att")
    assert r.returncode == 0, r.stdout + r.stderr
    with tarfile.open(tmp_path / "out" / "colophon-att.tar") as t:
        names = t.getnames()
    assert "attestation.txt" in names and "attestation.txt.p7m" in names
