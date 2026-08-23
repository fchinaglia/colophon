---
name: colophon
description: "Record, measure and disclose the human and AI contribution while writing. Use when the user says colophon, open the register, track this article, or measure the AI contribution."
---

# Colophon

*Written over, never erased.*

Records the writing process **as it happens**, measures the human and AI contribution to it along two independent axes, and produces a disclosure that third parties can verify.

## The rule that comes before all the others

**The register is opened when you start writing, not when you have finished.**

If the user asks you to apply the method to a text that is already written, you can — but the result is a **reconstructed estimate, made from memory**, not a measurement, and it must be declared as such on the verification page and in the closing note. Never pass it off as the other thing.

## Two modes

Ask the user which one, if it is not obvious from the context. When in doubt: pieces under 800 words → light; above that → full.

**Light mode.** Event register with a hash chain, no span-level annotation, closing note with coarse-grained estimated percentages declared as estimates. Almost no friction.

**Full mode.** The whole cycle: register, span-by-span annotation, measurement along the two axes, verification page, three-level disclosure, cryptographic seal.

You can move from light to full at any moment without losing anything: the register is the same.

## The cycle

### 1. Opening

Create `cases/NNN-<slug>/` with `versions/` inside it, and copy **all** of the skill's scripts in there: `record.py`, `measure.py`, `build_page.py`, `build_icon.py`, `build_note.py`, `seal.sh`. A case folder has to remain verifiable on its own even if the skill changes — and there is exactly one copy per folder: two copies of `measure.py` in the same case have already produced two different numbers. Then record two events: the opening of the case (with the mode, the capture method and the known limits) and the user's brief (subject, format, where it will be published, the process they say they intend to follow).

Create `case.json` too, from `case_example.json`: title, author, date, whether the register is reconstructed, and the two addresses — `verification_url`, where the verification page will be readable, and `register_url`, the folder with the register and the files. `build_note.py` puts the first in the technical line and falls back to the second; `build_page.py` uses the second to link the files from the page. Without either, the line tells the reader what to check and not where to find it.

An address you cannot keep is worse than none: the line is generated at render time, so a PDF freezes it forever. Do not move a case folder once it is published. If you do not know the address yet, add it before publishing — the line will pick it up at the next render.

The page has to be **served as a page**. A raw `.html` on a code host is delivered as plain text and the reader sees the markup: publish it where HTML renders, GitHub Pages or your own site.

**No underscore in the published address.** URL detectors — in mail clients, chat apps, PDF viewers — cut a link at the first underscore, so `…/cases/002/pagina_di_verifica.html` arrives at the reader as `…/cases/002/pagina`, which is a 404. Publish the page as `index.html` so the address ends at the folder, or put an `index.html` next to it that redirects. The file name inside the case can stay whatever the manifest already covers; it is the *address* that has to survive being clicked.

Among the known limits, always declare at least these: that capture happens through the conversation and not through an instrumented editor; that work done outside the conversation is not observed; that the user knows they are being observed and that this may change how they write.

```bash
python3 record.py '{"type":"case_open","actor":"system","phase":"—","payload":{...}}'
python3 record.py --verify
```

### 2. While writing

Record one event for every substantial exchange. Do not record housekeeping exchanges. The types in use: `brief`, `ai_proposal`, `human_contribution`, `editorial_decision`, `constraint`, `version`, `elicitation`, `register_note`, `status`.

Save a version in `versions/` every time the text changes substantially, and record the `version` event with the word count and the SHA-256.

**Watch out for lexical carry-over.** If a phrasing you produced — even in a comment, not only in a proposed edit — reappears in the user's text, **record it**. It is the contamination channel no tool catches on its own and only explicit vigilance picks up. The same goes for ideas: if the user adopts an angle of yours from the brainstorming, that span has AI ideational origin even if the words are theirs.

Mark with `"meta": true` the events that concern the design of the method and not the content: they are excluded from the denominator.

### 3. Revision

Print the text with **numbered blocks** (the index of the paragraph in the file, blank line as separator) so that the user can refer to `[12]`. The numbers must match those in the annotation.

Propose edits **marked one by one** with an identifier (`M01`, `M02`…), plus a closing index with the type, what changes and why. The user accepts or rejects by number. Every decision is an `editorial_decision` event with the outcome and the updated attribution.

**Purely formal** corrections — typos, agreement, double spaces, consistency of quotation marks and capitalization — are applied without asking but are **always listed**. Anything that touches meaning is proposed, not applied.

Do not rewrite the user's voice. Anglicisms, a colloquial register, personal lexical choices are theirs and are to be left alone, barring an actual error.

### 4. Closing

Annotate, measure, generate, seal. See reference/protocol.md for the attribution rules and reference/disclosures.md for the texts. The note is followed by a technical line — the number of events and the root — generated by build_note.py, never typed: the rules are in reference/disclosures.md.

```bash
python3 measure.py          # integrity check + computes the two axes
python3 build_page.py       # HTML verification page
python3 build_icon.py       # quadrant icon, from kpi.json
bash seal.sh events.jsonl   # Ed25519 signature + timestamp + anchoring
python3 build_note.py       # the technical line of the note
```

## The annotation

It lives in `annotation.json`, never inside the script. Every block receives **two independent attributions**:

- `lex` — who wrote **the words you read** in the final text
- `idea` — where **the content** those words express comes from

Values: `U` human, `A` AI, `UA` inseparably mixed. Plus the `phase`: `research`, `outline`, `first_draft`, `content_revision`, `copy_revision`, `titling`.

A block is split into several spans when the attribution changes inside it. The unit is the **contiguous homogeneous span**, never the token.

The complete rules, with the edge cases, are in `reference/protocol.md`. **Read them before annotating**: the hard cases are the majority.

## The two mandatory checks

`measure.py` runs both of them and they must **always** pass before you publish any number:

1. **Reconstruction check** — concatenating the spans must reproduce the text exactly, excluding the declared blocks.
2. **Coverage check** — every edit declared in the register must appear in at least one span, or be declared in `explained`.

The first check on its own is not enough: the text can be right while the annotation has fallen behind. It has already happened.

`measure.py` exits non-zero when either fails, so the pipeline stops before a number is published. An edit with no span is often legitimate — one a later edit replaced, or a diffuse pass the protocol tells you to record as an event without touching the attributions — so the check does not forbid it. It requires that you name it:

```json
"explained": {"R12": "superseded by R19", "R25": "diffuse, attributions unchanged"}
```

in `annotation.json`, next to the annotation it qualifies. Write the reason, not a placeholder: it is published on the verification page beside the edit it refers to, and a reader will judge the measurement by it. An exception that no longer matches an unmatched edit also stops the run — a stale one hides the next real gap.

## How the numbers are reported

Two percentages, never one. The difference between the two is the most useful piece of information the method produces.

AI share = `A + UA/2`, and it has to be said that mixed is counted as half.

**Always report the breakdown by phase as well.** An aggregate figure of 47% reads as "half of it was written by the machine"; knowing that the first draft is 86% human and that the AI worked on the revision tells the true story. Without the breakdown the number is misleading in both directions. (The values are those of the validation case, not a target to hit.)

In material addressed to the public use whole numbers. The precise value stays in the record.

## When the measurement stops

`measure.py` exiting non-zero is a normal moment in the cycle, not an accident, and the first thing to do is to say so to the user in one sentence: **the register is intact, nothing they wrote or you recorded is lost, and this is the closing step being repeated — not the work.** They are watching a red block of text about spans and declarations, in the vocabulary of a file they have never opened.

Then fix it, in this order:

1. **Never touch `events.jsonl`.** The register is the evidence. If an edit is in it and not in the annotation, the annotation is what is behind.
2. **Look for the span first.** Most stops are an edit whose trace is in the text and whose event was never attached to the span that carries it. Attach it.
3. **If the trace is genuinely not there, declare it** in `explained`, with the reason in a sentence a reader will see: it is published on the verification page next to the change it explains. "superseded by R19" is a reason; "n/a" is not.
4. **Ask the user only when the answer is a judgement about their text** — did this rewrite survive into the final version, or did the later one replace it? That is a question they can answer in a line. Never ask them to edit the annotation.
5. **Never remove the check, and never write the number by hand.** A measurement that skipped its own check is what the method exists to make impossible.

## The icon

`build_icon.py` reads `kpi.json` and produces `icon.svg`: a quadrant with two axes that both run from AI to Me — horizontally the human share of the **words**, vertically the human share of the **ideas** — and the text as a point. The cell the point falls in gives it its name.

| | author's ideas | AI's ideas |
|---|---|---|
| **author's words** | `human written` | `human edited` |
| **AI's words** | `machine polished` | `machine generated` |

Three of the names come from the classes of LLM-DetectAIve (EMNLP 2024); `human edited` replaces their fourth class, which describes a different case.

**The labels stay in English, whatever language the text is in.** The four names are the classes of a published taxonomy: translated, they stop pointing at it, and two people reading two icons in two languages would no longer be reading the same scale. An Italian article with an Italian note and an English quadrant is the intended result, not an oversight — the icon is a mark, and marks are not translated. The script has no language option for this reason.

**Never generate it by hand and never touch it up.** It comes from the measurement file, so it cannot diverge from the declared number: that is what makes it useful.

**Publish it with the point, not with the name of the category alone.** The classification rounds at 50% on both axes. The script warns when the point is less than five points from an edge: in that case the name on its own is a stronger claim than the data.

Below a hundred pixels a side the four labels become illegible. It is a document mark, not a favicon.

It is not a judgment of quality, and `human written` does not mean "no AI": in the validation case that cell contains a text whose words are 47% the AI's.

---


## What the method does not prove — always to be declared

- The hash chain proves that an event **has not been altered after being recorded**. It does not prove that the register is **complete**: no voluntary system can.
- The register is compiled by the AI about itself. It is the structural weak point and it must be written down, not hidden.
- Ideational attribution is a **judgment**, not a measurement. In the literature, agreement between independent annotators on graded judgments of the intensity of AI editing stops at a Krippendorff's α of 0.66–0.67, below the conventional threshold of 0.80 (EditLens, arXiv:2510.03154). Discrete attribution — who wrote this piece — holds up much better: 83–89% agreement (WikiWho).
- What happens outside the conversation is not observed.
- If every proposal is accepted, declare it: from a single case there is no way to tell whether they were well calibrated or whether deference was at work.

## Mistakes not to make

- Switching the method on at the end of the job and calling it a measurement.
- Publishing a number without saying what it is a percentage of.
- Using absolute formulations: "100% human", "no AI". They are indefensible.
- Building the disclosure as an implicit comparison with those who do not disclose. A moralizing tone is what sets the public against the person who discloses.
- Re-annotating dozens of spans as mixed because of a lexical intervention that changes two words in each: it inflates the AI share. Record it as an event and declare the choice.
- Leaving a silent gap. If something is not tracked, **the register must say that it was not tracked**.

---

*MIT License — Copyright (c) 2026 Fabio Chinaglia. See the LICENSE file.*
