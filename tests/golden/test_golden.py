# SPDX-License-Identifier: MIT
"""The widest net for the least code.

`example/` regenerates its four outputs byte for byte: nothing in that pipeline reads a
clock, so a golden comparison needs no time faking at all. Any silent change to a number,
a page or the icon shows up here.
"""
import filecmp
import json
import os
import shutil
import tarfile

import pytest

from conftest import ROOT, SCRIPTS, run

OUTPUTS = ["kpi.json", "spans.json", "icon.svg", "index.html"]


def test_example_regenerates_byte_for_byte(workspace):
    wd = workspace("example")
    for script in ("measure.py", "build_icon.py", "build_page.py"):
        r = run(wd, script)
        assert r.returncode == 0, f"{script}: {r.stderr}"
    for name in OUTPUTS:
        assert filecmp.cmp(wd / name, os.path.join(ROOT, "example", name), shallow=False), \
            f"{name} is not byte-identical to the committed example"


def test_the_shipped_bundle_still_measures_the_same(tmp_path):
    """The validation case ships as one file now, so this tests the file we ship rather
    than a folder beside it: extract `validation/colophon-001.tar`, run today's scripts
    over its inputs, and compare with the measurement sealed inside it.

    The comparison is on the measured values, not on the bytes. A file compared byte for
    byte also fails when a key is added that moves no number — noise, and the reason this
    assertion had to be loosened once already — and it passes when a value changes
    representation while staying equal, which is the one thing it was written to catch.
    """
    bundle = os.path.join(ROOT, "validation", "colophon-001.tar")
    wd = tmp_path / "case"
    wd.mkdir()
    with tarfile.open(bundle) as t:
        t.extractall(wd)
    frozen = json.loads((wd / "kpi.json").read_text(encoding="utf-8"))

    for name in os.listdir(SCRIPTS):
        if name.endswith((".py", ".sh")):
            shutil.copy2(os.path.join(SCRIPTS, name), wd / name)
    r = run(wd, "measure.py")
    assert r.returncode == 0, r.stderr

    def measured(ss):
        """A span's measurement is its text, its weight and its two attributions."""
        return [{k: s[k] for k in ("block", "text", "words", "lex", "idea", "phase")}
                for s in ss]

    frozen_spans = measured(json.loads((wd / "spans.json").read_text(encoding="utf-8")))
    today = json.loads((wd / "kpi.json").read_text(encoding="utf-8"))
    for k in ("words", "spans", "ai_lexical", "ai_ideational", "lexical", "ideational"):
        assert today[k] == frozen[k], f"{k} drifted on the validation case"

    assert list(today["by_phase"]) == list(frozen["by_phase"]), \
        "the phases of the validation case changed"
    for phase, was in frozen["by_phase"].items():
        now = today["by_phase"][phase]
        assert now["words"] == was["words"], f"{phase}: the word count drifted"
        assert now["ai_lexical"] == was["ai_lexical"], f"{phase}: the lexical share drifted"
        assert now["ai_ideational"] == was["ai_ideational"], \
            f"{phase}: the ideational share drifted"

    assert measured(json.loads((wd / "spans.json").read_text(encoding="utf-8"))) == \
        frozen_spans, "the spans drifted on the validation case"


def test_example_kpi_reports_both_axes(workspace):
    wd = workspace("example")
    assert run(wd, "measure.py").returncode == 0
    kpi = json.loads((wd / "kpi.json").read_text(encoding="utf-8"))
    assert kpi["integrity"] is True
    assert kpi["unexplained"] == []
    assert "by_phase" in kpi and kpi["by_phase"], "the breakdown by phase is not optional"
    for phase, d in kpi["by_phase"].items():
        # Both axes, and neither of them under a name that does not say which it is:
        # the note prescribed in reference/disclosures.md takes its per-phase figure
        # from here, and a key called "ai" was published as if it were the ideational one.
        assert set(d) == {"words", "ai_lexical", "ai_ideational"}, \
            f"{phase}: the breakdown does not carry both axes, each named"
