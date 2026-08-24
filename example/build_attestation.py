#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
The attestation: one page stating what the register is, in a form a reader can run.

It is two things and neither of them is a signature.

**A checkfile.** The digest lines are flush-left, in `sha256sum` format, so

    grep -E '^[0-9a-f]{64}  ' attestation.txt | shasum -a 256 -c -

checks every file the register closes over — no PDF, no PKI, no browser, no verifier.
It is the shortest path from a folder to *these are the bytes that were measured*.

**A declaration.** One paragraph, in a sentence a person reads, saying what the whole
apparatus does not claim: not that the register is complete — no voluntary record can
prove that, and this one is compiled by the model about itself — and not that the text of
the document it accompanies is the text that was measured. `measure.py` is what checks
that, against the manifest above.

DO NOT SIGN THIS FILE. Signing a text file canonicalises its line endings: `openssl cms
-sign` rewrites every \n as \r\n, so the copy extracted from the .p7m has digest lines
ending in a carriage return, `shasum -c` looks for `kpi.json\r`, and every line fails with
*No such file* — under a signature that verifies perfectly. That is this project's own
line-endings hazard in a new place, and it destroys the better of this file's two
properties in exchange for the weaker one. `attestation.txt.p7m` is still carried if you
make one; it is no longer the way in.

WHERE THE QUALIFIED SIGNATURE GOES, if you hold one: on the thing you actually hand over.
A PDF, signed as PAdES, which covers the document as well as the record. Or the bundle,
`colophon-<case_uid>.tar`, signed as CAdES.

Signing the bundle is safe with a client that signs the bytes it is given, and one real
Italian qualified-signature client was tested and does: a two-line text file came back out
of its own .p7m byte-identical, and a client that leaves `\n` alone in a .txt will not
touch a tar. Check yours once, before you rely on it — the failure is silent and total.
Sign a small text file, extract it with `openssl cms -verify -noverify -out`, and compare
the digests. If they differ, the client canonicalises: find its binary option, or sign the
PDF instead. The damage is not subtle — measured with OpenSSL's own default, 256,000 bytes
of tar in, 6,367 bytes and *Unrecognized archive format* out, with the signature over the
wreckage still perfectly valid.

Either way the signing happens in your own tool, with your own certificate, and nothing
here ever sees it. Pick level **LT**: below it a signature carries no revocation evidence,
and when the certificate expires — about three years for an Italian qualified certificate
— CAD art. 24 c. 4-bis treats it as never made, silently.

And whatever you sign, this file stays unsigned inside the bundle. **Its bytes are the
ones the digests describe**, and a signature over the document does not travel with the
evidence once someone opens the tar.

ORDER. Generated after `seal.sh`, so it can name the seal. It records no event and does
not reopen the case: like the technical line, it is derived from files the manifest
already covers and it changes none of them.

    python3 build_attestation.py                 attestation.txt
    python3 build_attestation.py --lang it       attestazione.txt

Usage: python3 build_attestation.py [--lang it|en] [-o OUT]
"""
import argparse
import hashlib
import json
import os
import sys

OUT = {"en": "attestation.txt", "it": "attestazione.txt"}

T = {
 "en": {
  "title": "COLOPHON — ATTESTATION OF THE REGISTER",
  "declare": ("I declare that the register described below is the one I kept while\n"
              "writing this text, and that the digests listed are those of the files\n"
              "it closes over."),
  "case": "case", "uid": "uid", "author": "author", "date": "date",
  "reconstructed": "reconstructed", "yes": "yes", "no": "no",
  "page": "page", "register_at": "register",
  "key": "key", "fingerprint": "fingerprint",
  "reg": "REGISTER  events.jsonl", "events": "events",
  "opened": "opened", "closed": "closed", "root": "root", "sha256": "sha256",
  "manifest": "MANIFEST  event {n} of the register, sha256",
  "seal": "SEAL  alongside the register",
  "ots": ("events.jsonl.ots   OpenTimestamps — named, not hashed: `ots upgrade`\n"
          "                     rewrites this file when the Bitcoin attestation\n"
          "                     confirms, so any digest of it would go stale by design."),
  "chain": ("The register is a hash chain: each event carries the digest of the one\n"
            "before it, so the root above commits every event, and the manifest — the\n"
            "last of them — commits every file listed. Signing this page therefore\n"
            "signs all of it."),
  "limits": ("This signature says who takes responsibility for the register. It does not\n"
             "say that the register is complete: no voluntary record can prove that, and\n"
             "this one is compiled by the language model about itself. It does not say\n"
             "that the text of the document it accompanies is the text that was measured\n"
             "— the manifest above is what a reader checks that against. What all of it\n"
             "is worth is stated in {verify}, alongside."),
  "check": ("TO CHECK EVERY DIGEST ABOVE, from the folder that holds these files:\n"
            "  grep -E '^[0-9a-f]{64}  ' " ),
  "unpublished": ("not published at an address: this record travels with the document,\n"
                  "                as colophon-{uid}.tar"),
 },
 "it": {
  "title": "COLOPHON — ATTESTAZIONE DEL REGISTRO",
  "declare": ("Dichiaro che il registro descritto qui sotto è quello che ho tenuto\n"
              "mentre scrivevo questo testo, e che i digest elencati sono quelli dei\n"
              "file su cui si chiude."),
  "case": "caso", "uid": "uid", "author": "autore", "date": "data",
  "reconstructed": "ricostruito", "yes": "sì", "no": "no",
  "page": "pagina", "register_at": "registro",
  "key": "chiave", "fingerprint": "impronta",
  "reg": "REGISTRO  events.jsonl", "events": "eventi",
  "opened": "aperto", "closed": "chiuso", "root": "radice", "sha256": "sha256",
  "manifest": "MANIFEST  evento {n} del registro, sha256",
  "seal": "SIGILLO  accanto al registro",
  "ots": ("events.jsonl.ots   OpenTimestamps — nominato, non hashato: `ots upgrade`\n"
          "                     riscrive questo file quando l'ancoraggio su Bitcoin si\n"
          "                     conferma, quindi un suo digest sarebbe stantio per\n"
          "                     costruzione."),
  "chain": ("Il registro è una catena di hash: ogni evento porta il digest del\n"
            "precedente, quindi la radice qui sopra impegna ogni evento, e il manifest\n"
            "— l'ultimo di essi — impegna ogni file elencato. Firmare questa pagina\n"
            "firma quindi tutto quanto."),
  "limits": ("Questa firma dice chi si assume la responsabilità del registro. Non dice\n"
             "che il registro sia completo: nessuna registrazione volontaria può\n"
             "dimostrarlo, e questa è compilata dal modello linguistico su sé stesso.\n"
             "Non dice che il testo del documento che accompagna sia il testo misurato\n"
             "— è il manifest qui sopra ciò contro cui il lettore lo verifica. Quanto\n"
             "vale tutto questo è scritto in {verify}, accanto."),
  "check": ("PER VERIFICARE OGNI DIGEST QUI SOPRA, dalla cartella che contiene i file:\n"
            "  grep -E '^[0-9a-f]{64}  ' "),
  "unpublished": ("non pubblicato a un indirizzo: questo record viaggia con il documento,\n"
                  "                come colophon-{uid}.tar"),
 },
}

# Immutable once written, so a digest of them cannot go stale. events.jsonl.ots is the
# exception and it gets its own line, in the voice of the manifest's own exclusions.
SEALS = [("events.jsonl.sig", "Ed25519, detached", "Ed25519, staccata"),
         ("events.jsonl.tsr", "RFC 3161 timestamp", "marca temporale RFC 3161"),
         ("events.jsonl.sha256", "the digest seal.sh printed", "il digest stampato da seal.sh")]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--log", default="events.jsonl")
    p.add_argument("--case", default="case.json")
    p.add_argument("--lang", choices=sorted(T), default="en")
    p.add_argument("-o", "--out", default=None)
    a = p.parse_args(argv)
    t = T[a.lang]

    rows = [json.loads(l) for l in open(a.log, encoding="utf-8") if l.strip()]
    if not rows:
        sys.exit(f"{a.log}: the register is empty")
    manifest, mi = None, None
    for i in range(len(rows) - 1, -1, -1):
        d = (rows[i].get("payload") or {}).get("sha256")
        if isinstance(d, dict):
            manifest, mi = d, i + 1
            break
    if manifest is None:
        sys.exit(f"{a.log}: no closing manifest. There is nothing to attest yet: the\n"
                 f"  signature would cover a register that does not commit to the text.")
    if not os.path.exists(a.log + ".sig"):
        print("  ! the register is not sealed. Run seal.sh first: an attestation that\n"
              "    names no seal asks a reader to trust the page instead of the chain.",
              file=sys.stderr)

    try:
        case = json.load(open(a.case, encoding="utf-8"))
    except (OSError, ValueError):
        case = {}
    uid = case.get("case_uid") or os.path.basename(os.path.abspath("."))

    L = [t["title"], "", t["declare"], ""]
    def row(k, v):
        L.append(f"  {k:<13} {v}")

    row(t["case"], case.get("title", "—"))
    row(t["uid"], uid)
    row(t["author"], case.get("author", "—"))
    row(t["date"], case.get("date", "—"))
    row(t["reconstructed"], t["yes"] if case.get("reconstructed") else t["no"])
    page = case.get("verification_url") or case.get("url_verifica")
    reg = case.get("register_url") or case.get("url_registro")
    if page:
        row(t["page"], page)
    if reg and reg != page:
        row(t["register_at"], reg)
    if not (page or reg):
        row(t["page"], t["unpublished"].format(uid=uid))
    if case.get("key_url"):
        row(t["key"], case["key_url"])
    if case.get("key_fingerprint"):
        row(t["fingerprint"], case["key_fingerprint"])

    L += ["", t["reg"]]
    row(t["events"], str(len(rows)))
    row(t["opened"], rows[0].get("ts", "—"))
    row(t["closed"], rows[-1].get("ts", "—"))
    row(t["root"], rows[-1].get("hash", "—"))
    # Flush-left, in checkfile format, and not indented like the rows above: the register
    # is the one file this whole page is about, and a `-c` run that checks everything
    # except it would be a strange thing to have signed.
    L.append(f"{sha256_file(a.log)}  {a.log}")

    L += ["", t["manifest"].format(n=mi)]
    missing = []
    for name in sorted(manifest):
        L.append(f"{manifest[name]}  {name}")
        if not os.path.exists(name):
            missing.append(name)

    L += ["", t["seal"]]
    for name, en, it in SEALS:
        if os.path.exists(name):
            L.append(f"{sha256_file(name)}  {name}")
            L.append(f"{'':<66}{en if a.lang == 'en' else it}")
    if os.path.exists("events.jsonl.ots"):
        L += ["  " + t["ots"]]

    # Name the file that is actually there. An Italian case may carry VERIFY.md and an
    # English one VERIFICA.md; pointing at the wrong one sends the reader to a 404 in the
    # paragraph that explains what the signature is worth.
    verify = next((n for n in ("VERIFY.md", "VERIFICA.md") if n in manifest),
                  "VERIFY.md")
    L += ["", t["chain"], "", t["limits"].format(verify=verify), "",
          t["check"] + (a.out or OUT[a.lang]) + " | shasum -a 256 -c -", ""]

    out = a.out or OUT[a.lang]
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))

    print(f"  {out}  {os.path.getsize(out):,} bytes, {len(manifest)} digests")
    if missing:
        print(f"  ! {len(missing)} covered files are not in this folder: "
              f"{', '.join(missing[:4])}{'…' if len(missing) > 4 else ''}")
        print("    The checkfile a reader runs will fail on them. Attest from the case\n"
              "    folder, not from a copy of part of it.")
        return 1
    print("  do not sign this file — sign the PDF or the bundle you hand over, and\n"
          "  leave this one plain: its bytes are what the digests describe")
    return 0


if __name__ == "__main__":
    sys.exit(main())
