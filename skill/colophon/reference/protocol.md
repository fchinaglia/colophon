# Attribution protocol

Working rules for annotating a text span by span. The hard cases are the majority: read this before you start.

---

## The two axes

Every span receives **two independent attributions**. They are not redundant and they must not be collapsed into one.

| | question | values |
|---|---|---|
| **lex** | who wrote the words you read in the final text? | `U` `A` `UA` |
| **idea** | where does the content those words express come from? | `U` `A` `UA` |

`UA` means **indivisible mixed**: not that two parties were involved, but that there is no traceable boundary between them. If the boundary exists, split the span instead of using `UA`.

In the count `UA` is worth half, and that has to be declared.

### Why two axes and not a scale of levels

An ordinal scale with five or six levels of "role" looks richer but is unusable in practice: too many real cases fall between two rungs and the choice becomes arbitrary. Two binary axes plus the mixed value cover the same space, can be assigned without hesitation in most cases, and produce directly the two percentages that are actually needed.

---

## The phases

`research` · `outline` · `first_draft` · `content_revision` · `copy_revision` · `titling`

The phase is **the one in which the content was produced**, not the one the text is currently in. A block added during revision is `content_revision` even if it sits in the middle of the first draft.

The key distinction, borrowed from the taxonomy of revision intentions: `content_revision` changes what the text asserts; `copy_revision` does not. Removing an unsupported quantification is content. Untangling a knotted sentence is form.

---

## The hard cases

### Absorption from the brainstorming

The user writes a draft in their own hand and declares it — in good faith — entirely human, but it contains phrasings you had produced an hour earlier while working out the ideas.

→ `lex: A`, and `idea` according to whose idea it was. This is the case no detector finds and no self-declaration remembers. **Go back and reread the brainstorming before annotating**: it is the only way to catch it.

### Carry-over from the conversation

A phrasing of yours that appeared in an **editorial comment** — not in a proposed edit — resurfaces in the user's text.

→ Same treatment as the previous case. It is more insidious because that sentence was never offered as text: an instrumented editor would not see it. Only explicit vigilance catches it.

### Elicitation

The AI writes nothing and proposes nothing: it **asks a question**, and that causes new human content to be produced.

→ The span is human in its words; the ideational origin is `UA`, because the question determined that the passage exists at all. Record an `elicitation` event with the exact question. No public schema represents this case.

### Deletion on suggestion

The AI proposes cutting a passage and the user accepts. No AI words enter the text, but the final text is different because of an AI intervention.

→ **Invisible in the word count.** Record the event and cite it on the verification page. It is the mirror image of elicitation.

### Rephrasing of human content

The AI rewrites a passage while preserving its meaning.

→ `lex: A`, `idea: U`. This is "homogeneous mixed authorship", the case the literature identifies as the hardest to attribute — and which here is trivial, because the decision was recorded.

### Human rewriting of AI text

The user rewrites a span the AI had produced.

→ Usually `lex: UA`. If nothing of the original phrasing survives, `lex: U`; `idea` stays `A` if the conceptual frame is still the one the AI proposed.

### Spans that went through several passes

AI proposes → human rewrites → AI proposes again → human accepts.

→ The attribution records **only the final state**. The history lives in the register, and that is exactly why it has to be cited: the word count does not contain it. If a span went through more than two passes, mention it on the verification page.

### Diffuse lexical intervention

A terminology pass touches twenty spans, changing two or three words in each.

→ **Do not re-annotate all of those spans as mixed**: it would inflate the AI share misleadingly, because those paragraphs remain the user's in everything but a word. Record it as an **event**, leave the attributions untouched, and declare the choice on the verification page. The threshold beyond which a diffuse intervention also changes the attribution is unsettled: declare it case by case.

### Moving a block

A block is moved without being rewritten.

→ Attribution unchanged. If the move was proposed by the AI, it is an `editorial_decision` event of the structural kind.

### Section headings

If they come from an outline proposed by the AI, they are `A` even if the user used them without comment. Check this: in most cases the structure is the component with the highest AI share, and it goes unnoticed.

### The user's primary material

Real cases, experiences, internal data, lived examples: `U`/`U` always, even if the phrasing was polished — in that case split the span.

### Sources and data brought in by the AI

Figures, references, factual corrections: phase `research`, `lex: A`, `idea: A`. If the AI corrects a wrong figure of the user's, record it explicitly: it is the most verifiable form of contribution and the easiest to forget.

---

## Granularity

The unit is the **contiguous homogeneous span**: typically anything from half a sentence to a paragraph.

Never the token. Word-by-word attribution is not more precise: it is only more fragile, and it produces a visualization that reads worse than the data it contains.

Split a block when the attribution changes. Do not split it for five words set inside someone else's sentence: in that case use `UA` on the whole sentence and explain it in the note.

---

## The format

`annotation.json`:

```json
{
  "source": "versions/v04_final_article.md",
  "excluded": [1, 57, 58],
  "explained": {"R12": "superseded by R19"},
  "blocks": {
    "0": {"lex": "UA", "idea": "A", "phase": "titling",
          "event": "M11", "note": "title proposed by the AI, then rewritten"},
    "3": [
      {"from": "A services company", "lex": "U", "idea": "U", "phase": "first_draft"},
      {"from": "In this second case", "lex": "A", "idea": "UA", "phase": "first_draft",
       "note": "AI phrasing absorbed from the brainstorming"}
    ]
  }
}
```

`excluded` holds the blocks that stay out of the count: typically the provenance disclosure itself, which must not measure itself.

In the lists, `from` is the start of the span: a short string that occurs only once inside the block. The first element starts at the beginning of the block, and its `from` is not used to cut anything.

`explained` holds the edits that the register declares and no span carries, with the reason for each:

```json
"explained": {"R12": "superseded by R19", "R25": "diffuse pass, attributions unchanged"}
```

Without it `measure.py` stops and publishes nothing. The two cases it exists for are the ones described above — an edit a later one replaced, and a diffuse intervention recorded as an event on purpose — and both are legitimate. What is not legitimate is leaving them unsaid: an unmatched edit is also what an annotation looks like when it has fallen behind, and from the outside the two are identical.

---

## Before publishing any number

1. `measure.py` must say **reconstruction: OK**.
2. It must exit zero: no unmatched edit left undeclared, and no stale entry in `explained`.
3. The percentages must be accompanied by the breakdown by phase.
4. The section on the limits gets written **before** the results, not after.

---

*MIT License — Copyright (c) 2026 Fabio Chinaglia. See the LICENSE file.*
