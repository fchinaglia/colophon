# SPDX-License-Identifier: MIT
"""The reader's page, generated rather than typed.

It is covered by the closing manifest, so an author who fills it in after the manifest
ships a case that fails its own check on the reader's machine and can only be repaired by
reopening a sealed register. These tests are about the holes: that the four the author
owns are filled, that the ones belonging to the reader are not, and that the address the
page hands out cannot be silently absent.
"""
import json
import os

import pytest

from conftest import ROOT, SCRIPTS, run

CASE = {"title": "A test piece", "author": "Someone", "date": "2026-08",
        "reconstructed": False, "case_uid": "042"}


@pytest.fixture
def case(tmp_path):
    """A case folder with the script, a case.json, and a config the test controls."""
    wd = tmp_path / "case"
    wd.mkdir()
    (wd / "case.json").write_text(json.dumps(CASE), encoding="utf-8")
    cfg = tmp_path / "cfg" / "colophon"
    cfg.mkdir(parents=True)
    import shutil
    shutil.copy2(os.path.join(SCRIPTS, "build_verify.py"), wd / "build_verify.py")
    return wd, cfg


def with_contact(cfg, address="someone@example.org"):
    (cfg / "author.json").write_text(
        json.dumps({"name": "Someone", "contact": address}), encoding="utf-8")
    return {"XDG_CONFIG_HOME": str(cfg.parent)}


def test_it_fills_the_four_holes_the_author_owns(case):
    wd, cfg = case
    r = run(wd, "build_verify.py", env=with_contact(cfg))
    assert r.returncode == 0, r.stderr
    text = (wd / "VERIFY.md").read_text(encoding="utf-8")
    assert "A test piece" in text
    assert "colophon-042.tar" in text
    assert text.count("someone@example.org") == 3   # two in the command, one to write to
    for hole in ("[title]", "[uid]", "[your-email]", "[contact]"):
        assert hole not in text, f"{hole} was left unfilled"


def test_it_leaves_the_readers_own_placeholders_alone(case):
    """[YYYYMMDD] is the seal date, which the reader takes from the .tsr, and [file]
    belongs to the commands they run. Filling those in would be answering a question
    that was not asked of the author."""
    wd, cfg = case
    assert run(wd, "build_verify.py", env=with_contact(cfg)).returncode == 0
    text = (wd / "VERIFY.md").read_text(encoding="utf-8")
    assert "[YYYYMMDD]" in text
    assert "[file]" in text


def test_a_missing_contact_stops_it(case):
    """The address is what a reader writes to when a digest does not match, and it is the
    identity `ssh-keygen -Y verify` checks the signature against. A page shipped without
    it names nobody, and it would ship looking finished."""
    wd, cfg = case
    r = run(wd, "build_verify.py", env={"XDG_CONFIG_HOME": str(cfg.parent)})
    assert r.returncode != 0
    assert "contact" in r.stderr.lower()
    assert not (wd / "VERIFY.md").exists()


def test_a_borrowed_contact_is_written_into_the_case(case):
    """author.json is a source of defaults and sits outside the manifest. A generated
    file whose input the manifest does not cover is only half covered, so what was used
    is recorded in case.json, which the manifest does cover."""
    wd, cfg = case
    assert run(wd, "build_verify.py", env=with_contact(cfg)).returncode == 0
    assert json.loads((wd / "case.json").read_text(encoding="utf-8"))["contact"] == \
        "someone@example.org"


def test_the_case_file_wins_over_the_config(case):
    """The per-case record is the authority; the config is where a default comes from."""
    wd, cfg = case
    (wd / "case.json").write_text(json.dumps({**CASE, "contact": "case@example.org"}),
                                  encoding="utf-8")
    assert run(wd, "build_verify.py", env=with_contact(cfg)).returncode == 0
    assert "case@example.org" in (wd / "VERIFY.md").read_text(encoding="utf-8")
    assert "someone@example.org" not in (wd / "VERIFY.md").read_text(encoding="utf-8")


def test_a_case_with_no_name_stops_it(case):
    """The tar is named after case_uid, so a page that cannot name it sends the reader
    looking for a file that has no name."""
    wd, cfg = case
    (wd / "case.json").write_text(json.dumps({"title": "A test piece"}), encoding="utf-8")
    r = run(wd, "build_verify.py", env=with_contact(cfg))
    assert r.returncode != 0
    assert "case_uid" in r.stderr
