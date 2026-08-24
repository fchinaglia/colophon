# SPDX-License-Identifier: MIT
"""What reaches the author, and how much of it.

The repository tests behaviour, and prose has three mechanical grips: that a string is
there, that a string is not, and that there is not too much of it. Only the second is
about harm, and it is the one that matters most here.

The honest limit, stated once so nobody mistakes this file for coverage: nothing here
executes a model. These tests cover the strings the scripts print and the volume they
print them in. The sentences the model composes from SKILL.md are unobservable from a
test suite, and that is most of what issue #14 is about.
"""
import ast
import os
import re

import pytest

from conftest import ROOT, SCRIPTS

# None of this is answerable by somebody who has not opened the file it names.
FORBIDDEN = ["manifest", "payload", "span", "seq", "sha256", "Ed25519", "digest",
             "attestation", "denominator", "canonical", "PAdES", "CAdES"]


def author_facing_strings(path, names):
    """String constants the author reads, named rather than swept up: build_bundle.py
    legitimately says *manifest* to whoever is packing, and review.py's T dictionary is
    the thing an author is shown."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id in names:
                    for sub in ast.walk(node.value):
                        if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                            out.append(sub.value)
    return out


def test_the_review_speaks_to_the_author_and_not_about_the_instrument():
    """review.py's T dictionary is everything an author sees at the last read."""
    said = author_facing_strings(os.path.join(SCRIPTS, "review.py"), {"T"})
    assert said, "the T dictionary was not found"
    blob = " ".join(said).lower()
    for word in FORBIDDEN:
        assert word.lower() not in blob, f"the review says {word!r} to the author"


def test_the_red_list_warning_is_three_lines_and_names_no_path():
    """A warning that costs five lines in a conversation where somebody is writing an
    article is an interruption, and a JSON path is a coordinate the author cannot use
    at the moment it is printed."""
    src = open(os.path.join(SCRIPTS, "record.py"), encoding="utf-8").read()
    tail = src[src.index("if redlist_violations(row.get"):]
    assert "payload" not in tail.split('print(')[1].split(', file=')[0]
    assert "for h in" not in tail, "one line per hit, again"


@pytest.mark.parametrize("section,end,budget", [
    ("### 1. Opening", "### 2. While writing", 1200),
    ("### 4. Closing", "## The annotation", 2300),
    ("## What the author hears", "## Before the first case", 400),
    ("## Before the first case", "## The cycle", 500),
])
def test_a_section_of_the_skill_stays_within_its_budget(section, end, budget):
    """Blunt, and the only thing here that would have fired on 24 August, when the
    closing region went from 668 words to 1,943 in one day without anyone deciding to
    let it. A budget is enforceable; "be concise" is not."""
    s = open(os.path.join(ROOT, "skill", "colophon", "SKILL.md"),
             encoding="utf-8").read()
    words = len(s[s.index(section):s.index(end)].split())
    assert words <= budget, f"{section} is {words} words, budget {budget}"
