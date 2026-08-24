#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
colophon — set up an author.

    colophon setup                  once, before the first case

One command, and it does one thing: make a signing key, and check that the place you
say you publish it really serves it. Everything else a case needs is in the case
folder, run from there, by the scripts the skill copies in.

`deposit` used to live here. It is gone with the instance it talked to: a case now
travels as a bundle its author packs — `build_bundle.py` in the case folder — and
nothing has to stay online for a reader to check it. The reasoning is in
docs/plan-local-first.md.

Standard library only, like every script this project ships: a case folder has to
still work in ten years with no `pip install`.

`setup` writes ~/.config/colophon/author.json. That file is a source of defaults,
never an authority — `case.json` remains the per-case record, and it is the one the
manifest covers.
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

# --------------------------------------------------------------------------- paths

def config_dir():
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(base, "colophon")


def config_path():
    return os.path.join(config_dir(), "author.json")


def load_config():
    try:
        with open(config_path(), encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def save_config(cfg):
    # The directory too, not only the file. makedirs applies the process umask to its
    # mode, so it comes out 0755 and the chmod is not redundant — and what lives in
    # here is not only this file: a case's red list is named after its case_uid, which
    # is a public name, so a world-traversable directory would leak the very thing the
    # list exists to keep out of the record.
    os.makedirs(config_dir(), exist_ok=True)
    os.chmod(config_dir(), 0o700)
    tmp = config_path() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, config_path())
    os.chmod(config_path(), 0o600)


# --------------------------------------------------------------------------- ssh

def ssh_keygen(*args, **kw):
    return subprocess.run(["ssh-keygen", *args], capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, **kw)


def fingerprint(pub_path):
    r = ssh_keygen("-lf", pub_path)
    if r.returncode:
        raise RuntimeError(r.stderr.strip() or "ssh-keygen -lf failed")
    for tok in r.stdout.split():
        if tok.startswith("SHA256:"):
            return tok
    raise RuntimeError(f"no fingerprint in: {r.stdout.strip()}")


def key_blob(pub_path):
    """The base64 key material from a .pub line — what must match what is published."""
    with open(pub_path, encoding="utf-8") as f:
        parts = f.read().split()
    for i, p in enumerate(parts):
        if p.startswith("ssh-") and i + 1 < len(parts):
            return parts[i + 1]
    raise RuntimeError(f"{pub_path} does not look like a public key")


# --------------------------------------------------------------------------- checks

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "colophon-setup"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def check_key_url(url, pub_path):
    """Fetch the published key and compare the key material byte for byte.

    One HTTP GET, and it is the most valuable check in the flow: it is the one nobody
    performed for the first published case, whose key was published inside the very
    repository it authenticates.
    """
    try:
        body = fetch(url)
    except urllib.error.HTTPError as e:
        return f"the address answered HTTP {e.code}"
    except Exception as e:                                     # noqa: BLE001
        return f"could not fetch it: {e}"
    return None if key_blob(pub_path) in body else \
        "it is reachable, but the key published there is not this key"


# --------------------------------------------------------------------------- setup

KEY_URL_MENU = """  Where will the key be published? Strongest first:
    1  https://<your-domain>/.well-known/colophon/keys   a domain you control
    2  https://api.github.com/users/<you>/ssh_signing_keys   corroborating, mutable
    3  a deposit instance                                 convenience copy, not an anchor
    4  not yet"""


def cmd_setup(a):
    cfg = load_config()
    if cfg and not a.force:
        print(f"Already set up: {config_path()}")
        print(f"  {cfg.get('name')} <{cfg.get('contact')}>  {cfg.get('key_fingerprint')}")
        print("Re-run with --force to replace it.")
        return 0

    def prompt(label, default="", attr=None):
        if a.batch:
            return (getattr(a, attr, None) if attr else None) or default
        v = input(f"  {label}{f' [{default}]' if default else ''}: ").strip()
        return v or default

    print("\ncolophon setup — runs once, before the first case.\n")

    name = prompt("your name", a.name or "", "name")
    contact = prompt("contact email", a.contact or "", "contact")
    author_id = prompt("ORCID or domain (optional)", a.author_id or "", "author_id")
    if not name or not contact:
        print("! name and contact are both required: VERIFY.md and allowed_signers "
              "each need one.", file=sys.stderr)
        return 1

    # -- key
    key_path = a.key or os.environ.get("COLOPHON_KEY") or os.path.expanduser("~/.ssh/colophon")
    pub_path = key_path + ".pub"
    if os.path.exists(key_path):
        print(f"\n  key: reusing {key_path}")
    else:
        print(f"\n  key: generating {key_path}")
        print("  A passphrase is safer. It also makes seal.sh stop and ask, and a script")
        print("  with no terminal to ask on simply hangs — so if you set one, add the key")
        print("  to your agent before sealing.")
        os.makedirs(os.path.dirname(key_path), exist_ok=True)
        args = ["-t", "ed25519", "-f", key_path, "-C", "colophon"]
        if a.batch:
            args += ["-N", ""]
            r = ssh_keygen(*args)
        else:
            r = subprocess.run(["ssh-keygen", *args])
        if r.returncode:
            print("! ssh-keygen failed", file=sys.stderr)
            return 1
    fp = fingerprint(pub_path)
    print(f"  fingerprint: {fp}")

    print("\n  Back up the private key now. It is your identity: it signs registers,")
    print("  and a register nobody can attribute is a register nobody has to believe.")
    print("  There is no cryptographic recovery, and there must not be.")

    # -- key url
    key_url = a.key_url or ""
    if not a.batch:
        print("\n" + KEY_URL_MENU)
        key_url = prompt("key URL (blank = not yet)")
    if key_url:
        problem = check_key_url(key_url, pub_path)
        if problem:
            print(f"  ! {problem}")
            if not a.allow_unverified:
                print("    Publish the key there first, then re-run. A key nobody can")
                print("    fetch is a key nobody can bind to you.", file=sys.stderr)
                return 1
            print("    continuing anyway (--allow-unverified)")
            verified = None
        else:
            print("  key URL verified: the published key is this key")
            verified = True
    else:
        print("  ! no key URL. A register signed by a key nobody can fetch proves that")
        print("    the folder is consistent with itself, which anyone arranges in ten")
        print("    seconds. Publish the key and re-run: it is once, not per case.")
        verified = None

    cfg = {
        "name": name, "contact": contact, "author_id": author_id or None,
        "key_path": key_path, "key_fingerprint": fp,
        "key_url": key_url or None, "key_url_verified": verified,
    }
    save_config(cfg)
    print(f"\n  written: {config_path()}  (mode 600)")
    return tidy(a.repo) if a.repo else 0


def tidy(repo):
    """The two files whose absence produces a failure nobody diagnoses."""
    ga = os.path.join(repo, ".gitattributes")
    line = "cases/** -text"
    have = os.path.exists(ga) and line in open(ga, encoding="utf-8").read()
    if not have:
        with open(ga, "a", encoding="utf-8") as f:
            f.write(("" if not os.path.exists(ga) or open(ga, encoding="utf-8")
                     .read().endswith("\n") else "\n") + line + "\n")
    print(f"  .gitattributes: {'already had' if have else 'added'} `{line}`")
    print("    Without it a checkout with core.autocrlf=true rewrites every line ending,")
    print("    every digest changes and the signature stops verifying — while")
    print("    `record.py --verify` still answers `chain intact`.")
    nj = os.path.join(repo, ".nojekyll")
    if not os.path.exists(nj):
        open(nj, "w").close()
    print(f"  .nojekyll: {'present' if os.path.exists(nj) else 'added'}"
          " — Pages will not serve dot-directories without it")
    return 0


# --------------------------------------------------------------------------- cli

def main(argv=None):
    p = argparse.ArgumentParser(prog="colophon", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("setup", help="once, before the first case")
    s.add_argument("--force", action="store_true", help="replace an existing config")
    s.add_argument("--repo", help="repository root to tidy (.gitattributes, .nojekyll)")
    s.add_argument("--key", help="key path (default $COLOPHON_KEY or ~/.ssh/colophon)")
    s.add_argument("--allow-unverified", action="store_true",
                   help="accept a key URL that does not serve this key")
    for f in ("name", "contact", "author-id", "key-url"):
        s.add_argument(f"--{f}")
    s.add_argument("--batch", action="store_true", help="no prompts; use the flags")
    s.set_defaults(func=cmd_setup)

    a = p.parse_args(argv)
    try:
        return a.func(a)
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
