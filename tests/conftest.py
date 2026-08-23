# SPDX-License-Identifier: MIT
"""Shared fixtures.

The scripts are not a package and never will be — a case folder carries its own copies,
which is what keeps it verifiable after the skill changes. So they are run as
subprocesses in a copied workspace, exactly as an author runs them, rather than imported.
"""
import os
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skill", "colophon", "scripts")


@pytest.fixture
def workspace(tmp_path):
    """A case folder seeded from a fixture, with today's skill scripts copied in."""
    def build(source, only=None):
        wd = tmp_path / "case"
        src = source if os.path.isabs(source) else os.path.join(ROOT, source)
        shutil.copytree(src, wd)
        for name in os.listdir(SCRIPTS):
            if name.endswith((".py", ".sh")) and (only is None or name in only):
                shutil.copy2(os.path.join(SCRIPTS, name), wd / name)
        return wd
    return build


def run(wd, *argv, env=None, stdin=subprocess.DEVNULL):
    """Always cwd=wd, always no stdin: a script that asks for a passphrase with no
    terminal to ask on hangs, and a hanging test is worse than a failing one."""
    cmd = [sys.executable, *argv] if str(argv[0]).endswith(".py") else list(argv)
    return subprocess.run(cmd, cwd=wd, capture_output=True, text=True, stdin=stdin,
                          env={**os.environ, **(env or {})})
