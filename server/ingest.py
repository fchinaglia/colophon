#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
The write path, and nothing else.

    POST /c    a signed submission, framed as a tar

Reads are served by nginx from static files: this process never touches them. That
separation is not tidiness — it makes the write kill switch a `docker stop`, and a
flooded deposit endpoint leaves every reader unaffected.

Checks run cheapest first, because throttling exists to protect the expensive ones:

    1  Content-Length cap        before a byte of body is read
    2  invite code               a header, checked against a file
    3  signature                 the first tar member, read alone
    4  rate                      a bucket per key fingerprint
    5  filenames                 a closed schema, not arbitrary files
    6  digests                   each file against what the submission declares
    7  chain and manifest        the expensive one, and therefore last

Refusing malformed input at the door is a spam filter. It is NOT a verdict about a
case, and this server never renders one: no badge, no tick, no "verified". It stores
bytes and serves them.
"""
import hashlib
import http.server
import importlib.util
import json
import os
import re
import shutil
import socketserver
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import traceback

DATA = os.environ.get("COLOPHON_DATA", "/data")
PUBLIC = os.path.join(DATA, "public")
PORT = int(os.environ.get("COLOPHON_PORT", "8000"))
MAX_BODY = int(os.environ.get("COLOPHON_MAX_BODY", str(25 * 1024 * 1024)))
MAX_FILES = int(os.environ.get("COLOPHON_MAX_FILES", "200"))
RATE_PER_DAY = int(os.environ.get("COLOPHON_RATE_PER_DAY", "20"))
GLOBAL_PER_HOUR = int(os.environ.get("COLOPHON_GLOBAL_PER_HOUR", "60"))
NAMESPACE = "colophon-deposit"
CASE_ID_RE = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{22}$")

_lock = threading.Lock()

# The canonicalization rule lives in one place. Import it rather than restate it.
_spec = os.environ.get("COLOPHON_SPEC",
                       os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "spec", "check_vectors.py"))
_s = importlib.util.spec_from_file_location("canon", _spec)
canon = importlib.util.module_from_spec(_s)
_s.loader.exec_module(canon)


# ----------------------------------------------------------------- small helpers

def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def read_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def append_line(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, sort_keys=True, ensure_ascii=False) + "\n")


class Refused(Exception):
    """A submission the server will not store. The message goes back to the client."""
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


# ----------------------------------------------------------------- 2. invites

def invite_ok(code):
    path = os.path.join(DATA, "invites.txt")
    if not os.path.exists(path):
        return True                              # no invite file: the gate is open
    if not code:
        return False
    with open(path, encoding="utf-8") as f:
        return code.strip() in {l.strip() for l in f if l.strip()
                                and not l.startswith("#")}


# ----------------------------------------------------------------- 3. signature

def fingerprint_of(pub_line):
    d = tempfile.mkdtemp(prefix="colophon-fp-")
    try:
        p = os.path.join(d, "k.pub")
        with open(p, "w", encoding="utf-8") as f:
            f.write(pub_line.strip() + "\n")
        r = subprocess.run(["ssh-keygen", "-lf", p], capture_output=True, text=True,
                           stdin=subprocess.DEVNULL)
        if r.returncode:
            raise Refused(400, "the public key is unreadable")
        for tok in r.stdout.split():
            if tok.startswith("SHA256:"):
                return tok
        raise Refused(400, "no fingerprint could be derived from the public key")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def verify_signature(body: bytes, armored_sig: str, pub_line: str, identity: str):
    """Prove the body was signed under our namespace by the holder of this key."""
    d = tempfile.mkdtemp(prefix="colophon-verify-")
    try:
        payload = os.path.join(d, "payload")
        sigfile = os.path.join(d, "payload.sig")
        allowed = os.path.join(d, "allowed_signers")
        with open(payload, "wb") as f:
            f.write(body)
        with open(sigfile, "w", encoding="utf-8") as f:
            f.write(armored_sig)
        with open(allowed, "w", encoding="utf-8") as f:
            f.write(f'{identity} namespaces="{NAMESPACE}" {pub_line.strip()}\n')
        with open(payload, "rb") as stdin:
            r = subprocess.run(
                ["ssh-keygen", "-Y", "verify", "-f", allowed, "-I", identity,
                 "-n", NAMESPACE, "-s", sigfile],
                stdin=stdin, capture_output=True, text=True)
        if r.returncode:
            raise Refused(401, "the signature does not verify")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ----------------------------------------------------------------- 4. rate

def rate_ok(fingerprint):
    """A bucket per key, and a global backstop so a mis-tuned per-key limit cannot
    take the instance down on its own."""
    path = os.path.join(DATA, "rate.json")
    now = time.time()
    with _lock:
        state = read_json(path, {})
        mine = [t for t in state.get(fingerprint, []) if now - t < 86400]
        every = [t for v in state.values() for t in v if now - t < 3600]
        if len(mine) >= RATE_PER_DAY:
            raise Refused(429, f"{RATE_PER_DAY} deposits in 24h from this key is the limit")
        if len(every) >= GLOBAL_PER_HOUR:
            raise Refused(429, "this instance is at its hourly limit; try later")
        mine.append(now)
        state[fingerprint] = mine
        state = {k: [t for t in v if now - t < 86400] for k, v in state.items()}
        state = {k: v for k, v in state.items() if v}
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f)
        os.replace(tmp, path)


# ----------------------------------------------------------------- 5/6/7. the case

SEAL_PREFIX = "events.jsonl"
READER = {"index.html", "README.md", "allowed_signers"}


def safe_member(name):
    """No absolute paths, no traversal, no links. A tar is untrusted input."""
    return (not name.startswith("/") and ".." not in name.split("/")
            and not name.startswith("./../"))


def check_files(tmp, submission):
    """5 — a closed schema. 6 — every digest as declared."""
    declared = submission["files"]
    if len(declared) > MAX_FILES:
        raise Refused(413, f"more than {MAX_FILES} files")

    on_disk = set()
    for base, dirs, files in os.walk(tmp):
        for fn in files:
            rel = os.path.relpath(os.path.join(base, fn), tmp)
            if rel != "submission.json":
                on_disk.add(rel)

    extra = on_disk - set(declared)
    if extra:
        raise Refused(400, "files not declared in the submission: "
                           + ", ".join(sorted(extra)[:5]))
    missing = set(declared) - on_disk
    if missing:
        raise Refused(400, "declared files not present: " + ", ".join(sorted(missing)[:5]))

    for rel in sorted(declared):
        with open(os.path.join(tmp, rel), "rb") as f:
            if sha256_bytes(f.read()) != declared[rel]:
                raise Refused(400, f"{rel}: digest does not match the submission")


def check_register(tmp, submission):
    """7 — the expensive one. Recompute the chain, then the manifest.

    This is a spam filter, not a verdict: the server refuses what is not a well-formed
    case, and never tells a reader whether a case is true.
    """
    path = os.path.join(tmp, "events.jsonl")
    if not os.path.exists(path):
        raise Refused(400, "no events.jsonl")
    with open(path, "rb") as f:
        raw = f.read()
    if sha256_bytes(raw) != submission.get("sha256_events"):
        raise Refused(400, "events.jsonl does not match the digest in the submission")

    text = raw.decode("utf-8", "strict")
    lines = [l for l in text.splitlines() if l.strip()]
    prespec = any(canon.is_prespec(l) for l in lines)

    if not prespec:
        prev = "0" * 64
        for i, line in enumerate(lines):
            row = json.loads(line)
            body = {k: v for k, v in row.items() if k != "hash"}
            if body.get("prev") != prev or canon.link(prev, body) != row.get("hash"):
                raise Refused(400, f"the chain breaks at event {i}")
            prev = row["hash"]
        if prev != submission.get("root"):
            raise Refused(400, "the root does not match the submission")

    # the manifest, and the drafts it does not cover
    rows = [json.loads(l) for l in lines]
    manifest = None
    for r in reversed(rows):
        d = (r.get("payload") or {}).get("sha256")
        if isinstance(d, dict):
            manifest = d
            break
    if manifest is None:
        raise Refused(400, "no closing manifest: the signature would commit to the "
                           "register and nothing else")

    covered = set(manifest)
    for rel in submission["files"]:
        if rel.startswith("versions/") and rel not in covered:
            raise Refused(400, f"{rel} is a draft. Only the version the manifest "
                               f"covers may be deposited.")
    for rel, want in manifest.items():
        p = os.path.join(tmp, rel)
        if os.path.exists(p):
            with open(p, "rb") as f:
                if sha256_bytes(f.read()) != want:
                    raise Refused(400, f"{rel} does not match the manifest that seals it")
    return prespec


# ----------------------------------------------------------------- storing

def build_bundle(case_dir):
    """A tar built once, at rest, so nginx only ever serves a static file."""
    out = os.path.join(case_dir, "bundle.tar")
    tmp = out + ".tmp"
    with tarfile.open(tmp, "w", format=tarfile.USTAR_FORMAT) as t:
        for base, dirs, files in os.walk(case_dir):
            for fn in sorted(files):
                full = os.path.join(base, fn)
                rel = os.path.relpath(full, case_dir)
                if rel in ("bundle.tar", "bundle.tar.tmp"):
                    continue
                info = t.gettarinfo(full, arcname=rel)
                info.mtime, info.uid, info.gid = 0, 0, 0
                info.uname = info.gname = ""
                with open(full, "rb") as f:
                    t.addfile(info, f)
    os.replace(tmp, out)


def store(tmp, submission, pub_line, fingerprint, prespec):
    case_id = submission["case_id"]
    dest = os.path.join(PUBLIC, "c", case_id)

    owners_path = os.path.join(DATA, "owners.jsonl")
    owners = {}
    if os.path.exists(owners_path):
        with open(owners_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    owners[r["case_id"]] = r["fingerprint"]
    known = owners.get(case_id)
    if known and known != fingerprint:
        raise Refused(403, "this address belongs to another key")

    staging = dest + ".incoming"
    shutil.rmtree(staging, ignore_errors=True)
    shutil.copytree(tmp, staging)
    os.remove(os.path.join(staging, "submission.json"))
    with open(os.path.join(staging, "submission.json"), "w", encoding="utf-8") as f:
        json.dump({"submission": submission, "public_key": pub_line.strip()},
                  f, indent=1, sort_keys=True)
    build_bundle(staging)

    with _lock:
        if os.path.exists(dest):
            shutil.rmtree(dest + ".old", ignore_errors=True)
            os.replace(dest, dest + ".old")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        os.replace(staging, dest)
        shutil.rmtree(dest + ".old", ignore_errors=True)

        keydir = os.path.join(PUBLIC, "k")
        os.makedirs(keydir, exist_ok=True)
        with open(os.path.join(keydir, fingerprint.replace("/", "_")), "w",
                  encoding="utf-8") as f:
            f.write(pub_line.strip() + "\n")

        if not known:
            append_line(owners_path, {"case_id": case_id, "fingerprint": fingerprint,
                                      "first_seen": int(time.time())})
        # The one genuinely new thing a server can produce: a dated third-party
        # observation that a key was already in use. Hash-chained, so it is itself
        # append-only, and stamped daily by a separate job.
        obs = os.path.join(PUBLIC, "observations.jsonl")
        prev = "0" * 64
        if os.path.exists(obs):
            with open(obs, encoding="utf-8") as f:
                rows = [json.loads(l) for l in f if l.strip()]
            if rows:
                prev = rows[-1]["hash"]
        rec = {"fingerprint": fingerprint, "key": pub_line.strip().split()[1],
               "seen": int(time.time()), "prev": prev}
        rec["hash"] = canon.link(prev, rec)
        append_line(obs, rec)
    return dest, prespec


# ----------------------------------------------------------------- the handler

class Handler(http.server.BaseHTTPRequestHandler):
    server_version = "colophon-ingest"

    def _send(self, status, obj):
        body = json.dumps(obj, indent=1, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):        # no request logging: readers are not
        pass                                   # tracked, and depositors barely

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, {"ok": True})
        self._send(404, {"error": "this process handles POST /c and nothing else"})

    def do_POST(self):
        try:
            if self.path.rstrip("/") != "/c":
                raise Refused(404, "POST /c")
            self._handle()
        except Refused as e:
            self._send(e.status, {"refused": e.message})
        except Exception:                                          # noqa: BLE001
            traceback.print_exc(file=sys.stderr)
            self._send(500, {"error": "internal"})

    def _handle(self):
        # 1 — the cap, before reading a byte
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            raise Refused(411, "Content-Length required")
        if length > MAX_BODY:
            raise Refused(413, f"body over {MAX_BODY} bytes")

        # 2 — the invite
        if not invite_ok(self.headers.get("X-Colophon-Invite")):
            raise Refused(403, "this instance is invite-only while it is being tested")

        body = self.rfile.read(length)
        tmp = tempfile.mkdtemp(prefix="colophon-in-")
        try:
            self._ingest(body, tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def _ingest(self, body, tmp):
        import io
        try:
            tar = tarfile.open(fileobj=io.BytesIO(body), mode="r:")
        except tarfile.TarError:
            raise Refused(400, "the body is not a tar archive")

        members = tar.getmembers()
        if not members or members[0].name != "submission.json":
            raise Refused(400, "submission.json must be the first member")
        for m in members:
            if not m.isfile() or not safe_member(m.name):
                raise Refused(400, f"refused tar member: {m.name}")

        env = json.loads(tar.extractfile(members[0]).read().decode("utf-8"))
        submission = env.get("submission") or {}
        signature = env.get("signature") or ""
        pub_line = env.get("public_key") or ""
        if not CASE_ID_RE.match(submission.get("case_id", "")):
            raise Refused(400, "case_id is not a 22-character base58 address")

        # 3 — the signature, over exactly the bytes the client signed
        fp = fingerprint_of(pub_line)
        if fp != submission.get("key_fingerprint"):
            raise Refused(400, "the key presented is not the one the submission names")
        signed = json.dumps(submission, sort_keys=True, separators=(",", ":"),
                            ensure_ascii=False).encode("utf-8")
        verify_signature(signed, signature, pub_line, "depositor")

        # 4 — the bucket
        rate_ok(fp)

        for m in members[1:]:
            tar.extract(m, tmp, set_attrs=False)
        with open(os.path.join(tmp, "submission.json"), "w", encoding="utf-8") as f:
            json.dump(env, f)

        check_files(tmp, submission)                # 5, 6
        prespec = check_register(tmp, submission)   # 7

        dest, prespec = store(tmp, submission, pub_line, fp, prespec)
        self._send(201, {
            "stored": submission["case_id"],
            "url": f"/c/{submission['case_id']}/",
            "bundle": f"/c/{submission['case_id']}/bundle.tar",
            "files": len(submission["files"]),
            "register": "pre-spec — its chain was not recomputed here; see "
                        "spec/canonical.md §5" if prespec else "chain recomputed",
            "note": "Stored, not endorsed. This instance says nothing about whether "
                    "a case is true; it holds bytes and serves them.",
        })


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    for d in (PUBLIC, os.path.join(PUBLIC, "c"), os.path.join(PUBLIC, "k")):
        os.makedirs(d, exist_ok=True)
    print(f"ingest on :{PORT}  data={DATA}  "
          f"invites={'on' if os.path.exists(os.path.join(DATA, 'invites.txt')) else 'off'}",
          file=sys.stderr, flush=True)
    Server(("", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
