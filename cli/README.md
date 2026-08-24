# The client

One command, standard library only.

```bash
python3 cli/colophon.py setup    # once, before the first case
python3 cli/test_cli.py          # 12 assertions, in a throwaway HOME
```

## `setup`

Writes `~/.config/colophon/author.json`, mode 600. The config is a source of defaults,
never an authority: `case.json` stays the per-case record and the manifest covers it.

It asks for a name and a contact — `VERIFY.md` and `allowed_signers` each need one —
generates an Ed25519 key at `$COLOPHON_KEY` (default `~/.ssh/colophon`), and then does
the one check nobody performed for the first published case: **it fetches the key URL
and compares the published key material against the local one, byte for byte.** A key
nobody can fetch is a key nobody can bind to you, and a key published inside the folder
it authenticates proves only that the folder agrees with itself.

With no domain, `https://api.github.com/users/<you>/ssh_signing_keys` works and is free.
It is weaker than a name you control — GitHub can change what it serves — but it breaks
the circle, which is the thing that matters.

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
