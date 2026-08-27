# SPDX-License-Identifier: MIT
"""The two checks that must stop the pipeline.

Each of these is a CHANGELOG entry: a regression that has already happened once. The
danger they guard is not manipulation, it is drift — an annotation falling behind a text
that still reconstructs, which is why a passing reconstruction is not enough on its own.
"""
import json
import os

from conftest import SCRIPTS, run


def annotate(wd, mutate):
    path = wd / "annotation.json"
    ann = json.loads(path.read_text(encoding="utf-8"))
    mutate(ann)
    path.write_text(json.dumps(ann, indent=1, ensure_ascii=False), encoding="utf-8")


def test_baseline_passes(workspace):
    wd = workspace("example")
    assert run(wd, "measure.py").returncode == 0


def test_an_unexplained_change_stops_the_run(workspace):
    """A change declared in the register with no span and no reason must fail, and
    must NOT leave a kpi.json behind: the 1.1.1 regression printed the percentages,
    wrote the file, and exited zero, leaving everything downstream free to publish."""
    wd = workspace("example")
    (wd / "kpi.json").unlink()

    def orphan(a):
        a["explained"] = {}
        # a block is either one attribution or a list of spans; detach both from the
        # change they carry, so every declared change is left with nowhere to live
        for block in a["blocks"].values():
            for span in (block if isinstance(block, list) else [block]):
                span.pop("event", None)

    annotate(wd, orphan)
    r = run(wd, "measure.py")
    assert r.returncode != 0, "an unexplained change must stop the run"
    assert not (wd / "kpi.json").exists(), \
        "nothing may be written when the run fails: downstream reads what is on disk"


def test_a_stale_exception_stops_the_run(workspace):
    """An `explained` entry that no longer matches any unmatched change hides the next
    real gap, so it fails rather than being ignored."""
    wd = workspace("example")
    annotate(wd, lambda a: a.setdefault("explained", {}).__setitem__(
        "R99", "a change that does not exist"))
    r = run(wd, "measure.py")
    assert r.returncode != 0, "a stale exception must stop the run"
    assert "R99" in (r.stdout + r.stderr)


def test_reconstruction_failure_stops_the_run(workspace):
    """If the spans no longer reproduce the text, no number may be published."""
    wd = workspace("example")
    src = wd / "versions" / "post.md"
    src.write_text(src.read_text(encoding="utf-8") + "\n\nAn extra paragraph nobody "
                   "annotated.\n", encoding="utf-8")
    r = run(wd, "measure.py")
    assert r.returncode != 0
    assert "reconstruction" in (r.stdout + r.stderr).lower()


def test_an_empty_source_is_not_a_success(workspace):
    wd = workspace("example")
    (wd / "versions" / "post.md").write_text("", encoding="utf-8")
    assert run(wd, "measure.py").returncode != 0


def measure_module():
    """The script itself, imported. Its module-level code is a guard clause under
    `__main__`, so importing it is safe and is how a function is reached directly."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "measure_under_test", os.path.join(SCRIPTS, "measure.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_a_marker_is_positioned_at_the_occurrence_the_check_approved():
    """Issue #42. `find()` positioned the cut with the marker's first four words while
    the ambiguity check tested the whole marker, so a marker that occurs once could be
    cut at a different occurrence that merely started the same way.

    Both gates stayed green — the spans still rebuilt the text and the change was still
    carried — and the published percentage was wrong. That is the failure this file
    exists to prevent, arriving through the one function nothing was checking.
    """
    m = measure_module()
    block = ("The reader who opens a piece today has a doubt. "
             "They cannot tell how much of a machine is inside the lines. "
             "The reader who opens a piece today has no way to check it either.")
    marker = "The reader who opens a piece today has no way to check it"

    assert m.norm(block).count(m.norm(marker)) == 1, \
        "the fixture is wrong: the ambiguity check would have refused this marker"
    assert sum(block.startswith("The reader who opens", i)
               for i in range(len(block))) == 2, \
        "the fixture is wrong: the first four words must repeat"
    assert m.find(block, marker) == block.find(marker), \
        "the cut landed on an occurrence the ambiguity check did not approve"


def test_a_marker_is_still_found_across_accents_and_apostrophes():
    """The four-word search exists because `norm()` changes lengths, and the fix must
    not cost that: it may correct the walk by a character, never relocate it."""
    m = measure_module()
    block = "La citt\u00e0 \u00e8 cambiata. E l\u2019idea di partenza non regge pi\u00f9."
    marker = "E l'idea di partenza"
    assert m.find(block, marker) == block.find("E l\u2019idea di partenza")


def test_an_excluded_block_written_as_a_string_is_not_silently_ignored(workspace):
    """`excluded` is compared against integer block indices and the file is written by
    hand, so `["0"]` used to exclude nothing at all and say nothing about it — a silent
    no-op on the field whose job is to keep the disclosure out of its own count."""
    wd = workspace("example")
    before = json.loads((wd / "kpi.json").read_text(encoding="utf-8"))["words"]
    annotate(wd, lambda a: a.__setitem__("excluded", [str(i) for i in a["excluded"]]))
    r = run(wd, "measure.py")
    assert r.returncode == 0, r.stdout + r.stderr
    after = json.loads((wd / "kpi.json").read_text(encoding="utf-8"))["words"]
    assert after == before, \
        "a string entry excluded nothing: %d words against %d" % (after, before)


def test_a_span_with_no_attribution_is_named_and_not_a_traceback(workspace):
    """A KeyError says the hand-written file is broken without saying where, at the one
    step this script otherwise explains."""
    wd = workspace("example")

    def strip_one(ann):
        for key, val in ann["blocks"].items():
            if isinstance(val, dict):
                val.pop("lex", None)
                return
        for key, val in ann["blocks"].items():
            if isinstance(val, list):
                val[0].pop("lex", None)
                return

    annotate(wd, strip_one)
    r = run(wd, "measure.py")
    assert r.returncode != 0, r.stdout
    assert "Traceback" not in r.stderr, r.stderr
    assert "has no lex" in (r.stdout + r.stderr), r.stdout + r.stderr
