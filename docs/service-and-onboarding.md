# Onboarding, the deposit service, and the three faces of verification

*Analysis document. The owner proposed a direction; the functional analyst and the
architect assessed it. This is what they concluded, including where each of them changed
their mind and where they refused to.*

The qualified-signature track is suspended for this document. It was taken up again on
25 August and settled the other way: see the status note below.

---

> **Status, 23 August 2026.** The instance described here exists and runs. Decisions since
> taken: the apex is canonical and the instance lives on its own name, so a depositor's key
> is not vouched for by the machine storing their case; the canonicalization rule is
> Python's, written down in `spec/canonical.md`, because RFC 8785 would break the registers
> already sealed; drafts are never deposited; addresses are opaque and carry no author
> component; mirroring at deposit is opt-in and inside the signed submission. Still open:
> whether `measure.py` should gate the missing `version` digests, and who operates the
> public instance in five years. §8 keeps both.

> **Status, 25 August 2026 — superseded in part.** Three releases have overtaken this
> document. **3.0.0** removed the address route entirely: a case travels as a bundle and
> nothing else, `case.json` has no `verification_url`, `register_url` or `key_url`, and
> the published key is gone — `seal.sh` copies the public half into the case as
> `colophon.pub` and `build_bundle.py` packs it. Identity comes from one place now: a
> qualified electronic signature on the PDF the bundle is attached to. **3.1.0** taught
> the verifier to open that PDF, read the record out of it, show the case's own report
> beside the checks, and check the signature over the document — including whether the
> record is inside the bytes it covers. **3.1.2** stopped calling the register's own
> signature `who`.
>
> Everything below about addresses, published keys and the deposit is **the record of a
> position that was held and then abandoned.** It is kept because the reasoning is why the
> current shape looks as it does, not because it describes the method. `CHANGELOG.md` has
> what replaced it.


## 1. The proposal, and the revised verdict

The proposal, in the owner's framing: a setup flow that makes a new user generate a key
and declare two URLs; a deposit service for users with no site; a verification client at a
URL that verifies locally; all three as a public HTML server in Docker, deployable as the
user's own instance, a self-run container, or a public instance the project operates.

`publication-and-identity.md` rejected hosted case storage. **That rejection is now
partly withdrawn, and the argument that withdrew it is worth stating in full**, because it
is the load-bearing one:

> Objecting to a Colophon-branded host while accepting Microsoft's is a position that
> cannot be defended.

The lines drawn earlier were about the **recording path** — event capture, hashing, the
private key, the annotation, the measurement, the decision to publish. None of them move.
Depositing is post-seal publication of artefacts that are already sealed. That is a web
host, and Colophon has always required one; the current one is GitHub Pages.

What genuinely changes the verdict is the packaging. **A service anyone can run in one
command is infrastructure; a service only one party can run is a gatekeeper.** The
distinguishing test is not intent, and it has a technical answer:

> **Can a user leave without losing anything?**

So the deposit service is approved, under a constraint the proposal does not yet contain:

> **The instance is a dumb static host over content-addressed files, with a one-command
> full export, and it is never required to verify anything.**

Storing bytes and serving them is fine. **Pronouncing on them is not.** If the instance
ever validates — a green tick, a badge computed by the server, a gate on a check — it has
become the authority the method exists to refuse, whether or not the image is public.

**One objection is held intact.** A deposit is storage; a key registry is a claim about
who someone is. Nothing in the packaging touches that difference, because the trust does
not come from the software but from whoever the reader believes runs the host. The
instance may *hold* keys. It must never *assert* anything about them: no verified mark,
no directory searchable by person.

**And one constraint inherited from the repository, non-negotiable.** Nothing in
`record.py`, `measure.py`, `build_*.py` or `seal.sh` may ever contact an instance.
Depositing is an action the author invokes, never a runtime dependency —
`CONTRIBUTING.md` ground rule 6, *nothing phones home*, which a tool about disclosure
cannot break.

**Two notes on the deployment story, from the personas.** Docker is not a realistic
instruction for a journalist on shared hosting, and she does not need it: she has hosting,
and what she lacks is a publish step. The most attractive deployment in the whole proposal
is the one the owner did not name — **an institution running an instance for its
researchers**, which solves the academic's identity binding and his permanence problem at
once. The deposit service, honestly scoped, serves one persona: the author with no
hosting at all. That is a real user and worth serving. It is also the persona whose
identity binding stays weakest whatever is built, because they have no independent anchor
to bind to.

---

## 2. Priority one — onboarding

This is the owner's first priority and it is correct on the merits, not only on effort.
For three of the four personas the defect was never missing infrastructure — it was a
missing publish step, a URL convention, and a validation.

Run once, before the first case: `colophon setup`.

**The order, and why this order.**

1. **Identity.** Name; contact email — already required twice, by `allowed_signers` and by
   `VERIFY.md`'s `[contact]`; optional `author_id` (ORCID, or a domain).
2. **Key.** `ssh-keygen -t ed25519 -f ~/.ssh/colophon -C colophon`, the path `seal.sh`
   already defaults to via `COLOPHON_KEY`. Print the fingerprint. **Ask about a passphrase
   here**, and say now what `seal.sh` says at seal time: a passphrase with an empty agent
   makes the script hang. The warning belongs at the moment of the decision, not at the
   moment of the failure. **And say plainly that losing this key loses control**: it is the
   identity for withdrawing a deposited case as well as for signing, there is no
   cryptographic recovery, and there must not be one. Press for a backup here, together
   with the `author_secret` generated at step 4.
3. **Key URL**, from a ranked menu: own domain at `/.well-known/colophon/keys` >
   `api.github.com/users/<u>/ssh_signing_keys` > the deposit instance > *not yet*.
   **Then validate it: fetch the URL and compare the key body byte-for-byte against the
   local `.pub`.** One HTTP GET, and it is the highest-value check in the whole flow — it
   is exactly what nobody did for `cases/001`.
4. **Evidence base URL** — a *prefix*, e.g. `https://example.com/colophon/`, from which
   each case derives `{base}{case_id}/` for both `register_url` and `verification_url`.
   This removes the worst defect in the current flow, where `SKILL.md` asks for two full
   URLs for a folder that does not exist yet. Validate: https, trailing slash, and **no
   underscore anywhere in the path**. Say in one sentence, as it is typed, that this
   address is a promise a PDF will freeze forever.
5. **Publication route** — git and Pages / rsync or FTP / deposit instance / manual. This
   determines what the later publish step actually does.
6. **Housekeeping.** Write `cases/** -text` into `.gitattributes` and verify it: the one
   failure that produces a *false* verdict of forgery must never depend on memory. Add
   `.nojekyll`. Offer the archival tail — Software Heritage, Zenodo.

**What it writes.** `~/.config/colophon/author.json`: name, contact, author_id, key_path,
key_fingerprint, key_url, `key_url_verified_at`, base_url, route, `previous_bases[]`.
**This config is a source of defaults, never an authority.** `case.json` remains the
per-case record and stays manifest-covered; setup only stops the author retyping it.

**"I don't have a URL yet."** Allowed, but as a *declared* state:
`"key_url": null, "deferred": true`. The mechanism that makes it safe is at closing, not
at setup: **the closing refuses to seal without an address**, with an explicit
`--unpublished` override that writes an event into the register saying so. Today
`build_note.py` only warns on stderr — and a stderr warning is precisely how `cases/002`
ended up pointing its key at `cases/001`. **Escalate warn to refuse.** No silent gaps.

**Second and later cases.** Setup does not re-run. Case-open reads the config, derives the
two URLs, and does one cheap re-check: re-fetch `key_url`, compare. If it 404s or the key
changed, **stop before a word is written** — the only moment when fixing it is free.

**Failure modes.**

- *The author changes their URL.* Unfixable in printed matter; make it visible. Record
  `previous_bases[]`, give `colophon doctor` a listing of every case whose published
  address is now stale, and require a 301 at the old base. The base should be on a domain
  the author can repoint, which is the real argument for domains over platform paths.
- *The author declares a URL and never publishes to it.* After the publish step, fetch
  `{case_url}events.jsonl` and compare against the `.sha256` that `seal.sh` already
  writes. If it does not match, the case is not published, whatever the author believes.
  Run this **before** saying "done".
- *The author runs setup on a second machine.* It must detect the absence of a key and
  **must not silently generate a second one** — two keys under one name is an unresolvable
  ambiguity for a reader. Offer: copy the key across (recommended, with the risk stated),
  or publish a rotation statement at `key_url` naming both fingerprints. This is the
  argument for the artefact at `key_url` being a small structured file *containing* the
  key rather than a bare `.pub`, so that `colophon setup --from <key_url>` can rebuild the
  config on the second machine.

---

## 3. Priority three — three faces, one verification

The proposal folds the verifier into the Docker server. **Do not.** The verifier's entire
value is that it needs no server, no operator and no trust: a reader checks a case with
files they downloaded once, offline, forever. Bundling it into the image that also holds
other people's data makes the trust-free component inherit the trust posture of the
data-holding component.

There is one verification, and three front ends. The division of labour is what keeps the
number honest.

| | audience | computes the number? |
|---|---|---|
| **`colophon verify`** — CLI | the technical reader | **yes** — `measure.py` is the single implementation |
| **single-file HTML** | everyone else | **no**, deliberately |
| **raw commands in `VERIFY.md`** | the reader who trusts neither of the above | yes, by hand |

**The CLI already exists, scattered.** `record.py --verify`, `ssh-keygen -Y verify`,
`openssl ts -verify`, `measure.py` — four commands and four toolchains in `VERIFY.md`.
Packing them into one `colophon verify` is step 2 of the path already recommended in
`publication-and-identity.md` (`pipx install colophon`), and it collapses four toolchains
into one command.

**The HTML file is not a shorter CLI.** The eleven-step reader journey fails because it
requires `python3`, `ssh-keygen`, `openssl` and `pip install opentimestamps-client`. A CLI
does not fix that; it restates it with better syntax. The journalist's reader has a
browser and knows how to drag a folder onto a page.

**The raw commands stay.** They need nothing installed that is not already on a Unix box,
and they are what proves the other two are not magic.

**`/verify/` served by the instance is not a fourth thing.** It is the same file, the same
bytes, handed over by a server that takes no part in the verification — which is precisely
the constraint under which the deposit service was approved.

### What the browser can actually verify — tested, not assumed

**The Ed25519 signature: solved, and smaller than expected.** `cases/001/events.jsonl.sig`
was parsed and its pre-image reconstructed independently:

```
blob = "SSHSIG" || u32 version(=1)
     || string publickey || string namespace(="colophon")
     || string reserved("") || string hash_algorithm(="sha512")
     || string signature

preimage = "SSHSIG" || string namespace || string reserved
                    || string hash_alg  || string SHA-512(file bytes)
```

The armored blob is **178 bytes**; the signed pre-image is **not the file** but a
structure of **exactly 100 bytes** carrying the register's SHA-512. An Ed25519 verification
over those 100 bytes with an independent implementation returned `VERIFY OK`. The formula
is confirmed.

What the browser must implement: strip the PEM armor, base64-decode, a ~25-line big-endian
length-prefixed string reader, rebuild the 100-byte pre-image, SHA-512 the uploaded
register, verify. The `.pub` line is `<type> <base64 of the same publickey blob>
<comment>`, so the same reader handles it. **Realistically 120–150 lines of hand-written
JS**, plus a bundled Ed25519.

**Do not use `crypto.subtle`.** Ed25519 support landed in recent Chrome, Firefox and
Safari **[unverified — browsers could not be tested from here]**, but the decisive reason
is different: `crypto.subtle` requires a secure context, and whether `file://` counts as
one is inconsistent across browsers. The offline single-file mode is exactly the mode that
must not break. Bundle `@noble/ed25519` (~6 KB minified) and a pure-JS SHA-256/SHA-512.

**The chain: the one real trap.** SHA-256 over bytes is trivial. The chain is
`h(n) = sha256(h(n-1) || canonical(event_n))`, and `canonical()` is one line of
`record.py`:

```python
json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
```

The hash is computed over **bytes**, but an event is a **JSON object**, and the same
object admits many byte serializations. That line is the rule that picks one — and it has
never been tested, because `record.py --verify` re-parses the file into Python objects and
re-serializes with the same function. It is self-consistent by construction and will
always agree with itself; it never asks whether the rule is *specifiable* by anyone else.
The moment a second implementation exists, that line stops being an implementation detail
and becomes part of the format.

Measured on this machine — Python 3.9 against Node 26:

| value | Python | JS |
|---|---|---|
| float `1.0` | `{"a":1.0}` | `{"a":1}` |
| percentage `46.0` | `{"p":46.0}` | `{"p":46}` |
| integer `9007199254740993` | `9007199254740993` | `9007199254740992` |
| keys `😀` and `＀` | `{"＀":2,"😀":1}` | `{"😀":1,"＀":1}` |
| `\n` inside a string | `"ab\nc"` | `"ab\nc"` |

Three of the five diverge. The integer row is the one that surprises: **JS loses precision
silently** above 2^53 and returns a different number without saying so. The key-ordering
row is Python sorting by code point against JS sorting by UTF-16 code units — an emoji is
a surrogate pair beginning `D83D`, which sorts *before* `＀` (U+FF00) in UTF-16 and *after*
it by code point. Control-character escaping agrees.

**The percentage row is the live risk.** The method is made of percentages. The day a
payload carries `46.0` rather than `46`, the two implementations compute different hashes
and the browser verifier declares the chain broken on a perfectly intact register. That is
the worst failure this project can produce.

**RFC 8785 (JCS)** is the IETF specification that fixes exactly this: property ordering,
no whitespace, string escaping, and — the part that matters — number representation, for
which it adopts ECMAScript's `Number::toString`, the shortest form that round-trips as an
IEEE-754 double. It is written from the JavaScript side, so `JSON.stringify` with sorted
keys is already almost canonical. Python needs a library (`rfc8785` on PyPI), which
collides with the rule that the scripts run on the standard library alone — a case folder
must still work in ten years with no `pip install`.

**And it is not hypothetical: it is already in the validation case.** `cases/001` carries
**72 non-integer numbers across 18 of its 80 events** — `"ai_lexical": 94.0`,
`"human_words": 6.0`, `0.0`, `100.0`, and fractional ones like `10.3`. Python wrote `94.0`;
a JS verifier re-serializing the same event writes `94`, hashes different bytes, and
**declares the chain broken on a perfectly intact register.**

**And the divergence is wider than integral floats**, which is why the detection rule cannot
just look for `.0`. Measured: `1e16` is `1e+16` in Python and `10000000000000000` in JS;
`1e-7` is `1e-07` against `1e-7`; `1e-6` is `1e-06` against `0.000001`. Some values agree
and no simple rule separates them, so **every non-integer is forbidden and every one is
detected** — see `spec/canonical.md` §4 and §5.1.

**Which kills the obvious fix.** After `JSON.parse`, `94.0` and `94` are the same JS
value — the distinction is destroyed by parsing and cannot be recovered afterwards. So a
verifier built on `JSON.parse` + `JSON.stringify` **cannot** verify the registers that
already exist, no matter what rule is adopted going forward. And RFC 8785 does not rescue
it either: JCS renders `94.0` as `94` too, so **adopting JCS would break `cases/001` and
`cases/002` as thoroughly as the naive JS path does.** JCS is not backward-compatible with
the registers this project has already sealed.

**So the format is not a choice to be made; it is a fact to be written down.** The
canonicalization rule *is* Python's

```python
json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
```

with everything that implies: integral floats keep their `.0`, keys sort by code point, and
numbers use Python's `repr`. That has to be specified explicitly in `spec/`, because it is
already load-bearing for two sealed cases.

**And reopening does not help**, which is the first idea anyone has. The reopening
procedure appends; the register is append-only; the floats are inside events already
recorded. There is no route that normalises a register already sealed.

**Consequence for the verifier — decided: it refuses what it cannot read, rather than
growing a parser to read it.**

Two options existed. A tokenizer of roughly 100–150 lines, preserving number literals as
source text and sorting keys by code point, placed inside the one component whose entire
value is being small enough for a reader to audit. Or a verifier that detects a pre-spec
register and says so.

**The second is chosen.** Detection costs about five lines of regex over the raw text —
`\d\.0` before a comma, brace or bracket, and any non-ASCII key — and the message is not
*chain broken* but:

> *This register predates the canonicalization spec. Check its chain with
> `python3 record.py --verify` in the case folder.*

A verifier that states precisely what it cannot do is worth more than one that can do
everything thanks to 150 lines nobody will re-read. It is also the move the project makes
everywhere else: name the limit rather than engineer around it.

**What this actually costs is one case.** `cases/002` is already declared incompatible —
Italian schema, CHANGELOG 1.0.0. And `cases/001` stays fully verifiable by the Python
path: `record.py --verify`, `ssh-keygen -Y verify` and `measure.py` work today and will
keep working. What is lost is browser verification of one historical artefact, which
should carry a line in its own `VERIFICA.md` saying so.

**Which promotes the forbid rule from hygiene to the fix itself.** `record.py` refuses at
`append()` time — refusing, not warning, the pattern the project uses everywhere else:

> **No floats in event payloads. Integers within ±2^53. ASCII keys.**

The integer bound matters most, because that failure is the silent one; ASCII keys make the
ordering question disappear entirely.

**And it costs almost nothing**, which is what makes it the right fix rather than a
concession. Those values — `"ai_lexical": 94.0` — are *descriptive* payload: nothing reads
them numerically, and the measurement of record is `kpi.json`, never the register. Writing
them as strings, `"94.0"`, loses no information a reader had.

**The conformance vectors are not optional.** Commit `spec/vectors/canonical.jsonl` —
pathological events with their expected canonical bytes and hashes — and make both
`record.py` and the JS verifier pass it in CI. **Shared test vectors, not shared code**, is
the only thing that stops two implementations diverging in silence.

**Two acceptance tests, and the second is the one people forget.** The JS verifier must
reproduce the sealed root of the first case closed under the spec, exactly. And it must
**refuse `cases/001` with the pre-spec message** — not fail on it, not silently mis-hash
it, but recognise it and say what to run instead. A verifier that reports a false forgery
on the project's own validation case is worse than no verifier at all.

**Reconstruction and coverage: do not reimplement.** `norm()` does NFD normalization,
strips `Mn` combining marks, folds six typographic characters, collapses whitespace and
lowercases; `find()` does a normalized `str.find`, then a character-by-character re-walk
to map the position back into the un-normalized block, with a `re.IGNORECASE` regex
fallback. Python's `IGNORECASE` and JS's `i` flag do not case-fold identically. It is
reimplementable, and it will diverge on exactly the edge cases the code exists to handle.

**So the browser verifier does not compute the KPI.** It verifies that `kpi.json`,
`spans.json` and `annotation.json` hash to the values in the signed manifest — which
proves the numbers on the page are the numbers that were sealed — and then says, in plain
language: *to recompute the measurement, run `python3 measure.py` in the case folder.* One
line of copy, and exactly one implementation of the number.

**Timestamps: partial, and say which part.** The browser *can* parse the `.tsr` and check
that the imprint inside it equals SHA-512 of the register — a real check, no network — and
display the genTime. It **cannot** validate the TSA's certificate chain without a trust
store. For OpenTimestamps it can parse the `.ots` and show the claimed block height, and
nothing more: confirming it needs a node or an explorer. **Do not query an explorer by
default** — that would silently turn the offline verifier into a networked one. Show the
parsed claim and the exact command.

**Packaging: one self-contained HTML file**, no network, no `fetch`, ever. The reader
drops their downloaded case folder onto it. The file must itself be hash-published in the
repository, so the verifier is verifiable, and it must open from `file://`.

---

## 4. Priority two — the deposit service

### What is deposited, and what is not

**Decided: the reader never sees the writer's drafts.**

`versions/` is the most intimate thing in a case — in `cases/001` it holds 22 successive
drafts — and the register alongside it holds the author's briefs, instructions and
editorial reasoning, which may name an editor or a source who consented to nothing. None
of it is needed to check anything.

The design already anticipated this, which is why the resolution costs almost nothing.
`cases/001`'s closing manifest covers **exactly one** file under `versions/`:
`versions/v22_final.txt`, the source of the measurement. The other 21 drafts are not
manifest-covered, are not read by `measure.py`, and are not touched by any check a reader
runs.

So the deposit is:

| deposited | withheld |
|---|---|
| `events.jsonl` and its seal files | every draft but the last |
| `annotation.json`, `spans.json`, `kpi.json` | |
| `case.json`, `icon.svg`, `verification.html` | |
| the scripts | |
| **the source version only** — the published text | |

The reader keeps everything: the chain verifies, the signature verifies, the manifest
verifies, and `measure.py` still reconstructs the text from the spans, because the file it
reconstructs is the published article. What they lose is the ability to read drafts, which
proved nothing to them in the first place.

**But this makes an unenforced rule in `SKILL.md` load-bearing, and it is not being
followed.** The skill says to record each `version` event *"with the word count and the
SHA-256"*. In `cases/001`, across 19 `version` events, **not one carries a digest or a word
count** — the payloads name the artifact path and describe the change, and nothing more.

That was a documentation gap while the drafts shipped alongside. Once they are withheld it
becomes the whole guarantee: **the digest is what commits the author to a draft without
revealing it.** With it, the register — signed and timestamped — proves that twenty-two
versions existed, in that order, at those sizes, with those fingerprints; and if a draft is
ever disputed, the author can produce it and it either matches the sealed digest or it does
not. Without it, withholding the drafts withholds the commitment too, and the reader is
left with a filename.

**So: make the digest and the word count mandatory in the `version` event, and have
`measure.py` refuse a case whose `version` events lack them.** The rule already exists; it
needs a gate, in the same spirit as the two checks that already stop the pipeline.

**Unlisted, not private.** Withholding drafts is a separate question from who can reach a
case. A URL is not an access control: an unguessable address is a bearer token, and URLs
leak through `Referer` headers, browser history, link previews, mail scanners and proxies.
What *is* achievable, and is what the requirement really asks for, is that the archive not
be a browsable shop window of everyone's writing process: **no index, no search, no
per-author directory, `noindex` for crawlers.** Whoever has the address gets in; nobody
finds a case by wandering. That constraint is already in this document for a different
reason — the instance must never be searchable by person, or it becomes the identity
authority — and it serves both purposes at once.

### The address

**An address cannot be both derived from the certificate and secret.** The public key is
public and the root is printed in the technical line, so anything computed from them alone
is computable by any reader.

**And an author-keyed namespace is worse than it looks.** `/u/<fingerprint>/cases/<root>/`
does not merely invite enumeration — it *correlates*. Two documents by the same author are
visibly by the same author to anyone holding one URL, and the whole of a person's output
hangs off a prefix that is published on their own key page. That is a property nobody asked
for and some authors would actively refuse.

**The address is therefore opaque, flat, and carries no author component:**

```
https://<instance>/c/<case-id>/

case-id = base58( HMAC-SHA256(author_secret, root) )[:22]      # 128 bits
```

- **`author_secret`**: 32 random bytes generated by `colophon setup`, kept in
  `~/.config/colophon/`, never published, backed up alongside the private key. It has no
  relation to the fingerprint, so knowing the public key gives an attacker nothing.
- **HMAC rather than a random id**, because a random id has to be stored somewhere and that
  store gets lost. With HMAC the author **recomputes any case's URL** from the root and the
  secret, locally, forever — there is no URL database to keep — while to anyone else the id
  is indistinguishable from 128 random bits, since HMAC is a pseudorandom function. Holding
  one case-id is no help in finding another. The server never learns the secret.
- **base58**, for two reasons specific to this project: it contains no underscore, and
  `SKILL.md` already documents that URL detectors cut a link at the first one; and it omits
  the look-alike characters (`0`/`O`, `I`/`l`), because that address gets printed in a PDF
  and somebody will retype it. Twenty-two characters.
- **No author component at all.** Cases are not merely unenumerable, they are mutually
  unlinkable. An author who *wants* an index of their own cases publishes one themselves,
  on their own site, listing the URLs they choose to reveal. The service does not offer
  one — the same logic by which it offers no search.

**What this gives up, and why it is affordable.** The address no longer commits to the
content, so it is not self-verifying. But link substitution stays detectable from a better
anchor: **the technical line of the note already prints the root**, so the reader compares
the case they downloaded against the article in their hands, not against the URL somebody
sent them. Whoever forges the link does not control the PDF being read.

**And one tension that must be stated rather than smoothed over.** A full export is what
makes mirroring real, and it is the condition under which the deposit service was approved
at all — but whoever holds it holds everything.
**Non-enumerability is therefore a property of the live service, not of the archive.** It
defends against drive-by correlation — someone holding one of your links does not thereby
discover the rest of your output — not against a party who obtains the whole set.
Promising both would be dishonest; saying which one is being bought is not.

**Which is why whole-instance mirroring is the wrong default.** An author chose to publish
*that case*; they did not choose to have the entire contents of an instance archived
forever as a collection, with every `case.json` naming its author inside it. So the
archival push is **per case, on the author's choice at deposit**, and `owners.jsonl` — the
private `case-id → fingerprint` map — never leaves the instance in any export at all.

### The circularity problem

If a user with no site publishes their key *and* deposits their evidence on the same
instance, that is `cases/001`'s defect relocated onto the owner's server: one host can
substitute both. The analyst and the architect arrived at the same answer by different
routes, which is a good sign.

**The instance serves a copy of the key, declared as a convenience copy, and never as the
trust anchor.** What it publishes instead is an **observation**: on first submission it
records `{fingerprint, key, first_seen, source_url}`, appends it to its own hash-chained
observation log, and OTS-stamps that log daily.

This is the one genuinely new thing a server can produce — a third party asserting *this
key was already published at this address on this date* — and it is worth building
precisely because the author cannot fabricate it afterwards. It converts "trust the host
today" into "the host attested this on a date you can check *without* the host", which is
strictly better than `cases/001`, where nothing external attests anything about the key.

Two supporting mechanisms:

- **Onboarding requires at least one anchor the instance does not control**, and offers
  the cheapest ones: a GitHub signing key, a DNS TXT record, a `.well-known` on any domain
  the author has.
- **If the author declines all of them, it is stated, generated and not typed.** When
  `key_url` and `register_url` share a host, `build_page.py` and `VERIFY.md` print a
  sentence saying so and saying the binding is only as strong as that host's account
  control. This is entirely in character: the README and `VERIFY.md` already lead with
  what is not proved. Colophon's answer to an unresolvable trust gap has always been to
  name it.

### The server, specified

**Storage: flat files, content-addressed, no database.** A case is an immutable directory
named by its sealed root hash. SQLite only as a rebuildable index — deleting it must lose
nothing.

```
/data/c/<case-id>/…                 # the byte-identical case folder
/data/c/<case-id>/MANIFEST.sha256
/data/keys/<fingerprint>.allowed_signers     # verbatim, served under its own path
/data/owners.jsonl                  # case-id -> fingerprint, private to the server
/data/observations.jsonl            # hash-chained, OTS-stamped daily
```

There is nothing to register and nothing to contend: a case lives at an opaque id, and the
mapping from id to owner stays inside the server.

| route | purpose |
|---|---|
| `GET /c/<case-id>/` | serves `index.html` as `text/html` |
| `GET /c/<case-id>/<file>` | **`application/octet-stream`, `Content-Encoding: identity`** for every non-HTML file |
| `GET /c/<case-id>/bundle.tar` | uncompressed tar, byte-exact |
| `GET /k/<fingerprint>` | the author's `allowed_signers`, `text/plain`, verbatim |
| `GET /find/<root>` | **lookup only** — answers with the case-id, to a caller who already has the root |
| `GET /c/<case-id>/challenge` | a short-lived nonce, for the author |
| `POST /c` | signed submission; the server derives placement from the signature |
| `DELETE /c/<case-id>` | signed withdrawal — see below |
| `GET /observations.jsonl` | the key-observation log |
| `GET /export.json` | date, SHA-256 and **where the export lives** — not the export itself |
| `GET /verify/` | the single-file verifier |
| `GET /.well-known/colophon-instance.json` | self-description, for mirrors |

**Byte-identity is a serving problem, not a storage problem.** Serve `events.jsonl` as
`text/plain` and a browser save may rewrite line endings; serve it gzipped through a proxy
that re-encodes and the digests change. Force `identity`, no transforms, no minification,
and use `tar` rather than `zip` for bundles. `.gitattributes` covers git; this covers
HTTP; the two together are what makes the manifest survive the trip.

**Authentication without accounts: signature only.** The `POST` body is a submission
manifest signed under namespace `colophon-deposit`, and it carries the case-id the author
computed. The server verifies the signature, records `case-id -> fingerprint` privately,
and refuses a later submission to the same id under a different key. **The path reveals
nothing; the server still knows exactly who owns what.** No passwords, no email, **nobody
to ban** — which is what makes the service structurally non-gatekeeping rather than
promised to be.

**The deposit refuses what it is not meant to hold.** It rejects any submission containing
files under `versions/` other than the manifest-covered source, and it caps size and rate.
A deposit service that accepts anything becomes a file host.

**The Jekyll trap, inverted.** GitHub Pages will not serve dot-directories, so
`.well-known` 404s without `.nojekyll` — add it to the repository today. The Docker
instance must explicitly *allow* dot-paths, which most static-server defaults block.

### What the instance must never become — mechanisms, not promises

Never a gatekeeper: no approval queue, no verified mark, no badge on the artefact. Never a
runtime dependency. And never a place where a published case can be *silently* deleted —
which is not the same as never deleted, a distinction the next subsection settles.

### The author's own data: retrieval, and withdrawal

**Retrieval needs no authentication at all.** The author fetches `bundle.tar` exactly as a
reader does, because they **recompute the address themselves** from the root and their
`author_secret`. That is the property earned by choosing HMAC over a random id: there is
nothing to keep and nothing to ask the server for.

**Withdrawal is by signature**, the same identity used to deposit:

```
GET    /c/<case-id>/challenge     → a nonce, valid for minutes
DELETE /c/<case-id>               → SSHSIG over the nonce, namespace "colophon-delete"
```

The server checks the signature against the fingerprint in `owners.jsonl`. The dedicated
namespace is doing real work: it is exactly what SSHSIG namespaces exist for, and it stops
a signature made to deposit from being replayed to delete. A server-issued challenge beats
a timestamp window because it needs no clock agreement, and for an irreversible operation
the extra round trip is worth its cost.

**What withdrawal means, and what it cannot mean.** Two different things wear the same
word:

- **Withdrawal from this instance** — the author's right, self-service, immediate.
- **Unpublication** — impossible once copies exist, and dishonest to promise.

The honest mechanism is the **tombstone** the takedown rule already uses: the id keeps
answering, and says *this case was withdrawn by its author on <date>*, not 404. A reader
holding a link and a document deserves to tell "wrong address" from "withdrawn"; and a
tombstone is what makes *not a gatekeeper* checkable, since it stops an operator making a
case vanish and claiming it was never there. It leaks nothing: the id is opaque, so only
someone who already had it learns anything.

**With one exception.** An author withdrawing *because they regret publishing* is the one
person for whom a tombstone confirming existence is the wrong answer. So: tombstone by
default, **hard deletion available**, and the accounting preserved in aggregate — the
instance states "3 cases permanently removed" without saying which.

**Two uncomfortable consequences, both to be written down rather than discovered later.**

*Losing the key loses control.* The key **is** the identity, exactly as it is for the
register. There is no cryptographic recovery and there must not be one. Onboarding says so
at the moment the key is generated, alongside the insistence on a backup.

*But the legal route cannot be gated on a key.* A data subject's right to erasure may not
be conditioned on holding a private key. So there are **two paths, and the second exists by
obligation rather than courtesy**: the signature is the fast, self-service one; a
substantiated request with out-of-band identity checking is slow, operator-mediated, and
logged. An instance that collects a verified email address at deposit can make that second
path self-service instead of manual — which is the one thing email tokens genuinely buy,
and it is not an anti-abuse property. See §5.

*And `observations.jsonl` is where append-only meets erasure.* It is hash-chained and holds
a fingerprint and a date, which are the author's personal data. Erasure there is answered by
**appending a redaction**, not by removing a line — and if the underlying datum genuinely
has to go, the chain breaks and the instance says so. Append-only integrity and the right to
erasure really do conflict; the only honest response is to state which one gave way.

- **Static file tree only.** Everything served is a file in the deposited folder, so
  shutdown reduces to copying a directory.
- **Mirror at deposit, not at shutdown — per case, and by the author's choice.** A
  deposited case the author elects to mirror is pushed to Software Heritage and the
  Internet Archive, and the permanent identifier appears on the case page. **This is the
  mechanism that converts the instance from *the* location into *one* location** — the
  whole difference between a guarantor and a convenience — and it must exist on day one.
  What is never pushed automatically is the instance *as a collection*: see §4.
- **Content-addressed identity, as a lookup and never as a listing.** `GET /find/<root>`
  answers a caller who already holds the root — which means they hold the document — so a
  reader can re-find a case after any move. It must not be a downloadable map: as a file it
  would be the index the opaque addresses exist to prevent.
- **A full export as a command, not a URL.** `colophon-export` produces the exact hostable
  tree, verifier included — but the bytes are **not served over HTTP**, which removes the
  single most expensive endpoint from the attack surface. They are *published* instead, to
  archives and to a swarm, and `GET /export.json` names the date, the SHA-256 and the
  locations. Removing the endpoint without publishing the result would kill the very
  condition under which this service was approved; publishing it makes the guarantee
  **stronger**, because an export the operator does not host is one the operator cannot
  withdraw. An operator-mediated export on request is not acceptable: it would make the
  operator the custodian of the exit.
- **No analytics.** A disclosure tool that logs its readers is self-refuting, by the same
  logic as *nothing phones home*.
- **A published shutdown commitment**: notice period, final tarball to every depositor,
  read-only as the failure state rather than off.

### The obligations the owner takes on

`versions/` holds unpublished drafts, and `events.jsonl` holds the author's briefs,
instructions and editorial reasoning — more intimate than the finished article, and it may
name third parties (an editor, a source) who never consented to anything.

The actionable minimum, all of it before the first deposit:

- **Show the author the file list and byte counts before upload**, per case. Not a
  checkbox — the actual list.
- **A privacy notice at the deposit step**: named controller, contact, lawful basis, and a
  short stated log retention.
- **Say before the deposit, not after a request, that deletion cannot mean
  unpublication.** Mirroring is the point, and the honest statement of that conflict has
  to precede the act.
- **Takedown as the only content decision the instance ever makes**, framed as a legal
  obligation and never as editorial judgement, with every removal logged as a public
  tombstone. Visible removal is what keeps *not a gatekeeper* true even when law forces
  one.
- **Size and rate caps.** A deposit service that accepts anything becomes a file host.
- **Log as little as possible.** Holding other people's evidence makes the operator a
  subpoena target for who deposited what.

---

## 5. Running an instance: abuse, limits, and terms

There are two surfaces and only one of them is a real question.

### Reading

Volumetric, and unrelated to the design: static files behind a cache, connection limits,
done. One property is worth making explicit, because it is a gift: **the read path and the
write path are independent.** If the deposit is swamped, it can be switched off entirely
and nothing breaks for any reader. **Suspending writes is a legitimate degradation**, the
same way read-only is already the stated failure mode rather than shutdown.

One caveat specific to this design: a CDN in front of the read path may re-encode
responses, and the digests depend on the bytes. Configure it to transform nothing, and
**verify by fetching an `events.jsonl` through the CDN and diffing it against the origin**
— serving non-HTML as `application/octet-stream` helps, since transformations target
textual types, but this must be tested and not assumed.

### Writing

**First, the defence that costs nothing and removes most of the problem: ingest accepts a
closed schema, not arbitrary files.** The server knows exactly which names belong to a
case — `events.jsonl` and its seal files, `annotation.json`, `spans.json`, `kpi.json`,
`case.json`, `icon.svg`, `verification.html`, the scripts, and the single source version.
Everything else is refused. That alone kills use as a file host, which is the likeliest and
costliest abuse.

**Second, validate on ingest** — recompute the chain and the manifest digests before
storing, and refuse what does not reconcile. This looks like it contradicts the rule that
the server must never validate, and it does not. The distinction is worth writing down,
because it reads like an inconsistency:

> **Refusing malformed input at the door is not pronouncing a verdict to a reader.** The
> first is a spam filter; the second is the authority the method refuses. The server may
> reject what is not a well-formed case without ever telling a reader whether a case is
> valid.

It also raises the attacker's cost: flooding now requires producing valid hash chains,
valid signatures and coherent manifests.

**Third, make a new key expensive.** The signature already gives a stable per-key identity
with no account, so quotas per fingerprint are free. The counter-move is generating keys at
will — a Sybil attack — so the problem reduces to one thing: the cost of an unseen key. A
tiered proof of work does it: the submission carries a nonce such that
`H(case-id ‖ nonce)` has N leading zero bits, **expensive for a fingerprint never seen
before and light for a known one**. For the honest author it is seconds, once per case; for
someone burning keys it is seconds *every time*. It does not confer immunity — it scales
linearly with the attacker's resources — but it buys orders of magnitude without
introducing accounts, which is the constraint that cannot be broken.

**Fourth, and it reuses a step the author already takes:** require the deposited register
to carry a valid RFC 3161 timestamp predating the submission. `seal.sh` produces one
anyway. An attacker must obtain real timestamps for each fabricated case, and free TSAs
rate-limit. A reinforcement rather than the gate itself, since it makes admission depend on
a third party's availability.

Plus the obvious, already stated elsewhere: size and rate caps, a global cap on accepted
deposits, and content-addressed storage, which deduplicates identical bytes.

### Policy belongs to the instance, not to the format

This matters more than any single measure.

**The format must never require an account. Any given instance may require whatever it
likes.** A university running the container for fifty researchers allowlists fifty
fingerprints and has no abuse problem at all. A public instance uses proof of work and
quotas. A third operator accepts only invited deposits. **They are the same Docker image
with a different policy file** — and that is what makes "anyone can run their own" true,
rather than a promise that breaks the first time someone abuses it.

### Email tokens: a policy option, and what they are actually for

An email-verified token is worth having, but not for the reason it first suggests itself.

**As an anti-abuse measure it earns less than it costs.** It raises the Sybil price — one
mailbox per identity — but disposable-address services lower that a great deal, and for a
trial instance an **invite code achieves the same effect with none of the baggage**: no
user database, no SMTP, no new personal data. Against volumetric read attacks it does
nothing whatever.

**And the cost is structural, because half of this document rests on it.** An email is an
account. The claim not to be a gatekeeper rests on *there is nobody to ban*: keep a
register of addresses and you can ban, you can be compelled to disclose, and you are
holding personal data that §5 has just committed to minimising — in the same breath as
noting that holding other people's evidence makes an operator a target for requests about
who deposited what. It also adds an SMTP dependency to a project whose rule is that nothing
phones home, and mail has its own ways of failing: spam folders, deliverability, a provider
down.

**It also cannot replace the signature.** A deposit must stay signed, because the signature
is what binds the case to the key that signed the register. Email would be *additional*,
never instead — two mechanisms where there was one.

**Where it genuinely earns its place** is a problem this document has already declared
unsolvable: losing the key loses control, and the right to erasure cannot be conditioned on
holding a private key, so **an operator-mediated recovery path has to exist anyway**. A
verified address does not add a mechanism; it makes an obligatory one self-service. That is
a real gain, and it is not an anti-DDoS gain.

So:

- **Upload — the signature is always required; email is never a substitute.** An instance
  may additionally gate deposits behind a verified address as policy. If email could
  authorise an upload in place of a signature, a compromised mailbox would deposit in
  someone's name; with the signature mandatory it cannot, because it does not hold the key
  that signed the register.
- **Withdrawal — the signature is the fast path; a verified address is the recovery path.**
  With the warning stated to the author when they supply it: **if email can withdraw, a
  compromised mailbox can withdraw.** Add latency as the standard defence — an
  email-initiated withdrawal takes effect after 24 hours, with notice to the address and a
  cancel link. It costs one line and removes the whole class.
- **Minimise what is kept.** A salted hash for rate-limiting and de-duplication; the
  plaintext address **only if the author opts into recovery**. An author who declines
  leaves no address at all.

All of it under the rule that carries the rest: **the format never requires an email; a
given instance may.** Same image, different policy file.

### The test instance, concretely

For a public instance meant for testing, the goal is not a hardened service. It is to cap
the blast radius and be able to switch it off without losing anything.

1. **Gate writes with an invite, and say so on the page.** It removes most of the problem
   for an afternoon's work, and it does not betray the principle: **not being a gatekeeper
   is a property of the format and the software, not of one operator's trial instance.**
   The container anyone downloads has no invite; this instance does. Build the proof of
   work when it is needed, not now.
2. **Do not expose the origin.** A tunnel, so the host has no directly reachable public
   IP and origin attacks stop being a category.
3. **Fixed-price hosting.** For a solo operator the real damage of a flood is not downtime
   but the bill. **Nothing billed per request or per byte** — a fixed-price host that
   throttles when its allowance is spent degrades instead of charging, which is the
   behaviour to want.
4. **A disk quota, a global cap, and log rotation.** A flood then fills a partition chosen
   in advance rather than the machine, and logs do not become a self-inflicted outage.
5. **A fully static read path and a kill switch for writes — tested before it is needed.**
6. **Isolate it.** Its own domain, its own host, no credentials shared with anything that
   matters.

### What the public instance must say

**No guarantee of service, stated plainly.** No SLO, no uptime commitment, and it is an
honest position rather than an evasion, because the design makes downtime survivable: the
root identifies the case, the published export mirrors it, and the disclosure copy carries
*"if this address is dead, the case is identified by its root hash"* — **provided the
mirroring happens at deposit**, which is the one requirement in this document that cannot
be deferred.

**No personal data, and the prohibition has to be worded precisely**, because a case
inherently contains some: the author's name is in `case.json`, their contact in
`VERIFY.md`, their key fingerprint in the seal. That is personal data, it is the author's
own, and publishing it is the entire point of a signed disclosure. So the rule is not "no
personal data" — it is:

> **Do not deposit anyone's personal data but your own.** No names or identifying details
> of sources, editors, interviewees or any third party in the register or the annotation;
> nothing in a special category; nothing confidential. Deposit the record of how a text was
> written, not the people who appear around it.

The mechanism that supports this is already in the design: the deposit step shows the
author the file list and byte counts before upload, and that is the moment to restate the
rule — at the act, not in a page nobody reads. The decision that **drafts are never
deposited** removes the largest single source of the problem before it arises.

**And a warning about what a notice can and cannot do.** Terms of service do not make an
operator not a controller. Personal data on your disk carries obligations regardless of
what the page says; the notice gives grounds to refuse and to remove, and reduces what
arrives, but it does not transfer the duty. What actually reduces exposure is structural,
and all of it is already decided here: drafts withheld, third-party data refused by policy
and narrowed by the closed schema, the invite gate during the trial, minimal logs — holding
other people's evidence makes the operator a target for requests about who deposited what —
and a takedown route that works and is logged as a public tombstone.

---

## 6. Migration and exit

A URL baked into `case.json`, into the technical line and into every rendered PDF is
permanent. The architecture must assume it will be wrong.

**The manifest already solves this and the tooling has not caught up.** Any copy is
provably *the* copy, by hash. Three things make that operational on day one:

1. **The root hash is the case's true identity. URLs are hints.** The verifier must accept
   a case from *any* source — local files, a mirror, an archive — and must never require
   the declared URL to resolve.
2. **A published export in v1.** The complete instance minus `owners.jsonl`: every case,
   every key, the observation log. It is a command, not a route, and its bytes go to
   archives and a swarm — torrent and IPFS fit particularly well, since the people who want
   an export are the people willing to seed it, so **the mirrors supply the bandwidth**.
   `GET /export.json` publishes the date, SHA-256 and locations, and the digest is
   OTS-stamped monthly.
3. **A `location` field, not a `url` field.** `case.json` carries a *list* of known
   locations with dates, appended to over time, and `build_note.py` renders the most
   recent — so moving hosts is an append, not a rewrite of history.

And one line for the disclosure copy, which is the exit strategy in a sentence:

> *If this address is dead, the case is identified by its root hash — any copy that
> matches it is the case.*

---

## 7. What must never move server-side, and the smallest v1

**Never:** event capture; the chain's computation; the private key; the annotation; **the
measurement** — `measure.py` stays the single implementation, the browser checks digests
and does not recompute the number; the decision to publish; and any validation verdict.
The server stores and serves. It never says whether something is good.

**In the first Docker image:**

- static file serving with forced `identity` encoding and dot-path support
- `POST /c`, signature auth, opaque case ids, private owner map, drafts rejected
- `GET /find/<root>`, lookup only
- `DELETE /c/<case-id>` with a server-issued challenge, tombstone by default
- the export as a command plus `GET /export.json` — day one, not later
- `observations.jsonl`, hash-chained, OTS-stamped daily
- the single-file verifier at `/verify/`, bundled offline
- `.well-known/colophon/keys` served verbatim as `text/plain`

**Deliberately not in v1:** accounts, search, badges, any web UI for creating cases, any
server-side execution of `measure.py`, any "verified" indicator, TSA relaying, rendering.

Each of those is a step toward the instance becoming the authority. And the moment the
project runs the only instance anyone uses *and* that instance pronounces verdicts,
Colophon has replaced an unverifiable self-declaration with an unverifiable third-party
one — which is the failure it was built to escape.

---

## 8. Decisions needed

1. **Is the public instance a commitment or an experiment?** The mirroring-at-deposit
   requirement and the shutdown commitment are what make the difference survivable, and
   both cost real work. Deciding this late is how a convenience becomes a guarantor by
   accident.
2. **Is `measure.py` the right place to gate the missing `version` digests?** The decision
   that the reader never sees the drafts makes the digest the only remaining commitment,
   and `cases/001` has none across 19 `version` events. Gating there stops a case from
   closing without them — but it also means the two existing cases can never satisfy the
   gate, and must be explicitly declared as predating it, the way the coverage check
   already is.
3. **Does `colophon verify` ship before or after the browser verifier?** The CLI is less
   work and serves the reader who is least stuck; the HTML file serves the reader the
   method actually fails today.
4. **Who operates the public instance in five years?** Not a rhetorical question — the
   answer determines whether the mirroring requirement is a feature or the whole point.
