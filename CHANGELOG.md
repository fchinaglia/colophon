# Changelog

All notable changes to Colophon are recorded here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [semantic versioning](https://semver.org/).

## [Unreleased]

The skill file gets smaller, and the reason it could is not the one #27 assumed. Five
sections, both tiers of that issue, and in every one of them most of what was to be
moved was already written somewhere the rule is enforced.

### Measured first

`claude plugin details` puts a number on what 6,902 words cost: **~12.8k tokens on
every invocation**, against ~62 always-on. The three files in `reference/` are 49,322
characters to `SKILL.md`'s 40,203 and do not appear in that figure at all — if they were
counted it would read ~28k. So a rule moved into a reference file does not cost less, it
costs nothing until the file is opened. That is the premise the whole issue rests on, and
until now it was an argument rather than a measurement.

### Changed

- **The float rule keeps its instruction and drops its proof** (148 words → 64). The
  argument — `JSON.parse` collapsing `94.0` into `94`, the silent precision loss past
  2⁵³, the append-only register that cannot be repaired afterwards — already stood in the
  docstring of `violations()` in `record.py`, the function that enforces it, and measured
  against Node in `spec/canonical.md` §4. The pointer names `violations()` and not the
  spec: `colophon.zip` ships `skill/colophon` alone, so an install from the Claude apps
  cannot reach `spec/`.
- **The icon keeps what decides; the craft goes to `reference/disclosures.md`** (317 →
  224), which is the file open when the block is composed. It already carried the
  hundred-pixel floor twice, and it pointed *backwards* — *see The icon in SKILL.md for
  why* — from the file that is open to the file loaded on every invocation. No back-pointer from
  `reference/` into `SKILL.md` is left.
- **Publication keeps its instructions** (404 → 241). `disclosures.md`, under *The
  technical line*, already held the no-address argument, the four rules of order and what
  `--attached` checks; `VERIFY.md` §2 holds the key argument for the reader it addresses.
  What stayed is what has to be held before opening anything: one route and it is a file,
  never offer an address, nothing is packed before the manifest, and check the copy you
  are about to send on `verify.html` — the one thing no script can do for you.
- **The last read points at the script that already explains it** (255 → 106), which is
  the most duplicated section in the file: `review.py`'s docstring held all four
  paragraphs, verbatim in places, down to *if it were conditional, its presence would
  itself be the leak*. And the section was classified high-risk because its position was
  *enforced by prose alone* — it is not. `review.py:202-207` refuses once the closing
  manifest is recorded, prints the reason, and says to reopen the case instead.
- **The closing manifest keeps the part nothing else knows** (593 → 388). The
  `build_*`/`render_*` rule stood in both render scripts, the tar that cannot be covered
  by a manifest it contains in `build_bundle.py:20-23`, reopening in `render_md.py`,
  `review.py` and `VERIFY.md` §2. No script builds the manifest, so the recipe and the
  list of what it covers stayed — and so did the rule that it is computed last, when
  every hand-edited file is final, `VERIFY.md` above all. **That one is nowhere else and
  nothing checks it**, which the section now says outright instead of leaving to be
  inferred. It cost three attempts in the validation case.

`SKILL.md` 6,902 → 6,208 words, **~12.8k → ~11.6k tokens**, −9.4%. #27 estimated −1,275
words across these five rows; the truth was −694, and the shortfall is the finding:
**the file was not too long, it was restating in the third person what the files read at
that moment already said in the first.** Three of the five destinations the issue named
were wrong, and one row it called high-risk turned out to be enforced in code.

### Added

- **Four budgets** — `2. While writing` (230), `The icon` (240), `The last read` (120),
  `The closing manifest` (400) — and `4. Closing` lowered **2,300 → 1,800** in three
  steps. A relocation that does not lower a budget has not been paid for: the words
  drift straight back, which is what
  `test_a_section_of_the_skill_stays_within_its_budget` exists to stop. That region had
  been standing at 2,299 of 2,300 — one word — for as long as the budget existed.
- **`test_every_script_declares_its_licence`.** 53 source files of 63 carried the SPDX
  line and nothing held it true; `tests/fixtures/signed-pdf/sign_pdf.py` had slipped. A
  case folder is read far from this repository and keeps its own copies of the scripts,
  so the licence has to be in the file.

### Not done

**The rule that the manifest is computed last is still only prose.** It is the one point in
the method where getting it wrong means reopening a sealed case, and the only rule in these
five sections with no authority anywhere else. Saying *nothing checks this for you* is an
admission, not a fix. The fix is a gate — compare the `VERIFY.md` digest in the manifest
against the file on disk, the way `measure.py` became a gate for coverage — and it belongs
to its own issue.

`claude plugin eval`, which would test whether relocation changes what the model does,
answers `plugin eval is currently in early access`. It was never needed here: five rows out
of five turned out to be duplicates of a file or a script read at that same moment, and the
one rule that is not stayed where it was.

