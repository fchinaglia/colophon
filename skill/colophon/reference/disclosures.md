# Disclosures

Texts to adapt, together with the reasons they are written the way they are. The choices below are not matters of taste: they come from empirical research on what AI labels do to a reader's trust.

---

## Why three levels and not one

Three findings, all pointing the same way.

Disclosing the use of AI **reduces trust**, and the effect is mediated by perceived legitimacy: what the reader is judging is not the tool, it is whether the writer knows what they are talking about and takes responsibility for it (Schilke & Reimann, *The transparency dilemma: how AI disclosure erodes trust*, "Organizational Behavior and Human Decision Processes", 2025, DOI 10.1016/j.obhdp.2025.104405).

But the drop only shows up **with detailed disclosures**: one-line disclosures keep trust at levels comparable to no disclosure at all. And at the same time readers **want** the detail: roughly two thirds prefer the detailed version, and among those who prefer the single line, most ask for a *detail-on-demand* model (Prajod et al., *Full Disclosure, Less Trust?*, ACM FAccT 2026; 3×2×2 factorial design, 40 participants).

Hence the only architecture that loses nothing: **a short marker where timeliness matters, the detail where context matters, and the record itself for whoever wants to check.**

The levels count **readers, not texts**: how far a given reader chooses to go, from the one who scrolls past to the one who verifies the signature. Two of the three are things you write; the third is the case folder, which already exists.

| level | who it is for | what it is |
|---|---|---|
| **1 — marker** | the reader skimming past | one line under the title, no numbers |
| **2 — note** | the reader who wants to understand | the icon, the note, the technical line |
| **3 — record** | whoever wants to verify | the register, the annotation, the verification page |

Level 2 has three **parts**, and they are parts, never levels: the count of levels is a count of readers. How the three sit on the page is in *The shape of the block*, below.

On placement, the only solid evidence concerns visibility: labels at the foot of the piece or in a side column go above 80% visibility, hover labels stop at 26% (Trusting News, *How AI disclosures in news help — and also hurt — trust with audiences*, 2024). **Never on hover.**

---

## Level 1 — the marker at the top

One line, in italics, right under the title. It says what the reader is reading and where to find the rest. It contains no numbers: if the reader meets a percentage before having read a single line of substance, they have nothing yet to judge it against, and the penalty is at its maximum.

> *Written with the assistance of a language model. The method note, with the contribution percentages, is at the bottom.*

---

## Level 2 — the block at the bottom

Three parts: the icon, the note, the technical line. **`build_block.py` produces all three as one object** — it takes the category and the boundary margin from `build_icon.py` and the technical line from `build_note.py`, so the block cannot disagree with the icon beside it or with the page it links to. What follows is what that script implements and why; it is not a form to fill in by hand. That was tried, and case 001 shipped a full-width, body-size, stacked version of the block specified below.

**The note is short by default.** Five lines, not a paragraph — this is the form to use everywhere, including in a PDF:

> human written · 337 words · 18 spans
> human words **54%** · human ideas **100%**
> The model wrote the words, the ideas are mine.
> the point is 4 points from the boundary: read the point, not the label alone
> I stand behind every statement in it.

In that order, and the order is the argument: **what** this is, **how much**, **what the gap means**, **how firm the classification is**, **who answers for it**. A reader who stops after the first line has been told something true; one who reads all five has been told everything the page can tell them, and the technical line below says where the rest is.

Two lines are conditional. The third drops when the two percentages are close — with nothing to explain, it is filler. The fourth appears only when `build_icon.py` reports the point within five points of a boundary; it is the script's warning, put where the reader can act on it.

**One treatment for all five.** Same face, same size, same colour, only the percentages in bold. No line is coloured to stand out: a block that raises its voice at the foot of an article puts the reader on the defensive at precisely the moment the method is trying to do the opposite. What separates the lines is what they say.

This is the detail-on-demand shape the research asks for: the numbers where the reader is, everything else one click away, at an address that leads to a page written for them.

### The full note, when there is room

The paragraph form still exists, and it is for a page that has space to explain itself — a site, a report, a document nobody is scrolling past:

> *I wrote this article with the assistance of a language model, and every intervention was recorded as it happened. Content: X% mine, Y% the AI's. Text: Z% mine, W% the AI's. The two numbers measure different things — the first the ideas, the second the words that express them — and the gap between them is the interesting part: the AI wrote more words than it brought ideas, because it came in mostly at [phases]. In the first draft the ideas are K% mine and the words J%. I stand behind every statement in it.*

It carries one thing the short form drops — **the breakdown by phase**, "in the first draft the ideas are 68% mine and the words none of them" — which is why it is worth keeping where a reader will actually read a paragraph. Everything else it says, the short form says in fewer words.

**A per-phase figure names its axis too, and it is the sentence where forgetting costs most.** The two aggregates are far apart by design; within a single phase they can be at opposite ends, because a phase is precisely where one of the two happens. The figures quoted above are case 001's first draft: entirely the model's words, two thirds the author's ideas. Written as one number it becomes "the first draft is 0% mine", which is the opposite of what happened, and the reader has no way to tell. `measure.py` prints both columns and `kpi.json` carries them as `ai_lexical` and `ai_ideational`; take K and J from there and say which is which.

Both forms carry the same four things, and none of them is optional: the two percentages **each with its semantic unit** ("42%" without saying *of what* is the commonest misunderstanding), **the gap explained**, **the breakdown** — by phase and on both axes, or in the short form by pointing at the page — and **taking responsibility**, the lever that mitigates the reputational cost, and the criterion the AI Act uses in its exception for editorial review.

### The essential form

For a square card, a slide, a newsletter footer — anywhere the five lines will not fit. Drop the third and the fifth, keep the technical line:

> human written · 337 words
> human words **54%** · human ideas **100%**
> the point is 4 points from the boundary: read the point, not the label alone

It is the weakest of the three, because responsibility is the thing that survives only if it is said. Use it when the alternative is not disclosing at all.

### Variant for light mode

> *I wrote this piece with the assistance of a language model. As a rough estimate, the content is about X% mine and the text about Y% mine; the AI came in mostly at [phases]. These are declared estimates, not measurements: the process was recorded, but not annotated step by step. I stand behind every statement in it.*

### Variant for retroactive application

> *This text was written with the assistance of a language model. The percentages given are a reconstruction made after the fact, not a record of the process: read them as orders of magnitude declared in good faith.*

### The same texts in Italian

The wording below is the one published with case 002, not a translation made for this document. Use `build_note.py --lang it` for the technical line that follows the note. The quadrant stays in English in any language: see *The icon* in SKILL.md for why.

Marker, level 1:

> *Scritto con l'assistenza di un modello linguistico e tracciato con il metodo Colophon. La nota sul metodo, con le percentuali di contributo, è in fondo.*

Note, level 2, the short form — the default:

> human written · 337 parole · 18 span
> parole umane **54%** · idee umane **100%**
> Il modello ha scritto le parole, le idee sono mie.
> il punto è a 4 punti dal confine: guardate il punto, non la sola etichetta
> Di ogni affermazione rispondo io.

The first line is the category as `build_icon.py` names it, in English: the four names are a taxonomy and are not translated. Everything else is in the language of the piece.

Note, level 2, the full form:

> *Ho scritto questo articolo con l'assistenza di un modello linguistico, e ogni intervento è stato registrato mentre accadeva con il metodo Colophon. Contenuto: X% mio, Y% dell'AI. Testo: Z% mio, W% dell'AI. I due numeri misurano cose diverse — il primo le idee, il secondo le parole che le esprimono — e la differenza è la parte interessante: l'AI ha scritto più parole di quante idee abbia portato, perché è intervenuta soprattutto in [fasi]. Nella prima stesura le idee sono mie al K% e le parole al J%. Il quadrante qui accanto colloca il testo sui due assi. Di ogni affermazione rispondo io.*

Light mode:

> *Ho scritto questo pezzo con l'assistenza di un modello linguistico. A stima, il contenuto è mio per circa X% e il testo per circa Y%; l'AI è intervenuta soprattutto in [fasi]. Sono stime dichiarate, non misure: il processo è stato registrato, ma non annotato passo per passo. Di ogni affermazione rispondo io.*

Retroactive application:

> *Questo testo è stato scritto con l'assistenza di un modello linguistico. Le percentuali indicate sono una ricostruzione fatta a posteriori, non la registrazione del processo: leggetele come ordini di grandezza dichiarati in buona fede.*

Two things that are not translation choices. **The phase names stay as the protocol writes them** — `first_draft`, `content_revision` — inside the files, and become plain Italian words only in the sentence a reader sees. And the note published with case 002 also carried the address of the register in prose; that sentence is gone here, because the technical line now does that work, and saying it twice weakens both.

---

## Level 3 — the record

The case folder itself: the register with its chain, the annotation, the versions, the verification page, and the seal if there is one. It is the only level you do not write — running the method produces it — and the only one that can be checked instead of believed.

Publishing it is what separates this from a declaration. `reference/VERIFY.md` is the template to publish next to it, so that a reader who gets this far is told exactly which commands to run and what each of them proves. And it is reached from level 2 by one route only, the technical line: a record nobody is pointed to is a record nobody reads.

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
- **"PDF/A-3", or any archival-format claim**, on a rendering produced by headless Chrome. It has no output intent, no conformant XMP and no guaranteed embedded fonts. An unverified compliance claim is the previous entry again, in the one artefact whose whole job is to be checkable.
- **Anything that lets a signature over the document stand in for the measurement.** A qualified signature says this file has not changed since it was signed, and a reader who sees a legal name in a signature panel will hear *and these numbers are right about this text*. They are two claims. The attestation says so itself, `VERIFY.md` says so, and the disclosure must not undo them by implying otherwise.
- **An address you are not sure will answer.** A dead link under a disclosure looks like evidence from a distance and is the opposite of it up close. If you are not certain, use the attached form or the held form below — both are true, and a true weaker claim beats a false stronger one.

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

## The technical line — the door from level 2 to level 3

Every disclosure note above is followed by one more line, set smaller and quieter, generated by `build_note.py` from the register. Three short lines by default, in a monospace face:

> signed and inspectable register
> fchinaglia.github.io/colophon/cases/002
> root ae68ae8dc078c46c6ac85b349ae08d2d104fea77767dce18a7b38a5388312793

`--form full` gives the sentence it replaced, naming each seal and printing the root whole:

> Register: 81 events, root ae68ae8dc078c46c6ac85b349ae08d2d104fea77767dce18a7b38a5388312793. Ed25519 signature, RFC 3161 timestamp and Bitcoin anchoring alongside the register. Verification page, with the register alongside it: fchinaglia.github.io/colophon/cases/002.

Use it where nobody will follow a link and the line has to stand alone — a printed sheet, an archive copy. Under an article, the address does that work, and enumerating three seals in prose is words a reader skips.

Without it the note asserts two numbers and gives the reader no way to check them, which is precisely the failure mode the method exists to avoid. With it, the disclosure stops being a claim and becomes a pointer.

This is why level 3 is a level and not an appendix: the record only counts as disclosure if a reader can get to it from the page they are on. The technical line is that route, and it is the reason dropping it is not a matter of layout.

Four rules govern it. It is generated, never typed — a hand-copied root goes stale at the next event, and a stale root looks like evidence while being none. It is generated last, after the final event and after sealing. Adding it is not recorded as an event: a new event would change the root and the line would contradict itself. And if the register is not sealed, the line says so — that sentence stays in.

**The root goes in whole.** An abbreviation can be recognised but not compared, and comparing is the reader's job: they recompute the chain and hold their value against yours. Both forms print it whole by default. `--short-root` abbreviates it to `ae68ae8d…88312793` for a layout that genuinely cannot hold sixty-four characters — a social card, a slide — and it is a concession to the column, never the default.

**And it carries an address.** A line ending in *verification instructions in VERIFY.md* helps a reader standing in the case folder — the one reader who did not need help. Everyone else is on a post, a PDF, a printed page, and for them a filename is not a place. `case.json` holds two addresses and the line prints one of them:

- `verification_url` — the published verification page. Preferred, because it is the artefact written for a reader, and the raw files are one click further on: the page links them.
- `register_url` — the case folder. Used when there is no page, and used by the page itself for that link.

`build_note.py` warns on stderr when it finds neither, because a line with no address is the failure this line exists to remove, wearing the costume of the fix.

Three things follow, and none is a detail.

**Serve the page as a page.** A raw `.html` on a code host arrives as plain text and the reader is shown the markup, which is worse than sending them nowhere.

**Give it an address with no underscore in it.** URL detectors cut a link at the first underscore: an address ending `pagina_di_verifica.html` is delivered to the reader as `…/pagina`, and clicking it gives a 404 while the printed line reads correctly. It is the worst shape a failure can take here — the text says one thing, the click does another. Publish the page as `index.html`, or put a redirect there, so the address ends at the folder.

**The address is a promise.** The line is generated at render time, so a PDF or a sheet of paper freezes what it said that day and will never update. Do not move a published case, do not rename it. A dead link under a disclosure looks like evidence from a distance and is the opposite of it.

---

## The shape of the block

Icon, note and technical line are the three parts of level 2 — parts of one object, not levels of their own, and they are always
arranged the same way: **the icon on the left, the note and the technical line
stacked in a column to its right**, in that order down the page.

### The three routes, and the line that says which one

The middle line of the technical block is the route to the record, and there are three.
The first line states the seal and qualifies it; only the root is in all three.

```
signed register                              signed register, attached to this file
example.com/cases/002                        verify offline: drop colophon-<uid>.tar on verify.html
root ae68ae8d…8312793                        root ae68ae8d…8312793

registro firmato                             registro firmato, allegato a questo file
example.com/cases/002                        verifica offline: trascina colophon-<uid>.tar su verify.html
radice ae68ae8d…8312793                      radice ae68ae8d…8312793
```

And when there is neither — legitimate, and said plainly rather than implied away:

```
signed register, not published               registro firmato, non pubblicato
root ae68ae8d…8312793                        radice ae68ae8d…8312793
```

`build_note.py --attached` picks the middle one; without it the line uses the address in
`case.json`, and with no address it uses the third. The earlier wording, *signed and
inspectable register*, said two things and checked one: a register with no route is not
inspectable by the reader holding the document, and the line printed the claim anyway.

**Two things the attached form must carry, or it is worse than an address.** Say the
attachment is there — most PDF viewers do not announce one, and Chrome's and Preview's do
not at all, so a route nobody is told about is not a route. And treat what travels as a
snapshot: a bundle in a reader's hands verifies perfectly and cannot announce that the
case was reopened afterwards. The root printed in the document is what makes that visible,
which is why it is in all three forms.

**The tier is the container, not the author.** A PDF can carry the attachment; a web page
can carry an address, and beats an attachment on citability and on saying *this was
superseded*; a post carries neither and must point at something that does. The marker, the
note and the root travel in every container. Only the route changes.

`python3 build_block.py` emits exactly this, styled. `--form svg` emits the same block as
one image, for a post or a slide that takes neither an HTML fragment nor an image and a
caption that stay together; `--inline-icon` inlines the quadrant, for a document that
travels without the folder that holds `icon.svg`. The markup below is what it writes.

```html
<table class="colophon">
  <tr>
    <td class="icon"><img src="icon.svg" alt="…"></td>
    <td class="body">
      <p class="line">human written · 3,126 words · 75 spans</p>
      <p class="line">human words <b>53%</b> · human ideas <b>69%</b></p>
      <p class="line">The model wrote more words than it brought ideas.</p>
      <p class="line">I stand behind every statement in it.</p>
      <p class="technical">signed and inspectable register<br>
        <a href="…">example.com/cases/002</a><br>root ae68ae8d…8312793</p>
    </td>
  </tr>
</table>
```

```css
.colophon    { width: 100%; border-collapse: collapse; }
.colophon td { vertical-align: top; padding: 0; }
.icon        { width: 56mm; padding-right: 8mm; }
.icon img    { width: 54mm; }
.line        { font-size: 9pt; line-height: 1.5; margin: 0 0 1.2mm; }
.line b      { font-weight: 700; }
.technical   { font-family: ui-monospace, monospace; font-size: 7pt;
               color: #7a7975; margin-top: 3.5mm; overflow-wrap: anywhere; }
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

**Let the root break.** `overflow-wrap: anywhere` on the technical line: the root is a sixty-four-character word with nowhere to hyphenate, and without it a narrow column pushes it straight out of the block. It fits on one line in a column of about sixty millimetres, which is why the event count is not printed beside it — the page at the address above carries that, and the room is better spent on the hash a reader compares.

**One treatment for the note, a quieter one for the technical line.** Every line of the note shares a face, a size and a colour, with only the percentages in bold: nothing is coloured to stand out, including the warning about the boundary. The technical line is smaller and grey, in a monospace face, because it is read character by character and not as prose. That is the only distinction the block makes, and it is enough.

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
