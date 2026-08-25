# The verifier

One self-contained HTML file. No network, no dependencies, no server. A reader drops a
case folder — or a `bundle.tar`, or **the PDF that carries one**, or the loose files —
onto it, and everything runs on their own machine. Saved locally it keeps working, forever.

```
core.js       the whole implementation, DOM-free so it can be tested
shell.html    the page, with a //__CORE__ marker
build.py      inlines core.js into shell.html -> verify.html, prints its digest
test.js       node harness: spec vectors + the real registers
verify.html   THE DELIVERABLE (generated — do not edit)
```

```bash
node verifier/test.js          # 61 assertions
python3 verifier/build.py      # rebuild verify.html and print its sha256
```

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

**The document's signature is not checked**, and the page says so where it says everything
else. A qualified signature is the one thing that names a person; validating it needs a
trust list and a certificate store this page will never carry. It reads the attachment and
tells the reader that the signature panel is elsewhere.

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
