# SPDX-License-Identifier: MIT
"""The three generators, and what each must refuse to do."""
import json
import re

from conftest import run

CELLS = ["human written", "human edited", "machine polished", "machine generated"]


def ungate(wd):
    kpi = json.loads((wd / "kpi.json").read_text(encoding="utf-8"))
    kpi["integrity"] = False
    (wd / "kpi.json").write_text(json.dumps(kpi, indent=1), encoding="utf-8")


def test_icon_labels_stay_english(workspace):
    """The four names are the classes of a published taxonomy. Translated, they stop
    pointing at it, and two readers in two languages stop reading the same scale."""
    wd = workspace("example")
    assert run(wd, "measure.py").returncode == 0
    assert run(wd, "build_icon.py").returncode == 0
    svg = (wd / "icon.svg").read_text(encoding="utf-8")
    texts = re.findall(r">([^<>]+)</text>", svg)
    # each cell name is wrapped onto two lines, so recompose the first eight
    names = {" ".join(texts[i:i + 2]) for i in range(0, 8, 2)}
    assert names == set(CELLS), f"the quadrant labels changed: {sorted(names)}"


def test_generators_refuse_an_ungated_measurement(workspace):
    """A caller that ignores exit codes must still not be able to publish a number that
    never passed its own checks."""
    wd = workspace("example")
    assert run(wd, "measure.py").returncode == 0
    ungate(wd)
    for script in ("build_icon.py", "build_page.py"):
        assert run(wd, script).returncode != 0, f"{script} rendered an ungated kpi.json"


def test_page_survives_extra_notes_as_string_and_as_list(workspace):
    """It rendered 537 one-character paragraphs once, because it iterated a string."""
    wd = workspace("example")
    assert run(wd, "measure.py").returncode == 0
    case = wd / "case.json"
    data = json.loads(case.read_text(encoding="utf-8"))
    for value in ("One note, as every case writes it.", ["First note.", "Second note."]):
        data["extra_notes"] = value
        case.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
        assert run(wd, "build_page.py").returncode == 0, f"failed on {type(value).__name__}"
        html = (wd / "index.html").read_text(encoding="utf-8")
        assert html.count("<p>") < 200, "the note was iterated character by character"


def test_note_forms_and_the_flag_that_exists(workspace):
    wd = workspace("example")
    assert run(wd, "measure.py").returncode == 0
    full = run(wd, "build_note.py", "--form", "full")
    compact = run(wd, "build_note.py")
    short = run(wd, "build_note.py", "--short-root")
    assert full.returncode == compact.returncode == short.returncode == 0
    # Two lines with no route to name, three when the enclosure is one of them. The
    # example carries no bundle, so this is the held form.
    assert len(compact.stdout.strip().splitlines()) == 2, "the held form is two lines"
    assert "…" in short.stdout, "--short-root must abbreviate the root"
    assert "…" not in compact.stdout, "the compact form prints the root whole by default"
    assert run(wd, "build_note.py", "--full-root").returncode != 0, \
        "--full-root does not exist; the docs said it did once"
