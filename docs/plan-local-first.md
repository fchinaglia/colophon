# Plan — the local-first turn

*Build document, 24 August 2026. The decision and its reasoning are in §1; the rest is the
order of work, what each step contains, and how you know it is done. Supersedes the
delivery model in `implementation-plan.md`, whose five phases all shipped and whose
server half is now being withdrawn.*

---

## 1. The decision

**A case travels as a document plus a bundle. Nothing has to stay online for it to be
checked.**

Step 1: the skill produces the document in markdown, the measurement, the icon, the
assessment, the root, and a `.tar` carrying the evidence and the verifier.
Step 2: the same things embedded in a PDF.
The qualified signature is the author's, applied with their own tools; the project
integrates no signing API and never sees a certificate.

Every server component leaves the project.

### Why, in one paragraph

`disclosures.md` judges a channel by who has to stay alive in ten years, and calls a dead
link under a disclosure *"evidence from a distance and the opposite of it"*. The project
then shipped one that depends on a droplet, a domain, a TLS renewal and one person. The
deposit was built to solve the circular key publication and to give authors without
hosting a route; the first is solved better by a domain or by GitHub's signing-keys
endpoint, and the second disappears when the evidence travels in the author's own file.
What is left is an operational surface — invite codes, bearer tokens, rate limits, GDPR,
uptime — that generated most of the project's open issues and none of its argument.

### What this costs, stated rather than discovered later

**Supersession is gone.** `cases/001` was reopened twice in a single day; a published
address absorbs that, because the reader who follows it finds the reopening event and the
current root. A bundle in a reader's hands is frozen, verifies perfectly, and cannot
announce that it has been superseded. This is structural: the copy has no channel back.
Mitigation is honesty, not machinery — the root is printed in the document, so a reader
comparing two copies sees the divergence, and `VERIFY.md` must say that an attached
record is a snapshot at its date.

**Citation and revocation go with it.** Nobody can link to a bundle, and nobody can
withdraw one. `collect()` refuses `versions/` precisely because the register *"holds
briefs and editorial reasoning that may name people who consented to nothing"* — that
judgement is now permanent and distributed rather than revocable. This makes issue #6
more urgent, not less.

**Forkability.** A deposit bound `case_id` to one key in `owners.jsonl` and refused
another. Nothing stops an author packing two different bundles under one `case_uid`.

### What it buys

The one thing the method claims: a record that outlives everyone involved in making it.
Given `trust/` and `verify.html` inside the bundle, no host, no domain, no operator and
no project has to exist for a reader to check the work.

### The gift nobody planned

`collect()` keeps the version the manifest covers and refuses renderings as *"derivable
from what is covered"*. If the document the reader gets **is** markdown, then the
document and the file `measure.py` reconstructs are the same bytes, and divergence
between the published text and the measured text is not prevented by a check — it is
impossible by construction. The gate only becomes necessary at step 2, where the PDF is
a rendering again, and there it is one digest comparison.

---

## 2. Order of work

The sequencing rule: **nothing is removed until its replacement works and the one live
case has been migrated.** The deposit currently answers the technical line of a published
article, frozen in a PDF that cannot be edited.

### Step 1 — `build_bundle.py`

The load-bearing piece. Everything else waits on it.

`collect()` moves out of `cli/colophon.py` into a skill script copied into the case
folder with the others, because SKILL.md requires a case to stay verifiable on its own
when the skill changes, and a packer that lives in a CLI cannot rebuild its own bundle.

- writes `colophon-<case_uid>.tar` **outside** the case directory, or `collect()` files
  it under `refused` on the next run as not covered by the manifest
- contents: what `collect()` keeps, plus `verify.html`, plus `trust/<tsa>-ca.pem`
- runs **after** the seal — it must carry `.sig`, `.tsr`, `.sha256`
- refuses a case with no manifest, as `deposit` already does
- the tar itself cannot be manifest-covered: it contains the manifest. This is not a
  defect. `core.js` hashes each *file* against the manifest, so tampering inside is
  caught and tampering with the container only breaks extraction. One sentence in
  SKILL.md so nobody tries to hash it.

**Open sub-decision — which CA ships.** Offline verification is the whole promise, and
today `openssl ts -verify` on `cases/001/events.jsonl.tsr` fails with *self-signed
certificate in certificate chain* because no CA is anywhere in the tree. `cases/001` was
sealed by freetsa (its errata added `freetsa-cacert.pem`); `seal.sh:34` now defaults to
DigiCert, which chains to the system bundle. Either the skill carries a small `trust/`
with the CAs for the TSAs `seal.sh` can use and the packer picks the matching one, or
`seal.sh` records which TSA it used and the packer resolves from that. The second is
better — it degrades correctly when someone points `seal.sh` at a TSA we never listed.

**Done when** the bundle for `cases/001`, dropped on `verify.html` in a browser with the
network disabled, verifies the chain, the signature, every manifest digest and the
timestamp.

### Step 2 — the unified disclaimer block

Icon, assessment and root become one generated graphic unit instead of three things
assembled by hand. This closes #17 directly.

Open sub-decision: in markdown the block is either an `<img>` at a generated SVG plus
text lines, or a single SVG carrying all three. The second travels better and reads worse
when scaled down; the first is greppable. Recommend the first, with the root as text so
it can be copied.

Touches `build_icon.py`, `build_note.py`, and whatever composes them. `build_page.py`
follows, which is #10.

### Step 3 — markdown as the deliverable

Make the published document the manifest-covered file rather than a rendering of it.
Mostly SKILL.md and the naming relationship between `versions/vNN_final` and the
published file; the code change is small and the discipline it buys is large (§1).

### Step 4 — migrate the live case, freeze the deposit

Build the bundle for the real article, publish it wherever its readers are, and put the
deposit into read-only: writes refused, the existing tree still served. **Do not delete
it.** Its address is in a published technical line; removing it produces exactly the
failure the method exists to prevent.

### Step 5 — remove `server/` and `deploy/`

Only now. Also removes `cmd_deposit`, `owners.jsonl`, invites, bearer tokens, the two
compose files, the nginx configs, `test_server.py` and `test_loop.py`.

What survives outside the repository as infrastructure, not as a component:
`colophonmethod.com/.well-known/colophon/keys`. A static file is not a service, and
without it the author's own signature is circular again.

`colophon setup` then shrinks to *generate the key, declare where you publish it* —
small enough to happen in conversation, which is #13.

### Step 6 — `build_attestation.py`

Plain text, unsigned, inside the bundle. Digest lines in `sha256sum` checkfile format, so
`grep -E '^[0-9a-f]{64}  ' attestation.txt | shasum -a 256 -c -` is a complete check with
no PDF and no PKI. Reads the manifest out of the register rather than a hardcoded file
list. Carries `case_uid`. Omits URL lines when there is no publication.

It stays in the bundle even when the PDF is signed, because **the PAdES signature does
not travel with the evidence**: extract the tar, hand it to a third party, and the legal
identity is gone.

### Step 7 — the PDF, in two pieces

**7a, cheap.** Chrome renders document plus disclaimer block plus appendix. New here is
one gate: the builder hashes the source and refuses if it does not match the manifest
digest. Without it a signed PDF attests *this file is unchanged since signing* and the
reader will read it as *this text is the text that was measured*.

**7b, expensive and gated.** Embedding the bundle needs an incremental-update writer —
an `EmbeddedFile` stream, a `/Names/EmbeddedFiles` tree, `/AF` associations — roughly
200–300 lines of stdlib, and a malformed incremental update opens in some readers and not
others. Behind four tooling tests on one real PDF with a real Italian client: does
signing preserve `/Names/EmbeddedFiles` and `/AF`; does the signature validate in Acrobat
*and* the EU DSS validator; is the attachment still extractable in Acrobat and pdf.js;
does level LT survive. Start with Aruba Sign, the one client with a confirmed level
chooser.

**Order is fixed: embed, then sign.** PAdES is an incremental update, so signing first
leaves the signature covering an earlier revision, which Acrobat reports as *signed, then
modified* — worse than broken, because it reads as tampering.

**Never call the output PDF/A-3.** Chrome's PDF is not PDF/A anything: no output intent,
no conformant XMP, no guaranteed embedded fonts. An unbacked compliance claim is what
`disclosures.md` forbids, and this project cannot afford one in the artefact whose job is
to be checkable.

### Step 8 — the prose

`SKILL.md` publication section, `disclosures.md`, `VERIFY.md` (the snapshot caveat, the
verifier's own digest, the qualified-signature recipe), `README.md`, `CHANGELOG.md`.

Two things the author must be told rather than left to discover:

- **level LT.** CAD art. 24 c. 4-bis makes a signature on an expired certificate
  *"equivalente a mancata sottoscrizione"*. Italian qualified certificates run about
  three years. Level LT embeds the revocation evidence; without it the attestation dies
  silently on a date nothing in the document mentions.
- **the verifier in the bundle is a convenience, not an anchor.** It arrives in the same
  package it is meant to check. `verifier/build.py` already prints its digest and already
  says to publish it alongside; VERIFY.md must tell the reader to compare, or to fetch
  their own copy.

---

## 3. Issues, forecast

Reviewed as each step lands, not now.

| # | expected fate |
|---|---|
| #20 invite codes | moot at step 5 — nothing to be invited to |
| #21 no way in | answered, not fixed: there is no door |
| #17 level-2 block by hand | closes at step 2 |
| #10 verification page redesign | closes at step 2 |
| #13 how to become an author | closes at step 5 |
| #22 two writers of index.html | likely moot — the cases index served a published tree |
| #19 website homepage | survives, shrinks: key, verifier, digests, no service |
| #14 the skill's vocabulary | untouched, still open |
| #6 unpublishable briefs | **more urgent**: the register now travels instead of sitting on a host the author controls |
