# The client

Two commands, standard library only.

```bash
python3 cli/colophon.py setup            # once, before the first case
python3 cli/colophon.py deposit <case>   # build and sign a submission
python3 cli/test_cli.py                  # 42 assertions, in a throwaway HOME
```

## `setup`

Writes `~/.config/colophon/author.json`, mode 600 because it holds `author_secret`.
The config is a source of defaults, never an authority: `case.json` stays the per-case
record and the manifest covers it.

It asks for a name and a contact — `VERIFY.md` and `allowed_signers` each need one —
generates an Ed25519 key at `$COLOPHON_KEY` (default `~/.ssh/colophon`), and then does
the one check nobody performed for the first published case: **it fetches the key URL
and compares the published key material against the local one, byte for byte.** A key
nobody can fetch is a key nobody can bind to you.

It validates the evidence base URL as a *prefix* — https, trailing slash, and no
underscore anywhere, because URL detectors cut a link at the first one and the reader
gets a 404 while the printed line reads correctly. And it writes `cases/** -text` into
`.gitattributes` and adds `.nojekyll`, the two absences that produce failures nobody
diagnoses from the symptom.

Both warnings land where the decision is made rather than where the failure is: the
passphrase one at key generation, not at seal time; and the plain statement that
**losing the key loses control**, since it is what signs a register and what withdraws
a deposited case, and there is no cryptographic recovery.

## `deposit`

```
case_id = base58( HMAC-SHA256(author_secret, root_ascii)[:16] )   left-padded to 22
```

HMAC rather than a random id, so the author recomputes any case's address from the root
and their secret and never stores a URL. To anyone else it is 128 bits of noise: holding
one address is no help in finding another, and **there is no author component**, so two
cases by the same person cannot be linked from their addresses alone. base58 because the
address is printed in PDFs and retyped by hand — no underscore, no `0`/`O`, no `I`/`l`.

**The manifest decides what goes.** It covers the source version, the annotation, the
measurement, `case.json`, the icon, the verification page and every script a reader
runs. Deposited alongside it: the register and every seal artifact, superseded ones
included, and the three reader-facing files the manifest excludes on purpose.

Everything else is refused, with the reason printed. On `cases/001` that is 27 files
deposited and 25 withheld: 21 drafts, 2 renderings, 1 uncovered script.

**Drafts are never deposited.** `versions/` holds unpublished writing and the register
holds briefs that may name people who consented to nothing. The register commits to
their digests, so they stay attested without being revealed — a reader keeps every check
and loses only the ability to read your drafts.

The submission is signed under namespace `colophon-deposit`, which is not the register's
namespace: a signature made to deposit cannot be replayed to sign a register, and the
test asserts it.

## Not built yet

`--to` prints the request it will make. There is no instance to send it to — that is
phase 3. `setup --from <key_url>`, to rebuild the config on a second machine, is
described in the design and not implemented.
