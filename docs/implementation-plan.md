# Implementation plan — first prototype

*Build document. The reasoning lives in `service-and-onboarding.md`; this is the order of
work, what each piece contains, and how you know it is done.*

---

> **Status, 23 August 2026 — all five phases are built.** `spec/` (the rule, 31 vectors,
> a checker), `verifier/` (one 34 KB self-contained page, 51 assertions), `cli/` (`setup`
> and `deposit`, 47), `server/` (ingest, 26, plus the end-to-end loop). The instance runs
> at `deposit.colophonmethod.com` and the key anchor at `colophonmethod.com`. The effort
> estimates below were roughly right; the order was the part that mattered, and building
> the verifier before any server existed is what let its first acceptance test run on day
> one. Read this as the record of a plan that was followed, not as work outstanding.

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


## Where things stand

The repository has the case pipeline — `record.py`, `measure.py`, `build_page.py`,
`build_icon.py`, `build_note.py`, `seal.sh` — and nothing else. **No server, no JavaScript,
no `spec/`, no Dockerfile, and no tests** (see `test-architecture.md`).

The prototype's job is to close one loop: **write → deposit → a reader verifies.** Anything
that does not serve that loop is deferred, and §6 says which.

---

## Phase 0 — the spec, which blocks everything else

Half a day, and it unblocks the largest piece.

The verifier must reproduce Python's bytes exactly, so the rule cannot stay implicit in one
line of `record.py`. Write it down.

```
spec/canonical.md              # the rule, stated
spec/vectors/canonical.jsonl   # pathological events + expected bytes + expected hash
```

`canonical.md` states that the canonical form of an event is

```python
json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
```

with everything that implies, spelled out rather than implied: **integral floats keep their
`.0`**, keys sort **by code point** (not by UTF-16 code unit), numbers use Python's `repr`,
and the chain is `h(n) = sha256(h(n-1) ‖ canonical(event_n))` over the body with `hash`
removed.

And it states the forward rule, which `record.py` will enforce at `append()`:

> **No floats in event payloads. Integers within ±2^53. ASCII keys.**

**Done.** `spec/canonical.md` plus 31 vectors in three files — 13 canonical, 9 pre-spec
detection, 9 append-guard — and `spec/check_vectors.py`, which passes. Measured against the
real registers: `cases/001` is flagged pre-spec at 18 of 80 events, and `example/` is
conforming and its chain verifies under the spec.

**Also in this phase, because it is three lines:** the `append()` guard that refuses a
payload violating the forward rule. Refuse, do not warn.

---

## Phase 1 — the verifier, before any server exists

Two to three days, and it is where the work is. Build it first: it needs no infrastructure,
and it has a known-answer test waiting for it.

One self-contained `verify.html`. No network, no `fetch`, opens from `file://`. Published in
the repository with its own SHA-256, so the verifier is itself verifiable.

**What it does, in order:**

1. Reader drops a case folder (or a `bundle.tar`) onto the page.
2. **Pre-spec detection first**, per `spec/canonical.md` §5.1 — a scanner that skips
   string literals and flags, outside them, any numeric literal containing `.`, `e` or `E`,
   any integer beyond ±2^53, and any non-ASCII object key. **Not a bare `\d\.0` search**:
   that misses `1e+16` and `1e-07`, and it would falsely flag the sentence *"the value was
   94.0 percent"*. If found, stop and say:
   > *This register predates the canonicalization spec. Check its chain with
   > `python3 record.py --verify` in the case folder.*
   Not "broken". Not a silent mis-hash.
3. **Chain.** Re-serialize each event per `spec/canonical.md`, SHA-256, compare to `hash`,
   and follow `prev`. Report the first broken link and the root.
4. **Signature.** Parse `events.jsonl.sig`:
   ```
   blob     = "SSHSIG" ‖ u32 version(=1) ‖ string publickey ‖ string namespace
              ‖ string reserved("") ‖ string hash_algorithm ‖ string signature
   preimage = "SSHSIG" ‖ string namespace ‖ string reserved
              ‖ string hash_alg ‖ string SHA-512(file bytes)
   ```
   The pre-image is **not the file** — for `cases/001` it is exactly 100 bytes. Verify
   Ed25519 over it. The `.pub` line is `<type> <base64 of the same publickey blob>
   <comment>`, so one length-prefixed reader (~25 lines) handles both.
5. **Manifest.** SHA-256 every file present, compare against the manifest event. Report
   what matched, what is missing, what is extra.
6. **Timestamp, partially.** Parse the `.tsr` DER, show the genTime, and check the imprint
   inside it equals SHA-512 of the register — a real check needing no network. State
   plainly that validating the TSA's chain requires `openssl ts -verify`. For `.ots`, show
   the claimed block height and the `ots verify` command. **Never query a block explorer**:
   that would turn an offline verifier into a networked one.
7. **The measurement it does not compute.** It confirms `kpi.json`, `spans.json` and
   `annotation.json` hash to the sealed manifest values, then says: *to recompute the
   measurement, run `python3 measure.py` in the case folder.* One implementation of the
   number, and this is not it.

**Bundled, not borrowed:** `@noble/ed25519` (~6 KB) plus a pure-JS SHA-256/SHA-512. Do not
use `crypto.subtle` — it needs a secure context, and whether `file://` qualifies varies by
browser. The offline mode is the one that must not break.

**Rough size:** 500–700 lines including the bundled crypto.

---

## Phase 2 — the client

One to two days.

### `colophon setup`

Runs once. Writes `~/.config/colophon/author.json`.

```
name, contact, author_id?
key      → ssh-keygen -t ed25519 -f ~/.ssh/colophon -C colophon
           print fingerprint; ask about a passphrase here, not at seal time;
           say plainly that losing this key loses control, and press for a backup
secret   → 32 random bytes, author_secret, backed up with the key
key_url  → ranked menu, then FETCH IT and byte-compare against the local .pub
base_url → a prefix; validate https, trailing slash, NO UNDERSCORE
route    → git+pages / rsync / instance / manual
tidy     → write and verify `cases/** -text` in .gitattributes; add .nojekyll
```

The key-URL fetch is the highest-value check in the whole flow. It is the one nobody did
for `cases/001`.

### `colophon deposit <case-dir>`

```python
case_id = base58(hmac_sha256(author_secret, root))[:22]
manifest = {case_id, root, sha256_events, files: {name: sha256}, ts}
sig      = ssh-keygen -Y sign -n colophon-deposit
POST /c  = manifest + sig + the files
```

base58, not base64: no underscore — `SKILL.md` documents that URL detectors cut at the
first one — and no look-alike characters, because the address gets printed in a PDF and
retyped by hand.

The author never needs to store the resulting URL: it is recomputable from the root and the
secret, forever.

---

## Phase 3 — the server and the container

Two days.

**Two containers, and the split is not tidiness.** Reads are static files behind nginx;
writes are a small Python app. That makes the write kill switch a `docker stop`, which is
the degradation mode the design already treats as legitimate rather than as failure.

```
compose.yml
  web    nginx        :80    reads only, static
  ingest python app   :8000  POST /c only
  volume /data
```

nginx, the parts that matter:

```nginx
gzip off;                       # digests depend on the bytes
default_type application/octet-stream;
location ~ /\. { allow all; }   # .well-known must be servable
# index.html as text/html; everything else octet-stream, identity
```

**Ingest, cheapest check first — the order is the point**, because throttling exists to
protect the expensive steps:

1. body size cap, before reading it all
2. invite code (see §6)
3. Ed25519 signature verify → gives the identity
4. token bucket on the fingerprint
5. filename whitelist — `events.jsonl` and its seal files, `annotation.json`, `spans.json`,
   `kpi.json`, `case.json`, `icon.svg`, `verification.html`, the scripts, and the single
   source version. **Everything else refused**, which is what stops it becoming a file host
6. recompute the chain and the manifest digests — the expensive one, and therefore last
7. store; record `case-id → fingerprint` in `owners.jsonl`, private, never exported

Refusing malformed input at the door is a spam filter, not a verdict to a reader. The server
never tells anyone whether a case is *valid*.

```
/data/c/<case-id>/…                       the byte-identical case folder
/data/keys/<fingerprint>.allowed_signers
/data/owners.jsonl                        private
```

Routes in the prototype: `GET /c/<id>/`, `GET /c/<id>/<file>`, `GET /c/<id>/bundle.tar`,
`GET /k/<fp>`, `GET /verify/`, `POST /c`.

---

## Phase 4 — the one thing not to defer

**Mirroring at deposit.** `service-and-onboarding.md` calls it the single requirement that
cannot be postponed, because it is what makes the instance *one* location rather than *the*
location — and therefore what makes "no guarantee of service" an honest position instead of
an evasion.

For the prototype it can be the minimum: a push to the Internet Archive per deposit, with
the identifier shown on the case page. Software Heritage and the author's opt-in come later.

---

## Deferred, deliberately

`DELETE` and tombstones · the observations log and its OTS stamping · `GET /find/<root>` ·
the export command and `export.json` · email tokens · proof of work · quotas beyond a crude
per-fingerprint bucket · Software Heritage · per-case mirroring opt-in.

None of them closes the loop, and each is easier to design once the loop exists.

**Writes are gated by an invite code** — a list in a file — for the entire trial. It costs
an hour and removes the whole abuse surface while the design settles. It does not betray
the principle: **not being a gatekeeper is a property of the format and the software, not of
one operator's trial instance.** The container anyone downloads has no invite.

---

## Acceptance tests

1. **The verifier refuses `cases/001` with the pre-spec message.** Runnable today, with no
   infrastructure, and it is the first thing to build toward: the first case sealed under
   the spec does not exist yet, while `cases/001` does and its expected answer is known.
   A verifier that cries forgery on the project's own validation case is worse than none.
2. **A new case, closed under the spec, verifies green in the browser** — chain, signature,
   manifest — and the verifier's computed root equals the sealed root.
3. **Round trip**: `colophon setup` → write a case → `colophon deposit` → fetch
   `bundle.tar` from the instance → drop it on `verify.html` → green. Nothing typed by hand.
4. **Byte integrity through the stack**: `events.jsonl` fetched through nginx (and through
   any CDN, if one is in front) is byte-identical to the deposited file. Test it, do not
   assume it.
5. **The kill switch**: `docker stop ingest` leaves every read path working.

---

## Effort

| phase | | |
|---|---|---|
| 0 | spec and vectors, `append()` guard | 0.5 day |
| 1 | the verifier | 2–3 days |
| 2 | `setup` and `deposit` | 1–2 days |
| 3 | server and compose | 2 days |
| 4 | mirroring at deposit | 0.5 day |

**About a week**, half of it in Phase 1.

---

## Decisions that block

1. **The canonical rule, confirmed** — Phase 0 cannot start without it, and Phase 1 cannot
   start without Phase 0. It is decision 1 of `service-and-onboarding.md` §8.
2. **Where the trial instance runs**, since it determines the disk quota and whether hosting
   is fixed-price. Nothing billed per request or per byte.
3. **Whether `record.py`'s log path stays script-relative** (`test-architecture.md`,
   scenario 30). It affects `colophon deposit`, which has to find the register.
