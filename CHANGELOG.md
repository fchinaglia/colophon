# Changelog

All notable changes to Colophon are recorded here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [semantic versioning](https://semver.org/).

## [1.5.0] — 2026-08-23

Two deliverables now live in this repository and they are versioned separately.
`v1.5.0` is the skill; the prototype is tagged `server/v0.1.0` and marked pre-release,
which is both accurate and what keeps the skill the one GitHub calls *latest*.

### Added — the specification

- **`spec/canonical.md`**, with 31 conformance vectors and a checker. The chain hashes
  bytes while an event is an object, so the mapping between them is part of the format,
  and a second implementation now needs it written down: `record.py --verify`
  re-serializes with the same function it wrote with, so it agrees with itself whatever
  that function does.
- The rule turned out not to be a choice. `cases/001` carries **72 non-integer numbers
  across 18 of its 80 events**, and after a JavaScript `JSON.parse` `94.0` and `94` are
  the same value. RFC 8785 formats `94.0` as `94` too, so **JCS is not backward
  compatible with the registers this project has already sealed.** The format forbids
  what JavaScript cannot hold, and the verifier refuses what came before rather than
  guessing at it.
- **`case_uid` in `case.json`.** Where a case is deposited, its address derives from it,
  so it must exist before the manifest — which covers `case.json`. An address derived
  from the register's root could not: the root is the hash of the manifest event.

### Added — tests

- **32 assertions and CI**, on Python 3.9 and 3.13 across Ubuntu and macOS, plus a
  Windows job whose only purpose is to fail loudly on the line-ending hazard, on the
  platform that causes it. Every unit test is an entry in this file — a regression that
  has already happened once.
- Writing them found something this file had not recorded: **`.gitattributes` did not
  cover `example/`**, the register every contributor is told to run before opening a PR.

## [Unreleased]

### Added

- **A test suite, and CI.** 32 assertions in about a second, in three layers. The golden
  layer earns the most for the least code: `example/` regenerates its four outputs byte
  for byte, and nothing in that pipeline reads a clock, so the comparison needs no time
  faking at all. The unit layer is the gates, and **every test there is an entry in this
  file** — a regression that has already happened once. The repository layer guards the
  silent ones: the worked example forking from the skill, a documented flag that exits
  with an argparse error, a missing `.gitattributes` line that turns a Windows checkout
  into a false accusation of forgery.
- **`.gitattributes` covers `example/` and `tests/` as well as `cases/`.** The example
  register — the one CONTRIBUTING tells every contributor to run before opening a PR —
  was not protected, and a test now asserts that all three are.
- CI runs on Python 3.9 and 3.13, on Ubuntu and macOS, plus a Windows job whose only
  purpose is to fail loudly on the line-ending hazard, on the platform that causes it.

### Fixed

All three were found the same way, and that is the part worth keeping: a full run of
the method on a real article, in a session that did nothing but follow `SKILL.md`. The
case came out sound in every respect the register can check — chain intact, `unexplained`
empty, fifteen manifest digests, a signature that verifies against the key published on
the author's domain — and the one thing it asks a reader to do, a reader could not do.
None of the three is visible from inside the repository, because everything in the
repository passes.

- **`build_page.py` writes `index.html`.** That a published address must end at the
  folder has been a rule since the underscore hazard was written down — link detectors
  cut at the first underscore, so `…/pagina_di_verifica.html` arrives as `…/pagina` — and
  the script that makes the page did not honour it: it wrote `verification.html`. A case
  deposited exactly as the method describes therefore answered **404 at the address its
  own note prints**. Measured on a real deposit: `events.jsonl`, `bundle.tar`, the page
  and `kpi.json` all 200, the folder 404. Nothing writes the old name now; keeping both
  would mean two manifest-covered files with identical content, which is a way for two
  things to drift apart. `cases/001` and `cases/002` keep theirs — they are sealed, their
  manifests cover that name, and they carry their own copies of the scripts, which is
  what those copies are for.
- **The cycle has a publication step.** §4 ended at `build_note.py`, so a model following
  the skill stopped where the instructions stop, and the address written into `case.json`
  at the opening — linked by the page, printed in the technical line, frozen by the
  manifest — was never deposited anywhere. Nothing in any of those artefacts said *and
  this has not been published yet*, which is the failure `reference/disclosures.md`
  already names arriving from a direction nobody guarded. The step covers the deposit
  through `cli/colophon.py` and, critically, the check that the address answers: `seal.sh`
  already writes `events.jsonl.sha256`, so fetching the register from the published
  address and comparing the digests is the whole check, and it runs before the author is
  told the case is done. With two rules — an address that has not been published is not
  done, and a deferred publication is recorded rather than left reading as live, before
  the manifest if it is known then and as a reopening if it is not.
- **The breakdown by phase carries both axes, and each one says which it is.** It was
  computed on the lexical axis alone and stored under the key `"ai"`, which names no axis
  at all — in a file that already distinguished `ai_lexical` from `ai_ideational` at the
  top level, and beneath a method whose central claim is that one number is not enough.
  `reference/disclosures.md` prescribes a sentence that publishes that figure — *the
  first draft is K% mine* — and lists the breakdown among the four things that are not
  optional. There was exactly one place to take K from, and it answered a different
  question from the one the sentence asks. In `cases/001` the first draft is **entirely
  the model's words and two thirds the author's ideas**: filled in from what the tool
  printed, the note would have told the reader the first draft was 0% the author's. The
  number was right and its label lied by omission, which is the one failure a check
  cannot see — reconstruction and coverage both passed, as they were bound to.
  What caught it was the author reading the table: *"mi sembra che il first draft fosse
  in gran parte mio, o sbaglio?"*, recorded verbatim as event 36 of that register. A
  method that asks a reader to trust a number it publishes cannot rely on the author
  happening to know better. `kpi.json` now carries `ai_lexical` and `ai_ideational` per
  phase, the names it already used above; the ambiguous key is gone rather than kept as
  an alias, because leaving it alive leaves the wrong way to read the file alive.
  `measure.py` prints a column for each, the verification page shows both beside every
  phase bar, and the prescribed sentence became *in the first draft the ideas are K% mine
  and the words J%* — in both languages. The golden test on the validation case now
  compares the measured values instead of the bytes of `kpi.json`: a key that moves no
  number is not drift, the assertion it was making failed on any extension of the schema
  and would have passed a value that changed representation while staying equal, and
  `cases/001` stays sealed and untouched, as its own copies of the scripts exist for.

## [1.4.0] — 2026-08-23

### Added

- **The key gets an address outside the case.** `case.json` carries `key_url` and
  `key_fingerprint`; `SKILL.md` says to publish the key on a domain you control, at
  `/.well-known/colophon/keys`, and not inside the folder it authenticates. A key
  published inside its own case proves only that the folder is internally consistent —
  which anyone can arrange in ten seconds by generating a key, altering the register,
  re-signing, and dropping in the new `.pub`. Every check then passes.
- **`VERIFY.md` §2 is a fetch-and-verify recipe**, and it uses `-Overify-time` with the
  sealing date rather than today's. The published file is a key *history*: asking whether
  a key was valid **when the timestamp says the signature existed** is a stronger question
  than whether it is valid now, and it is what makes a future rotation harmless instead of
  retroactively breaking every seal. The in-folder copy of the key stays, described for
  what it is — for reproduction, not for trust.

### Notes

The distinction the section now makes explicit: this is an **anchor, not a proof**. It
moves the question from "is this folder internally consistent", which anyone can arrange,
to "who controls that domain", which they cannot. No file can do more than that, and the
method has always said so about its other claims.

`cases/001` records the change in its errata: its key is published at
colophonmethod.com, and both of its seals verify against it.

## [1.3.0] — 2026-08-23

### Added

- **`record.py` refuses an event it cannot let a second implementation check.** No floats,
  integers within ±(2**53 − 1), ASCII keys — enforced at `append()`, refusing rather than
  warning. A reader outside Python cannot reproduce these bytes: after a JavaScript
  `JSON.parse`, `94.0` and `94` are the same value, and the distinction is destroyed by
  parsing rather than recoverable afterwards; past 2**53 JavaScript loses precision
  silently and returns a different number without saying so. None of it is repairable
  after the fact — the register is append-only and reopening a case adds events rather
  than rewriting them — so the check has to be at the door. The values that provoked it
  are descriptive payload; nothing reads them as numbers and the measurement of record is
  `kpi.json`, so writing them as strings loses nothing.
- **`.nojekyll`**, because GitHub Pages runs Jekyll by default and will not serve
  dot-directories. Without it any `.well-known/` path 404s, which is a failure nobody
  diagnoses from the symptom. **And `index.html` alongside it**, because turning Jekyll
  off also stops it rendering `README.md` as the site's front page: the fix for one
  absence opened another, and the landing page is now an artefact rather than a
  side effect of a Markdown renderer.
- **SKILL.md says how a number goes into a payload**, in §2: integers, or quoted. The
  guard below refuses anything else, and a rule enforced by a script but absent from the
  instructions is a rule the model discovers by failing.

### Fixed

- **The published timestamp could not be verified by anyone.** `seal.sh` defaulted to
  `freetsa.org`, whose tokens chain to nothing a reader already has: measured,
  `openssl ts -verify` against the system certificate bundle answers
  `Verification: FAILED`. The default is now `timestamp.digicert.com`, which answers
  `Verification: OK` with no setup, at the same cost, in the same format, and accepts the
  SHA-512 query the script already sends. `VERIFY.md` carried `-CAfile [TSA-cacert].pem`,
  a placeholder that was never resolved and that no reader could fill in; it now names the
  system bundle, and says what to do when the authority sits outside it. Neither authority
  carries an eIDAS presumption — that still needs a qualified TSA.
- **`seal.sh` promised an anchor it cannot deliver.** It printed
  `confirmed on Bitcoin within a few hours`. OpenTimestamps calendars batch submissions
  and have been observed to accept one and never anchor it, silently; a `.ots` file on its
  own therefore proves nothing. It now says *submitted — NOT yet anchored* and tells the
  author to run `ots upgrade` and `ots verify` before publishing anything that claims an
  anchor. `VERIFY.md` said the Bitcoin seal *requires trusting no authority at all*: it
  requires a node or a block explorer you decide to believe, which depends on no
  *authority* but is not the same as depending on nothing.
- **`disclosures.md` documented a flag that does not exist.** `--full-root` exits with an
  argparse error; the real flag is `--short-root` and it works the other way round, since
  both forms print the root whole by default. The sample compact line also showed an event
  count the code deliberately stopped printing in 1.2.0, and an abbreviated root the code
  does not abbreviate. All three read as instructions and none of them worked.

## [1.2.0] — 2026-08-23

### Added

- **The closing manifest is part of the method**, in SKILL.md: the last event of a case
  carries the SHA-256 of every file the measurement depends on and every script a reader
  runs, because `seal.sh` signs the register and nothing else — a signed register that
  does not commit the text it describes proves less than it appears to. With it, what
  the manifest deliberately leaves out (the renderings and the prose), the rule that it
  is computed last when every hand-edited file is final, and the rule that the only
  operation after it is the signature. Both were learned by reopening a sealed case
  twice in one day and had never been written down.
- **Line endings.** `cases/** -text` in `.gitattributes` before publishing, and why: a
  checkout with `core.autocrlf=true` changes every digest and the signature stops
  verifying, while `record.py --verify` still says `chain intact` — so the first check
  passes, the second fails, and an honest reader concludes the signature is forged.

### Fixed

- **A span marker that is ambiguous, missing or out of order now fails the run.** It was
  detected and reported, and the run carried on to print `reconstruction: OK` and exit
  zero — which is precisely the shape of the danger: an ambiguous marker moves a span
  boundary onto the wrong occurrence and the text still reconstructs, so the report was
  the only signal and nothing acted on it. Found by testing issue #2 against the current
  code rather than assuming it had been closed.

### Changed

- **The disclosure block is short by default, everywhere, PDFs included.** Five lines
  instead of a paragraph — what it is, how much, what the gap means, how firm the
  classification is, who answers for it — in that order, because the order is the
  argument. Two of the five are conditional: the gap sentence drops when the two
  percentages are close, and the boundary warning appears only when `build_icon.py`
  reports the point within five points of an edge. One treatment for all of them: same
  face, same size, same colour, only the percentages in bold. Nothing is coloured to
  stand out — a block that raises its voice at the foot of an article puts the reader on
  the defensive at the moment the method is trying to do the opposite.
- **The technical line is three short lines by default**: whether the register is
  signed, where it lives, and the root — in that order, each more specific than the one
  above it. The event count is gone: the page at the address carries it, and dropping it
  gives the root the room to sit on a single line instead of wrapping. The word `root`
  stays, because without it the last line is an unidentified string. `--form full`
  restores the sentence that names each seal, for a printed sheet or an archive copy
  where nobody will follow a link, and `--short-root` abbreviates the hash for a card or
  a slide.
- The paragraph note stays as **the full form**, for a page with room to explain itself:
  it is the only one that carries the breakdown by phase in words. And an **essential
  form** is documented for a card or a slide, with the warning that it drops the line
  about responsibility, which is the one that only exists if it is said.

This is the detail-on-demand shape the research the method cites asks for: two thirds of
readers want the detail, and among those who prefer one line most want it a click away.
Now they get the numbers where they are and the rest at an address written for them.

## [1.1.1] — 2026-08-23

### Fixed

- **The coverage gate could be walked past.** `measure.py` exited non-zero, and then
  printed the percentages anyway, wrote `kpi.json` and `spans.json` anyway, and left
  `build_icon.py` and `build_page.py` free to publish from them. The failure sat eight
  lines above a table that reads like success, and an exit status is a signal only for
  whoever thinks to look at one. A failing run now writes nothing, and closes with the
  reason instead of the numbers. `build_icon.py` and `build_page.py` refuse a `kpi.json`
  that reports undeclared changes or a failed reconstruction, so a caller that ignores
  exit codes is stopped too.
- **The stop said nothing to the person who wrote the text.** Every line of it was
  addressed to whoever annotates — spans, declarations, a JSON file the author has never
  opened — and none of it said the thing that matters to them: the register is intact,
  nothing recorded is lost, and this is the closing step being repeated, not the work.
  That line is now printed, and SKILL.md says to lead with it, along with the order in
  which to fix the rest and the one question worth asking the user.

## [1.1.0] — 2026-08-23

A day of using the method on its own cases, which is where all of this came from.

### Changed

- **`measure.py` now stops.** A change the register declares and no span carries has to
  be named, in an `explained` map inside `annotation.json`, with the reason — and the
  reason is published on the verification page beside the change it explains. Without
  one the script exits non-zero and nothing downstream runs. This is the rule SKILL.md,
  the protocol and the paper have always stated; until now only the documents enforced
  it. **A case that measured yesterday can fail today**: that is the point, and it is
  the one change to read before upgrading.
- **The technical line prints the whole root**, all sixty-four characters. An
  abbreviation can be recognised but not compared, and comparing is the reader's job.
  `--short-root` restores the old form for a social card or a slide.
- **And it carries an address.** `verification_url` in `case.json`, falling back to
  `register_url`: a line naming `VERIFY.md` helps only a reader already standing in the
  case folder. The page must be served where HTML renders, and at an address with no
  underscore — link detectors cut at the first one.
- **The disclosure is counted in three levels everywhere.** Marker, note, record — by
  reader, not by text. The paper said three in §5.1 and two in §8; the skill had copied
  the second. The technical line is now named as what it is: the route from the note to
  the record.
- **A manifest covers what the measurement depends on, not the renderings.** A rendering
  is derivable from what is covered, and freezing one means reopening a sealed case
  whenever it has to be made again.

### Added

- The disclosure texts in Italian — marker, note, and both variants — in the wording
  published with case 002 rather than a translation made for the document.
- `explained` in `annotation.json`; `explained` and `unexplained` in `kpi.json`.
- The verification page shows the coverage result and links the register.
- `register_url` and `verification_url` in `case.json`; `--url` and `--short-root` on
  `build_note.py`.
- `check_package.py` refuses a package carrying junk, and prints a rebuild command that
  excludes it — which is how a `.DS_Store` had been shipping inside `colophon.zip`.
- The quadrant labels are stated to stay English in every language, with the reason:
  three of the four are the classes of a published taxonomy.

### Fixed

- **`build_page.py` rendered the closing note as one paragraph per character** — 537 of
  them in a published case — because `extra_notes` is a string in every case file and
  the code iterated it as a list.
- `build_icon.py` drew the point on top of the cell label whenever a text landed in the
  lower half of its cell. The label now moves; the point never does.
- `seal.sh` could leave a signature covering an older register, hang on a passphrase
  prompt with no terminal to answer it, and wait forever on the timestamp authority.
  All three found by sealing a real case.
- `measure.py` counted `meta` events as changes to the text and demanded a declaration
  for something that never touched a word.
- The paper is re-rendered from its source, with `build_paper.py` and the intermediate
  HTML committed beside it: the first PDF was printed from an HTML that was never kept,
  and could not be reproduced by anyone, including its author.

### Cases

- **002** is complete: the annotation, the measurement, the verification page and the
  history were missing from the repository, so none of the numbers it quotes could be
  recomputed. All five artefacts the signed manifest covers now match.
- **001** was reopened twice, repaired and re-sealed, with every step recorded before it
  was taken. Its README says what was wrong with it. The seal of 22 August is kept
  alongside the new one and still verifies against the register as it stood then.

## [1.0.0] — 2026-08

First public release.

### Added
- The skill, in two modes: light (register only) and full (register, annotation,
  measurement, verification page, icon, seal).
- `record.py` — append-only register with a hash chain, `--verify` and `--root`.
- `measure.py` — annotation to spans to two axes, with the reconstruction and
  coverage checks.
- `build_page.py` — a self-contained verification page, light and dark.
- `build_icon.py` — the quadrant icon, generated from the measurement file, with
  a warning when the classification sits within five points of a boundary.
- `seal.sh` — detached Ed25519 signature, RFC 3161 timestamp, OpenTimestamps anchor.
- `reference/protocol.md`, `reference/disclosures.md`, `reference/VERIFY.md`.
- The method paper, twelve pages, with the evidence base.
- A worked example that runs end to end.

### Notes
- Split out of the original research repository, which stays in Italian.
  Identifiers, file names and event types were renamed to English in the process:
  a case folder produced before this release will not be read by these scripts.
  Case folders carry their own copies of the scripts, so old cases keep working
  with the versions they were made with.
- The method has been validated on one case, by one annotator who was a party to
  the writing. Inter-rater validation is the obligatory next step.
