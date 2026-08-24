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

Create `cases/NNN-<slug>/` with `versions/` inside it, and copy **all** of the skill's scripts in there: `record.py`, `measure.py`, `build_page.py`, `build_icon.py`, `build_note.py`, `build_block.py`, `build_attestation.py`, `build_bundle.py`, `render_md.py`, `render_pdf.py`, `seal.sh` — and `verify.html`, which is not a script but is the tool the reader runs, so it belongs to the case for the same reason. A case folder has to remain verifiable on its own even if the skill changes — and there is exactly one copy per folder: two copies of `measure.py` in the same case have already produced two different numbers. Then record two events: the opening of the case (with the mode, the capture method and the known limits) and the user's brief (subject, format, where it will be published, the process they say they intend to follow).

Create `case.json` too, from `case_example.json`: title, author, date, whether the register is reconstructed, and — **if the case will live at an address** — `verification_url`, where the verification page will be readable, and `register_url`, the folder with the register and the files. `build_note.py` puts the first in the technical line and falls back to the second; `build_page.py` uses the second to link the files from the page. Leave both out and the line says the record travels with the document, which is true when it does. See *Publication* for the three routes.

`case.json` also carries **`case_uid`**: a short, stable name for this case, fixed now
and never changed. It is not decoration — the bundle is named after it, so it is the only
thing that says which case a tar belongs to once the tar is detached from the folder that
made it. Fixed at the opening because the manifest covers `case.json`: a name derived
later from the register's root could not go in, since the root is the hash of the manifest
event and the manifest covers the file the name would have to live in.

`case.json` also carries `key_url` and `key_fingerprint`: where the author's public key
is published, and which key to expect. **Publish it on a domain you control, not inside
the case** — `/.well-known/colophon/keys`. A key published inside the folder it
authenticates proves only that the folder is internally consistent, which anyone can
arrange in ten seconds by generating a fresh key and re-signing. The copy in the folder
stays, for offline reproduction; the published one is what binds the key to a person.

An address you cannot keep is worse than none: the line is generated at render time, so a PDF freezes it forever. Do not move a case folder once it is published. If you do not know the address yet, add it before publishing — the line will pick it up at the next render.

The page has to be **served as a page**. A raw `.html` on a code host is delivered as plain text and the reader sees the markup: publish it where HTML renders, GitHub Pages or your own site.

**No underscore in the published address.** URL detectors — in mail clients, chat apps, PDF viewers — cut a link at the first underscore, so `…/cases/002/pagina_di_verifica.html` arrives at the reader as `…/cases/002/pagina`, which is a 404. `build_page.py` writes the page as `index.html` for this reason, so the address ends at the folder and there is nothing after it to truncate. A case sealed under an older name keeps it — its manifest covers that name — and gets an `index.html` next to it that redirects.

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

Print the text with **numbered blocks** (the index of the paragraph in the file, blank line as separator) so that the user can refer to `[12]`. The numbers must match those in the annotation.

Propose edits **marked one by one** with an identifier (`M01`, `M02`…), plus a closing index with the type, what changes and why. The user accepts or rejects by number. Every decision is an `editorial_decision` event with the outcome and the updated attribution.

**Purely formal** corrections — typos, agreement, double spaces, consistency of quotation marks and capitalization — are applied without asking but are **always listed**. Anything that touches meaning is proposed, not applied.

Do not rewrite the user's voice. Anglicisms, a colloquial register, personal lexical choices are theirs and are to be left alone, barring an actual error.

### 4. Closing

Annotate, measure, generate, seal, publish. See reference/protocol.md for the attribution rules. **The block is generated, not assembled**: `build_block.py` composes the icon, the note and the technical line into the one shape reference/disclosures.md prescribes — icon on the left, note and technical line stacked to its right, the icon in absolute units. Read that file for why the shape is what it is, not to retype it. The note is followed by a technical line — signed or not, where it lives, how many events and the root — generated by build_note.py, never typed. **Both are short by default**: five lines for the note, three for the technical line, and that is the form to use everywhere, PDFs included. The paragraph note and the one-sentence technical line remain, for a page that has room to explain itself: `--form full`. The rules, and what drops when, are in reference/disclosures.md.

```bash
python3 measure.py          # integrity check + computes the two axes
python3 build_page.py       # HTML verification page
python3 build_icon.py       # quadrant icon, from kpi.json
                            # then the closing manifest — see below
bash seal.sh events.jsonl   # Ed25519 signature + timestamp + anchoring
python3 build_note.py       # the technical line of the note
python3 build_attestation.py # the checkfile a reader runs, and what this does not claim
python3 build_bundle.py     # the bundle: the evidence and the verifier, in one file
                            # then publication, if any — see below
```

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

Git normalises line endings on checkout. A clone on Windows with `core.autocrlf=true`
turns every `\n` into `\r\n`: the files still read, **every digest changes, and the
signature stops verifying**. Worse, `record.py --verify` still answers `chain intact`,
because it recomputes from parsed JSON — so the first check passes, the second fails, and
an honest reader concludes the signature is forged.

Put `cases/** -text` in the repository's `.gitattributes` before publishing a case, and
check it is there before telling anyone to verify.

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

The three are not a ranking. A PDF can carry the attachment; a web page can carry the
address; a post can carry neither and must point at something that does. **The marker, the
note and the root travel in every container. Only the route changes.**

**What the attachment cannot do, and you should say so once.** A bundle in a reader's
hands is frozen. It verifies perfectly and it cannot announce that it has been superseded
— a case reopened next month leaves every distributed copy looking correct and being out
of date. This is why the root is printed in the document: a reader holding two copies can
see that they differ. It is also why an address, when you have one, is worth having
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

**If you did publish at an address, check that it answers before you call the case done.**
`seal.sh` writes `events.jsonl.sha256`, so fetching the register from where it was
published and comparing the two digests is the whole check:

```bash
curl -fsS "<register_url>events.jsonl" | shasum -a 256
cat events.jsonl.sha256
```

The same digest — the second column differs, the hash is the whole comparison — means the
address serves the bytes the signature attests. A different one, or a `curl` that fails,
means the case is not published, whatever anything printed on its way out.

**An address that has not been published is not done.** Do not report the closing sequence
as successful while the declared address 404s. That the numbers are right is not what the
note claims: it tells a reader where to go and check them, and a note whose address is
dead is the failure the note exists to remove, wearing the costume of the fix.

**Say what is not yet true.** A publication that is deferred — the domain does not exist
yet, the author wants to hold the piece — is recorded, and *when* it is recorded is the
whole difficulty. Before the manifest it is one event like any other. After the seal it is
a reopening: a new event saying why, a new manifest, a second signature, the old seal
kept. So find out early, before you compute the manifest, not after it. What is not
allowed is the third option: leaving a declared address that reads as live and saying
nothing. That is a silent gap, and it is the one a reader walks into.

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
