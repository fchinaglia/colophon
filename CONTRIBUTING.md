# Contributing to Colophon

The method rests on one validated case, annotated by one annotator who was also a party to the writing. Everything below follows from that.

## What is worth most

**A second case.** Run the method on something you were going to write anyway, and publish the case folder: `events.jsonl`, `annotation.json`, the versions, `kpi.json`, `index.html`. A case in another language, another genre, or another working style is worth more than any amount of discussion about the method. Open a pull request adding it under `cases/`, or open an issue with a link if you would rather host it yourself.

Say in the case what went wrong. A case where the reconstruction check failed twice and you had to re-annotate is more useful than a clean one.

**Inter-rater validation.** Take a text that already has a register, annotate it independently without looking at the existing annotation, and report the agreement. This is the single obligatory next step for the method, and it is the one thing the author cannot do alone. If you want to try it, open an issue first and we will agree the protocol before you spend the effort.

**Cases that break the protocol.** If you hit an attribution you cannot resolve with the rules in `reference/protocol.md`, that is a finding, not a failure. Open an issue with the text, what you were trying to attribute, and why both answers felt wrong. The three original categories in the protocol — elicitation, deletion on suggestion, lexical carry-over — all came from exactly this.

## Open problems

These are unsolved. Work on any of them is welcome.

- **Diffuse intervention.** When a model changes two words in each of forty spans, annotating all forty as mixed inflates the AI share. The protocol says to record it as an event and declare the choice, which is a workaround, not a rule.
- **An event-level measure.** Today the measurement is per word. A measure over events — how many interventions, of what kind — would say something the word count cannot, and the two together would say more than either.
- **Capture outside the conversation.** Anything written in another window is invisible to the method, and the register can only record that it was not tracked.
- **Translation.** A translated text inherits the ideas but not the lexical profile. The current answer is to declare it, which is right but thin.
- **The anchored-chain property.** A continuously anchored chain might make omission visible as a gap in time. That is a hypothesis, not a result, and it needs testing.

## Ground rules for changes to the method

The method makes a few commitments that a pull request should not quietly undo.

1. **Two axes, never one.** A single blended score is the thing the method exists to avoid.
2. **The denominator is always explicit.** Every percentage states what it includes and excludes.
3. **The span is the unit, not the token.** Per-word attribution is not more precise, only more fragile.
4. **Limits are stated before results**, not after.
5. **No silent gaps.** If something was not tracked, the register records that it was not tracked.
6. **Nothing phones home.** The scripts run locally and send nothing anywhere. A tool about disclosure that quietly collects telemetry would be self-refuting.

If you think one of these is wrong, that is a conversation worth having — open an issue and argue it. Just do not change it in passing inside a patch about something else.

## Practical

- **Code.** Python 3.9+, standard library only. The scripts must keep running with no dependencies to install: that is a feature, not an accident. Keep them readable over clever.
- **Language.** This repository is English. The research survey behind it is in Italian and lives elsewhere.
- **Before opening a PR**, run the example end to end and make sure it still works:

  ```bash
  cd example
  python3 record.py --verify && python3 measure.py && python3 build_icon.py && python3 build_page.py && python3 build_note.py
  ```

- **The package.** `colophon.zip` is what people install from the release;
  `skill/colophon/` is what you edit. Run `python3 check_package.py` before releasing:
  it fails if the two have drifted, or if the zip carries junk, and prints the command
  that rebuilds it. Copy that command rather than writing the `zip` flags by hand — the
  exclusion list is exactly where a `.DS_Store` slipped into a published package once.

- **The paper.** `paper/colophon-method.md` is the source; `paper/colophon-method.pdf` is
  a rendering of it. Change the Markdown, never the PDF. The two can drift, and today
  nothing catches it.

  To re-render it after changing the Markdown:

  ```bash
  cd paper && python3 build_paper.py --pdf
  ```

  `build_paper.py` converts the Markdown to `colophon-method.html` and prints that
  through headless Chrome. Both outputs are committed. It is standard library only,
  like everything else here, and deliberately not a general Markdown implementation:
  it covers what the paper uses and leaves anything else visible as literal text,
  which is the failure worth having. Commit the HTML along with the PDF — a rendering
  nobody else can reproduce is how the first one drifted from its source.

- **Commits and PRs.** Say what changed and why. If the change alters a measurement, say what the number was before and what it is now.

## Conduct

Be straightforward and be kind. Argue with the idea, not the person. Disagreement about the method is the point of publishing it.

---

*MIT License — Copyright (c) 2026 Fabio Chinaglia. See the LICENSE file.*
