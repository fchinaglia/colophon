#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
The bundle: everything a reader needs to check the case, in one file, with nothing
left online.

Reads the sealed register, takes the closing manifest as the authority on what
belongs to the case, and writes `colophon-<case_uid>.tar` — the evidence and the
verifier that checks it. A reader drops the tar on verify.html and gets the chain,
the signature, every manifest digest and the timestamp, with the network off.

Run it AFTER seal.sh. The bundle carries .sig, .tsr and .sha256, and those do not
exist until the register is sealed.

The tar is written OUTSIDE the case folder. Left inside, the next run would find it
and withhold it as a file no manifest covers — and the run after that would pack the
previous tar into the new one.

The tar itself is not covered by the manifest and cannot be: it contains the
manifest. That is not a gap. The tar is transport, not evidence; verify.html hashes
each *file* against the manifest, so tampering with anything inside is caught, and
tampering with the container only breaks extraction.

What travels and what does not is collect() below, which is the rule the
deposit used before it was withdrawn. Drafts stay home: `versions/`
holds unpublished writing and the register holds briefs and editorial reasoning that
may name people who consented to nothing. Only the one version the manifest covers
goes, because it is the text measure.py reconstructs. The register commits to the
digests of the rest, so they stay attested without being revealed.

What travels, and what its authority is.

The public key travels — `colophon.pub`, put there by seal.sh. It has to: there is no
address to fetch it from, and a reader with the bundle and no key can check the chain
and the digests but not the signature. What it is worth is stated plainly here and in
VERIFY.md, because a key inside the folder it signs is circular on its own: it proves
the register was signed by whoever holds this key, and nothing about whose key that is.
Two things make it more than that, and neither is inside the bundle. `case.json`
declares the fingerprint and the manifest covers `case.json`, so the chain itself says
which key this case expected — a substituted key changes the fingerprint and stops
matching. And a qualified electronic signature over the PDF that carries this tar binds
a natural person, identified by a supervised trust service, to the whole package.

No CA travels in the bundle. A root certificate arriving inside the evidence it
authenticates proves nothing. verify.html checks that the timestamp commits to this
register and stops there; validating who issued it is `openssl ts -verify` against the
reader's own store, which is why seal.sh times against a TSA whose root that store
already has.

The verifier that does travel is a convenience, not an anchor: it arrives in the
package it is meant to check. Its digest is printed below — publish it, and tell the
reader in VERIFY.md to compare or to fetch their own copy.

Usage:
    python3 build_bundle.py                     # from inside the case folder
    python3 build_bundle.py cases/003 -o /tmp   # or point at one
"""
import argparse
import hashlib
import json
import os
import sys
import tarfile

# The manifest is the authority on what belongs to a case: it covers the source
# version, the annotation, the measurement, case.json, the icon, the verification
# page and every script a reader runs. Two things sit outside it and still belong in
# a bundle — the seal artifacts, which cannot be inside a manifest that precedes
# them, and the reader-facing files the manifest deliberately leaves out.
SEAL_PREFIX = "events.jsonl"
# index.html is the verification page and the manifest covers it, so it is kept twice
# over; it stays named here because a case sealed before build_page.py took that name
# carries an index.html that is prose about the case, outside its manifest, and that
# file is still the door a reader arrives at. README.md is prose in every case.
# colophon.pub is the key the signature is checked against and allowed_signers is the
# same key in the form `ssh-keygen -Y verify` reads. seal.sh writes the first, after
# the manifest, which is why neither can be covered by one.
READER = {"index.html", "README.md", "colophon.pub", "allowed_signers"}
# The attestation and its signature. Generated after the manifest — they carry the root,
# which is the hash of the manifest event — so no manifest can cover them, and without
# this they would be withheld as uncovered: the one file in the bundle that carries a
# legal name would be the one that did not travel. Prefix, because the file is
# attestazione.txt in an Italian case and the signed form appends .p7m to the whole name.
ATTESTATION = ("attestation.", "attestazione.")

# Used only when a case has no manifest at all, which the caller has already refused
# over: better a conservative list than everything on disk.
FALLBACK = {
    "annotation.json", "spans.json", "kpi.json", "case.json", "icon.svg",
    "verification.html", "colophon.pub", "allowed_signers", "VERIFY.md",
    "VERIFICA.md", "LICENSE",
}

VERIFIER = "verify.html"


def read_register(case_dir):
    with open(os.path.join(case_dir, "events.jsonl"), "rb") as f:
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


def collect(case_dir, manifest, extra_skip=()):
    keep, refused = {}, []
    covered = set(manifest or ())
    for base, dirs, files in os.walk(case_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fn in sorted(files):
            if fn.startswith(".") or fn == "submission.json" or fn in extra_skip:
                continue
            full = os.path.join(base, fn)
            rel = os.path.relpath(full, case_dir)
            if rel.startswith(SEAL_PREFIX) or rel in READER or fn.startswith(ATTESTATION):
                keep[rel] = full                      # register, seals, landing, attestation
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


def find_verifier(case_dir, given):
    """Where verify.html comes from, strongest claim first.

    Given explicitly, then the case folder — a case that was opened with the verifier
    copied in carries its own, and the manifest covers it. Then next to this script,
    which is where the skill keeps it. Then the working tree, so the repository can
    build a bundle without installing anything.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (given,
                 os.path.join(case_dir, VERIFIER),
                 os.path.join(here, VERIFIER),
                 os.path.join(here, "..", VERIFIER),
                 os.path.join(here, "..", "..", "..", "verifier", VERIFIER)):
        if cand and os.path.isfile(cand):
            return os.path.abspath(cand)
    return None


def deterministic(info):
    """Two authors packing the same case get the same bytes.

    Ownership, timestamps and permissions describe the machine that ran the packer,
    not the case. Left in, they make every rebuild a different file for no reason, and
    a reader comparing two copies of one bundle would see a difference that means
    nothing.
    """
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    info.mtime = 0
    info.mode = 0o644
    return info


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("case_dir", nargs="?", default=".", help="the case folder (default: .)")
    ap.add_argument("-o", "--out", help="where to write the tar (default: beside the case)")
    ap.add_argument("--verifier", help="path to verify.html")
    ap.add_argument("--no-verifier", action="store_true",
                    help="pack without it, and say so to the reader")
    ap.add_argument("--uid", help="override case_uid, for a case that predates it")
    ap.add_argument("--force", action="store_true", help="pack an unsealed case anyway")
    a = ap.parse_args(argv)

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
    uid = a.uid or case_json.get("case_uid") or os.path.basename(case_dir.rstrip(os.sep))
    if not (a.uid or case_json.get("case_uid")):
        print(f"  ! no case_uid in case.json — naming the bundle after the folder, "
              f"'{uid}'. A uid fixed at Opening is what keeps a case identifiable once "
              f"the tar is detached from it.")

    manifest = manifest_of(rows)
    sealed = os.path.isfile(os.path.join(case_dir, "events.jsonl.sig"))

    print(f"\n  case      {case_dir}")
    print(f"  events    {len(rows)}")
    print(f"  root      {root}")

    if not manifest:
        print("\n  ! no closing manifest in this register. The bundle would carry a")
        print("    signature over the register and nothing else — the text, the")
        print("    annotation and the measurement would all sit outside it.")
        if not a.force:
            print("    Seal the case properly first, or pass --force.", file=sys.stderr)
            return 1
    if not sealed:
        print("\n  ! events.jsonl.sig is missing: this register is not signed.")
        print("    A bundle without a seal proves the chain is internally consistent")
        print("    and nothing about who made it.")
        if not a.force:
            print("    Run seal.sh first, or pass --force.", file=sys.stderr)
            return 1

    out_dir = os.path.abspath(a.out) if a.out else os.path.dirname(case_dir)
    out = os.path.join(out_dir, f"colophon-{uid}.tar")
    if os.path.abspath(out).startswith(case_dir + os.sep):
        print(f"\n! {out} is inside the case folder. The next run would withhold it as a",
              file=sys.stderr)
        print("  file no manifest covers, and the one after that would pack it.",
              file=sys.stderr)
        return 1

    # The tar of a previous run sits in the output directory, not in the case, so
    # collect() never sees it — but skip the name anyway if the two coincide.
    keep, refused = collect(case_dir, manifest, extra_skip={os.path.basename(out)})

    verifier = None if a.no_verifier else find_verifier(case_dir, a.verifier)
    if verifier is None and not a.no_verifier:
        print("\n! no verify.html found, and a bundle without one asks the reader to go",
              file=sys.stderr)
        print("  looking for the tool that reads it. Pass --verifier PATH, or",
              file=sys.stderr)
        print("  --no-verifier if you mean to tell them where to get it.", file=sys.stderr)
        return 1

    print(f"\n  packing {len(keep)} files:")
    for rel in sorted(keep):
        print(f"    {sha256_file(keep[rel])[:12]}…  {rel}")
    if verifier and VERIFIER not in keep:
        print(f"    {sha256_file(verifier)[:12]}…  {VERIFIER}  (the reader's tool)")
    if refused:
        print(f"\n  withheld {len(refused)}:")
        for rel, why in sorted(refused):
            print(f"    {rel}  ({why})")
        print("\n  Drafts never travel. The register commits to their digests, so they")
        print("  stay attested without being revealed — the reader keeps every check")
        print("  and loses only the ability to read your drafts.")

    # Flat, with no top-level directory: verify.html strips a single leading component
    # only when every entry shares it, and the verifier sits beside the evidence rather
    # than under it.
    os.makedirs(out_dir, exist_ok=True)
    tmp = out + ".part"
    with tarfile.open(tmp, "w", format=tarfile.USTAR_FORMAT) as t:
        for rel in sorted(keep):
            t.add(keep[rel], arcname=rel, filter=deterministic)
        if verifier and VERIFIER not in keep:
            t.add(verifier, arcname=VERIFIER, filter=deterministic)
    os.replace(tmp, out)

    if not ({"colophon.pub", "allowed_signers"} & set(keep)) and \
            any(k.startswith(SEAL_PREFIX + ".sig") for k in keep):
        print("\n  ! no colophon.pub in this bundle. The register is signed and the")
        print("    reader has nothing to check the signature against except the key")
        print("    inside the signature itself, which cannot be compared with the")
        print("    fingerprint case.json declares. Re-run seal.sh, or copy the public")
        print("    half of the key in as colophon.pub, and pack again.")

    print(f"\n  {out}")
    print(f"  {os.path.getsize(out):,} bytes")
    print(f"  sha256    {sha256_file(out)}")
    if verifier:
        print(f"  verifier  sha256 {sha256_file(verifier)}")
        print("            it arrived in the package it checks: publish that digest,")
        print("            and tell the reader to compare it or fetch their own copy.")
    print("\n  The bundle is a snapshot at its date. It cannot announce that it has")
    print("  been superseded, so keep the root in the document: a reader holding two")
    print("  copies can see they differ.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
