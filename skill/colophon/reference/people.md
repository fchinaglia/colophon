# People other than the author

*Read this when the author says someone else is in the piece, or asks what the record will
say about them. `SKILL.md` opens a case on the assumption that nobody has to be kept out;
everything here is what to do when that assumption is wrong.*

The register travels whole inside the bundle. A copy in a reader's hands cannot be
withdrawn, corrected, or told that it has been superseded — so what goes in is a decision
made once, at the moment it is recorded, and the last chance to undo it is the review
before the seal.

---

## 1. The two regimes

One question, and **the author never meets the two words**. You map what they say onto one
of them and record it as a `constraint` event before the brief:

    open           the author's instructions may be quoted, and the quotations travel
    confidential   they are recorded as what they required, never as what they said

The question, when there is a reason to ask it:

> *"May what you tell me be quoted in a record that is handed to other people?"*

For commissioned work the answer is usually no, and it is cheaper to know now than after
the signature.

**Anything that is not a clear yes is `confidential`.** Being wrong that way costs a page
that explains itself; being wrong the other way cannot be undone.

## 2. What `confidential` does not mean

It does not mean the case records less of the work. Every event, every editorial decision,
every attribution and every change is still recorded. What changes is that the author's
own words are not reproduced.

Under it, **quote nothing — anywhere, for the whole case**. The brief is not the only place
a register quotes: in the validation case 002, three of the four events that had to be
redacted were `editorial_decision` events documenting the removal of the very details they
quoted.

## 3. The red list, and how to get it

**Ask about people, not about matching.**

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

## 4. Where the list goes

One entry per line, at the path `redlist_path()` in `record.py` computes — **never in the
case folder**, and that function says why. The path is not shown to the author and the list
is never read back.

`record.py` warns when an entry appears and records the event anyway. The warning is one
line, and it names nothing: naming the match would write it into the terminal and into
whatever transcript is running, which is the harm arriving through the guard. Every one of
them comes back at the review before the seal, which is where the decision belongs.

## 5. What the author is told, either way

Two sentences belong at the opening of every case, whether or not anyone has to be
protected. They are in `SKILL.md` because they are said before any of this is known:

> *"I'm keeping a record of how this gets written from here. It only sees this
> conversation: anything you write elsewhere it won't know about, and knowing you're being
> recorded may change how you write. Both of those go in as limits."*

> *"Nothing in the record gets deleted. Before I seal it, wording can be replaced; after,
> not even that — it takes a new entry saying what changed and why."*
