# Case 001 — *Come rendere trasparente il tuo uso dell'AI* (Italian)

The first case run with the method: a short post, 337 measured words, written in session
with the register open from the first line, then measured and sealed — and reopened once,
which the register records.

| | |
|---|---|
| Title | *Come rendere trasparente il tuo uso dell'AI quando scrivi un contenuto* |
| Author | Fabio Chinaglia |
| Written | 21–22 August 2026 |
| Language | Italian, on the English schema |
| Register | 78 events, root `61ab43258a5703e5549312878c04461c178a6b1fa4e0618c3fb9c290623f8652` |
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
SHA-256 of eighteen files — the text, the annotation, the measurement, the page, the
icon and every script — so hashing those and finding them inside the signed register
closes the chain to the published artefacts. All eighteen match. `README.md` and
`index.html` are deliberately outside it: they are prose about the case, and freezing
them would mean reopening the case to correct a sentence.

---

## What was wrong with it, and what was done

The case was sealed on 22 August 2026 and **reopened on 23 August**, after its own manifest
had declared that nothing further could be recorded on it. The register is append-only, so
that declaration is superseded and still visible: an event announces the reopening and its
reasons *before* any file is touched, and a fourth manifest closes it.

Four things were wrong.

**The verification page was broken.** It rendered the closing note as one paragraph per
character — five hundred and thirty-seven of them — because `build_page.py` iterated
`extra_notes` as a list where every case writes a string. The bug was fixed in the skill on
23 August, in commit `6a2852f`; the fixed script is now in this folder and the page is
regenerated. Twelve paragraphs, the note intact.

**`case.json` had three false statements.** That the register was not sealed and the case
not published — both true when written, both overtaken — and that the model drafted the
text in full, "hence 100% AI words", where the annotation measures 46.0%. The note has been
rewritten, and it now says what the measurement says.

**Sixteen declared changes had no span and no explanation.** They now have one each, in
`explained` inside `annotation.json`, reconstructed from the register rather than from
memory. Four kinds: an edit inside a block excluded from the count (`F01`, `R25`); a
deletion whose text is not in the final version (`R03`, `R04`, `R14`, `R21`); an edit that
left the attribution exactly where it was (`R02`, `R05`, `R07`, `R12`, `R23`, `R24`); and
an edit that a later one replaced (`R10`, `R15`, `R16`, `R18`). The rule requiring this was
written on 23 August, after the case was sealed — the information existed all along and had
never been written down. The verification page now shows all sixteen with their reasons.

**`kpi.json` had gone stale**, recording fifteen of those sixteen because it was never
regenerated after the last edit. Regenerated.

**No attribution was touched, and no number moved.** 46.0% lexical, 0.0% ideational, 18
spans, 337 words — identical to what the seal of 22 August attested. Declaring where the
coverage gaps are is not the same as measuring differently, and if it had been, this case
would have been left alone.

Two more things the reopening produced, both recorded. The coverage check stopped the run
on the reopening's own script-update event, because it counted a `meta` event as a change to
the text: a defect in the tool, fixed in the skill and noted in the register. And an event
written during the work named a change `R18b`, which does not exist; append-only means it
was corrected by a later event and not erased.

## The two seals

The seal of 22 August is kept as `events.jsonl.v1.{sig,tsr,ots,sha256}` and still verifies
against the register as it stood then. The current one — `events.jsonl.{sig,tsr,ots}` —
covers 78 events, root `61ab43258a5703e5549312878c04461c178a6b1fa4e0618c3fb9c290623f8652`, timestamped 23 August 2026 at 08:47 UTC. The
first is not obsolete: it proves the register existed in its earlier form on its own date,
which no later signature can do.

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
