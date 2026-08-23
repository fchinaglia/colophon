# SPDX-License-Identifier: MIT
"""The two checks that must stop the pipeline.

Each of these is a CHANGELOG entry: a regression that has already happened once. The
danger they guard is not manipulation, it is drift — an annotation falling behind a text
that still reconstructs, which is why a passing reconstruction is not enough on its own.
"""
import json

from conftest import run


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
