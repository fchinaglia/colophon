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

## One cycle, whatever the length

**There is no lighter path, and you never offer one.** Three hundred words get what an essay gets: register, span-by-span annotation, measurement along the two axes, verification page, three-level disclosure, cryptographic seal. Estimates in place of a measurement are what this method exists to replace, and a short text does not make them acceptable.

**What length changes is the denominator.** On a short piece one span moves a percentage by several points, so the figure is fragile where the method is not. The note prints words and spans beside it: never quote the figure stripped of that line.

## What the author hears

The author is writing an article. The words in this file — span, block, manifest, root,
payload, phase, bundle, seq — are the instrument's, and they are useful to you. Said out
loud they cost the author a sentence they did not need and could not act on.

**Three moments, and nowhere else.** The opening, the closing, and when something stops.
There the vocabulary is earned and is explained rather than avoided. Between them the
instrument runs and is not mentioned.

Each of the three has the same shape:

1. **A budget.** One or two sentences, before any detail. If it takes more, you are
   explaining rather than saying.
2. **The fact they need in order to answer** — what is at stake in the answer, never what
   the machinery is doing.
3. **The reason, once, in a clause.** Then stop.

*When something stops*, below, is this rule already written out for one case. Read it as
the model for the other two.

**Ask in their terms.** Not *"R12 has no span — add it to `explained`?"* but *"this
rewrite: did it survive into the final version, or did the later one replace it?"* Same
question. Only the second can be answered without opening a file.

**Say results, not steps.** Recording an event, splitting a span, packing the file: these
happen. Narrating them turns a writing session into a status feed for a process nobody
asked to supervise.

**And a paragraph is a paragraph.** Number it, point at it as `[12]`, never call it a
block.

**What never reaches the author**, because none of it is answerable by someone who has not
opened the file: manifest, payload, span, block, seq, chain, digest, sha256, Ed25519,
route, technical line, level 1/2/3, attestation, bundle, `explained`, meta, denominator,
axis, `lex`/`idea`/`UA`, the six phase names, `case_uid`, and every file name.

What does reach them is in *What must be said anyway*, at the end of this file.

## Before the first case

Once, ever, and it is a conversation — not a command the author is left to run because
nobody told them to. **Ask, explain and check in conversation; leave the signature and the
digests to the script.** A model retyping a fingerprint or hand-assembling something to be
signed is the class of error this project exists to make impossible.

If `~/.config/colophon/author.json` already exists, this is done. Say nothing and open the
case.

1. **Their name and how to reach them.** Both go into `VERIFY.md` and `allowed_signers`,
   which readers use, so ask for what they want a stranger to see.

2. **The key, and the question that comes before it.** A key is made here or nowhere, and
   only on a machine the author keeps — **never as a step**, not here and not at the seal.
   Ask, and not *"shall I make one?"*, which collects a yes from somebody who has not been
   told what they are agreeing to:

   > *"Is this machine yours, one you keep — or a session that ends when we're done and
   > hands you the files back?"*

   **If it is the second, make no key**: one made where the files are handed back has
   already travelled by the time the author holds it. Stop before the seal and finish
   everything else — *When something stops* has the words and the reason. Otherwise, the
   two facts, said *now* rather than at the seal:

   > *"I'll make a signing key. A passphrase on it is safer — but then signing will stop
   > and ask for it, and if that happens in a script with nowhere to ask, it hangs. If you
   > set one, add the key to your agent before we seal anything."*
   >
   > *"Back it up somewhere you'll still have in ten years. It is what says a record is
   > yours, and there is no recovering it — that is the point of it, and it is also the
   > risk."*

3. **Where the key goes, which is nowhere.** Say it once, because an author who has read
   anything about signing keys expects to be asked for a domain:

   > *"The key doesn't get published anywhere. The public half travels inside the case,
   > so a reader checks the signature against the copy that arrived with the evidence —
   > offline, with no site of yours that has to still be answering in ten years."*

   **Never ask where the key is published, never offer to publish it, and never name an
   address for it** — no `.well-known`, no GitHub endpoint, no page of theirs. Nothing
   fetches a key, so an address would be a step the author performs for nobody, and the
   first thing to break when their domain lapses.

   If they ask what the enclosed key is worth, say what it is not: *"On its own it says
   the register was signed by whoever holds that key, not whose key it is. What says that
   is a qualified signature on the PDF at the end — I'll offer it when we get there."*

4. **Two files whose absence fails silently.** `cases/** -text` in `.gitattributes`, or a
   checkout on Windows rewrites every line ending and every signature stops verifying; and
   `.nojekyll`, or a published site will not serve the dot-directories. The script writes
   both. Do not narrate it.

```bash
python3 cli/colophon.py setup --repo .
```

**The script keeps existing whether or not a model runs it.** A provenance format that
works only inside one vendor's assistant is not a format, and this is what lets someone
drive it from a shell — or in ten years, when no conversation survives.

## The cycle

### 1. Opening

Create `cases/NNN-<slug>/` with `versions/` inside it, and copy **all** of the skill's scripts in there: `record.py`, `measure.py`, `build_page.py`, `build_icon.py`, `build_note.py`, `build_block.py`, `build_attestation.py`, `build_bundle.py`, `render_md.py`, `render_pdf.py`, `review.py`, `build_verify.py`, `seal.sh` — and `verify.html`, which is not a script but is the tool the reader runs, so it belongs to the case for the same reason. A case folder has to remain verifiable on its own even if the skill changes — and there is exactly one copy per folder: two copies of `measure.py` in the same case have already produced two different numbers. Then record two events: the opening of the case (with the mode, the capture method and the known limits) and the user's brief (subject, format, where it will be published, the process they say they intend to follow).

Create `case.json` too, from `case_example.json`: title, author, date, whether the register is reconstructed. It carries no address for the case, and there is nowhere to put one: the record travels with the document, as one file, and the technical line says so. See *Publication*.

`case.json` also carries **`case_uid`**: a short, stable name for this case, fixed now and
never changed. The bundle is named after it, so it is the only thing that says which case
a file belongs to once that file is on its own — and it has to exist before the manifest,
which covers `case.json`. `reference/protocol.md` has the rest.

**What you say at the opening.** Two sentences, then start. The folder, the scripts,
`case.json` and the case's short name are yours and are never mentioned.

> *"I'm keeping a record of how this gets written from here. It only sees this
> conversation: anything you write elsewhere it won't know about, and knowing you're
> being recorded may change how you write. Both of those go in as limits."*

> *"Nothing in the record gets deleted. Before I seal it, wording can be replaced; after,
> not even that — it takes a new entry saying what changed and why."*

**And one line more, which is the whole of what you ask.** The default is that nothing has
to be kept out — most pieces are the author writing about their own work, and a case that
opens with an interrogation about privacy makes a problem out of its absence:

> *"If there's anyone who must not appear in the record — not just in the article, in the
> record — tell me now and I'll keep them out."*

If they name someone, or if the piece turns out to be about other people, **stop and read
reference/people.md before recording the brief**: the two regimes, the question that
decides which one applies, and how to get the names out of the author in the forms that a
list can actually catch. Nothing there can be improvised, and the register travels whole:
a copy in a reader's hands cannot be withdrawn or told it has been superseded.

`case.json` also carries `key_fingerprint`, and it is the only key field there is: no
`key_url`, no address, as *Before the first case* has already said. The manifest covers
`case.json`, so the sealed chain itself records which key this case expected — which is
what stops the copy in the bundle from being merely circular, and is still not identity.

Among the known limits, always declare at least these: that capture happens through the conversation and not through an instrumented editor; that work done outside the conversation is not observed; that the user knows they are being observed and that this may change how they write.

**A space after every opening brace**: `{ "type"`, never `{"type"`. Not cosmetic — the
compact form is read as obfuscation and warned about at every event, and `record.py` says
so when it sees one. `--file` takes a long event from a file beside the case folder,
written with your file tool, never a heredoc.

```bash
python3 record.py '{ "type": "case_open", "actor": "system", "phase": "—", "payload": { } }'
python3 record.py --verify
```

### 2. While writing

Record one event for every substantial exchange. Do not record housekeeping exchanges. The types in use: `brief`, `ai_proposal`, `human_contribution`, `editorial_decision`, `constraint`, `version`, `elicitation`, `register_note`, `status`.

Save a version in `versions/` every time the text changes substantially, and record the `version` event with the word count and the SHA-256.

**Watch out for lexical carry-over.** If a phrasing you produced — even in a comment, not only in a proposed edit — reappears in the user's text, **record it**. It is the contamination channel no tool catches on its own and only explicit vigilance picks up. The same goes for ideas: if the user adopts an angle of yours from the brainstorming, that span has AI ideational origin even if the words are theirs.

Mark with `"meta": true` the events that concern the design of the method and not the content: they are excluded from the denominator.

**Numbers in a payload are integers, or they are strings.** A percentage goes in quoted — `"ai_lexical": "94.0"`, never `94.0` — integers stay within ±(2⁵³ − 1), keys are ASCII, and `record.py` refuses the event otherwise. Nothing is lost: a number in a payload is description, and the measurement of record is `kpi.json`. `violations()` in that file says why it refuses rather than warns.

### 3. Revision

Print the text with **numbered paragraphs** (the index of the paragraph in the file, blank line as separator) so that the user can refer to `[12]`. The numbers must match those in the annotation — which calls them blocks, and the author never has to.

Propose edits **marked one by one** with an identifier (`M01`, `M02`…), plus a closing index with the type, what changes and why. The user accepts or rejects by number. Every decision is an `editorial_decision` event with the outcome and the updated attribution.

**Purely formal** corrections — typos, agreement, double spaces, consistency of quotation marks and capitalization — are applied without asking but are **always listed**. Anything that touches meaning is proposed, not applied.

Do not rewrite the user's voice. Anglicisms, a colloquial register, personal lexical choices are theirs and are to be left alone, barring an actual error.

### 4. Closing

**What you say at the closing.** Four decisions belong to the author, in this order:
three before the seal, one after it. Everything between them is yours and is not
narrated.

**The numbers, once the measurement passes.** Two percentages, what each is a percentage
of, the phase that changes the reading, and the two things it does not prove:

> *"Of the words in the final text, 47% are the model's and 53% yours; of the ideas, 31%
> the model's and 69% yours. Almost all of the model's words are in the revision — the
> first draft is 86% yours. Two things this does not prove: it can't show the record is
> complete, only that nothing in it was changed after the fact, and the ideas figure is a
> judgement, not a count."*

**The last read.** It is an offer, and it is made once, after the measurement passes,
whatever the regime:

> *"One thing before I seal it. The record still holds what you told me about other
> people, and passages the article no longer has — this is the last point at which any of
> that can come out for free. Do you want to read it? It's about forty lines."*

If they say no, say nothing further and run `review.py --done`, which records that the
moment happened either way. If they say yes, say the limit once, because a list that comes
back clean reads as a clearance and is not one:

> *"It finds words, not inferences. Four harmless details that together point at one
> company will go straight past it."*

**Where the record travels.** Not a decision: there is one route. Say what you did, not
how, and say it once:

> *"I'll pack the record into one file you can attach to the article — a reader can check
> everything in it with the network off, and it needs nobody alive in ten years."*

Not the file names, not the digests, not what the manifest covers. Never offer an address,
a hosted copy or a link: the method has none, and a route invented at the closing is a
promise nothing in the case can keep.

**The point of no return.**

> *"From here on the record can only be added to. If anything in it should change, say so
> now: after I seal it, changing it means opening the case again and saying publicly
> why."*

**The qualified signature, once the PDF exists** — the fourth decision and the only one
after the seal. Offer it once, and do not press it:

> *"Last thing, and it's optional. The PDF carries the whole record as an attachment. If
> you sign it with a qualified signature — the one that names you legally — that covers the
> attachment too, and it's the only step that says who you are: everything inside the file
> proves the record is intact, none of it can say the person behind it is you."*

If they ask what it does not do, say it plainly: *"It doesn't say the numbers are right.
It says this package came from you and hasn't changed since."*

---

Annotate, measure, generate, seal, publish. See reference/protocol.md for the attribution rules. **The block is generated, not assembled**: `build_block.py` composes the icon, the note and the technical line into the one shape reference/disclosures.md prescribes — icon on the left, note and technical line stacked to its right, the icon in absolute units. Read that file for why the shape is what it is, not to retype it. The note is followed by a technical line — signed or not, where it lives, how many events and the root — generated by build_note.py, never typed. **Neither goes in the text** — `render_md.py` and `render_pdf.py` add both at render time, from the measurement. Both are short by default: five lines and three. reference/disclosures.md says why, what `--form full` is for, and what drops when.

```bash
python3 measure.py          # integrity check + computes the two axes
python3 review.py           # the last read: what the register says about other people
python3 build_page.py       # HTML verification page
python3 build_icon.py       # quadrant icon, from kpi.json
python3 build_verify.py     # VERIFY.md, the reader's page, from case.json
                            # then the closing manifest — see below
bash seal.sh events.jsonl   # Ed25519 signature + timestamp + anchoring
python3 build_note.py       # the technical line of the note
python3 build_attestation.py # the checkfile a reader runs, and what this does not claim
python3 build_bundle.py     # the bundle: the evidence and the verifier, in one file
python3 render_pdf.py --attached --embed   # the document, with the record inside it
```

**Both flags, always.** `--attached` writes the line saying the record is enclosed;
`--embed` puts it there. Without the second the document names a bundle it does not carry,
so the script refuses — unless you say `--beside`, because the tar really is travelling
alongside.

### The last read

`review.py` shows the author three lists — red-list hits recorded anyway, every
`human_contribution` event whole, every payload string that repeats thirty characters of a
draft — and it is the last moment at which anything in the register can be taken back for
free. `--set` rewrites a value and rebuilds the chain: **values are rewritten, events are
never deleted**, and nothing that is measured moves. Then `review.py --done`, **always,
whether or not anything changed**.

**It runs after `measure.py` passes and before `build_page.py`.** The docstring at the head
of `review.py` says why, clause by clause; after the closing manifest the script refuses
outright.

### The closing manifest

`seal.sh` signs `events.jsonl` and nothing else. On its own that is a signed register which
does not commit the text it describes: the final version, the annotation, the measurement
and the icon all sit outside the signature, and a reader who checks it has proved less than
they think.

So the **last event of every case is a manifest**: the SHA-256 of each file the measurement
depends on, and of each script a reader runs to check it.

```bash
python3 record.py '{ "type": "status", "actor": "system", "phase": "—", "meta": true,
  "payload": { "closing": "MANIFEST — final event. The next operation is the
  signature.", "algorithm": "sha256", "sha256": { "…": "…" } } }'
```

**What it covers**: the source version, `annotation.json`, `kpi.json`, `spans.json`,
`case.json`, `icon.svg`, `index.html` — the verification page — `verify.html`, and every
script in the folder, `review.py` included: a reader who wants to know what the review
looked at runs it themselves, over the register they were handed.

**What it leaves out, deliberately**: the renderings for publication — the article as
markdown, HTML or PDF, and whatever script makes them — any prose about the case, and the
bundle. The rule is in the names, so it is not a judgement made file by file: **`build_*`
is covered by the manifest, `render_*` is not.** Both render scripts say why in their own
docstrings, and `build_bundle.py` says why the tar it writes cannot be covered by a
manifest it contains.

**Two rules of order, and the second is where people trip.**

The manifest is computed **last**, when every file it covers is final. Nothing it covers is
typed by hand any more: `build_verify.py` writes `VERIFY.md` from `case.json`, the way the
icon and the verification page are written from the measurement. Regenerate anything after
the manifest and the manifest that covers it is invalid, and the verification page fails
its own check. In the validation case that was learned by redoing the manifest three times.

After the manifest, **the only permitted operation is the signature**. If anything else has
to change, the case is reopened: a new event says why, before any file is touched, a new
manifest supersedes the old one, and the register is signed again. Renderings are made
after sealing — one made earlier carries the root of the event before the manifest, which
is not the sealed root, and if that happened it is said rather than hidden.

### Line endings

`cases/** -text` has to be in the repository's `.gitattributes` before a case is published.
`colophon setup` writes it and prints why while it does; reference/VERIFY.md has the rest.

### Publication

A case is not finished when it is sealed. It is finished when the record it declares can
be reached, and there is one way to reach it: a file. `build_bundle.py` writes
`colophon-<case_uid>.tar`, `build_note.py --attached` names it in the technical line, and
the reader drops it on the verifier with the network off. It needs nobody alive in ten
years.

**Never offer an address** — not a hosted copy, not a deposit service, not a link to
somewhere the case supposedly lives, and not in conversation either. `case.json` has no
field for one and the scripts read none. With no bundle, the line says `signed register,
not enclosed` and the root: legitimate, said plainly.

**Packing records no event**, like the technical line: a new event would change the root.
Do not pack or render before the manifest, nor record having done so after.

**Check the copy you are about to send.** Drop it on `verify.html` yourself: it opens the
PDF and says what is actually inside it. `build_note.py --attached` and `render_pdf.py`
refuse to promise an enclosure that is not there, but neither can tell you what is.

reference/disclosures.md is open when the block is composed and carries the rest — why a
file and not an address, the four rules of the technical line, what `--attached` checks.
The key in the bundle is circular on its own: reference/VERIFY.md §2 says that to the
reader, and why one travels anyway.

### The qualified signature

Every check the case ships is one of internal consistency, which a forgery achieves too:
a case fabricated this morning, signed with a key made this morning, passes all of them.
Nothing in a folder can say who made it.

**One step closes that, and it is the last one.** The rendering above put the bundle and
the verifier inside the PDF, so a qualified signature over that file covers the article
*and* the evidence in one act, and a supervised trust service identified the signer first:
the reader gets a person, not a key fingerprint. Sign the PDF, never `attestation.txt`:
reference/VERIFY.md §0 says why that one travels unsigned.

**And it does not make the measurement true.** It says *this file came from this person
and has not changed since*, nothing about whether 47% is right. A reader seeing a legal
name in a signature panel hears the stronger claim unless somebody says otherwise, so say
it. reference/VERIFY.md §2b is the reader's side.

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

**Always report the breakdown by phase as well.** An aggregate figure of 47% reads as "half of it was written by the machine"; knowing that the words of the first draft are 86% the author's and that the AI worked on the revision tells the true story. Without the breakdown the number is misleading in both directions. (The values are those of the validation case, not a target to hit.)

**And a per-phase figure says which axis it is on, exactly as the aggregates do.** `measure.py` prints a column for each and `kpi.json` carries them as `ai_lexical` and `ai_ideational`. Inside one phase the two can sit at opposite ends — in case 001 the first draft is all the model's words and two thirds the author's ideas — so a single unlabelled number there says "the first draft is 0% mine" about a draft the author thought up.

In material addressed to the public use whole numbers. The precise value stays in the record.

## When something stops

`measure.py` exiting non-zero is a normal moment in the cycle, not an accident, and the first thing to do is to say so to the user in one sentence: **the register is intact, nothing they wrote or you recorded is lost, and this is the closing step being repeated — not the work.** They are watching a red block of text about spans and declarations, in the vocabulary of a file they have never opened.

**Everything in the closing sequence that refuses is the same moment, and gets the same
sentence: nothing is lost, here is what has to happen, and here is what it costs the
record.** The scripts print the diagnosis for whoever is working on the case; you say one
sentence for the person who wrote the text. The four you will actually meet:

> **The render gate.** *"The text has changed since it was measured, so I'm not printing
> it — the document would carry a signature saying this is the text that was measured, and
> it isn't any more. Nothing is lost. Either put back the version that was measured, or
> measure this one, and we go on."*
>
> **A piece of formatting the renderer will not guess at.** *"There's something on line 44
> I can't print without risking changing it, so it stopped rather than printing something
> you didn't write. Tell me what that line should look like and I'll set it plainly."*
>
> **The review, after the manifest.** *"This is past the point where the record can be
> edited quietly. Nothing is broken — but changing anything now means reopening the case,
> which is recorded and visible. Do you want to?"*
>
> **Packing before sealing.** *"I can pack this now, but nothing has signed it: a reader
> would be able to see that the record is consistent with itself and nothing about who
> made it. Shall I sign it first?"*
>
> **The seal, with no key.** *"I can't sign this: there's no signing key on this machine.
> That one isn't a step I should take here — a key made in a session that ends has already
> travelled by the time you hold it, and a signature from it would say nothing while
> looking like it said everything. Nothing is lost: the record, the measurement and the
> verification page are done and they check out. The seal is the one piece missing, and it
> is yours to add on a machine you keep."*

**And that last one is the exception in this list: it is never fixed by making a key.**
Every other refusal here is a step arriving late, and you perform it. `seal.sh` printing
`no key at …` is not — it means the case is being closed somewhere the author is not, and
the `ssh-keygen` line the script prints is addressed to the author on their own machine,
never to you. Do not run it, do not offer to, and do not treat a missing key at the seal as
the setup conversation arriving late: at the closing it is too late for that conversation,
because the answer it exists to collect is one only the author can give.

**Stop before the seal and finish everything else.** Skip `seal.sh`, run `build_note.py`
anyway — its `unsealed` state is built for exactly this and prints `register not sealed
yet — no signature or timestamp` — and say in the closing note that the case is unsealed
and why. A case that stops here is honest and incomplete, which is a state the method
supports. A case sealed with a key that leaked is neither.

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

**The labels stay in English and the icon is never shrunk below a hundred pixels a side.** reference/disclosures.md says why, and it is the file open when the block is composed.

**Never generate it by hand and never touch it up.** It comes from the measurement file, so it cannot diverge from the declared number: that is what makes it useful.

**Publish it with the point, not with the name of the category alone.** The classification rounds at 50% on both axes. The script warns when the point is less than five points from an edge: in that case the name on its own is a stronger claim than the data.

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
