# Changelog

All notable changes to Colophon are recorded here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [semantic versioning](https://semver.org/).

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
