#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Tests for cli/colophon.py. Standard library only, no framework.

    python3 cli/test_cli.py [path-to-colophon-repo]

Runs entirely in a temporary HOME with a throwaway key, so it touches neither your
config nor your real key. Exit 0 if everything passes.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = sys.argv[1] if len(sys.argv) > 1 else "/Users/fabiochinaglia/Projects/colophon"

spec = importlib.util.spec_from_file_location("colophon", os.path.join(HERE, "colophon.py"))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

passed = failed = 0


def ok(cond, label, extra=""):
    global passed, failed
    if cond:
        passed += 1
    else:
        failed += 1
        print(f"  FAIL {label}" + (f"\n       {extra}" if extra else ""))


def head(s):
    print(f"\n{s}")


# --------------------------------------------------------------- base58 / case_id
head("addresses")

# alphabet[0] is "1", so two zero bytes are "11" and the value 1 is "2"
ok(C.b58encode(b"\x00\x00\x01") == "112", "base58 keeps leading zero bytes",
   C.b58encode(b"\x00\x00\x01"))
ok(C.b58encode(bytes([255] * 16)), "base58 encodes 16 bytes")

SECRET = "11" * 32
cid1 = C.case_id(SECRET, "a" * 64)
cid2 = C.case_id(SECRET, "a" * 64)
cid3 = C.case_id(SECRET, "b" * 64)
cid4 = C.case_id("22" * 32, "a" * 64)
ok(cid1 == cid2, "the same secret and root give the same address")
ok(cid1 != cid3, "a different root gives a different address")
ok(cid1 != cid4, "a different secret gives a different address")
ok(len(cid1) == 22, "22 characters", f"got {len(cid1)}: {cid1}")
ok(all(ch in C.B58 for ch in cid1), "base58 alphabet only")
ok("_" not in cid1 and "0" not in cid1 and "O" not in cid1 and "l" not in cid1,
   "no underscore and no look-alike characters", cid1)

# --------------------------------------------------------------- url checks
head("url checks")

ok(C.check_base_url("https://example.com/colophon/") == [], "a good base URL passes")
ok(any("https" in p for p in C.check_base_url("http://example.com/c/")), "rejects http")
ok(any("/" in p for p in C.check_base_url("https://example.com/c")), "wants a trailing /")
ok(any("underscore" in p for p in C.check_base_url("https://example.com/my_cases/")),
   "rejects an underscore in the path")
ok(C.check_base_url("https://my_host.example.com/c/") != [], "rejects it in the host too")

# --------------------------------------------------------------- setup, in a sandbox
head("setup")

home = tempfile.mkdtemp(prefix="colophon-test-home-")
env = dict(os.environ, HOME=home, XDG_CONFIG_HOME=os.path.join(home, ".config"))
key = os.path.join(home, "k")


def run_cli(*args, expect=0):
    r = subprocess.run([sys.executable, os.path.join(HERE, "colophon.py"), *args],
                       capture_output=True, text=True, env=env,
                       stdin=subprocess.DEVNULL)
    ok(r.returncode == expect, f"`colophon {args[0]}` exit {expect}",
       f"got {r.returncode}\n{r.stdout}\n{r.stderr}")
    return r


repo_copy = os.path.join(home, "repo")
os.makedirs(repo_copy)

r = run_cli("setup", "--batch", "--name", "Test Author",
            "--contact", "test@example.com", "--key", key, "--repo", repo_copy)
cfg_path = os.path.join(home, ".config", "colophon", "author.json")
ok(os.path.exists(cfg_path), "config written")
cfg = json.load(open(cfg_path, encoding="utf-8"))
ok(oct(os.stat(cfg_path).st_mode)[-3:] == "600", "config is mode 600 — it holds the secret",
   oct(os.stat(cfg_path).st_mode))
ok(cfg["key_fingerprint"].startswith("SHA256:"), "fingerprint recorded",
   cfg.get("key_fingerprint"))
ok(len(bytes.fromhex(cfg["author_secret"])) == 32, "author_secret is 32 bytes")
ok(cfg["deferred"] is True, "no URLs yet, so recorded as deferred")
ok(os.path.exists(key) and os.path.exists(key + ".pub"), "key generated")

ga = open(os.path.join(repo_copy, ".gitattributes"), encoding="utf-8").read()
ok("cases/** -text" in ga, "wrote the line ending rule into .gitattributes")
ok(os.path.exists(os.path.join(repo_copy, ".nojekyll")), "wrote .nojekyll")

r = run_cli("setup")
ok("Already set up" in r.stdout, "a second setup refuses to clobber the first")

r = run_cli("setup", "--batch", "--force", "--name", "T", "--contact", "t@e.com",
            "--key", key, "--base-url", "https://example.com/bad_path/", expect=1)
ok("underscore" in r.stdout, "setup stops on a bad base URL")

# --------------------------------------------------------------- deposit
head("deposit")

case_src = os.path.join(REPO, "cases", "001")
if not os.path.isdir(case_src):
    print(f"  (skipped: {case_src} not found)")
else:
    case = os.path.join(home, "case")
    shutil.copytree(case_src, case)
    r = run_cli("deposit", case)
    out = json.load(open(os.path.join(case, "submission.json"), encoding="utf-8"))
    sub = out["submission"]

    rows = [json.loads(l) for l in open(os.path.join(case, "events.jsonl"),
                                        encoding="utf-8") if l.strip()]
    ok(sub["root"] == rows[-1]["hash"], "root is the last event's hash")
    ok(sub["case_id"] == C.case_id(cfg["author_secret"], sub["root"]),
       "address is recomputable from the root and the secret")
    ok(sub["key_fingerprint"] == cfg["key_fingerprint"], "carries the fingerprint")

    files = sub["files"]
    ok("events.jsonl" in files, "the register is deposited")
    ok("events.jsonl.sig" in files and "events.jsonl.v1.sig" in files,
       "every seal artifact goes, superseded ones included")
    ok("kpi.json" in files and "annotation.json" in files, "the measurement goes")

    drafts = [f for f in files if f.startswith("versions/")]
    ok(drafts == ["versions/v22_final.txt"],
       "exactly one version — the source the manifest covers", str(drafts))
    ok("versions/v1.txt" not in files, "the drafts are withheld")
    ok("post.pdf" not in files and "post.html" not in files, "renderings are withheld")
    ok("render_post.py" not in files,
       "a script the manifest does not cover is withheld, despite the .py")
    ok("submission.json" not in files, "the submission does not deposit itself")

    # every declared digest is right
    bad = [f for f, d in files.items()
           if C.sha256_file(os.path.join(case, f)) != d]
    ok(not bad, "every declared digest matches the file", str(bad))

    # the signature verifies, under its own namespace and no other
    body = json.dumps(sub, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")
    d = tempfile.mkdtemp()
    payload, sigfile = os.path.join(d, "p"), os.path.join(d, "p.sig")
    open(payload, "wb").write(body)
    open(sigfile, "w", encoding="utf-8").write(out["signature"])
    allowed = os.path.join(d, "allowed_signers")
    open(allowed, "w", encoding="utf-8").write(
        f'test@example.com namespaces="colophon-deposit" '
        f'{open(key + ".pub", encoding="utf-8").read().strip()}\n')

    def verify(ns):
        return subprocess.run(
            ["ssh-keygen", "-Y", "verify", "-f", allowed, "-I", "test@example.com",
             "-n", ns, "-s", sigfile],
            stdin=open(payload, "rb"), capture_output=True, text=True)

    ok(verify("colophon-deposit").returncode == 0, "the submission signature verifies")
    ok(verify("colophon").returncode != 0,
       "it does NOT verify under the register's namespace — namespaces are separated")

    tampered = bytearray(body)
    tampered[-3] ^= 1
    open(payload, "wb").write(bytes(tampered))
    ok(verify("colophon-deposit").returncode != 0, "a tampered submission fails")
    shutil.rmtree(d, ignore_errors=True)

shutil.rmtree(home, ignore_errors=True)
print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
