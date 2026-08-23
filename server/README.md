# The instance

Two containers, and the split is not tidiness.

```
web      nginx        static files, reads only
ingest   python        POST /c, and nothing else
```

Reads never touch the write process, so **the write kill switch is
`docker compose stop ingest`** and every reader is unaffected. A flooded deposit
endpoint degrades to read-only, which the design treats as a legitimate state rather
than as failure.

```bash
docker compose up --build            # :8080 reads, :8000 writes
python3 server/test_server.py        # 22 assertions against a live ingest
python3 server/test_loop.py          # the whole loop, nothing typed by hand
```

## What ingest checks, in order

Cheapest first, because throttling exists to protect the expensive ones.

| | check | why here |
|---|---|---|
| 1 | `Content-Length` cap | before a byte of body is read |
| 2 | invite code | a header against a file; no accounts, nobody to ban |
| 3 | signature | the first tar member, read alone |
| 4 | rate | a bucket per key fingerprint, plus a global backstop |
| 5 | filenames | a closed schema — this is what stops it becoming a file host |
| 6 | digests | each file against what the submission declares |
| 7 | chain and manifest | the expensive one, and therefore last |

Someone flooding it with unsigned rubbish stops at step 3 without ever touching the
disk.

**Refusing malformed input at the door is a spam filter, not a verdict.** The server
never tells a reader whether a case is true: no badge, no tick, no "verified". It
answers `stored, not endorsed`. The moment an instance pronounces, it has replaced an
unverifiable self-declaration with an unverifiable third-party one, which is the
failure the method exists to escape.

## The submission

One tar, `submission.json` first — so the signature is checked before anything else is
extracted. The envelope carries the submission, the SSHSIG under namespace
`colophon-deposit`, and the public key. The server derives the fingerprint from the key,
checks it against what the submission names, verifies the signature over the canonical
bytes, and binds `case-id → fingerprint` on first sight. A second key submitting to the
same address is refused.

**That map is private.** It lives in `/data/owners.jsonl`, never under `public/`: the
address must not reveal the author, or the opaque addressing was pointless.

## Storage

```
/data/public/c/<case-id>/…              the byte-identical case, plus bundle.tar
/data/public/k/<fingerprint>            the key, as a convenience copy
/data/public/observations.jsonl         hash-chained: this key was seen on this date
/data/owners.jsonl                      PRIVATE — case-id -> fingerprint
/data/invites.txt                       absent means the gate is open
```

`bundle.tar` is built once, at rest, so nginx only ever serves a static file. The
observation log is the one genuinely new thing a server can produce: a dated third-party
record that a key was already in use, which an author cannot fabricate afterwards.

## Byte identity is a serving problem

`gzip off`, `default_type application/octet-stream`, and only four types declared —
html, svg, css, js. Everything else, `events.jsonl` and every seal file included, is
served as octet-stream so a browser saves the bytes rather than interpreting them.
Compress a register on the way out and its digest changes; the signature then fails for
a reader who did everything right. `.gitattributes` covers git, this covers HTTP, and
both are needed.

## Not in v1, deliberately

`DELETE` and tombstones · `GET /find/<root>` · the export command and `export.json` ·
email recovery · proof of work · mirroring at deposit. Each is easier to design once the
loop exists, and the loop exists now.

Writes are gated by an invite for the trial. That does not betray the principle:
**not being a gatekeeper is a property of the format and the software, not of one
operator's trial instance.** The container anyone downloads has no invite file.

## Untested

**The compose stack has not been run** — it needs a Docker daemon, and none was
available. `nginx.conf` is unexercised: the tests stand a plain static file server in
for it, which proves the bytes survive storage and transport, not that the nginx
configuration is right. Run `docker compose up --build` and re-check a fetched
`events.jsonl` against its digest before trusting it.
