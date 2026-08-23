#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
The whole loop, against a live ingest process. No Docker needed.

    python3 server/test_server.py [path-to-colophon-repo]

Starts ingest.py on a free port with a throwaway data directory, sets up an author in
a throwaway HOME, deposits a real case, and then tries to break it.
"""
import io
import json
import os
import shutil
import socket
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO = sys.argv[1] if len(sys.argv) > 1 else "/Users/fabiochinaglia/Projects/colophon"
CLI = os.path.join(ROOT, "cli", "colophon.py")

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


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def post(url, body, invite=None):
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/x-tar")
    if invite:
        req.add_header("X-Colophon-Invite", invite)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            return e.code, json.loads(raw)
        except ValueError:
            return e.code, {"raw": raw}


# --------------------------------------------------------------------- fixtures
home = tempfile.mkdtemp(prefix="colophon-srv-home-")
data = tempfile.mkdtemp(prefix="colophon-srv-data-")
port = free_port()
base = f"http://127.0.0.1:{port}"
env = dict(os.environ, HOME=home, XDG_CONFIG_HOME=os.path.join(home, ".config"))
key = os.path.join(home, "k")

srv = subprocess.Popen(
    [sys.executable, os.path.join(HERE, "ingest.py")],
    env=dict(os.environ, COLOPHON_DATA=data, COLOPHON_PORT=str(port),
             COLOPHON_SPEC=os.path.join(ROOT, "spec", "check_vectors.py")),
    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)

for _ in range(60):
    try:
        urllib.request.urlopen(f"{base}/health", timeout=1).read()
        break
    except Exception:                                              # noqa: BLE001
        time.sleep(0.1)
else:
    print("the server never came up:\n" + (srv.stderr.read() if srv.stderr else ""))
    sys.exit(1)


def cleanup():
    srv.terminate()
    try:
        srv.wait(timeout=5)
    except subprocess.TimeoutExpired:
        srv.kill()
    shutil.rmtree(home, ignore_errors=True)
    shutil.rmtree(data, ignore_errors=True)


try:
    head("setup and a first deposit")
    subprocess.run([sys.executable, CLI, "setup", "--batch", "--name", "Test",
                    "--contact", "t@example.com", "--key", key],
                   env=env, capture_output=True, text=True, check=True)

    case = os.path.join(home, "case")
    shutil.copytree(os.path.join(REPO, "cases", "001"), case)
    r = subprocess.run([sys.executable, CLI, "deposit", case, "--uid", "srv-test", "--to", base],
                       env=env, capture_output=True, text=True)
    ok(r.returncode == 0, "deposit --to succeeds", r.stdout + r.stderr)

    with tarfile.open(os.path.join(case, "deposit.tar")) as tf:
        env_json = json.loads(tf.extractfile("submission.json").read().decode("utf-8"))
        tar_bytes = open(os.path.join(case, "deposit.tar"), "rb").read()
    sub = env_json["submission"]
    cid = sub["case_id"]

    stored = os.path.join(data, "public", "c", cid)
    ok(os.path.isdir(stored), "the case is on disk at its opaque address", stored)
    ok(not any(f.startswith("versions/v1.txt") for f in sub["files"]),
       "no drafts were sent in the first place")

    head("what the instance now serves")
    ok(os.path.exists(os.path.join(stored, "events.jsonl")), "the register is stored")
    ok(os.path.exists(os.path.join(stored, "bundle.tar")), "a bundle was built at rest")
    with tarfile.open(os.path.join(stored, "bundle.tar")) as tf:
        names = set(tf.getnames())
    ok(set(sub["files"]) <= names, "the bundle carries every deposited file",
       str(sorted(set(sub["files"]) - names))[:120])
    ok("bundle.tar" not in names, "the bundle does not contain itself")

    with open(os.path.join(stored, "events.jsonl"), "rb") as f:
        import hashlib
        ok(hashlib.sha256(f.read()).hexdigest() == sub["sha256_events"],
           "the stored register is byte-identical to what was signed")

    owners = [json.loads(l) for l in
              open(os.path.join(data, "owners.jsonl"), encoding="utf-8") if l.strip()]
    ok(owners and owners[0]["case_id"] == cid, "ownership recorded privately")
    ok(not os.path.exists(os.path.join(data, "public", "owners.jsonl")),
       "the owner map is NOT under public/ — the path must not reveal the author")

    obs = [json.loads(l) for l in
           open(os.path.join(data, "public", "observations.jsonl"), encoding="utf-8")
           if l.strip()]
    ok(len(obs) == 1 and obs[0]["prev"] == "0" * 64,
       "the key observation log starts from genesis")
    ok("hash" in obs[0], "and it is hash-chained")

    head("refusals")

    s, a = post(f"{base}/c", b"not a tar at all")
    ok(s == 400 and "tar" in str(a.get("refused", "")), "a body that is not a tar", str(a))

    # a file in the tar that the submission never declared
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as t:
        with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as src:
            for m in src.getmembers():
                t.addfile(m, src.extractfile(m))
        info = tarfile.TarInfo("versions/v1.txt")
        info.size = 5
        t.addfile(info, io.BytesIO(b"draft"))
    s, a = post(f"{base}/c", buf.getvalue())
    ok(s == 400 and "not declared" in str(a.get("refused", "")),
       "a draft smuggled into the tar", str(a))

    # the submission edited after signing
    tampered = json.loads(json.dumps(env_json))
    tampered["submission"]["files"]["kpi.json"] = "0" * 64
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as t:
        blob = json.dumps(tampered, indent=1, sort_keys=True).encode("utf-8")
        info = tarfile.TarInfo("submission.json")
        info.size = len(blob)
        t.addfile(info, io.BytesIO(blob))
        with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as src:
            for m in src.getmembers()[1:]:
                t.addfile(m, src.extractfile(m))
    s, a = post(f"{base}/c", buf.getvalue())
    ok(s == 401, "a submission edited after signing", f"{s} {a}")

    # submission.json not first
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as t:
        with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as src:
            ms = src.getmembers()
            for m in ms[1:] + ms[:1]:
                t.addfile(m, src.extractfile(m))
    s, a = post(f"{base}/c", buf.getvalue())
    ok(s == 400 and "first" in str(a.get("refused", "")),
       "submission.json anywhere but first", str(a))

    head("the address belongs to one key")
    key2 = os.path.join(home, "k2")
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-f", key2, "-N", "",
                    "-C", "other"], check=True)
    home2 = tempfile.mkdtemp(prefix="colophon-srv-home2-")
    env2 = dict(os.environ, HOME=home2, XDG_CONFIG_HOME=os.path.join(home2, ".config"))
    subprocess.run([sys.executable, CLI, "setup", "--batch", "--name", "Other",
                    "--contact", "o@example.com", "--key", key2],
                   env=env2, capture_output=True, check=True)
    cfg2 = json.load(open(os.path.join(home2, ".config", "colophon", "author.json"),
                          encoding="utf-8"))
    cfg2["author_secret"] = json.load(open(
        os.path.join(home, ".config", "colophon", "author.json"),
        encoding="utf-8"))["author_secret"]          # same address, different key
    json.dump(cfg2, open(os.path.join(home2, ".config", "colophon", "author.json"), "w"))
    case2 = os.path.join(home2, "case")
    shutil.copytree(os.path.join(REPO, "cases", "001"), case2)
    r = subprocess.run([sys.executable, CLI, "deposit", case2, "--uid", "srv-test", "--to", base],
                       env=env2, capture_output=True, text=True)
    ok(r.returncode != 0 and "another key" in (r.stdout + r.stderr),
       "a second key cannot overwrite the first's address", (r.stdout + r.stderr)[-200:])
    shutil.rmtree(home2, ignore_errors=True)

    head("the invite gate")
    with open(os.path.join(data, "invites.txt"), "w", encoding="utf-8") as f:
        f.write("# trial\nLETMEIN\n")
    s, a = post(f"{base}/c", tar_bytes)
    ok(s == 403, "no code, once invites.txt exists", f"{s} {a}")
    s, a = post(f"{base}/c", tar_bytes, invite="WRONG")
    ok(s == 403, "a wrong code", f"{s} {a}")
    s, a = post(f"{base}/c", tar_bytes, invite="LETMEIN")
    ok(s == 201, "the right code, and the same case re-deposited by its owner",
       f"{s} {a}")

    head("mirroring is opt-in, and its failure is not the deposit's failure")
    # A base that will never answer: the archive request must fail, and the deposit
    # must still be stored. Mirroring is a promise about the future, not a gate.
    home3 = tempfile.mkdtemp(prefix="colophon-srv-home3-")
    env3 = dict(os.environ, HOME=home3, XDG_CONFIG_HOME=os.path.join(home3, ".config"))
    subprocess.run([sys.executable, CLI, "setup", "--batch", "--name", "Mirror",
                    "--contact", "m@example.com", "--key", os.path.join(home3, "k")],
                   env=env3, capture_output=True, check=True)
    case3 = os.path.join(home3, "case")
    shutil.copytree(os.path.join(REPO, "cases", "001"), case3)
    r = subprocess.run([sys.executable, CLI, "deposit", case3, "--uid", "srv-mirror", "--to", base, "--mirror",
                        "--invite", "LETMEIN"], env=env3, capture_output=True, text=True)
    ok(r.returncode == 0, "a deposit with --mirror still succeeds", r.stdout[-300:])
    ok("permanent" in r.stdout,
       "and the client says plainly that archiving cannot be undone")
    with tarfile.open(os.path.join(case3, "deposit.tar")) as tf:
        s3 = json.loads(tf.extractfile("submission.json").read())["submission"]
    ok(s3.get("mirror") is True,
       "the choice travels INSIDE the signed submission, so the instance cannot make it")
    stored3 = os.path.join(data, "public", "c", s3["case_id"])
    ok(os.path.exists(os.path.join(stored3, "events.jsonl")),
       "the case is stored even though no mirror could be reached")
    shutil.rmtree(home3, ignore_errors=True)

    head("what the server says about a case")
    ok("note" in a and "not endorsed" in a["note"],
       "it says it stores rather than endorses", str(a.get("note")))
    ok("pre-spec" in a.get("register", ""),
       "and reports cases/001's register as pre-spec, not as broken",
       str(a.get("register")))

finally:
    err = ""
    cleanup()

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
