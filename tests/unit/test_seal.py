# SPDX-License-Identifier: MIT
"""seal.sh, entirely offline.

Every branch here is a CHANGELOG entry. The TSA is pointed at a closed port and `ots` is
kept off PATH, so nothing in this file touches the network.
"""
import os
import subprocess

import pytest

from conftest import SCRIPTS, run

ONLY = {"record.py", "seal.sh"}
OFFLINE = {"COLOPHON_TSA": "http://127.0.0.1:9/tsr", "COLOPHON_TSA_TIMEOUT": "2",
           "PATH": "/usr/bin:/bin:/usr/sbin:/sbin"}      # no `ots` on this PATH


def keyed(wd, passphrase=""):
    key = wd / "k"
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-f", str(key),
                    "-N", passphrase, "-C", "colophon"], check=True)
    return {"COLOPHON_KEY": str(key)}


def test_seals_offline_and_leaves_no_truncated_timestamp(workspace):
    wd = workspace("example", only=ONLY)
    r = run(wd, "bash", "seal.sh", "events.jsonl", env={**OFFLINE, **keyed(wd)})
    assert r.returncode == 0, r.stdout + r.stderr
    assert (wd / "events.jsonl.sig").exists()
    assert (wd / "events.jsonl.sha256").exists()
    assert not (wd / "events.jsonl.tsr").exists(), \
        "an unreachable TSA must leave no truncated .tsr behind"


def test_no_key_fails_and_removes_a_stale_signature(workspace):
    """A .sig from an earlier sealing sits beside the register looking exactly like a
    fresh one, and it verifies — against a shorter register. That is the one failure
    this script must not leave behind."""
    wd = workspace("example", only=ONLY)
    (wd / "events.jsonl.sig").write_text("a stale signature\n", encoding="utf-8")
    r = run(wd, "bash", "seal.sh", "events.jsonl",
            env={**OFFLINE, "COLOPHON_KEY": str(wd / "nonexistent")})
    assert r.returncode != 0
    assert not (wd / "events.jsonl.sig").exists(), \
        "the stale signature survived a failed sealing"


def test_a_passphrase_key_with_no_terminal_fails_instead_of_hanging(workspace):
    """With no tty to ask on, ssh-keygen used to block forever. The run must end."""
    wd = workspace("example", only=ONLY)
    env = {**os.environ, **OFFLINE, **keyed(wd, passphrase="secret"), "SSH_AUTH_SOCK": ""}
    try:
        r = subprocess.run(["bash", "seal.sh", "events.jsonl"], cwd=wd, timeout=25,
                           capture_output=True, text=True, stdin=subprocess.DEVNULL,
                           env=env)
    except subprocess.TimeoutExpired:
        pytest.fail("seal.sh hung waiting for a passphrase")
    assert r.returncode != 0
    assert not (wd / "events.jsonl.sig").exists()


def test_the_default_tsa_is_one_a_reader_can_verify():
    """freetsa's tokens chain to nothing a reader already has: `openssl ts -verify`
    against the system bundle answers FAILED on a perfectly valid token."""
    src = open(os.path.join(SCRIPTS, "seal.sh"), encoding="utf-8").read()
    default = src.split("COLOPHON_TSA:-")[1].split("}")[0]
    assert "freetsa" not in default, "the default TSA produces tokens a reader cannot verify"
    assert "digicert" in default


def test_the_bitcoin_anchor_is_not_announced_as_confirmed():
    """The calendars have been observed to accept a submission and never anchor it."""
    src = open(os.path.join(SCRIPTS, "seal.sh"), encoding="utf-8").read()
    assert "confirmed on Bitcoin" not in src
    assert "ots upgrade" in src, "the script must say what turns a submission into evidence"
