#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Acceptance test 3 — the whole loop, with nothing typed by hand.

    setup  ->  deposit --to  ->  fetch bundle.tar from the instance  ->  verify it

    python3 server/test_loop.py [path-to-colophon-repo]

The read path here is a plain static file server standing in for nginx: it proves the
bytes survive storage and transport, not that the nginx configuration is right. The
compose stack needs a Docker daemon and is not exercised here.
"""
import hashlib
import http.server
import json
import os
import shutil
import socket
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO = sys.argv[1] if len(sys.argv) > 1 else "/Users/fabiochinaglia/Projects/colophon"
CLI = os.path.join(ROOT, "cli", "colophon.py")

steps, bad = [], 0


def step(label, detail=""):
    steps.append((label, detail))
    print(f"  {label}" + (f"\n      {detail}" if detail else ""))


def fail(label, detail=""):
    global bad
    bad += 1
    print(f"  FAIL {label}" + (f"\n      {detail}" if detail else ""))


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


home = tempfile.mkdtemp(prefix="colophon-loop-home-")
data = tempfile.mkdtemp(prefix="colophon-loop-data-")
write_port, read_port = free_port(), free_port()
env = dict(os.environ, HOME=home, XDG_CONFIG_HOME=os.path.join(home, ".config"))
key = os.path.join(home, "k")
public = os.path.join(data, "public")
os.makedirs(public, exist_ok=True)

ingest = subprocess.Popen(
    [sys.executable, os.path.join(HERE, "ingest.py")],
    env=dict(os.environ, COLOPHON_DATA=data, COLOPHON_PORT=str(write_port),
             COLOPHON_SPEC=os.path.join(ROOT, "spec", "check_vectors.py")),
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class Reads(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=public, **kw)

    def log_message(self, *a):
        pass


reads = http.server.ThreadingHTTPServer(("127.0.0.1", read_port), Reads)
threading.Thread(target=reads.serve_forever, daemon=True).start()

for _ in range(60):
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{write_port}/health", timeout=1).read()
        break
    except Exception:                                              # noqa: BLE001
        time.sleep(0.1)

try:
    print("\nthe loop\n")

    r = subprocess.run([sys.executable, CLI, "setup", "--batch", "--name", "Loop",
                        "--contact", "loop@example.com", "--key", key],
                       env=env, capture_output=True, text=True)
    if r.returncode:
        fail("setup", r.stderr)
    else:
        step("1. setup", f"key {os.path.basename(key)}, config in a throwaway HOME")

    case = os.path.join(home, "case")
    shutil.copytree(os.path.join(REPO, "cases", "001"), case)

    r = subprocess.run([sys.executable, CLI, "deposit", case,
                        "--to", f"http://127.0.0.1:{write_port}"],
                       env=env, capture_output=True, text=True)
    if r.returncode:
        fail("deposit", r.stdout + r.stderr)
        raise SystemExit(1)
    with tarfile.open(os.path.join(case, "deposit.tar")) as tf:
        sub = json.loads(tf.extractfile("submission.json").read())["submission"]
    cid = sub["case_id"]
    step("2. deposit --to", f"stored at /c/{cid}/  ({len(sub['files'])} files)")

    url = f"http://127.0.0.1:{read_port}/c/{cid}/bundle.tar"
    with urllib.request.urlopen(url, timeout=30) as resp:
        bundle = resp.read()
    step("3. fetch the bundle", f"{len(bundle):,} bytes from {url.split('/c/')[0]}/c/…")

    # the register must come back byte-identical to what was signed
    with tarfile.open(fileobj=__import__("io").BytesIO(bundle)) as tf:
        got = {m.name: tf.extractfile(m).read() for m in tf.getmembers() if m.isfile()}
    reg = got.get("events.jsonl")
    if reg is None:
        fail("the bundle has no register")
    elif hashlib.sha256(reg).hexdigest() != sub["sha256_events"]:
        fail("the register changed in transit")
    else:
        step("4. bytes survived", f"sha256 {sub['sha256_events'][:24]}… unchanged "
                                  f"through storage and transport")

    # 5 — the verifier, exactly as a reader would run it
    harness = os.path.join(home, "run.js")
    with open(harness, "w", encoding="utf-8") as f:
        f.write(f"""
const fs=require('fs'),C=require({json.dumps(os.path.join(ROOT,'verifier','core.js'))});
const b=new Uint8Array(fs.readFileSync({json.dumps(os.path.join(home,'bundle.tar'))}));
const td=new TextDecoder(); const files=new Map(); let off=0;
while(off+512<=b.length){{
  const name=td.decode(b.subarray(off,off+100)).replace(/\\0.*$/,'');
  if(!name){{off+=512;continue;}}
  const size=parseInt(td.decode(b.subarray(off+124,off+136)).replace(/\\0.*$/,'').trim(),8)||0;
  const type=String.fromCharCode(b[off+156]); off+=512;
  if(type==='0'||type==='\\0') files.set(name,b.subarray(off,off+size));
  off+=Math.ceil(size/512)*512;
}}
const r=C.verifyCase(files);
console.log(JSON.stringify({{
  files:r.files,
  chain: r.chain.ok?'intact':(r.chain.preSpec?'pre-spec':'broken'),
  preSpecEvents: r.chain.preSpec?r.chain.preSpec.length:0,
  signature: r.signature? (r.signature.ok?'valid':'invalid') : 'absent',
  manifest: r.manifest? [r.manifest.matched.length, r.manifest.mismatched.length,
                         r.manifest.missing.length] : null,
  timestamp: r.timestamp? (r.timestamp.commits||'no match') : 'absent',
  notComputed: r.notes,
}}));
""")
    with open(os.path.join(home, "bundle.tar"), "wb") as f:
        f.write(bundle)
    r = subprocess.run(["node", harness], capture_output=True, text=True)
    if r.returncode:
        fail("the verifier", r.stderr[-400:])
    else:
        v = json.loads(r.stdout)
        step("5. verify", json.dumps(v, indent=None))
        if v["signature"] != "valid":
            fail("the signature did not verify after the round trip")
        if v["manifest"] and v["manifest"][1:] != [0, 0]:
            fail(f"manifest mismatches after the round trip: {v['manifest']}")
        if v["chain"] != "pre-spec":
            fail(f"cases/001 should come back pre-spec, got {v['chain']}")
        if v["notComputed"] != ["kpi.json", "spans.json", "annotation.json"]:
            fail(f"the verifier should decline the measurement: {v['notComputed']}")

finally:
    ingest.terminate()
    try:
        ingest.wait(timeout=5)
    except subprocess.TimeoutExpired:
        ingest.kill()
    reads.shutdown()
    shutil.rmtree(home, ignore_errors=True)
    shutil.rmtree(data, ignore_errors=True)

print(f"\n{len(steps)} steps, {bad} failed"
      + ("" if bad else "  —  nothing was typed by hand"))
sys.exit(1 if bad else 0)
