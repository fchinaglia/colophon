# The writing application — functional requirements for v1

What the first version has to do, taken from the mockup and from what this repository already enforces.

**The governing rule is one sentence: nothing appears on the screen that has not passed the two checks,
and everything that can honestly move while you write is something other than a share.** Every requirement
below either serves that rule or is machinery.

Architecture is not repeated here — see issue #36 for why the shape is a local process rather than a
service, and §10 for how the source is managed.

---

## 1. Scope

One author, one case at a time, on their own machine. A local process serves the interface to the browser
and owns the case folder; the model is reached over an API; the private key never leaves. **A case opened
in the application and a case opened in a chat produce the same folder and verify with the same single
HTML file.**

| in v1 | not in v1 |
|---|---|
| Open, write, converse, annotate, measure, seal, export, reopen | Multiple concurrent cases, or a case list |
| One author, configured once | Collaboration, or more than one author on a case |
| The two-zone rail, the quadrant with the uncertainty circle | Per-phase reporting on screen — the published note still carries it |
| Ed25519 seal, RFC 3161 timestamp, optional anchor | Applying the qualified signature: the app hands off the PDF |
| Export the folder, and the tar | Publishing to an address, or any hosted service |

---

## 2. The rules that cannot be traded

**No share is ever shown before both checks pass.** No live percentage, no provisional point, no
greyed-out draft figure, no interpolation between measurements. A number on screen becomes the number
quoted, and a share computed over a partial annotation is an estimate — which is the thing the method
exists to replace.

**The register is append-only and the application never edits a row.** Every action that changes the
content appends. Corrections before the closing manifest go through `review.py`; after it, the only
permitted operation is the signature, or a declared reopening.

**The measurement is the authority; the application's index never is.** The editor keeps a derived index
of which paragraph holds which change, because a live screen cannot work without one. It is rebuilt from
the register at every start, and where it disagrees with `measure.py`, the measurement wins and the index
is wrong.

**The forbidden vocabulary never reaches the author.** *manifest, payload, span, block, seq, chain,
digest, sha256, Ed25519, route, attestation, bundle, meta, denominator, axis, lex/idea/UA*, the phase
identifiers, `case_uid`, and every file name. Block → **paragraph**, cited as `[12]`; span →
**passage**. The instrument is named at three moments only: the opening, the closing, and when something
stops.

---

## 3. The screen

Three regions: the article, editable in place; the composer under it; the rail beside it. The rail is two
zones and **the order never inverts** — what can move while you write is not a waiting room for what
cannot.

### 3.1 The article

- **Unmarked at rest.** No tint, no underline. The attribution markup is present in the DOM and invisible,
  identical to what `build_page.py` ships.
- **A margin band per paragraph, two states**: a recorded change is attached here, or nothing is. Never an
  attribution colour — that belongs to the preview.
- **A paragraph number** left of the band, right-aligned, tabular figures. It is how every other surface
  refers to a paragraph.
- **The attribution preview** — `words` / `ideas` / `no highlighting` — is off until a measurement exists,
  then applies `build_page.py`'s exact rules.
- **A proposal from the model** arrives in the flow, set in the body face, with *accept · reject · or type
  over it*. Typing over it is accept-with-edit and is the common case.
- **The acknowledgement** is one line where the proposal was: `Recorded — accepted. [8]`. Never a toast,
  never focus theft, never a number the author cannot use.

### 3.2 The composer

A field the eye finds without looking: its own ground, a label, body-size text, and a send control that
says what pressing it does. While the model works, **no spinner** — the caret becomes a slow bar. Output
streams into the proposal block, not into the field.

The red-list warning appears on that exchange's footer, names no row and quotes no match:

> Something on your list is in what I just recorded. Nothing is blocked and nothing is lost. It comes back
> before you close, and can still be changed then.

### 3.3 The rail — NOW

| tile | computed from | updates |
|---|---|---|
| Paragraphs with something recorded, *n of m*, with a per-paragraph strip | the derived index against the paragraph count | on append, on annotate |
| Changes still to place | declared changes with no passage and no reason | on append, on answer |
| words · paragraphs | the text as it stands | on edit, debounced |
| exchanges recorded · decisions you made · versions saved | event-type counts | on append |
| text changed since measuring | digest of the source against the measured one | on edit |

### 3.4 The rail — the quadrant, at the top

The quadrant leads, because with the uncertainty circle it is the most live thing on the screen. Its
geometry, its four English names and its boundary warning come from `build_icon.py` and are not redrawn by
hand.

- **Nothing settled yet → no circle at all.** Not a faint one, not a centred one: a circle in the middle
  of the cell reads as *somewhere around half*, which nobody has established.
- **While writing**: one circle whose **centre is the measured share over the settled part of the text**
  and whose **radius is what is still in play**. Earlier circles stay behind it, fading with age. Drawn
  whole — a circle cut at the frame reads as a smaller circle, and its size is the whole of what it says.
- **The lit cell follows the last circle's centre**, at a lower intensity than the measured state. Two
  intensities because they are two claims: *this is where it sits* and *this is what it is*. Only the
  measured state puts the name in bold.
- **At consolidation** the circles clear and the published point remains. A later measurement adds a
  second point beside it — that trail is of measurements, not of uncertainty.
- **No number is printed on or beside the circle** until the measurement exists.

**The radius is a bound, not an estimate.** The words whose attribution is not yet settled can at most be
all the model's or all the author's, which fixes exactly how far each axis can still travel. The circle is
therefore guaranteed to contain the final point and claims nothing beyond what is already known. The
mockup approximates this; the product must not.

---

## 4. Flows

### 4.1 Opening

Two sentences and one question, then writing starts. What the record is and that nothing in it is deleted;
then the one line about anyone who must not appear. The folder, the scripts and the case's short name are
never mentioned.

**The declared limits change and must be rewritten for this surface**: capture happens through this editor
and the conversation inside it; work done elsewhere is not seen; phrasing absorbed from discussion rather
than from a proposed edit is still caught only by explicit vigilance; and the author knows they are being
observed, which changes how people write.

### 4.2 Writing

Every substantial exchange appends one event. Accepting or rejecting a proposal appends an
`editorial_decision` carrying its change identifier. The author's own material appends a
`human_contribution`. Saving appends a `version` with its word count and digest. Housekeeping appends
nothing.

### 4.3 Answering the waiting changes

A change lands in the waiting list when the record says something happened and no passage of the text
carries it. **Two answers, and exactly one is right for each**: a paragraph holds it and the author says
which, or nothing holds it and the author says why. Choosing wrongly is refused with the reason, not
silently allowed.

The legitimate reasons, all of which `cases/001` actually used: the change deleted text that is no longer
there; a later change replaced it; it touched two words in eighty-seven and moving the attribution would
inflate the AI's share; it landed in a block the count excludes.

**Silence is the one answer not available** — an unanswered change looks exactly like an annotation that
has fallen behind, and from outside the two are identical.

Recorded reasons collapse to one line by default. Six of them open at once is the whole rail.

### 4.4 Consolidating

Available only when nothing is waiting. Runs the reconstruction and coverage checks. **On failure nothing
is written at all** — no partial file, no stale figure that reads like success — and the screen says which
check failed and what would fix it. On success the measurement lands, the preview unlocks, and the outputs
appear.

### 4.5 Sealing, and what the case then holds

Signature, timestamp, optional anchor. Then a list the author can open in place: the note and its
technical line with the root printed whole; the icon; the piece as PDF with the record embedded — **embed
first, sign second**; the tar carrying the evidence and the verifier together; the reader's page.

**Export is a folder the author picks.** Nothing is uploaded, there is no account, and the verifier
travels inside the tar rather than living at an address.

### 4.6 Reopening — two branches, and only one is ceremony

| state | what happens |
|---|---|
| **Nothing published** | A non-event. One line recorded, marked `meta` so it weighs nothing on the measurement and needs no passage. Reopen and continue. |
| **Something published** | The reason is required and the application will not proceed without it. A note out there names a root, a reader who recomputes will get a different value, and the register is the only place that can tell them what happened. |

In both: the record only grows, and **the earlier seal is kept beside the new one** — not as ceremony, but
because the timestamp cannot be obtained again for a past day and costs kilobytes to keep.

Whether something has been published is read from the configured address, never asked at the closing.

*This flow assumes the rule proposed in issue #37. If it is decided differently, this section changes with
it.*

---

## 5. Setup

Written once, per author. It is a source of defaults and never an authority: each case keeps its own copy,
and that copy is what the seal covers.

| field | notes |
|---|---|
| name, contact | the author line of every case |
| ORCID or personal page | new; not in the current `author.json` schema |
| address for the record | empty is allowed as a *declared* state, not a missing one — and it is what tells the reopening flow which branch it is in |
| signing key: path, fingerprint | **Created here, once, on a machine the author keeps.** Never at install, never silently, never in a session that ends. A key nobody knows they have is a key nobody backs up, and losing it does not break one case — it breaks the thread that makes all of them one body of work. |
| qualified signature | **Not created here and it cannot be.** It comes from a supervised trust service that identifies the author first, and that identification is the whole of what it adds. The application hands over the finished PDF and names the file to sign. |

### 5.1 Reaching the model

**An account with the model's provider is required, and there is no anonymous route.** Nor should there
be: a middleman relaying prompts on the author's behalf would put the text through a third party, which is
the one thing the trust boundary is drawn to prevent.

| route | what it needs | what it costs |
|---|---|---|
| **An API key** | a key from the provider's console, pasted once and stored with the author config at the same permissions | paid per use, works with no other software installed — the obvious default |
| **Delegate to an installed assistant CLI** | that client already installed and signed in | no key to hold or leak, and it draws on a subscription the author may already have; only works while it is signed in |

Either way the request goes from this machine to the provider and nowhere else, and either way **the text
and the conversation reach the model** — the same exposure a chat already has, stated in the case's
declared limits rather than left to be assumed.

The provider is a setting, not an assumption. v1 ships with one tested endpoint and a field, not a
hard-coded name.

**The application does not install the skill, and must not offer to.** They are two hosts for one method,
not a product and its plug-in. The judgement the model needs ships inside the application's own download
and is sent as its context. Installing the skill would mean writing into another program's configuration
on the author's behalf, for a host they may not even use, and it would suggest a dependency that does not
exist. The application may *mention* the skill in one line. That is a pointer, not an installer.

---

## 6. Acceptance

Each of these is a test, not a wish.

1. No screen state exists in which a percentage is displayed and `kpi.json` is absent or stale.
2. A failing gate writes no file, and the previous measurement is byte-identical afterwards.
3. No author-facing string contains a word from the forbidden list. `tests/repo/test_vocabulary.py` is
   extended to cover the application's strings the way it covers `review.py`'s.
4. A case produced by the application and one produced in a chat, from the same events, yield identical
   `kpi.json`, `spans.json` and root.
5. The derived index is discarded and rebuilt from the register on start, and the rebuild is compared
   against the discarded copy in a test.
6. Editing after the closing manifest is refused, not warned about.
7. The drift indicator has no dismiss control anywhere in the markup.
8. Sealing with no key refuses and does not offer to make one.
9. Reopening an unpublished case requires no reason; reopening a published one cannot proceed without.
10. Every uncertainty circle contains the point the eventual measurement produces, checked over recorded
    sessions.
11. No case file is ever created under the plugin cache, whatever directory the application was started
    from.
12. The application refuses to open a case when no model is configured, and says so at launch rather than
    at the first exchange.
13. The application renders no verdict of its own on a case: the only *valid* a user sees comes from the
    verifier that travelled inside the bundle.
14. No sentence appears in both `SKILL.md` and the application's prompt.
15. The application installs nothing outside its own folder and the author config, and creates no key
    except at setup, on this machine, with the author watching.

---

## 7. Opening someone else's case

The application should be able to open any case and check it — and it should do that by **launching the
verifier that ships inside the bundle, not by becoming one.**

**Why it must not be its own verifier.** The verifier's value is that it needs nothing: one self-contained
HTML file, offline, no assistant, no application, no account. A reader asked to install something in order
to check a claim has been asked for more than the method promises. And a producer that also judges is a
circle — if one program both writes the record and rules on it, a bug consistent across the two is
invisible from inside. Today that separation is free, and
`test_every_maintained_verifier_matches_the_built_one` already holds every copy byte-identical.

**A verdict rendered by the author's tool is weaker evidence than the same verdict in a file the reader
opened.** The application never draws its own *valid*: it shows the verifier's, or it shows nothing.

| flow | what happens |
|---|---|
| **Open a case** — a folder or a tar, anyone's | The application extracts it, opens **the verifier that came inside that bundle** with the case loaded, and stays out of the result. |
| **Check the copy you are about to send** | The one the author actually needs, and `SKILL.md` already asks for it: verify the packed file rather than the folder on disk, because they can differ and only one of them travels. |
| **Read a case for its content** | Open the reader's page from the bundle. Reading is not verifying, and the two views should not be blended. |

**Two layers, never blurred.** Verification answers arithmetic — the chain holds, the digests match, the
signature is over these bytes — entirely offline. It does not answer *whose key that is*, which needs a
trusted list and a revocation service, or a qualified signature naming a person.

This feature adds no verification code at all: a file picker, an extractor, and a browser tab.

---

## 8. Finding it, installing it, starting it

The install is the launch. Standard library only means there is nothing to resolve. What replaces
installation is **a first launch that tells the author what this machine can and cannot do, before a case
exists rather than after one is sealed.**

### 8.1 Three routes, ordered by who is walking in

**Most of the people this method is for do not know what git is**, and a route that starts with *clone the
repository* loses them at the first word. The primary route has to be a download.

| route | what they do | who it is for |
|---|---|---|
| **A zip, from the site** | Download, unzip into a folder they choose, double-click the launcher. No git, no terminal, no package step. The zip carries the application, the scripts it calls, the references and the verifier — a few hundred kilobytes, because there are no dependencies to bundle. | **The default.** A writer. |
| Clone the repository | The same folder, kept current with a pull. | Someone who already works this way. |
| Already has the skill → ask for it | The skill's scripts run from the plugin's copy, so they compute the path from their own location and start the application. Nobody types a path. | A convenience, never the documented route. |

**The plugin's copy is a cache, not an installation.** Installing the skill does put the whole repository
on disk, under `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`, one directory per version.
That is not a place and must never be published as one: nobody finds it, the path changes with every
update, and it is an implementation detail of another program.

**Worse, and this is the requirement: that directory is swept.** A case folder created inside it can be
deleted because an old plugin version was cleaned up — the silent loss of sealed evidence, for a reason
the author could never guess. **No case data is ever written inside the plugin cache.** Started that way,
the first thing the application does is say where it is running from and ask which folder of the author's
own the cases belong in.

### 8.2 The friction that is left, named rather than glossed

- **A launcher downloaded from the internet is blocked on first run** — Gatekeeper on macOS, SmartScreen
  on Windows. The workaround is one line of instruction on the site, and it is genuinely ugly: the
  author's first contact with a tool about trustworthiness is their operating system warning them about
  it. This is the real cost of not packaging, and it should be measured with actual authors rather than
  argued about. **If it is what stops them, the signed and notarised application is not "later" — it is
  the price of the audience.**
- **Python on Windows.** Present on macOS and Linux, frequently absent there. The launcher detects it and
  points at where to get it instead of failing with a shell error.
- **No version check, and nothing phones home.** The application shows which version it is; the site says
  which is current. `cli/colophon.py` already refuses to open a network connection, for a reason paid for
  once — a down address used to stop an author before they had written a word — and the same restraint
  applies here. Updating is downloading the zip again, or a pull.

### 8.3 The prerequisite check, at launch

Nothing in the method checks the machine today, and the two moments that need something are the last two:
the seal and the rendering. An author discovers there is no browser *after* the register is sealed — past
the point where a case can be quietly redone. **The application's first launch is where this is fixed,
because it is the one moment that happens before anything is at stake.** This is issue #30's resolution,
and the inventory below is its table, verified rather than assumed.

| tool | needed for | when it bites | what the application says |
|---|---|---|---|
| `python3` 3.9+ | everything | now | Refuses to start and names the version it found. On a clean Mac the first `python3` triggers the Command Line Tools prompt — say so rather than showing a shell error. |
| **a model** | every exchange — **the only prerequisite without which nothing works at all** | at setup | An API key, or an assistant CLI installed and signed in. Checked before the first case: discovering it at the first exchange means discovering it after the register is already open. |
| `ssh-keygen` | the key and the signature | at sealing | Present on macOS and Linux, and new enough for `-Y sign`. |
| `openssl` · `curl` · `shasum` | the timestamp | at sealing | Present on macOS and Linux. The system `openssl` is enough — no Homebrew build is required, which is worth stating because people assume otherwise. |
| `ots` | the Bitcoin anchor | at sealing, optional | **Usually absent.** The anchor is redundant by design, so its absence is reported and never blocks: one line, with the install command, and the case proceeds. |
| Chrome or Chromium | the PDF | at rendering — **the one that actually bites** | Absent on most clean machines. Reported **at launch**, with what it costs: the page and the record are complete without it, only the PDF is not. |
| `git` | the repository route, and the line-ending attribute | at setup | Present where the author cloned anything. |

**Report, do not repair.** The check names what is missing, what it will cost at which step, and the
command that fixes it. It installs nothing on its own, and it never offers to make the signing key as a
convenience — a key made where it must not live is issue #26, and a check that helpfully creates one would
reintroduce it wearing a friendlier face.

**And it never blocks on what is optional.** The posture is *no silent gaps*, not *no gaps*: an author who
knows the anchor will be missing and proceeds anyway has made a decision, which is the point.

### 8.4 First launch is setup

**It reuses `cli/colophon.py setup` rather than reimplementing it.** That command already writes
`~/.config/colophon/author.json` at mode 600, asks for a name and a contact, and makes the Ed25519 key —
and it opens no network connection, deliberately.

What the application adds is the two fields above — ORCID or page, and the address, which may be empty as
a declared state — and the prerequisite report. Nothing else. The key is created here, once, on a machine
the author keeps, and the author is told where it lives and to keep a copy.

### 8.5 Updating

For anyone who came through the plugin, the command that refreshes the local clone refreshes the
application with it: one update path for both. For a plain clone it is a pull. There is no updater and no
version check against a server.

### 8.6 The whole sequence, for a new author

1. Download the zip from the site and unzip it wherever they keep their work.
2. Launch it once. It reports what this machine can do, asks who they are, and makes the key, saying where
   it lives and to back it up.
3. Open a case and write.
4. Consolidate, seal, and take the folder wherever they want.

**No account at any point beyond the model's, no service to keep alive, no address that has to stay
reachable.** It is the property that makes the verifier a single file, and the installation should not be
the step where the method takes on its first dependency.

---

## 9. Where the judgement lives

The application takes over the orchestration — when to run what, the order, the mechanics — because that
becomes control flow. It cannot take over the judgement, and the judgement is most of what the method is:
the attribution rules and their edge cases, the disclosure texts and the research behind them, what the
author hears and in which three moments, and what is said when something stops.

**One correction worth carrying into the build.** It is tempting to say the application leaves a shorter
`SKILL.md` behind. It does not. A host where the model executes still needs the whole cycle, so nothing
comes out of that file on the application's account. What is a fraction of it is *the application's own
prompt*. This is not a reduction of what exists; it is a second, much smaller entry point beside it.

### 9.1 Not two skills

Two files sharing most of their content diverge, and prose drift is invisible to a byte comparison — two
sentences can part in meaning while both stay plausible. This repository has paid for that failure three
times already in code, where a check could catch it. In prose nothing would.

```
skill/colophon/
├── SKILL.md          the cycle, for a host where the model executes
└── reference/        judgement — shared verbatim, never copied
                      protocol.md · disclosures.md · people.md
app/
└── prompt/ROLE.md    what the model answers for when the app executes:
                      annotate, speak to the author, judge attribution.
                      Names no script. Points at the same references.
```

**The reference files never mention who executes**, which is exactly why they are the shared half. Only
the cycle is host-specific, and the application's file is not a variant of it but a different and much
shorter document.

### 9.2 What keeps the two entry points small

**Every rule that a script can enforce is written where it is enforced**, and then neither host has to
remember it. When `record.py` stopped accepting non-integer numbers, the argument left the prose. When
`measure.py` stopped writing anything on a failed check, the same. Each migration shortens *both* entry
points at once, and it is the only reduction that costs nothing in ambiguity.

One mechanical grip is worth adding beside it: **a test that fails when a sentence appears in both entry
points.** `test_vocabulary.py` already works this way on prose — that a string is present, that it is
absent, that there is not too much of it. *That it is not there twice* is the same family, and the only
automatic defence against prose drifting from prose.

---

## 10. Source management

**One repository, a new top-level directory, and no second copy of anything.** This project's recurring
failure is drift between copies — the worked example against the skill, the package against the folder,
the website's vendored clone against three releases — and each time the answer was a check that fails
loudly. A separate repository for the application would create a fourth copy of the scripts with no check
at all, and it would go stale the same way, silently.

```
colophon/
├── skill/colophon/        the method: scripts, references, the verifier
├── app/                   NEW — the local process and the interface
│   ├── CHANGELOG.md       its own, so the method's version stays the method's
│   └── tests/
├── cases/  example/  paper/  spec/  verifier/
└── CHANGELOG.md           the method's, unchanged
```

**The application calls the scripts; it does not copy them.** No reimplementation of the chain, in any
language, without a conformance suite against `spec/canonical.md` — two implementations without one is two
sources of truth, and on the day they disagree nobody can say which is right.

### Branching

**Trunk, in small commits, from the first day.** A long-lived branch for a change this size is a trap: the
scripts underneath it keep moving, and the merge arrives when nobody remembers why. The application is
additive — nothing existing changes behaviour because `app/` exists — so it can land unreleased and
unadvertised while it is built.

The exception is any change to the shared scripts that the application needs. Those are the method's, they
ship to every skill user, and they go through the normal path: their own commit, their own reason in the
changelog, the tests green before the application depends on them.

### Two release trains, one repository

| | tag | changelog | bumped when |
|---|---|---|---|
| **the method** | `v3.7.0` | root | `skill/` changes — and only then, so the plugin never announces an update that reaches nobody |
| **the application** | `app-v0.1.0` | `app/` | the application changes |

This keeps `check_manifests.py` intact — it ties the plugin's version to the newest released heading of the
root changelog — and it stops an app-only fix from telling every skill user to update.

### Before the first commit under `app/`

- **CI covers it** in the same run: the app's tests beside the method's, on the same Python versions and
  both operating systems.
- **Standard library only**, as everywhere else here.
- **Line endings**: any fixture whose bytes are digested is pinned in `.gitattributes` before it is
  committed, not after. A checkout that rewrites them makes the first check pass and the signature fail,
  which reads as forgery.
- **The package check keeps its scope**: `colophon.zip` is the skill folder and nothing else. The
  application is installed from the repository or its own zip, never from the plugin.

**Where the drift will actually happen is not in the code — it is in the prose.** The application will
encode the cycle in control flow while `SKILL.md` keeps describing it in sentences, and the two will part
silently. The answer is §9.2.

---

## 11. Open questions, and where they live

Four of these are issues rather than decisions taken here, and this document depends on how they land.

| issue | what it settles for this build |
|---|---|
| **#30** — prerequisites discovered when they fail | §8.3 is its resolution: the check moves to the one moment that happens before anything is at stake. Its inventory, verified rather than assumed, is the table. |
| **#33** — the render gate checks only the source | The application calls the same renderers, so it inherits the fault: a covered file that is missing fails wherever it happens to be opened, rather than being named. |
| **#36** — the skill splits rather than retires | §9 is the shape that issue leaves open: one entry point per host, references shared verbatim, no second copy. |
| **#37** — reopening costs the same published or not | §4.6 assumes the rule proposed there. If it is decided differently, that flow changes with it. |

---

*MIT License — Copyright (c) 2026 Fabio Chinaglia. See the LICENSE file.*
