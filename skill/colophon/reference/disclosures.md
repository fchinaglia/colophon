# Disclosures

Texts to adapt, together with the reasons they are written the way they are. The choices below are not matters of taste: they come from empirical research on what AI labels do to a reader's trust.

---

## Why two levels and not one

Three findings, all pointing the same way.

Disclosing the use of AI **reduces trust**, and the effect is mediated by perceived legitimacy: what the reader is judging is not the tool, it is whether the writer knows what they are talking about and takes responsibility for it (Schilke & Reimann, *The transparency dilemma: how AI disclosure erodes trust*, "Organizational Behavior and Human Decision Processes", 2025, DOI 10.1016/j.obhdp.2025.104405).

But the drop only shows up **with detailed disclosures**: one-line disclosures keep trust at levels comparable to no disclosure at all. And at the same time readers **want** the detail: roughly two thirds prefer the detailed version, and among those who prefer the single line, most ask for a *detail-on-demand* model (Prajod et al., *Full Disclosure, Less Trust?*, ACM FAccT 2026; 3×2×2 factorial design, 40 participants).

Hence the only architecture that loses nothing: **a short marker where timeliness matters, the detail where context matters.**

On placement, the only solid evidence concerns visibility: labels at the foot of the piece or in a side column go above 80% visibility, hover labels stop at 26% (Trusting News, *How AI disclosures in news help — and also hurt — trust with audiences*, 2024). **Never on hover.**

---

## Level 1 — the marker at the top

One line, in italics, right under the title. It says what the reader is reading and where to find the rest. It contains no numbers: if the reader meets a percentage before having read a single line of substance, they have nothing yet to judge it against, and the penalty is at its maximum.

> *Written with the assistance of a language model. The method note, with the contribution percentages, is at the bottom.*

---

## Level 2 — the note at the bottom

In italics, after a separator. It says what, how much, why, and who answers for it.

> *Method note. I wrote this article with the assistance of a language model, and every intervention was recorded as it happened. Content: X% mine, Y% the AI's. Text: Z% mine, W% the AI's. The two numbers measure different things — the first the ideas, the second the words that express them — and the gap between them is the interesting part: the AI wrote more words than it brought ideas, because it came in mostly at [phases]. The first draft is K% mine. I stand behind every statement in it.*

Four elements, all of them necessary:

- **the two percentages, each with its semantic unit spelled out.** "42%" without saying *of what* is the most common source of misunderstanding.
- **the explanation of the gap between the two numbers.** It is the information the method produces and that no other scheme provides.
- **the breakdown**, at least in outline. Without "the first draft is 87% mine", the aggregate figure reads badly.
- **taking responsibility.** It is the lever that mitigates the reputational cost, and it is also the criterion the AI Act uses in its exception for editorial review.

If there is a published verification page, the note ends with the link.

### Variant for light mode

> *Method note. I wrote this piece with the assistance of a language model. As a rough estimate, the content is about X% mine and the text about Y% mine; the AI came in mostly at [phases]. These are declared estimates, not measurements: the process was recorded, but not annotated step by step. I stand behind every statement in it.*

### Variant for retroactive application

> *Method note. This text was written with the assistance of a language model. The percentages given are a reconstruction made after the fact, not a record of the process: read them as orders of magnitude declared in good faith.*

---

## Excluding the disclosure from your own count

The blocks of the disclosure go in `excluded` inside `annotation.json`. The disclosure does not measure itself, and that has to be said.

---

## What never to write

- **"100% human", "no AI", "written without AI".** There is no shared definition of AI-free text, and with AI built into every writing tool these are indefensible claims.
- **Implicit comparisons with people who do not disclose.** It is the moralizing tone that turns the public *against* the person disclosing.
- **Claims of regulatory compliance.** For a professional post or blog the AI Act obligation almost never applies: the guidelines exclude advertising and product descriptions from "matters of public interest", and the exception for human review with editorial responsibility covers anyone who genuinely reads their text back. The correct framing, if you want to invoke the regulation at all, is **voluntary adherence**: adopting the standard of human review and editorial responsibility even where you would not be required to.
- **The effort.** "It still took me three hours" is not an argument the public weighs. What it weighs is whether the AI contribution was substitutable, who was steering, and whether AI text went straight into the finished product — substitutability, intentionality and directness (Fang, Wen & Lee, 2026, arXiv:2604.27129).
- **Numbers with decimals** in material addressed to the public. They convey a precision the construct does not have.

---

## Anticipating the strongest objection

The serious criticism of any voluntary disclosure is that it is **costless signalling**: authors declare whatever they like and no one can check it on the merits, because a text cannot prove its own authorship.

The criticism is sound, and it should be anticipated rather than absorbed. Two moves:

1. **Admit it first.** The verification page says openly that the register cannot be verified on the merits, and that its value lies in the responsibility taken on and in the fact that it can be inspected, not in proof.
2. **Build the cost outside the text** — which is what makes the only certification schemes with real defenses credible. Verifiable identity, a signed and timestamped register, a dated public policy applied to all content with no convenient exceptions, an inspectable history.

A credible voluntary disclosure is **expensive to fake**, not verifiable on the merits. Pretending otherwise destroys the very credibility it is meant to build.

---

## The sources

The empirical claims in this document come from the research survey carried out for the method; each is cited inline above, with author, year and identifier. The full survey — twelve annexes, in Italian — lives in the research repository, and marks as unverified every claim that could not be checked against a primary source.

---

## The technical line

Every disclosure note above is followed by one more line, set smaller and quieter, generated by `build_note.py` from the register:

> Register: 72 events, root 4179f3f0…3a522b33. Ed25519 signature, RFC 3161 timestamp and Bitcoin anchoring alongside the register; verification instructions in VERIFICA.md.

Without it the note asserts two numbers and gives the reader no way to check them, which is precisely the failure mode the method exists to avoid. With it, the disclosure stops being a claim and becomes a pointer.

Four rules govern it. It is generated, never typed — a hand-copied root goes stale at the next event, and a stale root looks like evidence while being none. It is generated last, after the final event and after sealing. Adding it is not recorded as an event: a new event would change the root and the line would contradict itself. And if the register is not sealed, the line says so — that sentence stays in.

---

## The shape of the block

Icon, note and technical line are three parts of one object, and they are always
arranged the same way: **the icon on the left, the note and the technical line
stacked in a column to its right**, in that order down the page.

```html
<table class="colophon">
  <tr>
    <td class="icon"><img src="icon.svg" alt="…"></td>
    <td class="body">
      <p class="note">Method note. …</p>
      <p class="technical">Register: 72 events, root 4179f3f0…3a522b33. …</p>
    </td>
  </tr>
</table>
```

```css
.colophon    { width: 100%; border-collapse: collapse; }
.colophon td { vertical-align: top; padding: 0; }
.icon        { width: 56mm; padding-right: 8mm; }
.icon img    { width: 54mm; }
.note        { font-style: italic; font-size: 9pt; line-height: 1.55;
               text-align: justify; }
.technical   { font-family: ui-monospace, monospace; font-size: 7pt;
               color: #7a7975; margin-top: 3.5mm; }
```

The reading order is deliberate. The icon answers the question in one glance; the
note says in words what the icon says as a position; the technical line says where
to go and check. A reader who stops after the first has still been told something
true, and one who reads all three has been told everything.

Three rules are not matters of taste.

**Align to the top, never centre.** The icon and the first line of the note must
start on the same line, so the eye finds them together. With vertical centring, a
note of a different length shifts the icon up or down and the block stops looking
like the same object across cases.

**Set the icon in absolute units, not a percentage.** The hundred-pixels-a-side
rule holds only if the size does not depend on the width of the container. At a
percentage, a narrow column makes the four labels illegible, which is the one
failure the icon cannot survive: an unreadable quadrant is worse than no icon,
because it looks like a claim while being none.

**Use a table, not flexbox.** This block has to render in HTML, in PDF and inside
an image. Older rendering engines — including the ones behind common HTML-to-PDF
tools — ignore `gap`, and a flex row silently collapses into overlapping text. A
table is duller and more predictable, and this block must be predictable.

### When the layout will not fit

On a narrow column, stack the three parts instead: icon, then note, then technical
line, in the same order. Do not shrink the icon below a hundred pixels a side to
keep them side by side.

When the disclosure travels as a single image — a social card, a slide — the same
order applies, and the note may be shortened, but **the technical line is never
dropped**: it is the part that turns the numbers into something a reader can check.
If there is no room for it, there is no room for the numbers either.

---

*MIT License — Copyright (c) 2026 Fabio Chinaglia. See the LICENSE file.*
