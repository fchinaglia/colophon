# SPDX-License-Identifier: MIT
"""Things about the repository that must stay true.

These cost nothing and each guards a failure that is silent: a worked example that has
quietly forked from the skill, a documented flag that errors, a missing line that turns a
Windows checkout into a false accusation of forgery.
"""
import os
import re
import subprocess
import sys

import pytest

from conftest import ROOT, SCRIPTS

DOCS = ["skill/colophon/SKILL.md",
        "skill/colophon/reference/disclosures.md",
        "skill/colophon/reference/protocol.md",
        "skill/colophon/reference/VERIFY.md"]


@pytest.mark.parametrize("name", ["record.py", "measure.py", "build_page.py",
                                  "build_icon.py", "build_note.py",
                                  "build_block.py", "build_bundle.py", "build_attestation.py",
                                  "render_md.py", "render_pdf.py", "review.py"])
def test_the_example_has_not_forked_from_the_skill(name):
    """example/ is the worked case a reader runs. If it drifts, the golden tests are
    measuring a copy nobody ships."""
    a = open(os.path.join(SCRIPTS, name), "rb").read()
    b = open(os.path.join(ROOT, "example", name), "rb").read()
    assert a == b, f"example/{name} has drifted from the skill"


@pytest.mark.parametrize("pattern", ["cases/**", "example/**", "tests/**"])
def test_line_endings_are_pinned(pattern):
    """A checkout with core.autocrlf=true rewrites every line ending: every digest
    changes and the signature stops verifying, while `record.py --verify` still answers
    `chain intact`. The first check passes, the second fails, and an honest reader
    concludes the signature is forged."""
    attrs = open(os.path.join(ROOT, ".gitattributes"), encoding="utf-8").read()
    assert re.search(rf"^{re.escape(pattern)}\s+-text\s*$", attrs, re.M), \
        f"{pattern} is not protected in .gitattributes"


def test_every_documented_flag_exists():
    """`--full-root` was documented for weeks and exits with an argparse error."""
    flags = set()
    for doc in DOCS:
        text = open(os.path.join(ROOT, doc), encoding="utf-8").read()
        for m in re.finditer(r"`(--[a-z][a-z-]+)`", text):
            flags.add(m.group(1))
    helps = {}
    for script in ("record.py", "measure.py", "build_page.py", "build_icon.py",
                   "build_note.py", "build_block.py", "build_bundle.py",
                   "build_attestation.py", "render_md.py", "render_pdf.py",
                   "review.py"):
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, script), "--help"],
                           capture_output=True, text=True, stdin=subprocess.DEVNULL)
        helps[script] = r.stdout + r.stderr
    blob = " ".join(helps.values()) + open(os.path.join(SCRIPTS, "record.py"),
                                           encoding="utf-8").read()
    missing = [f for f in sorted(flags) if f not in blob]
    assert not missing, f"documented but not implemented: {missing}"


def test_the_package_matches_the_folder():
    """The zip is what people install; the folder is what gets edited. Nothing keeps
    them in step, so a fix can sit in the repository while every download gets the old
    one."""
    r = subprocess.run([sys.executable, os.path.join(ROOT, "check_package.py")],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_pages_serves_dot_directories_and_has_a_front_page():
    """.nojekyll makes /.well-known servable and stops Jekyll rendering README.md as the
    front page — so the front page has to exist as a file."""
    assert os.path.exists(os.path.join(ROOT, ".nojekyll"))
    assert os.path.exists(os.path.join(ROOT, "index.html"))


@pytest.mark.parametrize("copy", [("skill", "colophon", "verify.html"),
                                  ("cases", "001", "verify.html"),
                                  ("cases", "002", "verify.html")])
def test_every_maintained_verifier_matches_the_built_one(copy):
    """build_bundle.py packs skill/colophon/verify.html into every bundle, and
    cases/NNN/verify.html is what a reader on the published page opens. A stale copy
    would ship an old verifier beside new evidence — and it would still say everything is
    fine, because an old verifier verifies an old case perfectly.

    The copy inside each case's bundle is deliberately not covered here: it is
    sealed, its digest is in a signed manifest, and it is the verifier as it stood when
    that case was closed. It is meant to go stale; these are not."""
    a = open(os.path.join(ROOT, "verifier", "verify.html"), "rb").read()
    b = open(os.path.join(ROOT, *copy), "rb").read()
    assert a == b, f"{'/'.join(copy)} is stale — run python3 verifier/build.py"
