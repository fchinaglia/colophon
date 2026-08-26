# Test architecture

*Analysis document. Not part of the method — this is about keeping the method from
breaking when it changes.*

State of the repository when this was written: 56 commits, no test framework, no
`.github/`, no `conftest.py`, no `pyproject.toml`. The only automated check that exists
is `check_package.py`, which compares `colophon.zip` against `skill/colophon/`.

---

> **Status, 23 August 2026.** The deterministic surface is covered: 32 assertions in
> `tests/` on `main`, green in CI on Python 3.9 and 3.13 across Ubuntu, macOS and a Windows
> job that exists only to fail loudly on the line-ending hazard. Writing them found one
> thing this document had not: `.gitattributes` did not cover `example/`, the register
> every contributor is told to run. **The non-deterministic surface — §2's dialogue
> fixtures, the model actually following SKILL.md — is not built.** `claude plugin eval`
> was still gated when this was written, and the DIY runner described in §5 remains the
> plan.

## 1. Two surfaces, and they need different machinery

**Surface A — deterministic.** `record.py`, `measure.py`, `build_page.py`,
`build_icon.py`, `build_note.py`, `seal.sh`, plus the two repo-level scripts nobody
tests at all: `cases/build_index.py` and `paper/build_paper.py`. Pure functions over
files, Python 3.9+, standard library only. The whole `example/` pipeline runs in
**0.12 seconds**: a complete deterministic suite will stay under a second.

It catches wrong numbers, a gate that stops gating, a renderer that mangles its input,
an exit code that lies, a signature covering the wrong file. It cannot catch anything
about *when* a script is run, or whether it is run at all.

**Surface B — non-deterministic.** The model executing `SKILL.md`. Everything that
worries us lives here: opening the register at the right moment, choosing among the nine
event types, catching lexical carry-over, refusing to call a reconstructed estimate a
measurement, stopping instead of hand-writing a number when `measure.py` exits non-zero,
keeping the icon labels English in an Italian article, computing the manifest last, not
reopening a sealed case silently. None of it is reachable from Python.

Worth stating plainly: **the surface that changes most is the one with no coverage.**
Across the last twenty-five commits to `skill/`, `SKILL.md` and `reference/disclosures.md`
were touched eleven times each; `measure.py` six.

**Surface C — doc↔code consistency.** Cheap, usually forgotten, and already broken twice:

- `disclosures.md` line 184 says "`--full-root` overrides it". `build_note.py` has no
  such flag — `python3 build_note.py --full-root` exits with an argparse usage error.
  The real flag is `--short-root`, and it works the other way round.
- `disclosures.md` line 170 shows the compact technical line as
  `81 events · root ae68ae8d…88312793`. The code prints no event count — deliberately,
  CHANGELOG 1.2.0 — and prints the root in full. Real output from `cases/001` is three
  lines, no count, 64 characters.

Twenty lines of test would have caught both.

---

## 2. Simulated dialogues: yes, in one form only

**Yes — as replay of the user side against a live model, with assertions on the
artefacts on disk. Never as transcript comparison.**

The idea works here better than it does in most projects, for one structural reason:
**this skill's output is a directory, not prose.** A run produces `events.jsonl`,
`annotation.json`, `kpi.json`, `spans.json`, `icon.svg`, `verification.html`, and exit
codes. Those are machine-checkable, stable in shape, and they are exactly where the
failures the CHANGELOG records actually landed. The model's chat text is nearly
irrelevant to whether the method was followed — with three exceptions, which are the
cases for a judge.

**Transcript diffing is a trap, and specifically so here.** The model is asked to write
prose in the author's language for the note, to name events, to phrase reasons in
`explained` — "write the reason, not a placeholder". Every one of those is legitimately
variable. A diff-based suite goes red on a synonym and still does not notice the model
quietly writing `kpi.json` by hand. It inverts the signal-to-noise ratio.

### What a fixture is

User turns only, plus a seed workspace, plus assertions. **Not** expected assistant turns.

```yaml
# evals/happy-path/case.yaml
name: happy-path
tags: [closing, P0]
seed: fixtures/seed-empty/
skill: skill/colophon
turns:
  - "Open the register. I'm about to write a 1200-word post on data
     fragmentation. It goes on my site at example.com/posts/frag."
  - "Here's my draft, all mine: {{file:fixtures/draft-v1.md}}"
  - "Tighten the closing paragraph."
  - "Accept M01, reject M02."
  - "We're done. Close the case and produce everything."
assertions: assertions.yaml
```

```yaml
# evals/full-mode-happy-path/assertions.yaml
workspace:
  - exists: "cases/*/events.jsonl"
  - script_copies_present: [record.py, measure.py, build_page.py,
                            build_icon.py, build_note.py, seal.sh]
  - script_copies_identical_to: skill/colophon/scripts/     # "exactly one copy"
register:
  - chain_verifies: true
  - first_event_type: case_open
  - first_event_payload_has: [mode, capture, known_limits]
  - known_limits_count_min: 3
  - event_types_subset_of: [brief, ai_proposal, human_contribution,
      editorial_decision, constraint, version, elicitation,
      register_note, status, case_open]
  - last_event: {type: status, meta: true, payload_has: sha256}
  - manifest_covers: [annotation.json, kpi.json, spans.json, case.json,
                      icon.svg, verification.html, "*.py", "*.sh"]
  - manifest_excludes: ["*.pdf", "README.md", "index.html"]
kpi:
  - integrity: true
  - unexplained: []
  - by_phase_nonempty: true
invariants: [all]
judge:
  - "The final message reports two percentages, each stated as a percentage of
     something specific (words / ideas), and does not present one blended number."
```

### Three levels of assertion, in descending order of trust

1. **Structural** — predicates over `events.jsonl`, `kpi.json`, `annotation.json`, plus
   exit codes and file existence. Free, deterministic, and where about 85% of the value is.
2. **Invariants** — a fixed set run against *every* case, whatever the scenario. The
   chain verifies. `kpi.json` never exists with `integrity:false` or a non-empty
   `unexplained`. `icon.svg` always carries exactly the four English cell names. No file
   in the case folder was touched after the manifest event. `events.jsonl` is append-only
   *across turns* — the prefix at turn n is still a prefix at turn n+1, which is worth
   checking after every turn and not only at the end.
3. **LLM-as-judge** — three or four narrow prose claims per case. Trustworthy for "does
   this sentence declare X" over a short bounded span. **Not** trustworthy for "is this
   annotation correct" or anything that asks it to re-derive the measurement. A judge
   never decides a number: the number is in `kpi.json` and a structural assertion owns it.

Flakiness on harmless rewording falls out of the design — no assertion reads the
assistant's prose except the judge ones, and those are existence claims, not
equivalences. Run each case three times; gate judge-bearing cases at 2/3, purely
structural ones at 3/3.

---

## 3. The architecture

```
tests/
  conftest.py                  # workspace builder, script loader, fake env
  unit/
    test_record.py             # canonical(), link(), verify()
    test_measure_checks.py     # reconstruction, coverage, stale, ambiguous, empty
    test_build_icon.py         # quadrant naming, boundary warning, label language
    test_build_note.py         # forms, languages, address fallback
    test_build_page.py         # extra_notes string-vs-list, reconstructed banner
    test_seal.py               # offline, via env stubs
  golden/
    fixtures/example-min/{inputs,expected}/
    fixtures/case001/{inputs,expected}/
    test_golden.py
  docs/
    test_docs_match_code.py    # flags and sample outputs in SKILL.md / disclosures.md
  evals/                       # surface B — not in the fast suite
  lib/
    invariants.py              # shared by golden AND evals
```

### The golden fixtures, and the complication the repo already knows about

Scripts are copied into each case folder on purpose — `SKILL.md` §1, and
`cases/001/README.md` says "run the scripts **in this folder**". So running `cases/001`
as it stands tests nothing about today's skill. Running today's skill scripts over case
001's *inputs* gives:

| output | result |
|---|---|
| `kpi.json` | **byte-identical** to the committed file |
| `spans.json` | **byte-identical** |
| `icon.svg` | differs — today's `build_icon.py` adds the `HALO` stroke attributes |
| `verification.html` | differs — committed page says 77 events / root `17e58649…`, the register now holds 80 / `e9b04919…` |

**So case 001 is a valid golden fixture for `measure.py` and nothing else.** Freeze
`kpi.json` and `spans.json` as expected output; leave its `icon.svg` and
`verification.html` alone — they are historical artefacts of the case, not of the skill.

**`example/` is the better fixture and it is already in place.** `example/record.py`,
`measure.py`, `build_page.py`, `build_icon.py` and `build_note.py` are byte-identical to
`skill/colophon/scripts/` today, and regenerating all four outputs from its inputs
returns them byte-identical. Nothing in that pipeline embeds a clock: dates come from
`case.json` and `events.jsonl`, the root from the register. Only `record.py` calls
`datetime.now()`, and only when appending. **The byte-for-byte golden works with no time
faking at all.**

Add one invariant that costs nothing and stops the fixture rotting: **`example/*.py` must
equal `skill/colophon/scripts/*.py`** — the same idea as `check_package.py`, applied to
the worked example instead of the zip.

`cases/002` is unusable as a fixture: Italian schema (`misura_kpi.json`, `parole`,
`ai_lessicale`, `integrita`), which CHANGELOG 1.0.0 already declares incompatible.

### Line endings

`.gitattributes` contains exactly one line, `cases/** -text`. `git check-attr` confirms
`cases/001/events.jsonl` → `text: unset`, but **`example/events.jsonl` → `text:
unspecified`**. The example register — the one CONTRIBUTING tells every contributor to
run before opening a PR — is not protected.

Widen to `cases/** -text`, `example/** -text`, `tests/golden/** -text`, and add a test
that asserts those lines exist. `SKILL.md` says "check it is there before telling anyone
to verify"; nothing checks it.

---

## 4. Scenario catalogue

**P0** ship first, **P1** phase two, **P2** when convenient. Surface **A** deterministic,
**B** model eval.

| # | Scenario | S | What regresses in the real world | P |
|---|---|---|---|---|
| 1 | Example pipeline, four outputs byte-identical | A | Any silent change to a number, a page or the icon. Widest class, least code. | P0 |
| 2 | `measure.py` over case 001 inputs | A | The measurement drifts on a real case with 16 `explained` entries. | P0 |
| 3 | Coverage fails, no `explained` → exit 1, **nothing written** | A | The 1.1.1 regression returns: percentages printed, `kpi.json` written, downstream free to publish. | P0 |
| 4 | Coverage fails, valid `explained` → exit 0, reason reaches the page | A | Legitimate orphans become a hard block; or reasons stop reaching the reader. | P0 |
| 5 | Stale `explained` entry → exit 1 | A | "A stale one hides the next real gap." | P0 |
| 6 | Reconstruction fails (ambiguous / missing / out-of-order marker) | A | The exact 1.2.0 fix: ambiguous marker moved a boundary, text still reconstructed, run exited zero. | P0 |
| 7 | Empty or truncated source → `nothing to reconstruct`, exit 1 | A | A destroyed text reports OK. | P0 |
| 8 | `build_icon.py` / `build_page.py` on ungated `kpi.json` → exit 1 | A | A caller ignoring exit codes publishes unchecked numbers. | P0 |
| 9 | `meta:true` events excluded from the coverage denominator | A | 1.1.0: a method event demanded a declaration for something that touched no word. | P0 |
| 10 | Tampered event → `--verify` exit 1 at the right index | A | The chain stops being evidence. | P0 |
| 11 | `extra_notes` as string **and** as list | A | 537 one-character paragraphs in a published case. | P0 |
| 12 | Icon labels are the four English names, always | A | Translated labels stop pointing at LLM-DetectAIve. | P0 |
| 13 | Point within five points of a boundary → warning fires | A | The disclosure's fourth line is conditional on this warning. Case 001 sits at 4.0. | P0 |
| 14 | `seal.sh` with no key → exit 1 **and** stale `.sig` deleted | A | A signature covering a shorter register sits next to it looking fresh. | P0 |
| 15 | `seal.sh`, passphrase key, empty agent, no tty | A | The script hangs forever (fixed in 1.1.0). | P0 |
| 16 | `seal.sh`, TSA unreachable → no `.tsr`, `.sig` stands, exit 0 | A | Sealing becomes all-or-nothing, or a truncated `.tsr` is kept. | P0 |
| 17 | Every flag named in the docs exists | A | **Already broken** (`--full-root`). Users copy commands that error. | P0 |
| 18 | `.gitattributes` covers `cases/`, `example/`, `tests/golden/` | A | CRLF checkout: digests change, signature dies, `--verify` still says intact. | P0 |
| 19 | `example/*.py` == `skill/colophon/scripts/*.py` | A | The published worked example silently forks from the skill. | P0 |
| 20 | Happy path, opening to closing | B | The cycle stops being followed at all. Baseline for every other eval. | P0 |
| 21 | A piece of 300 words | B | The model under-serves: it invents an abridged path — estimates instead of a measurement — where the cycle is the same at any length. | P0 |
| 22 | Reconstructed estimate | B | The worst failure the method has: an estimate passed off as a measurement. | P0 |
| 23 | `measure.py` exits 1 mid-close | B | Model hand-writes the number, edits `events.jsonl`, or drops the check. Must lead with "the register is intact". | P0 |
| 24 | Non-English article, English icon labels | B | An Italian note with translated quadrant labels. | P0 |
| 25 | Manifest computed too early (VERIFY.md filled in after) | B | Manifest covers a file that then changed; the page fails its own check. | P1 |
| 26 | Reopening a sealed case | B | Files touched before the reopening event; old seal deleted instead of renamed `.v1.*`. | P1 |
| 27 | Underscore in the published address | B | Link cut at the first underscore → 404 under a disclosure. | P1 |
| 28 | Lexical carry-over from a comment into the user's text | B | The contamination channel no tool catches. | P1 |
| 29 | Diffuse pass over many spans | B | Twenty spans re-annotated mixed, inflating the AI share, instead of one event plus `explained`. | P1 |
| 30 | `record.py` invoked from the skill directory | A/B | **Verified bug** — see below. | P1 |
| 31 | Register declares a change id that exists nowhere (`R18b`) | A | Real, in case 001. | P1 |
| 32 | Technical line hand-typed into a rendering | A/B | Real, in case 001: `71 eventi, radice 6fa3e24f`, wrong by one event on the day it shipped. | P1 |
| 33 | `case.json` asserting what the measurement contradicts | B | Real, in case 001: "100% AI words" against a measured 46.0%. | P1 |
| 34 | `build_note.py` with no address → warning, line still prints | A | Silent loss of the route from level 2 to level 3. | P1 |
| 35 | `check_package.py` on a drifted or junk-bearing zip | A | How a `.DS_Store` shipped inside `colophon.zip`. | P1 |
| 36 | Smoke tests for `build_index.py`, `build_paper.py` | A | Two scripts with zero coverage; CONTRIBUTING admits paper↔PDF drift is uncaught. | P2 |
| 37 | `verification.html` renders headings, lists, bold | A | Structural regressions in the page a reader actually opens. | P2 |

### Scenario 30, stated separately because it is a live bug

`record.py` sets its log path relative to the script:
`LOG = dirname(abspath(__file__))/events.jsonl`. Every other script —
`measure.py`, `build_page.py`, `build_note.py` — resolves against the working directory.
A model that runs the *installed* copy of `record.py` therefore writes the event into
`~/.claude/skills/colophon/scripts/events.jsonl` instead of the case, and nothing says so.
The asymmetry should be resolved deliberately, then pinned by a test.

---

## 5. Tooling and CI

**pytest**, as the one dev dependency, declared in `requirements-dev.txt`. This does not
violate the stdlib-only rule, which is about the scripts — "the scripts must keep running
with no dependencies to install" — not about the harness.

**Running the scripts.** They are not a package and never will be. Do not import them:

```python
@pytest.fixture
def workspace(tmp_path):
    """A case folder with today's skill scripts copied in, as SKILL.md requires."""
    def build(fixture_name):
        wd = tmp_path / "case"
        shutil.copytree(FIXTURES / fixture_name / "inputs", wd)
        for s in SKILL_SCRIPTS.iterdir():
            if s.suffix in (".py", ".sh"):
                shutil.copy2(s, wd)
        return wd
    return build

def run(wd, *argv):
    return subprocess.run([sys.executable, *argv], cwd=wd,
                          capture_output=True, text=True, stdin=subprocess.DEVNULL)
```

Always `cwd=wd`, always copy the scripts in — that is both what the method requires and
the only way `record.py`'s script-relative log behaves. Always `stdin=DEVNULL`: that is
what turns the passphrase case from a hang into a clean failure.

**Faking time, keys and network — all three are already parameterised by the code.**

- **Time** — not needed for the renderers, which are byte-stable. For `record.py`, pass
  `"ts"` in the event body; `append()` only calls `now()` via `setdefault`.
- **Keys** — `COLOPHON_KEY`. A throwaway `ssh-keygen -N ""` in `tmp_path`, and one with
  `-N secret` for scenario 15.
- **TSA** — `COLOPHON_TSA=http://127.0.0.1:9/tsr` with `COLOPHON_TSA_TIMEOUT=2`. Verified:
  curl fails immediately, the `.tsr` is removed, the script continues and exits 0.
- **OpenTimestamps** — the only unparameterised network call, but `seal.sh` guards it with
  `command -v ots`, so a stub on `PATH` (or its absence) makes the script fully offline.
  Both branches are worth a test.

**GitHub Actions.** No `.github/` exists today.

```yaml
# .github/workflows/test.yml — every push and PR
- run: python -m pytest tests/unit tests/golden tests/docs -q
- run: python check_package.py
- run: cd example && python record.py --verify && python measure.py \
         && python build_icon.py && python build_page.py && python build_note.py
- run: git diff --exit-code example/     # the example must be byte-reproducible
```

Matrix on 3.9 and 3.13, `ubuntu-latest` and `macos-latest` — `seal.sh` uses `shasum`,
which is not on stock Ubuntu, and that is itself a portability finding worth a test. Add
a `windows-latest` job with `core.autocrlf=true` that only asserts `git check-attr` and
re-verifies a fixture chain: the CHANGELOG 1.2.0 hazard, mechanised.

`check_package.py` folds in unchanged. It passes today and is already written for CI.

**`claude plugin eval` — checked, and gated.** `claude plugin eval --help` (v2.1.241)
prints a full option list: `--case`, `--tag`, `--runs`, `--threshold`, `--json`,
`--ablation with-without`, `--max-cost-usd`, `--allow-tools`, `--judge-model`,
`--scaffold`. `claude plugin eval init --help` confirms the on-disk layout is
`prompt.md` + `graders/criteria.md` under `evals/`. **But invoking it returns
`plugin eval is currently in early access` and does nothing.** The shape is right; not a
single case could be run, so everything about grader YAML and multi-turn
`context.history_file` is unverified.

**So build the harness so it does not depend on that.** The stock CLI already provides
what is needed — `-p`, `--output-format stream-json`, `--session-id`, `--resume`,
`--plugin-dir`, `--permission-mode`, `--allowedTools`. A runner of roughly 150 lines that
drives one `claude -p` per turn in a temp workspace, captures the trace and then evaluates
`assertions.yaml` gives multi-turn replay today, with no gating. Keep the fixture format
close to `prompt.md` + `graders/*.md` so the turns and judge criteria port over if
`plugin eval` opens up — and keep the structural assertions in your own runner either
way, because they are free and exact.

**Tiering, because model runs are slow and paid.**

| tier | when | contents | cost |
|---|---|---|---|
| fast | every commit and PR | unit + golden + docs + `check_package.py` + example replay | free, under 5s |
| eval-smoke | nightly, and on any diff to `SKILL.md` or `reference/` | scenarios 20–24, one run each, judge on Haiku | ~$1–3 |
| eval-full | pre-release, on demand | scenarios 20–33, three runs each, with the ablation arm | ~$15–40 (estimate) |

Gate the fast tier at 100%. Gate eval-smoke at 2/3 per case, and treat a drop as a review
trigger rather than a hard block — a red eval on a prose change usually means the prose
changed, which is the information you wanted.

---

## 6. Phases

**Phase 0 — one day. The golden harness.** `conftest.py`, `tests/golden/` with the
`example` fixture (all four outputs byte-for-byte, already proven to work) and the
`case001` fixture (`kpi.json` and `spans.json` only). Widen `.gitattributes`. Add the
`example == skill scripts` invariant. The `test.yml` workflow. **This alone closes
scenarios 1, 2, 11, 18 and 19**, and it would have caught the `build_page.py`
`extra_notes` bug and the `build_icon.py` label fix.

**Phase 1 — two days. The gates.** `tests/unit/` for `measure.py` (3–7, 9, 31), the
ungated paths (8), `record.py --verify` (10, 30), `build_icon.py` (12, 13),
`build_note.py` (34), `seal.sh` offline (14–16), and `tests/docs/` (17) — which fails on
day one, and should. Every one of these is a CHANGELOG entry: each is a regression that
has already happened once.

**Phase 2 — two to three days. The eval runner and the first five dialogues.**
`runner.py`, the fixture and assertion format above, `lib/invariants.py` shared with the
golden layer, scenarios 20–24. Budget half of it for calibration: the first pass produces
assertions that are too tight, and the fix is to move a claim from prose to artefact, not
to loosen the judge.

**Phase 3 — two days. Breadth.** Scenarios 25–29, 32, 33. The nightly and pre-release
workflows with a cost ceiling. Smoke tests for `build_index.py` and `build_paper.py`.

**Seven to eight working days to full coverage. One day to the point where the most
expensive class of regression stops being possible.**

---

## 7. Decisions needed

1. **Is `colophon.zip` a build artefact or a tracked file?** It is committed, and
   `check_package.py` polices drift after the fact. If CI regenerated it, scenario 35
   disappears and the release gate becomes trivial.
2. **Are `cases/001` and `cases/002` re-verifiable in CI, or explicitly frozen?** Case
   001's committed `verification.html` is already stale against its own register — 77
   events and root `17e58649…` against 80 and `e9b04919…`. That is expected, per the
   skill's own note about renderings, but it needs to be *declared* frozen rather than
   left looking like a failure.
3. **`record.py` resolving its log relative to the script, while every other script uses
   the working directory — deliberate, or a latent bug?** Recommend CWD-relative with a
   `--log` flag. Either way the test pins whichever you choose.
4. **Which prose claims may a judge score?** Proposed: exactly three per case — declares
   reconstructed, reports two percentages each with its unit, leads a stop with the
   register-is-intact line. More than that and the suite starts failing on style.
5. **Is `claude plugin eval` early access available on any of your accounts?** With it,
   the eval layer gets a supported runner, a report and an ablation arm for free. Without
   it, the DIY runner is the plan, and the fixtures are written to survive either answer.
