# Changelog

All notable changes to Colophon are recorded here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [semantic versioning](https://semver.org/).

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
