# SPDX-License-Identifier: MIT
"""build_bundle.py — the tar that replaces the deposit.

The bundle is the whole delivery now, so every refusal here guards a case that would
travel looking complete and be less than it looks: unsealed, unmanifested, or missing
the tool that reads it.
"""
import hashlib
import json
import os
import subprocess
import tarfile

import pytest

from conftest import ROOT, run

ONLY = {"record.py", "seal.sh", "build_bundle.py"}
OFFLINE = {"COLOPHON_TSA": "http://127.0.0.1:9/tsr", "COLOPHON_TSA_TIMEOUT": "2",
           "PATH": "/usr/bin:/bin:/usr/sbin:/sbin"}      # no `ots` on this PATH
VERIFIER = os.path.join(ROOT, "verifier", "verify.html")


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


@pytest.fixture
def sealed(workspace, tmp_path):
    """A case carried all the way to the seal: manifest recorded, register signed."""
    wd = workspace("example", only=ONLY)
    covered = {}
    for base, dirs, files in os.walk(wd):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fn in sorted(files):
            rel = os.path.relpath(os.path.join(base, fn), wd)
            if rel != "events.jsonl" and not fn.startswith("."):
                covered[rel] = sha256(os.path.join(base, fn))
    event = {"type": "status", "actor": "system", "phase": "—", "meta": True,
             "payload": {"closing": "MANIFEST", "algorithm": "sha256", "sha256": covered}}
    r = run(wd, "record.py", json.dumps(event, ensure_ascii=False))
    assert r.returncode == 0, r.stdout + r.stderr

    key = tmp_path / "k"
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-f", str(key), "-N", "",
                    "-C", "colophon"], check=True)
    r = run(wd, "bash", "seal.sh", "events.jsonl",
            env={**OFFLINE, "COLOPHON_KEY": str(key)})
    assert r.returncode == 0, r.stdout + r.stderr
    return wd


UID = "example-case"


def pack(wd, out, *extra):
    return run(wd, "build_bundle.py", ".", "-o", str(out), "--verifier", VERIFIER,
               "--uid", UID, *extra)


def test_packs_a_sealed_case_and_the_verifier_travels(sealed, tmp_path):
    out = tmp_path / "out"
    r = pack(sealed, out)
    assert r.returncode == 0, r.stdout + r.stderr
    tar = out / f"colophon-{UID}.tar"
    assert tar.exists(), r.stdout
    with tarfile.open(tar) as t:
        names = t.getnames()
    assert "events.jsonl" in names
    assert "events.jsonl.sig" in names, "a bundle without its seal proves nothing about who"
    assert "verify.html" in names, "the reader needs the tool, not a link to it"


def test_the_tar_is_flat(sealed, tmp_path):
    """verify.html strips one leading directory component only when every entry shares
    it. A top-level folder plus verify.html beside it strips nothing, and every lookup
    inside core.js then misses."""
    out = tmp_path / "out"
    assert pack(sealed, out).returncode == 0
    with tarfile.open(out / f"colophon-{UID}.tar") as t:
        names = t.getnames()
    roots = {n.split("/")[0] for n in names}
    assert len(roots) > 1, f"the tar has a single top-level component: {roots}"


def test_drafts_never_travel(sealed, tmp_path):
    out = tmp_path / "out"
    assert pack(sealed, out).returncode == 0
    with tarfile.open(out / f"colophon-{UID}.tar") as t:
        names = t.getnames()
    covered = json.loads(open(os.path.join(sealed, "events.jsonl"),
                              encoding="utf-8").read().splitlines()[-1])
    covered = set(covered["payload"]["sha256"])
    drafts = [n for n in names if n.startswith("versions/")]
    assert drafts, "the version the manifest covers has to travel: it is the measured text"
    assert all(n in covered for n in drafts), \
        f"an uncovered draft is in the bundle: {[n for n in drafts if n not in covered]}"


def test_two_authors_packing_one_case_get_the_same_bytes(sealed, tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    assert pack(sealed, a).returncode == 0
    assert pack(sealed, b).returncode == 0
    assert sha256(a / f"colophon-{UID}.tar") == sha256(b / f"colophon-{UID}.tar")


def test_refuses_to_write_inside_the_case(sealed):
    """The next run would withhold the tar as a file no manifest covers, and the one
    after that would pack the previous tar into the new one."""
    r = pack(sealed, sealed / "out")
    assert r.returncode == 1
    assert "inside the case folder" in r.stderr


def test_refuses_an_unsealed_case(sealed, tmp_path):
    os.remove(sealed / "events.jsonl.sig")
    r = pack(sealed, tmp_path / "out")
    assert r.returncode == 1
    assert "not signed" in r.stdout + r.stderr


def test_refuses_a_case_with_no_manifest(workspace, tmp_path):
    wd = workspace("example", only=ONLY)
    r = pack(wd, tmp_path / "out")
    assert r.returncode == 1
    assert "no closing manifest" in r.stdout + r.stderr


def test_refuses_when_no_verifier_can_be_found(sealed, tmp_path):
    """A bundle silently missing its reader looks exactly like a complete one."""
    lone = tmp_path / "lone"
    lone.mkdir()
    os.link(os.path.join(ROOT, "skill", "colophon", "scripts", "build_bundle.py"),
            lone / "build_bundle.py")
    r = run(sealed, str(lone / "build_bundle.py"), ".", "-o", str(tmp_path / "out"))
    assert r.returncode == 1
    assert "no verify.html found" in r.stderr


def test_force_packs_an_unsealed_case_and_says_so(sealed, tmp_path):
    os.remove(sealed / "events.jsonl.sig")
    r = pack(sealed, tmp_path / "out", "--force")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "not signed" in r.stdout


def test_the_bundle_is_named_after_the_case_not_the_folder(sealed, tmp_path):
    """Once the tar is detached from the folder that made it, its name is all that says
    which case it is."""
    out = tmp_path / "out"
    assert pack(sealed, out).returncode == 0
    assert (out / f"colophon-{UID}.tar").exists()


def test_a_case_with_no_uid_falls_back_and_warns(sealed, tmp_path):
    r = run(sealed, "build_bundle.py", ".", "-o", str(tmp_path / "out"),
            "--verifier", VERIFIER)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "no case_uid" in r.stdout
    assert (tmp_path / "out" / "colophon-case.tar").exists()
