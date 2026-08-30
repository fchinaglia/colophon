# Plan — a setup that finishes, and a closing that runs

*Build document, 30 August 2026. §1 is what an author does today and what it costs; §2 is
what may not move; §3 is the four changes; §4–§6 are what they do to `SKILL.md`, to the
application and to the tests; §7 is the order of work with a done-condition per step.
Carries the work of #30 as its first step and does not replace it.*

---

## 1. The problem, as it is rather than as it feels

Two facts about the current cycle, both checkable.

**Two artefacts of every case are copied by hand, by a model.** `case.json` is filled in
from `case_example.json` at the opening, `key_fingerprint` included — a fingerprint the
author never types and the model transcribes out of `author.json`. And the closing
manifest is a `record.py` invocation whose payload carries a `sha256` map with one entry
per covered file, composed in the conversation. `SKILL.md` states the rule these two
break, in *Before the first case*:

> A model retyping a fingerprint or hand-assembling something to be signed is the class of
> error this project exists to make impossible.

Neither is caught early. A wrong fingerprint is caught by `seal.sh`, which refuses at the
signature — the last step, after everything else is final. A manifest with a stale digest
is caught by the verification page failing its own check, in the reader's hands.

**What the machine needs is discovered at the moment it is needed, and those moments are
the end of a case.** `cli/colophon.py` contains no `shutil.which`: setup asks for a name
and a contact, makes the key, writes two files, and says nothing about `openssl`, `curl`,
`ots` or a browser. `render_pdf.py` exits non-zero with no Chrome — correctly, and after
the register is sealed. This is #30, and its inventory is the authority for the tiering
used below.

**And the order of the closing is remembered rather than run.** Eleven commands, in one
order, with two rules that are easy to state and easy to break: the manifest is computed
last, and after it the only permitted operation is the signature.

---

## 2. What may not move

Recorded first, because every proposal below is bounded by it.

1. **Nothing creates a key but `colophon setup`, and only after the question.** *Is this
   a machine you keep, or a session that hands the files back?* Issue #26 is that rule
   learned the expensive way. `app/close.py` states the application's half of it: it
   creates no key, never offers to, and does not name the tool that makes one — not in a
   constant, not in a comment. Anything written under this plan inherits that.
2. **The four decisions of the closing stay in conversation**: the numbers, the last read,
   the point of no return, and the qualified signature. An orchestrator that swallows one
   of them has taken a decision that belongs to the author.
3. **No gate is removed and no number is written by hand.** Both checks in `measure.py`,
   the render gate, `review.py` refusing after the manifest: a script that runs them in
   sequence must let each one refuse, not route around it.
4. **The scripts keep working with no model.** `SKILL.md`'s own reason: *this is what lets
   someone drive it from a shell — or in ten years, when no conversation survives.*
   Whatever leaves `SKILL.md` lands in a script's docstring, where the reasoning of this
   repository already lives.
5. **Standard library only, Python 3.9+, no network.**

---

## 3. The changes

### 3.1 Prerequisites reported at setup, not discovered at the seal

`colophon setup` reports what the machine has, in three tiers, and installs nothing:

- **stops everything** — `python3`;
- **stops the last step** — a browser, for `render_pdf.py`;
- **degrades, legitimately** — `ots`, and the TSA being unreachable, both of which already
  have their words at the moment they happen and a state in the technical line.

`git` is named and blocks nothing: it is how the skill stays current, and it has no part
in closing a case.

The probe already exists, written and covered by tests, in `app/prerequisites.py` — the
tool table, the `BLOCKS`/`OPTIONAL` tiering, `signing_key()`'s three-line precedence
matching `seal.sh`, and the sentences. It is not to be copied into `cli/`: see §6.1.

### 3.2 `case.json` written from `author.json`

The opening writes `case.json` from the configuration plus the two things that are the
author's — the title and `case_uid` — instead of handing the model a template with a
`key_fingerprint` field to fill in. The divergence `seal.sh` guards against then cannot be
manufactured at the opening; the guard stays, because it also catches the author who seals
with `COLOPHON_KEY` pointing elsewhere.

### 3.3 `build_manifest.py`

One script: census the folder, compute the digests, append the event.

- **census** — `covered`, `outside by design`, `stray`, from the rule already in the names:
  `build_*` is covered, `render_*` is not.
- **a stray refuses.** A file the census cannot classify is not silently excluded.
- **the event** is the manifest event `record.py` already recognises.

`app/close.py` has `census`, `outside_by_design`, `manifest_event` and `_digest` working
today. This step is a move, not an invention (§6.2).

### 3.4 A closing that runs, in two acts

```
close.py --prepare     measure → review lists → review --done → build_page
                       → build_icon → build_verify → build_manifest
        [conversation: the numbers, the last read, the point of no return]
close.py --seal        seal.sh → build_note → build_attestation → build_bundle
                       → render_pdf --attached --embed
```

Two acts and not one, because §2.2's decisions fall between them.

- **Order first, append second.** `review.py --done` appends and cannot be undone, so it is
  taken while nothing else has happened; everything after it is repairable. A case carrying
  `--done` and no manifest is a normal state and closes again cleanly.
- **Snapshot and restore.** A failure after the append restores the files the run had
  rewritten and leaves the case open, complete and re-closable.
- **Refusals are not repaired.** Each non-zero exit maps to the sentence already written in
  `SKILL.md`'s *When something stops*, and the run ends there.
- **No key is a stop, not a step.** With no key `--seal` runs nothing that could make one:
  it stops, and `build_note.py`'s `unsealed` state says so on the record.
- **Renderings stay outside the manifest**, and are produced after the seal, as now.

### 3.5 Setup: fewer questions, and a key an author can actually keep

- **Defaults, not prompts.** Name and contact proposed from `git config`, confirmed rather
  than typed. Where there is no git, the prompts of today.
- **The environment is probed before the question is asked.** `/.dockerenv`,
  `/proc/1/cgroup`, a non-persistent `HOME`, and the marker that already exists —
  `prerequisites.SWEPT`, the directory another program empties. Where the signals say
  *ephemeral*, the default inverts to **no key is made**, and the reason is said. No signal
  is conclusive, so the question stays: the signals decide the default, never the answer.
- **Backup as an operation, not a sentence.** `colophon key --backup <path>` copies the
  pair at mode 600 where the author says, and **refuses a path inside a git repository,
  inside `cases/`, or inside the skill folder** — a private key copied there travels in the
  bundle, which is #26 with the blast radius of a tar. `colophon key --passphrase` wraps
  `ssh-keygen -p` and says what it costs at sealing time.
- **One line in the README.** The two install routes documented for Claude Code both need
  git. The zip route works there identically — `colophon.zip` has `colophon/` at its root,
  so it unpacks into `~/.claude/skills/` — and is documented only under the Claude apps.

Not proposed: an X.509 certificate. The method's key is an Ed25519 pair; a self-signed
certificate would add no identity and would look like it did, which is the shape of claim
this project refuses. Identity comes from the qualified signature on the PDF.

---

## 4. What it does to `SKILL.md`

About forty-four lines out of 518, which is under nine per cent — and the distribution
matters more than the total.

| Section | Now | After | Δ |
|---|---|---|---|
| Before the first case | 63 | ~67 | **+4** — the prerequisites line #30 asks for, and the backup |
| 1. Opening | 51 | ~46 | **−5** — `case.json` is no longer a form to fill in |
| 4. Closing | 79 | ~66 | **−13** — eleven commands become two; the four decisions, 60 of those 79 lines, do not move |
| The closing manifest | 42 | ~12 | **−30** — the `sha256` example, what it covers, what it leaves out, the two rules of order: all of it becomes `build_manifest.py`'s docstring |
| When something stops | 55 | 55 | 0 — they are the sentences the author hears |
| Everything else | 206 | 206 | 0 |

The lines that go are the ones a model must *execute* correctly; the lines that stay are
judgement. This is the split #36 already describes, arriving one script at a time instead
of all at once.

---

## 5. What it does not touch

The writing. Events per exchange, versions, lexical carry-over, numbered paragraphs,
`M01`/`M02`, the annotation pass at the closing: unchanged, and the author's attention cost
is unchanged. Reopening a sealed case is #37 and is not in this plan. A live quadrant
during the conversation was considered and is deliberately out: it needs span judgements
recorded as the piece is written, which is a change to the protocol's shape, not to its
plumbing.

---

## 6. What it does to the application

`colophon-app` is a worktree of this repository on branch `app`, so everything here reaches
it by merge. Three consequences, in order of cost.

### 6.1 `prerequisites` is shared, never copied

A second copy in `cli/` would be a second answer to a normative question — *is there a key
that will sign* — and the application states the cost of a second wording plainly: *a
second wording for one condition is a second condition as far as the author can tell.*

So: the probe core and its sentences move under `skill/colophon/scripts/`, where the
application already reaches for scripts through `case.kit_module()` and where `build_icon`
already lives. What stays in `app/prerequisites.py` is the application's own — the model
probe, `find_chrome`, `scripts_dir`, `running_from`, `app.json`. This is the most expensive
item in the plan, and it is expensive only because of the application.

### 6.2 `build_manifest.py` makes the application smaller

`census`, `outside_by_design`, `manifest_event` and `_digest` leave `close.py` and come back
as an import from the kit. Less code on both sides, one answer to what a manifest covers.

### 6.3 The closing order: one implementation or two, decided before any code

The application's close route is the same order expressed as control flow. Two options,
and the choice belongs in the issue, not in a patch:

- **(a) the route delegates** to the case folder's own `close.py`, added to `ALLOWED`. The
  application already runs the case's copies of scripts; the route keeps snapshot/restore,
  the refusals in the author's words, and the wire data the screen needs.
- **(b) two implementations stand**, and each is tested against the other's order.

The repository's own rules argue for (a). It is also the larger piece of work.

### 6.4 Setup improvements arrive free, with two constraints

The application invokes `cli/colophon.py setup` and does not reimplement it, so §3.5 lands
without a line of application code. Two constraints follow from how it invokes:

- it runs `setup --batch` with `stdin` closed, so nothing added may prompt on that path;
- it passes neither `--key` nor `--force`, for reasons already written in
  `setup_handoff.py`, and new flags inherit that silence.

One visible behaviour change: where §3.5's probe declines to make a key, setup succeeds
with no key, and the launch report has to say so in its own words rather than the CLI's.

### 6.5 Blast radius on the tests

The five most exposed files hold 124 of the application's 764 tests:
`test_phase0_prerequisites.py` (54), `test_phase0_setup_handoff.py` (25),
`test_phase5_closing.py` (19), `test_phase5_key.py` (14), `test_phase5_seal.py` (12). Not
all of them move; that is where to look when one does.

---

## 7. The order of work

Ordered so that `main` and `app` are both green at every step, which is not the order the
work looks cheapest in.

| # | Step | Done when |
|---|---|---|
| 1 | `build_manifest.py` (§3.3) | The validation case closes with no digest typed anywhere; `check_manifests.py` and the verification page pass; `close.py` in the application imports the census instead of holding one |
| 2 | `case.json` from `author.json` (§3.2) | A fresh case opens with a fingerprint nobody transcribed; `seal.sh`'s guard is exercised by a test that sets `COLOPHON_KEY` elsewhere, and still refuses |
| 3 | Setup defaults and key backup (§3.5) | `--backup` refuses a repository, `cases/`, and the skill folder; `--batch` prompts for nothing; the README names the zip route for Claude Code |
| 4 | The environment probe (§3.5) | On a container the default is *no key* with the reason said, and the question is still asked; the application's launch report says the same thing in its own words |
| 5 | Prerequisites shared (§3.1, §6.1) | One probe, imported by both; #30's inventory is reported at setup; no sentence exists twice |
| 6 | `close.py --prepare` / `--seal` (§3.4) | The validation case closes in two commands; every refusal in *When something stops* is reachable and stops the run; a case with no key completes everything but the seal and says `unsealed`; §6.3 decided in the issue before the first line |

---

## 8. Verified against

`SKILL.md` (518 lines, sections as counted in §4) · `cli/colophon.py` (setup, `tidy`,
`already_unset`) · `skill/colophon/scripts/seal.sh` (key precedence, fingerprint guard) ·
`skill/colophon/scripts/case_example.json` · `skill/colophon/scripts/record.py`
(`redlist_path`) · `app/prerequisites.py` (`SWEPT`, `ORDER`/`BITES`/`BLOCKS`,
`signing_key`, `scripts_dir`) · `app/close.py` (the close route, the census, the manifest
event, the key rule) · `app/setup_handoff.py` (how setup is invoked) · `app/case.py`
(`kit_module`) · the application's test tree · issues #26, #30, #36, #37.

---

*MIT License — Copyright (c) 2026 Fabio Chinaglia. See the LICENSE file.*
