#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
colophon — set up an author, and deposit a sealed case.

    colophon setup                  once, before the first case
    colophon deposit <case-dir>     build and sign a submission

Standard library only, like every script this project ships: a case folder has to
still work in ten years with no `pip install`.

`setup` writes ~/.config/colophon/author.json. That file is a source of defaults,
never an authority — `case.json` remains the per-case record, and it is the one the
manifest covers.
"""
import argparse
import hashlib
import hmac
import io
import json
import os
import re
import secrets
import shutil
import subprocess
import tarfile
import sys
import tempfile
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
    os.makedirs(config_dir(), exist_ok=True)
    tmp = config_path() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, config_path())
    os.chmod(config_path(), 0o600)          # it holds author_secret


# --------------------------------------------------------------------------- base58

# Bitcoin's alphabet: no 0/O, no I/l. The address gets printed in a PDF and retyped
# by hand, and it must survive a URL detector, which cuts a link at an underscore.
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
CASE_ID_LEN = 22


def b58encode(data: bytes) -> str:
    n = int.from_bytes(data, "big")
    out = ""
    while n:
        n, r = divmod(n, 58)
        out = B58[r] + out
    return "1" * (len(data) - len(data.lstrip(b"\0"))) + out


def case_id(author_secret_hex: str, case_uid: str) -> str:
    """The address a case lives at.

        case_id = base58( HMAC-SHA256(author_secret, case_uid)[:16] )   padded to 22

    Derived from an identifier the author fixes when the case is OPENED, not from the
    register's root. That is what makes the address exist before the case is sealed, so
    it can go into case.json and be covered by the manifest — a root-derived address
    cannot, because the root is the hash of the manifest event and the manifest covers
    case.json.

    HMAC rather than a random id, so the author recomputes any case's address from its
    uid and their secret and never has to store a URL. To anyone else it is
    indistinguishable from 128 random bits: holding one address is no help in finding
    another, and there is no author component, so two cases by the same person cannot be
    linked from their addresses.

    What it gives up is that the address no longer commits to the content — but that was
    already given up when the root left the path, and link substitution stays detectable
    from a better anchor: the note prints the root, so the reader compares against the
    article in their hands rather than against the URL somebody sent them.
    """
    mac = hmac.new(bytes.fromhex(author_secret_hex), case_uid.encode("utf-8"),
                   hashlib.sha256).digest()
    return b58encode(mac[:16]).rjust(CASE_ID_LEN, "1")


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


def sign(key_path, namespace, data: bytes) -> str:
    """Detached SSHSIG over `data`, returned armored."""
    d = tempfile.mkdtemp(prefix="colophon-sign-")
    try:
        f = os.path.join(d, "payload")
        with open(f, "wb") as fh:
            fh.write(data)
        r = ssh_keygen("-Y", "sign", "-f", key_path, "-n", namespace, f)
        if r.returncode:
            raise RuntimeError(r.stderr.strip() or "ssh-keygen -Y sign failed")
        with open(f + ".sig", encoding="utf-8") as fh:
            return fh.read()
    finally:
        shutil.rmtree(d, ignore_errors=True)


# --------------------------------------------------------------------------- checks

UNDERSCORE = "an underscore: URL detectors cut a link at the first one, so the address " \
             "arrives at the reader truncated and 404s while the printed line reads right"


def check_base_url(url):
    problems = []
    if not url.startswith("https://"):
        problems.append("it is not https")
    if not url.endswith("/"):
        problems.append("it does not end in / — it is a prefix, each case hangs off it")
    if "_" in url.split("://", 1)[-1]:
        problems.append(UNDERSCORE)
    return problems


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

    # -- the secret that makes an address recomputable
    secret = (cfg or {}).get("author_secret") or secrets.token_hex(32)

    print("\n  Back up BOTH the private key and this config now.")
    print("  The key is your identity: it signs registers and it is what withdraws a")
    print("  deposited case. There is no cryptographic recovery, and there must not be.")
    print("  The config holds author_secret, which is what recomputes a case's address.")

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
        print("  ! no key URL. Recorded as deferred — full mode will refuse to seal")
        print("    until there is one, or until you pass --unpublished explicitly.")
        verified = None

    # -- evidence base
    base_url = a.base_url or ("" if a.batch else prompt(
        "\n  evidence base URL, a prefix like https://example.com/colophon/"))
    if base_url:
        bad = check_base_url(base_url)
        if bad:
            for b in bad:
                print(f"  ! {b}")
            return 1
        print("  This address is a promise. It is rendered into every note and frozen")
        print("  into every PDF. Do not move a case once it is published.")

    cfg = {
        "name": name, "contact": contact, "author_id": author_id or None,
        "key_path": key_path, "key_fingerprint": fp,
        "key_url": key_url or None, "key_url_verified": verified,
        "author_secret": secret,
        "base_url": base_url or None,
        "previous_bases": (cfg or {}).get("previous_bases", []),
        "deferred": not (key_url and base_url),
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


# --------------------------------------------------------------------------- deposit

def read_register(case_dir):
    p = os.path.join(case_dir, "events.jsonl")
    with open(p, "rb") as f:
        raw = f.read()
    rows = [json.loads(l) for l in raw.decode("utf-8").splitlines() if l.strip()]
    if not rows:
        raise RuntimeError("the register is empty")
    if "hash" not in rows[-1]:
        raise RuntimeError("the last event carries no hash")
    return raw, rows


def manifest_of(rows):
    """The closing manifest: the last event carrying a payload.sha256 table."""
    for r in reversed(rows):
        d = (r.get("payload") or {}).get("sha256")
        if isinstance(d, dict):
            return d
    return None


# The manifest is the authority on what belongs to a case: it covers the source
# version, the annotation, the measurement, case.json, the icon, the verification
# page and every script a reader runs. Two things sit outside it and still belong in
# a deposit — the seal artifacts, which cannot be inside a manifest that precedes
# them, and the two reader-facing files the manifest deliberately leaves out.
SEAL_PREFIX = "events.jsonl"
# index.html and README.md are prose the manifest excludes on purpose; allowed_signers
# is the ready-made form of the key a reader feeds to `ssh-keygen -Y verify`, and it is
# there for reproduction, not for trust — the binding to a person lives elsewhere.
READER = {"index.html", "README.md", "allowed_signers"}

# Used only when a case has no manifest at all, which the caller has already warned
# about: better a conservative list than everything on disk.
FALLBACK = {
    "annotation.json", "spans.json", "kpi.json", "case.json", "icon.svg",
    "verification.html", "colophon.pub", "allowed_signers", "VERIFY.md",
    "VERIFICA.md", "LICENSE",
}


def collect(case_dir, manifest):
    """What may be deposited, what may not, and why not.

    Drafts are the reason this exists. `versions/` holds unpublished writing, and the
    register holds briefs and editorial reasoning that may name people who consented
    to nothing. Only the one version the manifest covers goes: it is the published
    text, the one measure.py reconstructs. The register commits to the digests of the
    rest, so they stay attested without being revealed.
    """
    keep, refused = {}, []
    covered = set(manifest or ())
    for base, dirs, files in os.walk(case_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fn in sorted(files):
            if fn.startswith(".") or fn == "submission.json":
                continue
            full = os.path.join(base, fn)
            rel = os.path.relpath(full, case_dir)
            if rel.startswith(SEAL_PREFIX) or rel in READER:
                keep[rel] = full                      # register, seals, landing page
            elif rel in covered or (not manifest and rel in FALLBACK):
                keep[rel] = full
            elif rel.startswith("versions/"):
                refused.append((rel, "a draft"))
            elif rel.lower().endswith((".pdf", ".html", ".md", ".png", ".jpg")):
                refused.append((rel, "a rendering — derivable from what is covered"))
            else:
                refused.append((rel, "not covered by the manifest"))
    return keep, refused


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def cmd_deposit(a):
    cfg = load_config()
    if not cfg:
        print("! not set up yet — run `colophon setup` first.", file=sys.stderr)
        return 1

    case_dir = os.path.abspath(a.case_dir)
    try:
        raw, rows = read_register(case_dir)
    except (OSError, RuntimeError, ValueError) as e:
        print(f"! {case_dir}: {e}", file=sys.stderr)
        return 1

    root = rows[-1]["hash"]
    try:
        case_json = json.load(open(os.path.join(case_dir, "case.json"), encoding="utf-8"))
    except (OSError, ValueError):
        case_json = {}
    uid = a.uid or case_json.get("case_uid")
    if not uid:
        print("! this case has no `case_uid` in case.json, and none was given with --uid.",
              file=sys.stderr)
        print("  The address is derived from it, and it must be fixed when the case is",
              file=sys.stderr)
        print("  opened — before the manifest, which covers case.json.", file=sys.stderr)
        return 1
    cid = case_id(cfg["author_secret"], uid)
    manifest = manifest_of(rows)
    keep, refused = collect(case_dir, manifest)

    if a.mirror:
        print("\n  Mirroring requested. A copy will be pushed to a public archive, and")
        print("  that is permanent: it is what keeps this case reachable if the instance")
        print("  goes away, and it cannot be undone afterwards.")
    print(f"\n  case      {case_dir}")
    print(f"  events    {len(rows)}")
    print(f"  root      {root}")
    print(f"  address   /c/{cid}/")
    if not manifest:
        print("  ! no closing manifest in this register. The signature would commit to")
        print("    the register and nothing else — seal the case properly first.")
        if not a.force:
            return 1

    print(f"\n  depositing {len(keep)} files:")
    for rel in sorted(keep):
        print(f"    {sha256_file(keep[rel])[:12]}…  {rel}")
    if refused:
        print(f"\n  withheld {len(refused)}:")
        for rel, why in sorted(refused):
            print(f"    {rel}  ({why})")
        print("\n  Drafts are never deposited. The register commits to their digests,")
        print("  so they are attested without being revealed — the reader keeps every")
        print("  check and loses only the ability to read your drafts.")

    submission = {
        "case_id": cid,
        "case_uid": uid,
        "mirror": bool(a.mirror),
        "root": root,
        "sha256_events": hashlib.sha256(raw).hexdigest(),
        "files": {rel: sha256_file(p) for rel, p in sorted(keep.items())},
        "key_fingerprint": cfg["key_fingerprint"],
    }
    body = json.dumps(submission, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")

    if a.no_sign:
        sig = None
        print("\n  not signed (--no-sign)")
    else:
        try:
            sig = sign(cfg["key_path"], "colophon-deposit", body)
        except RuntimeError as e:
            print(f"\n! signing failed: {e}", file=sys.stderr)
            return 1
        print(f"\n  signed under namespace colophon-deposit ({len(sig)} bytes armored)")

    with open(cfg["key_path"] + ".pub", encoding="utf-8") as f:
        pub_line = f.read().strip()
    envelope = {"submission": submission, "signature": sig, "public_key": pub_line}

    out = a.out or os.path.join(case_dir, "deposit.tar")
    build_tar(out, envelope, keep, case_dir)
    print(f"  written   {out}  ({os.path.getsize(out):,} bytes)")

    if not a.to:
        print("\n  No instance given. Pass --to <instance> to send it;")
        print("  the address above is already final, because it is derived from the")
        print("  root and your secret, and you can recompute it at any time.")
        return 0

    url = a.to.rstrip("/") + "/c"
    print(f"\n  POST {url}")
    with open(out, "rb") as f:
        payload = f.read()
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/x-tar")
    if a.invite:
        req.add_header("X-Colophon-Invite", a.invite)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            answer = json.loads(r.read().decode("utf-8"))
            status = r.status
    except urllib.error.HTTPError as e:
        answer, status = json.loads(e.read().decode("utf-8") or "{}"), e.code
    except Exception as e:                                          # noqa: BLE001
        print(f"  ! {e}", file=sys.stderr)
        return 1

    if status == 201:
        print(f"  {status}  stored at {a.to.rstrip('/')}{answer.get('url','')}")
        print(f"        bundle: {a.to.rstrip('/')}{answer.get('bundle','')}")
        print(f"        {answer.get('register','')}")
        print(f"\n  {answer.get('note','')}")
        return 0
    print(f"  {status}  refused: {answer.get('refused') or answer}", file=sys.stderr)
    return 1


def build_tar(path, envelope, keep, case_dir):
    """submission.json FIRST, so the server can read it and check the signature
    before extracting anything else — cheapest check first is the whole ordering."""
    tmp = path + ".tmp"
    with tarfile.open(tmp, "w", format=tarfile.USTAR_FORMAT) as t:
        blob = json.dumps(envelope, indent=1, sort_keys=True,
                          ensure_ascii=False).encode("utf-8")
        info = tarfile.TarInfo("submission.json")
        info.size, info.mtime, info.mode = len(blob), 0, 0o644
        t.addfile(info, io.BytesIO(blob))
        for rel in sorted(keep):
            info = t.gettarinfo(keep[rel], arcname=rel)
            info.mtime, info.uid, info.gid = 0, 0, 0
            info.uname = info.gname = ""
            with open(keep[rel], "rb") as f:
                t.addfile(info, f)
    os.replace(tmp, path)


def cmd_address(a):
    """Print where a case will live, given its uid. Run this when the case is opened:
    the answer goes into case.json, and the manifest then covers it."""
    cfg = load_config()
    if not cfg:
        print("! not set up yet — run `colophon setup` first.", file=sys.stderr)
        return 1
    cid = case_id(cfg["author_secret"], a.uid)
    base = (cfg.get("base_url") or "").rstrip("/")
    print(f"  uid      {a.uid}")
    print(f"  case_id  {cid}")
    if base:
        print(f"  url      {base}/c/{cid}/")
    return 0


# --------------------------------------------------------------------------- cli

def main(argv=None):
    p = argparse.ArgumentParser(prog="colophon", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    a2 = sub.add_parser("address", help="the address a case will live at, before it exists")
    a2.add_argument("uid")
    a2.set_defaults(func=cmd_address)

    s = sub.add_parser("setup", help="once, before the first case")
    s.add_argument("--force", action="store_true", help="replace an existing config")
    s.add_argument("--repo", help="repository root to tidy (.gitattributes, .nojekyll)")
    s.add_argument("--key", help="key path (default $COLOPHON_KEY or ~/.ssh/colophon)")
    s.add_argument("--allow-unverified", action="store_true",
                   help="accept a key URL that does not serve this key")
    for f in ("name", "contact", "author-id", "key-url", "base-url"):
        s.add_argument(f"--{f}")
    s.add_argument("--batch", action="store_true", help="no prompts; use the flags")
    s.set_defaults(func=cmd_setup)

    d = sub.add_parser("deposit", help="build and sign a submission")
    d.add_argument("case_dir")
    d.add_argument("--to", help="instance base URL")
    d.add_argument("--invite", help="invite code, while an instance is invite-only")
    d.add_argument("--uid", help="the case uid, if case.json does not carry one")
    d.add_argument("--mirror", action="store_true",
                   help="ask the instance to push a copy to a public archive. Permanent "
                        "and public: it is what makes the instance one location rather "
                        "than the only one, and it is your choice, not its")
    d.add_argument("--out", help="where to write the submission (default: in the case)")
    d.add_argument("--no-sign", action="store_true")
    d.add_argument("--force", action="store_true", help="deposit without a manifest")
    d.set_defaults(func=cmd_deposit)

    a = p.parse_args(argv)
    for attr in ("author_id", "key_url", "base_url"):
        if not hasattr(a, attr):
            setattr(a, attr, None)
    try:
        return a.func(a)
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
