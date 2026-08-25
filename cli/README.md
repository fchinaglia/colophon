# The client

One command, standard library only.

```bash
python3 cli/colophon.py setup    # once, before the first case
python3 cli/test_cli.py          # 16 assertions, in a throwaway HOME
```

## `setup`

Writes `~/.config/colophon/author.json`, mode 600. The config is a source of defaults,
never an authority: `case.json` stays the per-case record and the manifest covers it.

It asks for a name and a contact — `VERIFY.md` and `allowed_signers` each need one —
and generates an Ed25519 key at `$COLOPHON_KEY` (default `~/.ssh/colophon`). That is all
it does.

**It opens no network connection, and that is the property to keep.** It used to fetch a
published key and refuse to finish when the address did not serve it, which meant a down
domain — or simply not having published anything yet — stopped an author at the first
step, before they had written a word. `test_cli.py` asserts the source imports no
`urllib` and names no `.well-known`, because that failure came back the moment the check
existed.

The key is published nowhere now. `seal.sh` copies the public half into the case as
`colophon.pub`, `build_bundle.py` packs it, and the reader checks the signature against
the copy that travelled with the evidence. What that cannot say is whose key it is — for
that there is a qualified electronic signature on the PDF the bundle is attached to, and
`setup` says so on its way out rather than offering an address it no longer has.

It also writes `cases/** -text` into `.gitattributes` and adds `.nojekyll`, the two
absences that produce failures nobody diagnoses from the symptom.

Both warnings land where the decision is made rather than where the failure is: the
passphrase one at key generation, not at seal time; and the plain statement that
**losing the key loses control**, since it is what signs a register and there is no
cryptographic recovery.

## What used to be here

`deposit`, and `address` — the base58 case id derived from an author secret. Both are
gone with the instance they talked to. A case now travels as a bundle its author packs,
with `build_bundle.py` in the case folder, and nothing has to stay online for a reader
to check it. `docs/plan-local-first.md` has the reasoning and what it costs.

## Why this is not in the case folder

It holds the author's key, and a case has to stay verifiable without one.

It is also the last thing here that is a *command the author runs about themselves*
rather than about a case, which is why issue #13 asks whether it should be a
conversation instead of a script. Now that it does one thing, that question is easier
to answer than it was.
