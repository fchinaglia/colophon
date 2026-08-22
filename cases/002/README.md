# Case 002 — *Frammentazione dei dati* (Italian)

The first real application of the Colophon method: a 3,126-word professional article
in Italian, written in session over three days with the register open from the first
line, then measured, sealed and published.

| | |
|---|---|
| Title | *Frammentazione dei dati: usare l'AI per affittare il debito tecnologico o estinguerlo* |
| Author | Fabio Chinaglia |
| Written | 19–22 August 2026 |
| Language | Italian (an English translation is included) |
| Register | 81 events, root `ae68ae8dc078c46c6ac85b349ae08d2d104fea77767dce18a7b38a5388312793` |
| **AI lexical share** | **47.1%** |
| **AI ideational share** | **30.6%** |
| Reconstructed after the fact? | No. Recorded live. |

The sixteen-point gap between the two axes is the point of the case: the model wrote
far more words than it brought ideas. Broken down by phase, the first draft is 86%
human and the AI worked mostly in revision, research and titling — which a single
blended number would have hidden in both directions.

| phase | words | AI share |
|---|---|---|
| research | 141 | 100% |
| outline | 174 | 65% |
| first draft | 1,828 | 14% |
| content revision | 621 | 98% |
| copy revision | 349 | 100% |
| titling | 13 | 50% |

---

## ⚠️ This case uses the Italian schema

**The scripts here are not the ones in `skill/colophon/`, and the two are not
interchangeable.** This case was produced before the method was translated, so its
file names, JSON keys and phase values are in Italian:

| here | in the skill |
|---|---|
| `eventi.jsonl` | `events.jsonl` |
| `annotazione.json` | `annotation.json` |
| `misura_span.json` / `misura_kpi.json` | `spans.json` / `kpi.json` |
| `registra.py --verifica` / `--radice` | `record.py --verify` / `--root` |
| `misura.py` | `measure.py` |
| `genera_pagina.py` / `genera_icona.py` | `build_page.py` / `build_icon.py` |
| `sigilla.sh` | `seal.sh` |
| `tipo`, `attore`, `fase`, `nota` | `type`, `actor`, `phase`, `note` |
| `prima_stesura`, `revisione_forma`, … | `first_draft`, `copy_revision`, … |

Run the scripts **that are in this folder**. Pointing `measure.py` at
`annotazione.json` will fail, and rightly so.

This is deliberate, and it is the reason a case folder carries its own copy of every
script it needs: a case has to stay reproducible after the tools move on. The case was
not migrated, because migrating it would have meant rewriting artefacts that are
covered by a signature.

---

## Verify it yourself

You do not have to take any of the numbers on trust. Full instructions are in
[`VERIFY.md`](VERIFY.md); in short:

```bash
python3 registra.py --verifica     # the chain is intact
python3 misura.py                  # reconstruction and coverage, then the two axes
```

The signature is detached, in `eventi.jsonl.sig`, made with the Ed25519 key published
at [`cases/001/colophon.pub`](../001/colophon.pub) — fingerprint
`SHA256:0woBfwGMoKA6zsd9c0701YhBa+0aqIAI03JzaRV7raQ`. The register is timestamped
(RFC 3161, `.tsr`) and anchored to Bitcoin (`.ots`).

The signature covers `eventi.jsonl` only. The link to the published text is the last
event, which carries the SHA-256 of the final article, the annotation and the
measurement — so hashing those files and finding them inside the signed register
closes the chain.

---

## What is in here

**To verify** — `eventi.jsonl`, `eventi.jsonl.{sig,tsr,ots,sha256}`, `annotazione.json`,
`versioni/v04_articolo_finale.md`, `registra.py`, `misura.py`, `caso.json`, `VERIFY.md`

**To inspect without recomputing** — `misura_span.json`, `misura_kpi.json`,
`pagina_di_verifica.html`, `icona.svg`, and the scripts that regenerate them

**The history** — `versioni/v01`–`v03`, each with its SHA-256 recorded in the register,
plus the English translation `v04_article_en.md`

**The published artefacts** — the PDFs, the illustrated source, `immagini/`, and the
render scripts

---

## What this case does not prove

The chain proves that no event was altered after being recorded, and the timestamp
proves the register existed on that date. **Neither proves the register is complete.**
No voluntary system can: an author can record faithfully or omit, and cryptography does
not tell the two apart. This register was moreover compiled by the model about its own
contribution.

Two limits specific to this case. All fourteen changes proposed in the first revision
cycle were accepted, and from a single case it is not possible to tell whether they
were well calibrated or whether deference was at work. And the author knew he was being
observed, which is not a neutral condition.

The percentages refer to the **Italian** text, the only one the measurement was taken
on. The English version is a translation produced by the model: on the lexical axis it
is almost entirely the model's work, and 47.1% does not describe it.

---

*MIT License — Copyright (c) 2026 Fabio Chinaglia. See the LICENSE file at the root.*
