# How to verify this register

*Template to publish next to the register. Replace the parts in square brackets.*

---

The file `events.jsonl` contains the register of the interventions made while writing
[title]. Each line is an event; each event contains the fingerprint of the previous one,
so the sequence is a chain: **altering a past event invalidates every hash that follows
it**.

Next to the register you will find three files that let you verify it without taking my
word for anything.

## 0. The fastest check, if `attestation.txt` is here

```bash
grep -E '^[0-9a-f]{64}  ' attestation.txt | shasum -a 256 -c -
```

Every file the register closes over, in one command, with no PDF, no PKI and no browser.
The file is deliberately unsigned: its bytes are the ones those digests describe. If you
have only a copy extracted from a `.p7m`, normalise it first — signing rewrites line
endings and `shasum` will then look for `kpi.json\r`:

```bash
tr -d '\r' < extracted.txt | grep -E '^[0-9a-f]{64}  ' | shasum -a 256 -c -
```

**If it arrived inside a PDF**, the bundle is an attachment. Firefox opens the attachments
panel and downloads it; `pdfdetach -saveall file.pdf` does the same from a terminal.
**Adobe Reader may show the attachment and refuse to save it** — measured on Adobe Reader
2026.001.21789 on macOS, on every file tried, including ones written by other tools
entirely. If that happens, nothing is wrong with the document: use Firefox or `pdfdetach`,
both of which read the same files without complaint.

**If this arrived as a bundle** — `colophon-[uid].tar` — everything below is already in
it, and so is `verify.html`. Open that file in a browser with the network off and drop
the tar on it: it checks the chain, the signature, every digest the manifest covers and
the timestamp's imprint, in one action. The commands below are the same checks by hand,
and they are what you use if you would rather not run my copy of the verifier — which is
the sensible instinct, since it arrived in the package it is meant to check. Its digest
is published with each release; compare it, or fetch your own copy.

**A bundle is a snapshot at its date.** It verifies perfectly and it cannot tell you that
the case was reopened afterwards, because a copy in your hands has no way back to me. The
root printed in the document is what makes that visible: two copies with two different
roots are two different states of the same case.

**And that the copy you were handed is the one the signature attests.** `seal.sh` writes
`events.jsonl.sha256`, so comparing it against the register beside it is the whole check,
and it needs no network:

```bash
shasum -a 256 events.jsonl
cat events.jsonl.sha256
```

The same digest — the second column differs, the hash is the whole comparison — means
these are the bytes that were signed. A different one means the copy has been altered
since, whatever anything printed on its way out.

## 1. The chain has not been altered

```bash
python3 record.py --verify
```

It recomputes the whole chain and reports the first broken link. It must answer
`chain intact`, with the current root.

## 2. The register was signed, and by which key

The signature is Ed25519, detached, in the `.sig` file. The public key is here, as
`colophon.pub`, and it needs to be: this record travels as a file, with no address to
fetch anything from. Check the signature against it:

```bash
awk '{print "[your-email] " $1 " " $2}' colophon.pub > allowed_signers
ssh-keygen -Y verify -f allowed_signers -I [your-email] -n colophon \
           -Overify-time=[YYYYMMDD] -s events.jsonl.sig < events.jsonl
```

It must answer `Good "colophon" signature`. Use the date the register was sealed — the
`.tsr` states it — rather than today's: asking whether the key was valid when the
timestamp says the signature existed is a stronger question than whether it is valid now.

**Then check it is the key this case declared.** `case.json` records `key_fingerprint`,
and `case.json` is covered by the closing manifest, so the sealed chain itself says which
key to expect:

```bash
ssh-keygen -lf colophon.pub          # compare with key_fingerprint in case.json
```

A substituted key changes that fingerprint and stops matching something a signature
already commits to. That is a real check and it is worth running.

**What it still does not tell you.** A key inside the folder it signs cannot say whose
key it is: whoever could fabricate this folder could fabricate a key to sign it with, in
about ten seconds. Everything above proves the record is intact, internally consistent
and unchanged since it was sealed. None of it proves who made it. For that, read on.

## 2b. Signed by a named person — the only step that says who

The Ed25519 signature above proves that a key signed. A qualified electronic signature
moves that to a natural person, because a supervised trust service identified them before
issuing the certificate. **This is where identity comes from in this method, and there is
no other source of it** — no published key, no domain, no profile page. If the author
signed the PDF that carries this record as an attachment, the signature covers the
document and the evidence together, in one act.

**What is signed is whatever the author handed you** — the PDF, or the bundle
`colophon-[uid].tar` — not `attestation.txt`, which travels unsigned on purpose. Its
digest lines are the checkfile in §0 above, and signing a text file rewrites its line
endings, which breaks that.

For a signed bundle or any `.p7m`:

```bash
openssl cms -verify -in [file].p7m -inform DER -binary -out [file] \
            -CAfile [the EU trusted-list bundle, or your own]
openssl cms -verify -in [file].p7m -inform DER -noverify -signer signer.pem \
  && openssl x509 -in signer.pem -noout -subject -dates
```

The `-binary` matters on the reading side too: without it OpenSSL canonicalises the
content, and a tar comes back out mangled even though the signature verifies. The second command prints who signed and until when the certificate was
valid. For a signed PDF, open it in a reader that shows the signature panel.

**And read what it claims carefully.** A qualified signature says *this file came from
this person, on this date, and has not changed since*. It does not say the measurement is
correct: that is what the register is for, and checking it is §0 to §4 here. Two claims,
one file — do not let the signature panel answer a question it was not asked.

**If there is no `.p7m` and no signed PDF**, nobody has been named, and the honest
reading of everything above is: a consistent, sealed, timestamped record, from an author
you are taking on their word.

For a full check against the European Trusted Lists, upload the file to the EU DSS
validator (`ec.europa.eu/digital-building-blocks/DSS/webapp-demo/validation`), which
resolves the trust anchors for you.

**Look at the signature level**, and this is the part nobody mentions. A `CAdES-B` or
`PAdES-B` signature carries no revocation evidence: once the certificate expires — Italian
qualified certificates run about three years — Italian law (CAD art. 24 c. 4-bis) treats
the signature as **not made at all**, silently. A signature at level **LT** or **LTA**
embeds the revocation data and stays checkable afterwards. The validator reports the level.

Two things this signature does not say. It does not say the register is complete. And it
does not say that the text of the document is the text that was measured — §4 below is
what checks that, and a signature panel showing a legal name is not a substitute for it.

One thing it stops saying the moment you unpack. A signature over a bundle covers the
bundle; extract it and hand the folder to someone else, and the legal name does not go
with it. What travels is the Ed25519 signature and the key at §2.

## 3. The register already existed on that date

Two independent timestamps, so as not to depend on a single guarantor.

**RFC 3161** — `events.jsonl.tsr`. The second command is the one that verifies; the first
only prints what the token claims.

```bash
openssl ts -reply -in events.jsonl.tsr -text | grep "Time stamp"
openssl ts -verify -data events.jsonl -in events.jsonl.tsr \
           -CAfile "$(openssl version -d | sed 's/.*"\(.*\)"/\1/')/cert.pem"
```

It must answer `Verification: OK`. That `-CAfile` is **your own system's** certificate
bundle, and the command above finds it for you — `seal.sh` times against an authority
that chains to it precisely so there is nothing to download.

No CA certificate travels in the bundle, and that is deliberate: a root certificate
arriving inside the evidence it authenticates proves nothing, for the same reason the
enclosed `colophon.pub` proves nothing about whose key it is. If a case was stamped by
an authority your system does not carry, the check fails here and the case has to name
where you can fetch that CA — from the authority, not from me.

The browser verifier does less than this command, on purpose: it reads the imprint and
the time from the token and stops there. It tells you the timestamp commits to *this*
register; it does not tell you who issued it. That is what the command above is for.

**OpenTimestamps** — `events.jsonl.ots`, submitted for anchoring in the Bitcoin blockchain:

```bash
pip install opentimestamps-client
ots upgrade events.jsonl.ots && ots verify events.jsonl.ots
```

Two honest qualifications, because this seal is the one most easily overstated. A `.ots`
file means the register was *submitted*; the calendars batch submissions into a Bitcoin
transaction and have been observed to accept one and never anchor it, so `ots upgrade` is
what turns a submission into evidence. And verifying the result needs a Bitcoin node, or a
block explorer you decide to believe: it depends on no *authority*, which is not the same
as depending on nothing.

## 4. The text matches the annotation

```bash
python3 measure.py
```

It must say `reconstruction: OK`. That means that the annotated spans, concatenated,
reproduce the published text exactly: no step has been attributed to a piece of text
that does not exist, and no piece of text has been left without an attribution.

---

## What all this proves, and what it does not

**It proves** that the register existed in that form on that date, that it has not been
altered since, and that it was signed by the holder of the key enclosed as
`colophon.pub`, whose fingerprint the sealed manifest commits to. That is internal
consistency, and internal consistency is not identity: it says the record hangs together,
not who assembled it. **Identity comes from exactly one place** — a valid qualified
signature over the document that carries this record. With one, the holder of that key is
a named natural person, for as long as you hold the file. Without one, everything above
is a consistent record from an author you are taking on their word.

**It does not prove that this document is the text that was measured.** A signature over
a file says the file has not changed since it was signed; §4 is the only check that ties
the words you are reading to the numbers in the note.

**It does not prove** that the register is **complete**. No voluntary system can prove
that: I can record everything faithfully, or I can leave things out, and cryptography
does not tell the two cases apart. The register is, moreover, compiled by the language
model about itself.

I say it first because it is the soundest criticism that can be made of a voluntary
disclosure, and it is a fair one: **the value of this register does not lie in the proof,
it lies in the responsibility I take on by publishing it and in the fact that it can be
inspected.**

If you find an inconsistency, write to me: **[contact]**

---

*MIT License — Copyright (c) 2026 Fabio Chinaglia. See the LICENSE file.*
