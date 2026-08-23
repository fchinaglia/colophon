# Case 001 — *Come rendere trasparente il tuo uso dell'AI* (Italian)

The first case run with the method: a short post, 337 measured words, written in session
with the register open from the first line, then measured, sealed, and left as it was.

| | |
|---|---|
| Title | *Come rendere trasparente il tuo uso dell'AI quando scrivi un contenuto* |
| Author | Fabio Chinaglia |
| Written | 21–22 August 2026 |
| Language | Italian, on the English schema |
| Register | 72 events, root `4179f3f0f88ee7286fa17bf4eb3d84e77bb04285ab106727884511423a522b33` |
| **AI lexical share** | **46.0%** |
| **AI ideational share** | **0.0%** |
| Reconstructed after the fact? | No. Recorded live. |

The two numbers are as far apart as they can get: every idea in the piece is the
author's, and nearly half the words are the model's. The text is the author's own
methodological document turned into a post — the model wrote sentences for content that
already existed, which is the `machine polished` pattern, sitting in the `human written`
cell only because the words came out just over half his.

| phase | words | AI share |
|---|---|---|
| first draft | 159 | 55.0% |
| content revision | 119 | 36.6% |
| copy revision | 48 | 50.0% |
| titling | 11 | 0.0% |

---

## Verify it yourself

```bash
python3 record.py --verify     # the chain is intact
python3 measure.py             # reconstruction, then the two axes
```

Run the scripts **in this folder**, not the ones in `skill/colophon/`: they are the
versions this case was made with, and they are the ones its manifest covers.

The signature is detached, in `events.jsonl.sig`, made with the Ed25519 key in
[`colophon.pub`](colophon.pub) — fingerprint
`SHA256:0woBfwGMoKA6zsd9c0701YhBa+0aqIAI03JzaRV7raQ`. Full instructions, in Italian, are
in [`VERIFICA.md`](VERIFICA.md). The register is timestamped (RFC 3161, `.tsr`) and
anchored to Bitcoin (`.ots`).

The signature covers `events.jsonl` alone. The last event, a manifest, carries the
SHA-256 of seventeen files — the text, the annotation, the measurement, the page, the
icon and every script — so hashing those and finding them inside the signed register
closes the chain to the published artefacts. All seventeen match.

---

## What is wrong with this case

Four things. None of them is being corrected, and the reason is the same for all four:
they are inside the signed manifest, and reopening a sealed case to tidy it would cost
more than the tidying is worth. A case that says what went wrong is worth more than one
that looks clean — which is what `CONTRIBUTING.md` asks of anyone contributing a second
one.

**`verification.html` is broken.** It renders one paragraph per character for the
closing note: five hundred and thirty-seven of them. The cause was a bug in
`build_page.py` — `extra_notes` is a string in every case file ever written and the code
iterated it as a list — fixed in the skill on 23 August 2026, in commit `6a2852f`. The
copy in this folder still has the bug, because both the script and the page it produced
are covered by the manifest. The numbers on that page are correct; the layout of one
paragraph is not.

**`case.json` has gone stale in two places.** It says the register is not sealed — it
was sealed afterwards, on 22 August — and that the case is not published, which this
repository has since made untrue. It also says the model drafted the text in full,
"hence 100% AI words", where the measurement says 46%: the note was written before the
annotation, and the annotation is the thing that was checked.

**Sixteen declared changes have no span, and none of them is declared.** The register
names them — `F01`, `R02`, `R03`, `R04`, `R05`, `R07`, `R10`, `R12`, `R14`, `R15`,
`R16`, `R18`, `R21`, `R23`, `R24`, `R25` — and the annotation attaches them to no piece
of the final text. Most are edits a later edit replaced. The rule that requires each one
to be named, in `explained` inside `annotation.json`, was written on 23 August, after
this case was sealed; the current `measure.py` in the skill stops on a case like this
one, and the copy here does not. Read the number as what it is: sixteen interventions
whose trace in the final text cannot be pointed at.

**`kpi.json` records fifteen of them, not sixteen.** It was written before `R25`, the
last editorial change, and never regenerated. It is the same drift the coverage check
exists to catch, preserved here in the state it was caught in.

---

## What this case does not prove

The chain proves that no event was altered after it was recorded, and the timestamp that
the register existed on that date. **Neither proves the register is complete.** No
voluntary system can: an author can record faithfully or omit, and cryptography does not
tell the two apart. This register was moreover compiled by the model about its own
contribution.

Two limits specific to this case. It is 337 measured words — small enough that a single
span moves the percentage by a point, so treat the figures as orders of magnitude. And
the ideational share of 0.0% is a boundary value: it says the annotator found no idea
he could attribute to the model, which is a judgement about a text whose subject was the
annotator's own method.

---

*MIT License — Copyright (c) 2026 Fabio Chinaglia. See the LICENSE file.*
