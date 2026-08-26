# Colophon

### *Written over, never erased.*

**A method — and a skill for Claude — for recording, measuring and disclosing the human and AI contribution while a text is being written.**

A *colophon* is the note that has closed books since the fifteenth century, declaring how they were made: printer, typeface, paper, date. This project moves that function from the book to the text written together with a language model. The payoff comes from the palimpsest, the reused manuscript in which the earlier writing stays visible beneath the new — which is also the formal property of the register: append-only, no event overwritten, every revision added rather than substituted.

---

## Why

There are two ways to say how a text was made today, and both fail.

**Statistical detection does not survive the real case.** On "pure" documents it reaches very high accuracy in the lab, but on AI text edited by hand it falls to around 39%, and on paraphrased text to 26%. At word level, on genuinely co-written texts, it performs below chance. The difficulty curve peaks at roughly 50% AI contribution: the most common scenario is the worst one. Detectors also penalize non-native writers systematically.

**Self-declaration alone is not verifiable.** Across more than 164,000 academic papers, 70% of journals have an AI policy but only about 0.1% of papers disclose use. And the objection of principle stands: a text cannot prove its own authorship, so any voluntary statement is costless signalling.

Colophon takes the third path: capture the process while it happens, measure it on two independent axes, and publish an inspectable record instead of a label.

---

## Install

**This is a skill for Claude.** It follows the [Agent Skills](https://agentskills.io) open
standard and nothing in it is deliberately tied to one vendor — the scripts are Python
standard library only, `seal.sh` calls tools the operating system already has, and the
verifier is one HTML file that needs no assistant at all. But Claude Code and the Claude
apps are the only hosts it has been run on, so that is what the instructions below cover
and what the method has been measured through.

Anywhere else is untested rather than unsupported. **What another assistant would need is
not the file format but the ability to run code on your machine**: the case folder has to
persist for as long as you are writing, and `seal.sh` has to reach a private key that must
never leave it. An assistant that executes in a cloud sandbox can hold the conversation and
produce the annotation, and cannot seal — putting the key there would void the thing the
signature is for.

**Claude Code** — this repository is also a plugin marketplace, so one command installs the skill and a second keeps it current:

```
/plugin marketplace add fchinaglia/colophon
/plugin install colophon@colophon
```

That brings down the whole repository rather than the skill folder alone — the verifier, the worked example and the cases come with it, which for this project is the point and not the cost. `claude plugin update colophon` picks up later releases.

To take the skill folder by itself, without the plugin machinery, copy it into your personal skills directory, available across all your projects:

```bash
git clone https://github.com/fchinaglia/colophon.git
cp -r colophon/skill/colophon ~/.claude/skills/colophon
```

For a single project, use `.claude/skills/colophon/` instead. Either way Claude loads it when relevant, or you can invoke it directly with `/colophon`.

**Claude apps (web and desktop)** — go to **Customize → Skills → Add** and upload `colophon.zip` from the [latest release](../../releases). The zip has the skill folder at its root, as required.

Verify the install by asking Claude: *open the register, I am about to write an article.*

---

## Use

The rule that matters more than all the others: **the register is opened when you start writing, not when you have finished.** Applying the method to a finished text is allowed, but it produces a *reconstructed estimate*, not a measurement, and it must be declared as such.

Two modes:

| | what it costs | what it gives |
|---|---|---|
| **light** | almost nothing | the register with its hash chain, and a closing note with declared estimates |
| **full** | an annotation pass | register, span annotation, measurement on both axes, verification page, icon, cryptographic seal |

Moving from light to full loses nothing, because the register is the same.

A finished case is a folder that verifies itself:

```
cases/001-my-article/
├── events.jsonl        the register, one JSON event per line, hash-chained
├── annotation.json     which span belongs to whom, on both axes
├── versions/           every version of the text as it was saved
├── spans.json          the spans, expanded
├── kpi.json            the measurement
├── index.html          the verification page, read from inside the bundle
├── icon.svg            the quadrant, generated from kpi.json
└── record.py measure.py build_page.py build_icon.py build_note.py seal.sh
```

The scripts live **inside** the case folder, not only in the skill: a case stays reproducible even after the skill changes.

---

## What it measures

Two independent axes, because "who wrote the words" and "whose content is it" are different questions with different answers.

- **lexical contribution** — who wrote the words on the page
- **ideational contribution** — whose content those words express

The difference between the two numbers is the most useful thing the method produces. In the validation case it is sixteen points: the AI wrote far more words than it brought ideas.

Each span is attributed `U` (human), `A` (AI) or `UA` (indivisible mixed, counted as half), plus the phase it was produced in. The AI share is `(n_A + n_UA / 2) / n_total`.

### The quadrant

Two axes, each running from AI to Me: horizontally the human share of the **words**, vertically the human share of the **ideas**. The measured text is a point, and the cell it falls into gives it a name.

<p align="center"><img src="paper/figures/example_1.svg" width="200" alt="the quadrant, with a point in human written"></p>

| | author's ideas | AI's ideas |
|---|---|---|
| **author's words** | `human written` | `human edited` |
| **AI's words** | `machine polished` | `machine generated` |

Three names come from the classes of LLM-DetectAIve (Abassy et al., EMNLP 2024 System Demonstrations, arXiv:2408.04284); `human edited` replaces their fourth class, which describes a different case.

`build_icon.py` generates the icon **from the measurement file**, never by hand, so it cannot diverge from the number it declares. It warns when the point sits less than five points from a boundary: the classification rounds at 50%, and near the edge the category name alone claims more than the data supports.

### The two mandatory checks

`measure.py` runs both, and both must pass before any number is published.

1. **reconstruction** — concatenating the annotated spans must reproduce the text exactly.
2. **coverage** — every change declared in the register must appear in at least one span, or be declared in `explained`, with the reason, which the verification page then shows the reader.

`measure.py` stops with a non-zero status when either fails, so nothing downstream runs on a number that has not passed. The two cases in `cases/` predate the rule and keep their own copies of the scripts, as every case folder does: they are unaffected by it, and they are not evidence that it passes.

The second was added after an incident during validation: an annotation update failed silently, the text came out right, the reconstruction check passed, and the KPI reported a wrong value for several minutes. The risk is not manipulation. It is drift.

---

## What the method does not prove

The chain proves that an event was not altered after it was recorded and — with timestamping — that it existed at a given date.

**It does not prove the register is complete.** No voluntary system can: you can record faithfully or you can omit, and cryptography does not tell the two apart. The register is also compiled by the model about itself.

We say it first because it is the strongest criticism that can be made of a voluntary disclosure, and it is a fair one. **The value of a register like this one is not in the proof: it is in the responsibility the author takes on by publishing it, and in the fact that it can be inspected.**

Also worth stating plainly: ideational attribution is a judgement, not a measurement; nothing that happens outside the conversation is observed; and `human written` does not mean "without AI".

---

## Publishing what you wrote

**You need no account, no invite, no instance and no hosting.** A case travels as one
file:

```bash
python3 build_bundle.py        # in the case folder, after sealing
```

That writes `colophon-<case_uid>.tar` — the register, the signature, the timestamp, the
measurement, everything the closing manifest covers, and `verify.html`. A reader drops it
on the verifier **with the network off** and gets the chain, the signature, every digest
and the timestamp's imprint. Nothing has to stay online, and nobody has to be alive in ten
years for it to still check.

**Your key is not published anywhere.** `seal.sh` copies the public half into the case
as `colophon.pub` and it travels in the tar, so the signature is checked against the copy
that arrived with the evidence — offline, with no address of yours that has to still be
answering in ten years. `colophon setup` opens no network connection at all.

A key inside the package it signs is circular, and the method says so rather than
pretending otherwise. Two things answer it, in order of what they are worth:

| | |
|---|---|
| `key_fingerprint` in `case.json` | the sealed manifest covers `case.json`, so the chain itself records which key this case expected — swap the key and the fingerprint stops matching something a signature already commits to |
| **a qualified electronic signature on the PDF** | the only step that names a *person*. `render_pdf.py --embed` puts the bundle inside the document, so one signature covers the article and the evidence together, and a supervised trust service identified the signer before issuing the certificate |

The first is internal consistency, which is real and is not identity. The second is
identity, and it is the last thing to do — after sealing, after the PDF exists.

The case itself is published nowhere. There is no address to declare, no instance to
deposit it with and no field in `case.json` to hold one: an address is a promise about a
server that somebody has to keep renewing, and a dead link under a disclosure looks like
evidence from a distance while being the opposite. What the document prints instead is the
root, so two copies with two different roots are visibly two states of the same case.

---

## What is here

| | |
|---|---|
| [`skill/colophon/`](skill/colophon/) | the skill: SKILL.md, the reference documents, the scripts |
| [`skill/colophon/reference/protocol.md`](skill/colophon/reference/protocol.md) | attribution rules and the hard cases |
| [`skill/colophon/reference/disclosures.md`](skill/colophon/reference/disclosures.md) | ready-to-publish disclosure texts, with the reasons behind their wording |
| [`skill/colophon/reference/VERIFY.md`](skill/colophon/reference/VERIFY.md) | the template you publish next to a register so readers can check it |
| [`paper/colophon-method.md`](paper/colophon-method.md) · [`.pdf`](paper/colophon-method.pdf) | the method paper, 12 pages, with the evidence base. The Markdown is the source; the PDF is a rendering of it and can lag behind |
| [`verifier/`](verifier/) | one self-contained HTML page. No network, no dependencies, no server: drop a bundle on it |
| [`cli/`](cli/) | `colophon setup` — once, to make a key and check where you publish it |
| [`example/`](example/) | a small worked case you can run end to end |
| [`cases/`](cases/) | the two sealed cases. Open `verify.html`, drop the bundle beside it on it, network off. Each PDF carries both as attachments |

---

## Contributing

The method has been validated on **two cases, by one annotator, and the annotator is an interested party** — the attribution was compiled by the model that co-wrote the text. That is the honest state of it, and it is why contributions are wanted.

The most valuable thing anyone can bring is **a second case**: run the method on your own writing and publish the case folder. The next most valuable is **inter-rater validation**: annotate the same text independently and measure the agreement.

See [CONTRIBUTING.md](CONTRIBUTING.md) for how, and for the open problems the method has not solved.

---

## License

MIT — see [LICENSE](LICENSE). Use it, change it, redistribute it. A standard that cannot be reused is not a standard.

