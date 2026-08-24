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
import tarfile
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
ok(oct(os.stat(cfg_path).st_mode)[-3:] == "600", "config is mode 600",
   oct(os.stat(cfg_path).st_mode))
ok(cfg["key_fingerprint"].startswith("SHA256:"), "fingerprint recorded",
   cfg.get("key_fingerprint"))
ok("author_secret" not in cfg and "base_url" not in cfg,
   "nothing left over from the deposit: both derived an address that no longer exists")
ok(os.path.exists(key) and os.path.exists(key + ".pub"), "key generated")

ga = open(os.path.join(repo_copy, ".gitattributes"), encoding="utf-8").read()
ok("cases/** -text" in ga, "wrote the line ending rule into .gitattributes")
ok(os.path.exists(os.path.join(repo_copy, ".nojekyll")), "wrote .nojekyll")

r = run_cli("setup")
ok("Already set up" in r.stdout, "a second setup refuses to clobber the first")

r = run_cli("setup", "--batch", "--force", "--name", "T", "--contact", "t@e.com",
            "--key", key, "--key-url", "https://example.invalid/nope", expect=1)
ok("Publish the key there first" in r.stdout + r.stderr,
   "a key URL that does not serve this key stops setup")

ok(oct(os.stat(os.path.dirname(cfg_path)).st_mode)[-3:] == "700",
   "the config directory is 0700, not only the file inside it",
   oct(os.stat(os.path.dirname(cfg_path)).st_mode))

shutil.rmtree(home, ignore_errors=True)
print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
