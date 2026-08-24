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

**Decide it; do not ask.** Under 800 words → light, above → full. If you genuinely cannot tell, ask what they are writing — a post or a long piece — not which mode they want. `light` and `full` are names in this file.

**Light mode.** Event register with a hash chain, no span-level annotation, closing note with coarse-grained estimated percentages declared as estimates. Almost no friction.

**Full mode.** The whole cycle: register, span-by-span annotation, measurement along the two axes, verification page, three-level disclosure, cryptographic seal.

You can move from light to full at any moment without losing anything: the register is the same.

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

## The cycle

### 1. Opening

Create `cases/NNN-<slug>/` with `versions/` inside it, and copy **all** of the skill's scripts in there: `record.py`, `measure.py`, `build_page.py`, `build_icon.py`, `build_note.py`, `build_block.py`, `build_attestation.py`, `build_bundle.py`, `render_md.py`, `render_pdf.py`, `review.py`, `seal.sh` — and `verify.html`, which is not a script but is the tool the reader runs, so it belongs to the case for the same reason. A case folder has to remain verifiable on its own even if the skill changes — and there is exactly one copy per folder: two copies of `measure.py` in the same case have already produced two different numbers. Then record two events: the opening of the case (with the mode, the capture method and the known limits) and the user's brief (subject, format, where it will be published, the process they say they intend to follow).

Create `case.json` too, from `case_example.json`: title, author, date, whether the register is reconstructed, and — **if the case will live at an address** — `verification_url`, where the verification page will be readable, and `register_url`, the folder with the register and the files. `build_note.py` puts the first in the technical line and falls back to the second; `build_page.py` uses the second to link the files from the page. Leave both out and the line says the record travels with the document, which is true when it does. See *Publication* for the three routes.

`case.json` also carries **`case_uid`**: a short, stable name for this case, fixed now and
never changed. The bundle is named after it, so it is the only thing that says which case
a file belongs to once that file is on its own — and it has to exist before the manifest,
which covers `case.json`. `reference/protocol.md` has the rest.

**What you say at the opening, and in what order.** Four things, then start. The folder,
the scripts, `case.json` and the case's short name are yours and are never mentioned.

1. The question below, about who else is in this.
2. If there is anyone to protect, build the list. If there is not, skip it and say nothing.
3. *"I'm keeping a record of how this gets written from here. It only sees this
   conversation: anything you write elsewhere it won't know about, and knowing you're
   being recorded may change how you write. Both of those go in as limits."*
4. *"Nothing in the record gets deleted. Before I seal it, wording can be replaced; after,
   not even that — it takes a new entry saying what changed and why."*

**Ask one question before recording the brief, and record the answer.** *May what you
tell me be quoted in a record that is handed to other people?* The register travels whole
inside the bundle; a copy in a reader's hands cannot be withdrawn, corrected, or told it
has been superseded. For commissioned work the answer is usually no, and it is cheaper to
know now than after the signature.

One question, one answer. **The author never meets the two words.** You map what they say
onto one of them and record it as a `constraint` event before the brief:

    open           the author's instructions may be quoted, and the quotations travel
    confidential   they are recorded as what they required, never as what they said

**Anything that is not a clear no is `confidential`.** Being wrong that way costs a page
that explains itself; being wrong the other way cannot be undone.

`confidential` does not mean the case records less of the work. Every event, every
editorial decision, every attribution and every change is still recorded; what changes is
that the author's own words are not reproduced. Under it, quote nothing — anywhere, for
the whole case. The brief is not the only place a register quotes: in the validation case
002, three of the four events that had to be redacted were `editorial_decision` events
documenting the removal of the very details they quoted.

**If there is anyone to protect, get the list out of the author by asking about people,
not about matching.**

> *"Are there people or companies in this that must not appear in the record — not just in
> the article, in the record? Give me the names the way they'd actually turn up: the
> surname on its own, the way you'd say it in passing, the company without its legal
> form."*

Three variants a full name will not catch, and you ask for each rather than explaining why:

- the surname alone, and with an article — `Mario Rossi` does not match `il Rossi`
- the short form of a company — `Rossi & Figli S.r.l.` does not match `Rossi & Figli`
- anything they habitually call the person that is not their name

Two things it cannot reach, said once and not dwelt on: **initials and misspellings**.
`M.R.` and `Rosi` are not findable. Do not describe substring matching to get there.

You write the file, at `~/.config/colophon/redlists/<case_uid>.txt`, one entry per line.
The path is not shown to the author and the list is never read back. `record.py` warns when
an entry appears and records the event anyway; the warning comes back at the review before
the seal. **Never in the case folder** — the case's short name is public, the file the
reader receives is called after it, and a list of the names an author is protecting must
not be committed.

`case.json` also carries `key_url` and `key_fingerprint`: where the author's public key
is published, and which key to expect. **Publish it on a domain you control, not inside
the case** — `/.well-known/colophon/keys`. A key published inside the folder it
authenticates proves only that the folder is internally consistent, which anyone can
arrange in ten seconds by generating a fresh key and re-signing. The copy in the folder
stays, for offline reproduction; the published one is what binds the key to a person.

**An address is a promise**: the line is generated at render time, so a PDF freezes it
forever. Do not move a case folder once it is published. It must be served as a page, at
an address with no underscore in it — `reference/disclosures.md` says why both of those
matter, and `build_page.py` already writes `index.html` for the second.

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

**Numbers in a payload are integers, or they are strings.** A percentage goes in quoted — `"ai_lexical": "94.0"`, never `94.0` — and `record.py` refuses the event otherwise. The refusal is the point: a reader working outside Python cannot reproduce the bytes of a float, because after a JavaScript `JSON.parse` `94.0` and `94` are the same value and the distinction is destroyed by parsing rather than recoverable afterwards. A register carrying one cannot be checked in a browser at all, and it cannot be repaired later either, because the register is append-only and reopening a case adds events instead of rewriting them. Integers must stay within ±(2⁵³ − 1), because past that JavaScript loses precision silently and returns a different number without saying so; keys must be ASCII. Nothing is lost by the rule — the measurement of record is `kpi.json`, and a number in a payload is description.

### 3. Revision

Print the text with **numbered paragraphs** (the index of the paragraph in the file, blank line as separator) so that the user can refer to `[12]`. The numbers must match those in the annotation — which calls them blocks, and the author never has to.

Propose edits **marked one by one** with an identifier (`M01`, `M02`…), plus a closing index with the type, what changes and why. The user accepts or rejects by number. Every decision is an `editorial_decision` event with the outcome and the updated attribution.

**Purely formal** corrections — typos, agreement, double spaces, consistency of quotation marks and capitalization — are applied without asking but are **always listed**. Anything that touches meaning is proposed, not applied.

Do not rewrite the user's voice. Anglicisms, a colloquial register, personal lexical choices are theirs and are to be left alone, barring an actual error.

### 4. Closing

**What you say at the closing.** Four decisions belong to the author, in this order.
Everything between them is yours and is not narrated.

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

**Where the record travels.**

> *"Do you want the record to travel with the document, or to sit at a web address people
> can link to? Both work, and the document will say which. Travelling with it needs nobody
> alive in ten years; an address is the only one that can later say the case was
> reopened."*

Then say what you did, not how: *"I'll pack the record into one file you can attach to the
article — a reader can check everything in it with the network off."* Not the file names,
not the digests, not what the manifest covers.

**The point of no return.**

> *"From here on the record can only be added to. If anything in it should change, say so
> now: after I seal it, changing it means opening the case again and saying publicly
> why."*

---

Annotate, measure, generate, seal, publish. See reference/protocol.md for the attribution rules. **The block is generated, not assembled**: `build_block.py` composes the icon, the note and the technical line into the one shape reference/disclosures.md prescribes — icon on the left, note and technical line stacked to its right, the icon in absolute units. Read that file for why the shape is what it is, not to retype it. The note is followed by a technical line — signed or not, where it lives, how many events and the root — generated by build_note.py, never typed. **Neither goes in the text** — `render_md.py` and `render_pdf.py` add both at render time, from the measurement. Both are short by default: five lines and three. reference/disclosures.md says why, what `--form full` is for, and what drops when.

```bash
python3 measure.py          # integrity check + computes the two axes
python3 review.py           # the last read: what the register says about other people
python3 build_page.py       # HTML verification page
python3 build_icon.py       # quadrant icon, from kpi.json
                            # then the closing manifest — see below
bash seal.sh events.jsonl   # Ed25519 signature + timestamp + anchoring
python3 build_note.py       # the technical line of the note
python3 build_attestation.py # the checkfile a reader runs, and what this does not claim
python3 build_bundle.py     # the bundle: the evidence and the verifier, in one file
                            # then publication, if any — see below
```

### The last read

`review.py` shows three lists and nothing else: where the red list matched and the event
was recorded anyway, every `human_contribution` event whole, and every payload string that
reproduces thirty characters of a draft. A register holds five to six hundred strings and
nobody reads that; these are forty lines and a person does.

The author says what should not travel. `review.py --set` rewrites the value and rebuilds
the chain from that event on. **Values are rewritten; events are never deleted** — the
count of events is printed into a page the manifest covers. Every original timestamp
survives, and the measurement does not move: `measure.py` reads `payload.change` from the
register and nothing else.

Then `review.py --done`, which records **one event, always, whether or not anything
changed** — that the author read what the register says about other people, and whether
something was removed. Never which events, never how many. Naming them would tell a reader
where to dig, and a review that only appears when something was found is itself the
disclosure. If it were conditional, its presence would be the leak.

**It runs after `measure.py` passes and before `build_page.py`.** Not earlier: a stopped
measurement sends you back to the register and makes any earlier read stale. Not later:
the verification page prints the root, and the manifest covers the page. Not after the
manifest, which is the last event — rebuilding then changes the hash of the manifest
itself. Not after the seal: the signature can be remade, the timestamp cannot.

### The closing manifest

`seal.sh` signs `events.jsonl` and nothing else. On its own, that is a signed register
that does not commit the text it describes: the final version, the annotation, the
measurement and the icon all sit outside the signature, and a reader who checks it has
proved less than they think.

So the **last event of every case is a manifest**: the SHA-256 of each file the
measurement depends on, and of each script a reader runs to check it.

```bash
python3 record.py '{"type":"status","actor":"system","phase":"—","meta":true,"payload":{
  "closing":"MANIFEST — final event. The next operation on this case is the signature.",
  "algorithm":"sha256","sha256":{ "…":"…" }}}'
```

`review.py` is covered like the others: a reader who wants to know what the review looked
at runs it themselves, over the register they were handed.

**What it covers**: the source version, `annotation.json`, `kpi.json`, `spans.json`,
`case.json`, `icon.svg`, `index.html` — the verification page, under the name the
address needs — `verify.html`, and every script in the folder. Hashing
those and finding them inside the signed register is what closes the chain from the
signature to the published text.

**What it leaves out, deliberately**: the renderings for publication — the article as
markdown, HTML or PDF, and whatever script makes them — and any prose about the case, a
README or a landing page.

The rule is in the names, so it is not a judgement made file by file: **`build_*` is
covered by the manifest, `render_*` is not.** A `build_` script produces something the
measurement depends on and a reader re-runs to check it. A `render_` script produces the
document a reader receives, which carries the root and therefore cannot exist before the
seal. A rendering is derivable from what is covered and carries a technical
line that can only be generated *after* the seal, so freezing it would forbid the very
step the method requires. Freeze one and you will be reopening a sealed case to correct
a rendering.

**And the bundle, for a different reason.** `build_bundle.py` writes a tar that contains
the manifest, so the manifest cannot contain the tar. That is not a gap: the tar is
transport, not evidence. `verify.html` hashes each *file* inside it against the manifest,
so tampering with anything the case depends on is caught, and tampering with the
container only breaks extraction. Nobody should try to hash it.

**Two rules of order, and the second is where people trip.**

The manifest is computed **last**, when every file that is edited by hand is final —
`VERIFY.md` above all, which the author fills in with a key URL and a contact. Filling it
in *after* the manifest invalidates the manifest that covers it, and the verification
page then fails its own check. In the validation case this was learned by redoing the
manifest three times.

After the manifest, **the only permitted operation is the signature**. If anything else
has to change, the case is reopened: a new event says why, before any file is touched, a
new manifest supersedes the old one, and the register is signed again. The old seal is
kept — rename it `events.jsonl.v1.*` — because it still proves what the register looked
like on its own date, which no later signature can do.

One consequence to declare rather than hide: **a rendering made before the seal carries
the root of the event preceding the manifest**, not the sealed root. It cannot be
otherwise — a document cannot contain the fingerprint of a chain that then fingerprints
the document. Generate the renderings *after* sealing, with `build_note.py`, and the
problem disappears; if one was made earlier, say so.

### Line endings

Put `cases/** -text` in the repository's `.gitattributes` before publishing a case. Without
it a checkout on Windows rewrites every line ending, every digest changes and the signature
stops verifying — while `record.py --verify` still answers `chain intact`, so the first
check passes, the second fails, and an honest reader concludes the signature is forged.
reference/VERIFY.md has the rest.

### Publication

A case is not finished when it is sealed. It is finished when the record it declares can
be reached.

There are three ways to reach it, and the document says which one it is. The technical
line, generated by `build_note.py` and never typed, is where it says so.

**Attached.** `build_bundle.py` writes `colophon-<case_uid>.tar` — the register, the seal,
the measurement, everything the manifest covers, and `verify.html`. The reader drops it on
the verifier with the network off and gets the chain, the signature, every manifest digest
and the timestamp. Nothing has to stay online, no domain has to be renewed, and no
instance has to exist. This is the route that needs nobody alive in ten years, and it is
the default.

**At an address.** A site, a page, a folder you control. It is the only route a reader can
cite, link to, or come back to — and the only one that can say *this case was reopened,
here is the current root*. Put it in `case.json` as `verification_url` or `register_url`
and the line prints it.

**Neither.** Legitimate, and the line says so rather than implying an address that is not
there.

The three are not a ranking: **the marker, the note and the root travel in every
container, and only the route changes.** reference/disclosures.md has the three forms and
which container takes which.

**What the attachment cannot do, and you say so once.** A bundle in a reader's hands is
frozen: it verifies perfectly and cannot announce that it has been superseded. That is why
the root is printed in the document, and why an address, when you have one, is worth having
alongside.

**Your key is published once, and it is not part of the case.** A public key inside the
folder it authenticates proves only that the folder is consistent with itself, which
anyone arranges in ten seconds. Publish it at a domain you control, at
`/.well-known/colophon/keys` — or, with no domain at all, at
`https://api.github.com/users/<you>/ssh_signing_keys`, which is free and which
`case.json` records as `key_url`. That is the whole setup, and it is done once, not per
case.

**Publication records no event.** Like the technical line, it happens after the last one:
a new event would change the root the line prints and the manifest already covers. So do
not pack, publish or render before the manifest, and do not record having done so after.

**If you did publish at an address, check that it answers before you call the case done** —
fetch the register from where it was published and compare its digest with the one
`seal.sh` wrote. reference/VERIFY.md §0 has the two commands. A different digest, or a
fetch that fails, means the case is not published, whatever anything printed on its way
out.

**An address that has not been published is not done.** Do not report the closing sequence
as successful while the declared address 404s. That the numbers are right is not what the
note claims: it tells a reader where to go and check them, and a note whose address is
dead is the failure the note exists to remove, wearing the costume of the fix.

**Say what is not yet true.** A deferred publication is recorded, and *when* decides the
cost: before the manifest it is one event like any other; after the seal it is a reopening.
So find out before you compute the manifest. What is never allowed is the third option —
leaving a declared address that reads as live and saying nothing.

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
