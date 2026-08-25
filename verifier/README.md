# The verifier

One self-contained HTML file. No network, no dependencies, no server. A reader drops a
case folder — or a `bundle.tar`, or **the PDF that carries one**, or the loose files —
onto it, and everything runs on their own machine. Saved locally it keeps working, forever.

```
core.js           the whole implementation, DOM-free so it can be tested
ui.js             wires #drop #dir #fil #out to core.js and renders what it returns
components.css    everything core.js emits: cards, badges, notes, tabs, report pane
shell.html        the page that travels in a case — palette and chrome, no site
shell-site.html   the page served at a URL — masthead, nav, a line saying which
                  copy this is
build.py          inlines the shared parts into both shells, prints both digests
test.js           node harness: spec vectors + the real registers
verify.html       THE DELIVERABLE (generated — do not edit)
verify-site.html  the served build (generated — do not edit)
```

```bash
node verifier/test.js          # 78 assertions
python3 verifier/build.py      # rebuild both and print both digests
```

## Two shells, one behaviour

The copy sealed into a case must carry nothing of any website: it has to still work
in ten years, with no network and no address answering. The copy served at a URL has
the opposite job — a reader who lands on it should be able to tell where they are and
get back. One file cannot do both, and byte-identity was quietly serving the first
need while failing the second.

So there are two shells and one of everything else:

```
components.css ─┐
core.js ────────┼──► shell.html      ──► verify.html      (4 copies, identical)
ui.js ──────────┴──► shell-site.html ──► verify-site.html (served by the site)
```

A shell supplies a palette and the chrome, and must provide four elements:
`#drop` `#dir` `#fil` `#out`. **Everything else is inlined into both**, so the two
differ in chrome and palette and never in what they check or show — a property of the
build rather than a promise somebody has to keep. `build.py` refuses to build a shell
that has lost one of the four, and `tests/repo/test_invariants.py` asserts the shared
parts arrived intact in each.

**Publish both digests.** A verifier nobody can check is not one, and a served page
that cannot be compared with anything is exactly the thing this project tells readers
not to trust. `build.py` prints them.

## What it checks

- **the chain**, recomputed from the bytes supplied, per `spec/canonical.md`
- **the signature** — SSHSIG framing, the 100-byte pre-image, Ed25519
- **the manifest**, every digest against the file in front of it
- **the RFC 3161 token**, that its imprint commits to *these exact bytes*, plus whether it
  carries the eIDAS qualified marker

## What it opens

`render_pdf.py --embed` writes the bundle into the document as an incremental update,
Flate-compressed, and a PAdES signature adds a further revision on top. Dropping that PDF
here reads the attachment back out, so the reader is not sent to `pdfdetach` for a file
they were already handed. The published `cases/001/colophon-001.pdf` is a test fixture:
what comes out is compared with the tar beside it byte for byte, not merely parsed.

The file is scanned rather than walked through its xref chain, and that is the point:
several revisions are the normal shape of a colophon PDF, and the last definition of an
object number wins, which is what a revision means. Decompression is
`DecompressionStream('deflate')` — native, offline, no inflate of our own to carry for ten
years. Where it is missing, the page says to use `pdfdetach` or Firefox rather than
failing obscurely.

## What it says about the signature over the document

Four things, and the fourth is why the other three are worth computing:

- **which bytes the signature covers**, from the `/ByteRange`, and that the gap between
  its two runs is exactly the `/Contents` string — a signature cannot sign itself
- **that the digest in the signed attributes is the digest of those bytes**
- **that the signature verifies** against the public key in the signer's certificate —
  `crypto.subtle`, RSA PKCS#1 v1.5 and ECDSA, offline; anything else is named and not
  claimed — and who that certificate says the signer is
- **whether the record it just read is inside the signed bytes**

The last one is the question the method actually asks. `SKILL.md` says *embed, then sign,
in that order*, and a document signed the other way round shows a perfectly valid
signature over pages that do not include the evidence. `tests/fixtures/signed-pdf/` holds
one of each; both verify, and only one has signed anything that matters.

**None of this is a trust check, and the card says so in bold.** Whether the certificate
is qualified, was valid on the day, or has been revoked needs the EU trusted list and a
revocation service: network and policy, not arithmetic. A valid digest is not a valid
identity, and a page that blurred the two would be doing the thing this project exists to
stop.

## What it also shows

When the supplied files carry the case's own page — `index.html`, which the manifest
covers — a second tab holds it, and the checks stay on the first. The reader gets the
verdict and the report the verdict is about without extracting a tar to disk, and the dot
on the Verification tab keeps the worst finding visible while the report is in front.

The page is fed to an iframe through `srcdoc`, with **`sandbox="allow-scripts"` and
deliberately not `allow-same-origin`**. The report needs its own scripts — the
words/ideas toggle, the tooltips — and it is content out of the very package this page
exists to distrust; granting both flags together would undo the sandbox and let a crafted
bundle rewrite the verdict rendered around it. With `allow-scripts` alone it runs in an
opaque origin, fully usable and unable to reach anything. The cost is that its height
cannot be measured from the parent, which is why the pane is sized and scrolls inside
rather than growing to fit.

## What it deliberately does not

**It does not recompute the measurement.** It confirms `kpi.json`, `spans.json` and
`annotation.json` carry the digests the register sealed — which proves the published
numbers are the sealed numbers — and leaves the arithmetic to `measure.py`. `measure.py`'s
normalisation (NFD, combining marks, typographic folding, a case-insensitive regex
fallback) does not have identical semantics in JavaScript, and two implementations of one
number is worse than one.

**It refuses pre-spec registers instead of guessing.** `cases/001` carries 72 non-integer
numbers across 18 of its 80 events, and after `JSON.parse` a JavaScript program cannot tell
`94.0` from `94`. Rather than re-serialize and report a false forgery, it says the register
predates the spec and prints the command that does work. See `spec/canonical.md` §5.

**It never touches the network.** Validating a timestamp authority's certificate and
confirming a Bitcoin anchor both require it, so the page shows the commands instead of
pretending. Querying a block explorer by default would quietly turn an offline verifier
into a networked one.

## Crypto

Hand-written and bundled: SHA-256, SHA-512, Ed25519 verification. **Not `crypto.subtle`** —
it requires a secure context, and whether `file://` qualifies varies by browser. The
offline single-file mode is precisely the one that must not break.
