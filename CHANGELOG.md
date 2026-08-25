# Changelog

All notable changes to Colophon are recorded here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [semantic versioning](https://semver.org/).

## [Unreleased]

## [3.3.0] — 2026-08-25

A signing key is made in one place and only on a machine the author keeps — the rule that
closes #26, where an environment the author was not sitting at turned `seal.sh`'s advice
into the instruction that leaked the key. Alongside it the repository becomes installable
in one command, stops being a website, and the served build looks like the site rather than
nearly like it. Nothing that travels in a case is touched: `verify.html` is still
`2e8a461a…` and the four copies do not move.

### Security

- **A signing key is made in one place, and only on a machine the author keeps.** Closes
  #26. `seal.sh` printed `no key at … — generate one with: ssh-keygen …` unconditionally.
  Run inside a folder-scoped VM whose files are handed back at the end of the session, that
  line is not advice but an instruction: the key was generated in the sandbox and returned
  to the author among the downloads, having already travelled by the time they held it. The
  bundle was never at fault — `build_bundle.py` has an allowlist and takes only
  `colophon.pub`. The key did not leave the package, it left the sandbox.

  **And it did not fail loudly**, which is the worse half. It produced `.sig`, `.tsr` and a
  verification page reading `VALID` over a signature that means nothing. The key is the only
  thing binding an author's cases together over time, so whoever holds a copy can sign a
  colophon that appears to come from the same hand as every genuine one — the forgery the
  method exists to prevent. And the plugin manifests promise, in the description a reader
  sees before installing, an Ed25519 key that stays on your machine. Nothing enforced it.

  **The rule does not try to detect the environment.** Nothing detects it reliably, and a
  guard that fails silently exactly where it is needed is worse than none. It constrains
  where a key may be created instead — in the setup conversation, on a machine the author
  keeps, and nowhere else. `SKILL.md` gains the question that separates the two cases at
  setup, put as *is this machine yours, or a session that ends*, rather than as *shall I
  make one*, which collects a yes from somebody who has not been told what they are
  agreeing to. In *When something stops* it gains a fifth refusal, and that one is the
  exception in the list: every other stop there is a step arriving late and you perform it,
  while `seal.sh` reporting no key means the case is being closed somewhere the author is
  not. Stop before the seal and finish everything else — `build_note.py`'s `unsealed` state
  was already built for this and prints `register not sealed yet — no signature or
  timestamp`. A case that stops there is honest and incomplete, which the method supports.
  One sealed with a key that leaked is neither.

  `seal.sh` and `cli/colophon.py` carry the caveat as well, so the warning survives outside
  the skill for anyone driving the scripts from a shell — and `cli/colophon.py` generates a
  key too, which the issue did not name. Its non-interactive path is the narrower hole: the
  prompts raise `EOFError` before the key when there is no terminal, so it fails closed
  unless the flags are supplied. An invariant in `tests/repo/` holds the caveat in all three
  files and reads the no-key branch of `seal.sh` to check it still says both what fixes a
  missing key and where it must not be fixed.

  The word budget on `## Before the first case` goes from 500 to 620 to pay for the rule —
  deliberate rather than drift, which is the distinction that test exists to force. #27
  relocates the paragraph on where the key goes and brings it back down.

### Added

- **The repository is a plugin marketplace as well as a repository.**
  `.claude-plugin/marketplace.json` and `.claude-plugin/plugin.json`, so that
  `/plugin marketplace add fchinaglia/colophon` followed by `/plugin install colophon@colophon`
  stands in for the clone-and-copy that was the only way in for Claude Code. The skill
  folder does not move to meet the convention: `skills` is the one manifest field that adds
  to the default location rather than replacing it, so `./skill/` is declared and
  `skill/colophon/` stays where `check_package.py` and the README already expect it. What
  comes down is the whole repository rather than the folder alone, which for this project
  means the verifier and the cases arrive with the skill. The description in both manifests
  says what the skill does *to your machine* and not only what it does for you — that it
  signs with a key which stays there and sends a digest, never the text, to a timestamp
  authority. The directory review's bar is that the install description discloses what the
  plugin actually does, and a sentence about the method alone does not clear it. It is also
  the honest line to read before installing something that touches a private key.

  The skill's own `description` is untouched: that one is how Claude decides when to open a
  register, and a disclosure about keys in it would only make it fire on the wrong prompts. The marketplace entry declares `category: productivity`, which is the
  closest of the categories the directory offers — there is no `writing` among them.
- **`check_manifests.py`, and a `manifests` job that runs it** after `claude plugin validate`
  has read both manifests — two invocations, because with a marketplace present the plain
  one reads that and leaves `plugin.json` unexamined. The two manifests state the same two
  facts twice, and both matter to somebody who is not the author. The version now lives in
  four places instead of two, and the two new ones are load-bearing for anybody who
  installed through `/plugin install`: `claude plugin update` compares what is installed
  against what the manifest declares, so a `version` left behind at the previous number
  does not fail — it quietly stops offering the update. The description is what a reader
  sees before installing, which is where the key and the timestamp authority are named, so
  a copy that drifts is a disclosure that stops being one. Both are checked; the CHANGELOG
  is the source of truth for the version and the newest released heading is what the
  manifests have to match, while the description has no third source and the two only have
  to say the same thing. `[Unreleased]` is skipped, so a working tree with unreleased
  changes sits at the last released number and passes. It is the job `check_package.py`
  does for the zip, in the place the zip does not reach.

### Fixed

- **The page was set in the site's serif and did not look it.** Three properties the
  site's body has and the site shell did not: `font-synthesis-weight`,
  `-webkit-font-smoothing` and `text-rendering`. On macOS the first two are not cosmetic —
  the same typeface renders visibly heavier without them, and `<strong>` gets a synthetic
  bold instead of the one the face carries. Same stack, different weight, and the tool
  read as a different document from the pages linking to it.
- **A scale mismatch nobody had looked for.** `components.css` carries the verifier's own
  weights, tuned for a system sans where 640 is unremarkable; in a serif it reads as
  heavy, and every other heading on the site is 500. Card titles, the tab strip, badges
  and the ghost buttons now match the site's scale, and the labels that are states rather
  than prose — `INTACT`, `VALID`, the tab names — move to the mono face, which is the
  site's rule for anything that is a value and not a sentence.
- **The masthead was an imitation of `colophon.css`**, close enough to look intentional
  and wrong enough to look like another site: the rule under it fell six pixels high, the
  wordmark was set smaller than on every other page, and the standfirst was 16px where the
  site sets 21 — that last one is why the page read as a different document before anyone
  could say which part was off. The chrome is now that stylesheet transcribed: same token
  values, same selectors, same numbers, down to the `.42em` gap in the wordmark and the
  `.16em` tracking on the eyebrow. The mark uses the site's own classes and inherits
  `currentColor`, so dark mode follows without a second declaration.

Copying a stylesheet is not the obvious choice and it is the right one here: the site's CSS
cannot be linked, because an external subresource would break the property that justifies
this file existing at all — that it is one file you can save and keep. The alternative to
copying is drifting, and drifting is what makes a page feel like it belongs somewhere else.

**All of it lives in the site shell, after the shared block**, and `components.css` is
untouched: weight and face are chrome, which is the line this pair of shells exists to draw.

### Changed

- **The README lists three ways in, not two.** The plugin route goes first because it is
  one command and it updates; the clone-and-copy stays underneath, for taking the skill
  folder by itself. Both now say that the skill can be invoked with `/colophon` however it
  arrived, which the page previously attached to the copied folder alone.
- **The README says plainly that this is a skill for Claude.** It claimed conformance to an
  open standard and left the rest to inference, while carrying no instruction file for any
  other host and having been run on none. Both things are now stated: the format is not
  tied to a vendor and the scripts depend on nothing but the standard library — and Claude
  Code and the Claude apps are the only hosts it has been used on, so anywhere else is
  untested rather than unsupported. With the criterion that actually decides it, which is
  not the file format: an assistant has to run code on your machine, because the case folder
  must persist for as long as you are writing and `seal.sh` must reach a key that must never
  leave it. One that executes in a cloud sandbox can hold the conversation and produce the
  annotation, and cannot seal.
- **`deploy/` says that it is a record, and not instructions.** The directory described a
  deployment that has since been replaced, and did not say so: the live configuration
  sends a content security policy, HSTS and a `404` page of its own, and
  `colophonmethod.conf` here carries none of them. Both addresses it stood up are closed —
  `/.well-known/colophon/keys` answers `404` since the site was republished, and
  `deposit.colophonmethod.com` no longer resolves. The README promised in bold that both
  would be kept alive, which a reader would reasonably have taken for the state of the
  world. It records the decision instead. Cases 001 and 002 print the anchor URL three
  times in their `VERIFICA.md` and again in their PDF, and it does not matter: both
  bundles carry `colophon.pub`, the verifier checks the signature against the key it finds
  in the bundle, and neither case needs the network to come out `VALID`. They are worked
  examples for somebody reading the repository, not evidence anyone is asked to trust from
  a distance — which is the distinction that decides whether a printed URL going dead is a
  failure or a fact. The reasoning that outlived the servers is kept, the apex canonical
  because addresses get printed and the key kept off the machine that holds the evidence,
  and `well-known/colophon/keys` stays in the directory because it is what the two cases
  were signed against.
- **The hat on the served page is one line.** It argued a case nobody had made — which
  copy to trust, and why not this one — in three sentences, on a page whose visitor is
  already holding a case and looking for a drop target. What is left is the fact without
  the argument around it: this is a convenience copy, and a case carries its own verifier
  inside it. Nothing true was lost in the cut. That the two builds differ in chrome and
  palette only is asserted by `build.py` and by `tests/repo/`, which is where a property
  belongs — a paragraph asking the reader to take it on faith was the weaker of the two
  statements, and the digests it linked to are printed by the build itself. `MIT` is
  written `MIT Licence` wherever the name stands alone, in the page's closing note and in
  the site footer, to match colophonmethod.com, which serves this build byte for byte.
  `SPDX-License-Identifier` is untouched: that one is an identifier with a fixed
  vocabulary, not a name. **`verify.html` does not move** — all four copies stay
  `2e8a461a…`, and only the served build changes, from `e216aef8…` at 70,348 bytes to
  `d826e0a3…` at 69,937.

### Removed

- **The repository stops publishing a homepage of its own.** `index.html` was written when
  `.nojekyll` stopped Jekyll rendering `README.md` and GitHub Pages was what
  `colophonmethod.com` pointed at — it was the front page because there had to be one. The
  site is served from its own source on its own machine now, and the two had drifted into
  different pages under the same `<title>`: twenty kilobytes with the mark and the
  navigation at one address, three with four links at the other. Nothing pointed at the
  second one. The string `github.io` does not occur anywhere in this repository, the site
  links `github.com/fchinaglia/colophon` and `releases/latest`, and the case pages carry no
  `href` at all — so it was reachable, indexable and orphaned at the same time, which is
  the combination that gets a stale page found by somebody who then quotes it. Pages is
  switched off with the file. `.nojekyll` stays: it is zero bytes, and it is the guard that
  has to be in place before Pages, not after, if it is ever turned back on. The invariant
  in `tests/repo/` that required a front page now forbids one, which is the same test doing
  the same job on the other side of the decision.

## [3.2.0] — 2026-08-25

The verifier gets a second shell, so the page served at a URL can look like the site
that serves it without the copy sealed into a case acquiring a single line of it.

### Measured first

`/verify/` was the one address on the domain that threw the reader out: no masthead, no
way back except the browser's own button, and nothing on it saying where they were. The
answer that kept being refused was *byte-identity* — the served file had to match the
four copies in the repository, so it could carry nothing.

That constraint was real when the verifier only existed at a URL. Since 3.1.0 it travels
inside the document, and a reader handed a PDF already has the copy that matters. **The
served file had stopped being load-bearing and nobody had noticed**, so it was still
being defended as though it were.

### Added

- **`shell-site.html`**, the served build: the site's masthead and nav, its palette and
  its serif, and two lines saying plainly that this is a convenience copy and that the
  one to trust is the one inside your own case.
- **`components.css` and `ui.js`**, extracted from `shell.html` and inlined into **both**
  shells by `build.py`. The two builds differ in chrome and palette and cannot differ in
  behaviour, because there is one copy of the behaviour. `verify.html` is byte-identical
  to what it was before the extraction — the same `2e8a461a…`.
- **Four tests.** That both shells provide `#drop` `#dir` `#fil` `#out`, which core.js and
  ui.js reach for by id — a shell that drops one produces a page that loads, looks right
  and quietly does nothing. That the shared parts arrived intact in each build. That the
  two builds are *not* identical, which would mean a shell had stopped doing its job. And
  that the travelling copy names no website.
- **`build.py` prints both digests** and refuses a shell missing one of the four elements.

### Not done

The served build is not deployed by anything in this repository: `verify-site.html` is
the artefact, and the site that serves it copies it. A fifth write target pointing into a
`site/` directory would presume a layout this repository does not have.
## [3.1.4] — 2026-08-25

The paper, brought back to the implementation. **Methodological document version 0.2.**

### Measured first

`paper/colophon-method.md` still described the seal as it stood at the validation case,
three releases earlier. It survived the 3.0.0 turn better than `docs/` did — it never
described distribution routes, so removing the address left it untouched — but §7 and §8
had drifted, and §9.2 carried a number that was simply wrong.

### Fixed

- **§9.2 reported 75 events in the chain.** The sealed register of the validation case
  holds **83**; 75 is the span count, duplicated one row down. Checked by extracting
  `events.jsonl` from `cases/002/colophon-002.tar`. Every other figure in that table
  holds — 3,126 words, 75 spans, 47.1%, 30.6%, first draft ~86% human.
- **§7 labelled the Ed25519 signature `who`**, the word removed from `seal.sh` in 3.1.2 and
  from the reader-facing documents in 3.1.3. It now says what the signature does answer:
  which key sealed the register, in one act, the same key across the author's cases, with
  the fingerprint the closing manifest commits to.
- **§7 held that the qualified signature was unusable** — the Italian one engulfs the
  document, and a register lives by being inspectable — and proposed signing a periodic
  manifest of digests instead. That route was never built. The one that was keeps the
  objection and drops its cost: the register is never wrapped, it rides as an attachment
  inside the PDF, and the signature goes on the PDF. The paper asked the right question
  and printed the answer that got superseded.
- **§8 listed six of the twelve scripts and never mentioned `verify.html`**, which is the
  artefact a reader actually opens. Complete now, with a new **§8.1** on what the reader
  receives: one file, no address, and a verifier that reads the bundle or the PDF offline
  and deliberately does not recompute the measurement.
- **§11 gave precedence to an Italian original the repository does not carry.** The claim
  was true when written — the register records the translation at event 77 — but it handed
  precedence to something no reader can obtain, the same shape as the dangling reference
  fixed in 3.1.3. Nothing material goes with it: §9.1 already states the validation article
  is Italian.

### Added

- **A revision note in §11**, because a version number with no account of what moved is the
  kind of unverifiable claim §1.2 objects to. It says what 0.2 changed and, as plainly,
  that nothing in §1–§6 or in the results did.
- Smaller: §5.1's L3 row names the bundle, and §9.4 notes the second sealed case while
  saying it is a demonstration of the pipeline and not a second validation.

`colophon.zip` and `verify.html` are unchanged from 3.1.3 — nothing outside `paper/` moved.
The paper's PDF is attached to this release for the first time.

## [3.1.3] — 2026-08-25

The documents in `docs/` had not moved since 23 August. One of them did not just lag: it
asserted the opposite of how the method now works.

### Measured first

`docs/colophon-onepager.html` is what someone arriving from outside reads. Its seal table
said the Ed25519 signature is *"verified against a key published on a domain the author
controls — never one that lives inside the folder it authenticates."* Since 3.0.0 the key
lives exactly inside the folder it authenticates, and is published nowhere. The section
heading made the same claim — *"Who, and when — each from a source that does not depend on
the others"* — and the *who* has not come from an independent source since that release.

Four releases in two days, and the reader-facing page was the last place anyone looked.

### Fixed

- **The one-pager's seal table.** The row is `sealed by`, and says what an enclosed key can
  and cannot establish. A paragraph after the three seals says where *who* actually comes
  from — a qualified signature on the document, outside the package, optional — and what
  is left without one. The heading no longer promises an independence it does not have.
- **`colophon-anatomy.html` and `colophon-a4.html`** labelled the signature check *"who is
  answerable for it?"*, the word removed from `seal.sh` in 3.1.2. Now *"which key closed
  it, and in one act?"*, and the anatomy's `aria-label` says none of the four checks names
  a person.
- **`colophon-a4.pdf`** regenerated from the corrected HTML — and it was Letter, in a file
  called `a4`, against an `@page { size: A4 }` the HTML has always declared.
- **`service-and-onboarding.md` pointed at `qualified-signature.md`**, which exists only on
  an unpushed local branch. A public document sending readers to a file nobody can open,
  about the very thing that became the anchor of identity in 3.0.0.

### Added

- **A dated status note on the three analysis documents**, naming the releases that
  overtook them and saying plainly that everything in them about addresses, published keys
  and the deposit is the record of a position held and then abandoned — kept because the
  reasoning is why the current shape looks as it does, not because it describes the method.

## [3.1.2] — 2026-08-25

Documentation, and it started as a question nothing in the repository could answer: if
identity now comes from the qualified signature on the PDF, what is the register's own
signature still for?

### Measured first

`seal.sh` labelled the three seal artefacts `who` / `when` / `when`, and contradicted
itself four lines below, in a paragraph added the same morning: *"it cannot say whose key
it is, and it does not pretend to."* The label had been false since 3.0.0 removed the
published key, and nobody had gone back for it. The TSA failure message carried the same
split — *"a claim about when, not about who"*.

Underneath the wrong word, a gap. The repository said at length what the internal
signature does **not** prove and nowhere why it is still made. Read on its own that is a
defence, not a reason, and it left the honest question unanswered.

### Fixed

- **`sealed by`, not `who`**, in `seal.sh`, with four lines saying why: the key is
  published nowhere, so on its own the signature names nobody — it says one key closed
  this register in one act, and that the same key closed the author's other cases.
- **The TSA failure message** no longer opposes *when* to *who*. It says the timestamp
  fixes the date, which the signature does not — true of both.

### Added

- **`VERIFY.md` §2 answers the question**, and the first reason is the one that applies
  most often: a qualified signature covers the *document* the record arrived in, and the
  bundle also travels alone — published beside the case, forwarded, archived — at which
  point there is no document and this key is the only one left in the package. Then: one
  key seals every case an author closes and `key_fingerprint` sits inside each sealed
  manifest, which makes a body of work one body; publishing that key later anchors every
  case sealed with it, retroactively, which an unsigned register can never do; and a
  reopening keeps the old seal beside the new one. The section still says, before and
  after, that none of this is identity.
- A pointer in `SKILL.md`, which cost three sentences trimmed elsewhere: the closing
  section's word budget had seven words of headroom.

## [3.1.1] — 2026-08-25

A patch, and it is the one 3.1.0 made findable. Two documents were generated with the
bundle nowhere inside them, and nothing said so.

### Measured first

The closing pipeline in `SKILL.md` ran to `build_bundle.py` and stopped. `render_pdf.py`
appeared nowhere in it — only in the list of scripts to copy at the opening, and in the
section about the qualified signature. So the model reached the last step of the sequence
with the tar on disk and improvised the command that makes the document: a plain
`render_pdf.py`, no `--embed`, no attachment.

Underneath it, a worse one. `--attached` wrote the line; `--embed` put the file in;
nothing tied them together. `render_pdf.py --attached` alone produced a document whose
disclosure reads *verify offline: drop `colophon-<uid>.tar` on verify.html* and which
carries nothing — to anyone forwarded the PDF alone, a route that leads nowhere. It is
mistake #16 in a new costume, in the one artefact the method tells an author to hand over,
and it was silent.

**Both were found by dropping those PDFs on the verifier released an hour earlier**, which
answered *this document carries no attachment*. The tool that diagnosed the fault shipped
before the fix for it.

### Fixed

- **The closing pipeline runs to the rendering.** `python3 render_pdf.py --attached
  --embed` is the last line of the block, so the step is not left to improvisation.
- **`--attached` without `--embed` is refused**, naming both ways out. Not made a hard
  rule: `enclosed` means *travels with the document*, and a PDF mailed together with its
  tar is honestly described by it — so that case is now `--beside`, said out loud instead
  of being what you get by forgetting a flag.
- **`--embed` without `--attached` warns.** It under-claims rather than over-claims — the
  document carries the record and its own line says it does not — so it is a warning.

### Added

- Two tests pinning the pair, and the sentence in the closing that tells the model to drop
  the copy it is about to send on `verify.html` itself: the page opens the PDF and says
  what is actually inside it.

## [3.1.0] — 2026-08-25

The verifier stops being a page about a tar. It opens the document the record travels in,
reads the record out of it, shows the case's own report beside the checks, and looks at
the signature the method now ends by recommending.

### Measured first

3.0.0 made the enclosure the only route: a case travels as a file, attached to a PDF, and
the closing offers a qualified signature over that PDF as the one thing that names a
person. Three gaps followed from it on the same day, and none was a bug report.

A reader handed that PDF still had to run `pdfdetach` before this page would look at
anything — the manual step the enclosure exists to remove. A reader who did that got a
verdict with no way to see what the verdict was *about*, because `index.html` sits inside
the tar. And the signature the method had just made the anchor of identity was the one
artefact nothing checked.

### Added

- **A second tab, holding the case's own page.** The checks keep the first. The strip
  appears only when the files actually carry `index.html`, and the dot on the Verification
  tab carries the worst finding, so the state stays visible while the report is in front —
  a strip that always showed green would be a claim. The report goes into an iframe with
  `sandbox="allow-scripts"` and **deliberately not** `allow-same-origin`: it needs its own
  scripts for the words/ideas toggle, and it is content out of the package this page exists
  to distrust. Both flags together undo the sandbox and would let a crafted bundle rewrite
  the verdict around it.
- **Drop the PDF itself.** `render_pdf.py --embed` writes the bundle in as an incremental
  update, Flate-compressed; the page reads it back out with `DecompressionStream`, offline,
  with nothing written to disk. A card names the attachment it opened before anything is
  claimed about it. Where `DecompressionStream` is missing, the page names `pdfdetach` and
  Firefox rather than failing obscurely.
- **The signature over the document**, in four parts: which bytes the `/ByteRange` covers
  and that the gap between its runs is exactly the `/Contents` string; that the digest in
  the signed attributes is the digest of those bytes; that the signature verifies against
  the key in the signer's certificate, through `crypto.subtle`, with the signer's name read
  out of the certificate; and **whether the record just read is inside the signed bytes.**

  The fourth is the one this project needs. `SKILL.md` says *embed, then sign, in that
  order*, and a document signed the other way round shows a perfectly valid signature over
  pages holding none of the evidence. `tests/fixtures/signed-pdf/` holds one of each. Both
  verify. Only one has signed anything that matters.
- **`tests/fixtures/signed-pdf/`** — the two orders, about 10 KB each, with the generator
  beside them. The certificate is self-signed and says so in its own subject; no real
  document or certificate is in the repository.

### Fixed

- **A `.pytest_cache` shipped inside `colophon.zip`** and `check_package.py` passed it: the
  junk filter matched on the basename, and a pytest cache holds files called `README.md`
  and `.gitignore`, while the folder walk ignored caches on both sides so the two agreed
  about a directory neither should have carried. Caches are now tolerated in the working
  folder and refused in the package, matched on the path, with a regression test.

### What it still does not do, and says so

**The signature check is not a trust check**, and the card states that in bold rather than
in a footnote. Whether the certificate is qualified, was valid on the day, or has been
revoked needs the EU trusted list and a revocation service: network and policy, not
arithmetic. A valid digest is not a valid identity, and a page that let the first read as
the second would be doing the exact thing this project exists to stop. RSA PKCS#1 v1.5 and
ECDSA are verified; RSA-PSS is named and not claimed.

Checked against a real qualified signature — ETSI.CAdES.detached, RSA with SHA-256, an
ArubaPEC EU Qualified certificate — and the verdict agrees with poppler's `pdfsig`,
including the DSS revision appended after signing, which this page names as long-term
validation material instead of reporting a modified document.

### Not done

The published cases still carry their old address fields, unchanged since 3.0.0: they are
sealed, and the gap between what the method says and what its two worked examples say
closes only when a third case is sealed.

## [3.0.0] — 2026-08-25

**Breaking, twice.** A case no longer has an address, and a key is no longer published at
one. What is left is a file the author hands over and, if they want a name attached to it,
a qualified signature on the document that carries it.

### Measured first

Both changes came out of one test run, and neither was a bug report about code.

At the closing, the model offered the author a choice between a self-contained file and
depositing the case at `deposit.colophon.com` — **a host that has never existed**. The
deposit instance was withdrawn in 2.0.0, but `### Publication` still described three
routes and the second was *"a web address people can link to"*. A route stated as a choice
gets filled in, and the model filled it in with an address it invented.

The second was worse because nothing was invented. `colophon setup` fetched the key URL
and returned `1` with *"Publish the key there first, then re-run"* when it did not answer
— so with `colophonmethod.com` refusing connections on 443, an author could not finish
setup at all, before writing a word. The check was added in 1.x as *the one check nobody
performed for the first published case*. It was a good check. It was also the only step in
the whole method that could stop an author because of somebody else's DNS.

### Removed

- **The address route.** `verification_url` and `register_url` in `case.json` (and the
  Italian aliases), `--url` in `build_note.py`, `build_block.py`, `render_md.py` and
  `render_pdf.py`, the link to the raw files on the verification page, and the two address
  rows in `attestation.txt`. An address left in an old `case.json` is now ignored, never
  printed; `tests/unit/test_block.py` pins that.
- **The published key.** `key_url` in `case.json`, `--key-url` and `--allow-unverified` in
  `colophon setup`, the ranked key-URL menu, `check_key_url`, and the `urllib` import that
  made it possible. `colophon setup` now opens no network connection at all, and
  `cli/test_cli.py` asserts the source names no `.well-known` and imports no `urllib` —
  because that check came back once already and would come back again.
- **The third form of the technical line.** There were three routes and three forms; there
  is one route and two forms, `signed register, enclosed` and `signed register, not
  enclosed`. A file is either there or it is not, and that exhausts the vocabulary.

### Added

- **`colophon.pub`, in the bundle.** `seal.sh` copies the public half of the signing key
  into the case folder and `build_bundle.py` packs it, so the signature is checked against
  the copy that arrived with the evidence, offline. `build_bundle.py` refuses to stay quiet
  about a signed register packed without one: the reader would fall back to the key inside
  the signature, which verifies just as well and can be compared with nothing.
- **The fingerprint check, in the verifier.** A key inside the package it signs is
  circular. `case.json` is not: the closing manifest covers it, so the `key_fingerprint`
  it declares is committed to by the signature itself. `verify.html` now compares the two
  and says **DOES NOT MATCH** in the signature card when they differ. Run against the
  sealed `cases/001` bundle, they match — and with the fingerprint swapped, it is caught.
  That is a real check, and it is still not identity.
- **`### The qualified signature`**, and a fourth decision at the closing — the only one
  after the seal. `render_pdf.py --embed` already put the bundle inside the PDF; what was
  missing was anyone saying why that matters. A qualified electronic signature over that
  PDF covers the article *and* the evidence in one act, and a supervised trust service
  identified the signer first, so the reader gets a natural person rather than a domain.
  It is offered once, it is optional, and it is never allowed to sound like a claim about
  the numbers: it says *this file came from this person and has not changed since*, and
  letting it stand in for the measurement stays on the list of mistakes in
  `reference/disclosures.md`.

### Changed

- **`VERIFY.md` §2 no longer sends the reader to a domain.** It verifies against
  `colophon.pub`, compares the fingerprint with `case.json`, and then says plainly what
  none of that proves. §2b stops being *only if a `.p7m` is here* and becomes the section
  about identity, because it is now the only source of it.
- **`SKILL.md` forbids what it used to offer.** *Never ask where the key is published,
  never offer to publish it, and never name an address for it* — no `.well-known`, no
  GitHub endpoint. Same for the case: *never offer an address, a hosted copy or a link.*
  A prohibition is what a description of a route that no longer exists has to become.
- **`deploy/README.md` marks the published key legacy.** It claimed that without
  `/.well-known/colophon/keys` every signature in the project is circular again. That was
  true when it was written. The file stays served because cases 001 and 002 were sealed
  naming it — but both bundles carry `colophon.pub`, so a reader who never reaches the
  domain can still check them.

### Fixed

- **A `.pytest_cache` shipped inside `colophon.zip`**, and `check_package.py` passed it.
  The junk filter matched on the basename, and a pytest cache contains files called
  `README.md` and `.gitignore`; the folder walk ignored caches on both sides, so the zip
  and the folder agreed about a directory neither should have carried. Caches are now
  tolerated in the working folder and refused in the package, like every other kind of
  junk, with a regression test.

### Not done

**The two sealed cases keep their addresses.** `cases/001` and `cases/002` carry
`key_url`, `register_url` and `verification_url` in a `case.json` that a signed manifest
covers, and their published `VERIFY.md` still tells a reader to fetch a key from
`colophonmethod.com`. Changing any of it means reopening both cases, and the scripts
ignore those fields anyway. What the method now says and what its two worked examples say
are not the same thing, and that gap closes only when a third case is sealed.

`docs/plan-local-first.md` and `docs/service-and-onboarding.md` still argue for the key
URL at length. They are the record of decisions taken, not instructions, and they are left
as they were.

## [2.4.0] — 2026-08-24

Closes #14 and #13. The mechanism shipped in 2.3.0; this is what the author actually
hears, which was left to the model and is now written out.

### Measured first

The closing section of `SKILL.md` went from **668 words on 23 August to 1,943** the next
day — almost tripling in a day, because `### Publication` and `### The last read` did not
exist before it. That growth is the defect, and the word budgets added here are the only
thing in this release that would have caught it happening.

### Added

- **`## What the author hears`** — the rule, stated generally. *When the measurement
  stops* had it right in one place: it reclassifies the event before describing it, fixes
  a budget a model can obey, gives the content of the sentence rather than its wording,
  and states the reason from the author's chair. The other two boundaries now follow it,
  and the section names what never reaches the author at all.
- **`## Before the first case`** (#13). `SKILL.md` described the cycle and said nothing
  about the one-time setup that precedes it, so the model had no reason to conduct that
  conversation and the author was left running a command nobody had mentioned. It states
  the split as a rule: ask, explain and check in conversation; leave the signature and the
  digests to the script — a model retyping a fingerprint is the class of error this
  project exists to prevent.
- **What you say at the opening and at the closing**, written out. Four things in order,
  then four decisions. The author never meets `open` and `confidential`; the model maps
  their answer, and anything that is not a clear no is `confidential`, because being wrong
  that way costs a page that explains itself and being wrong the other way cannot be
  undone.
- **One sentence for each refusal** the closing sequence gained this week — the render
  gate, the markdown subset, the review after the manifest, packing before sealing. The
  section is now `## When something stops`, because five things stop and only one of them
  is the measurement.
- **`tests/repo/test_vocabulary.py`** — that the review's strings carry none of the twelve
  words nothing can be done with, that the warning stayed one line, and that four sections
  stay inside a word budget. Its docstring says what it cannot cover, which is most of the
  issue: nothing here executes a model.

### Fixed

- **The red-list warning printed one line per matching field.** Case 002's seq 68 matches
  in five, so it would have produced seven lines of warning about one event, into a
  conversation where somebody is writing an article. And it printed a JSON path at the one
  moment nothing can be done with it — by construction, since the decision happens at the
  review — while carrying no `seq`, so it was a poor locator for the transcript reader it
  was written for. One line, located by `seq`, no path.
- **`review.py`'s three headers were three shouts of equal weight**, which says the three
  lists are the same kind of thing. Two are *worth a look*; the first is *a thing you were
  already told once*. One shout and two invitations now, and the entries are numbered
  across all three so the author says "3 and 7" and the model finds the path — the file's
  own rule that the author is never asked to edit anything, applied to the review.

### Not done

Roughly 700 words of rationale still sit in `SKILL.md` that belong in `reference/`. Only
the moves with an existing home were made: the `curl | shasum` recipe into `VERIFY.md`,
the route rationale into `disclosures.md`. The rest needs a fifth reference file, which is
a fifth thing to keep in step. **So the author hears less and the file the model reads is
longer**, and the budgets are set at today's numbers rather than at the targets: they
guard against further growth, they do not claim a reduction that did not happen.

## [2.3.0] — 2026-08-24

Closes #6. A case travels as one file handed to whoever the author hands it to, so the
question stopped being what may be deposited and became what may be recorded.

### Added

- **Two regimes, declared before the brief: `open` and `confidential`.** Under
  `confidential` the author's instructions are recorded as **what they required, never as
  what they said** — and that is the whole of the difference. Every event, every editorial
  decision, every attribution and every change is still recorded, and `build_page.py` says
  so to the reader, because someone who counts the events and assumes none were held back
  is being misled by omission.
- **A red list the author declares**, matched word-bounded after NFD, accent stripping and
  casefolding. `record.py` **warns and records**; it does not refuse. What may not be said
  about a third party is a judgement, and the only part a machine decides is whether a
  string named in advance is present. The check lives in `redlist_violations()`, never in
  `violations()`: `spec/canonical.md` §4 is normative about what `append()` refuses and a
  second implementation must reproduce it, while a machine-local list is reproducible by
  nobody. The list lives in the config directory, never in the case folder.
- **`review.py`, the last read before the register is sealed** — and the guard the warning
  is not. A warning printed into a conversation while somebody is writing an article is a
  warning nobody reads, so every hit comes back here, beside two structural filters: every
  `human_contribution` event whole, and every payload string reproducing thirty characters
  of a draft. `--set` rewrites a value and rebuilds the chain; **values are rewritten,
  events are never deleted**. Every original timestamp survives, and the measurement does
  not move — `measure.py` reads `payload.change` and nothing else, asserted by a test that
  compares `kpi.json` across a rewrite.
- `review.py --done` records **one event, always, in both regimes**, whether or not
  anything changed: that the author read what the register says about other people, and
  whether something was removed. Never which events, never how many. A review that only
  appears when something was found is itself the disclosure.

### Fixed

- **`save_config()` chmodded the file and left the directory at umask.** With red lists in
  that directory — named after `case_uid`, which is public, because the bundle is called
  after it — a world-traversable directory would have exposed the names the list exists to
  keep out of the record. This one is worth taking even if you never declare a red list.

### Measured

The first design of this gated `record.py` on quotation-shaped field names. The four
events case 002 actually had to redact used `caso_A`, `caso_B`, `cambiamenti`, `rimossi`
and `sostituzioni` — **none of them quotation-shaped** — so it would have caught nothing,
and the inspector that printed "every quoted string" would have printed none of it either.
Both were withdrawn. Two of those four events were *already summaries*, which is why
`summarised` is a writing habit here and not a regime a register can promise.

What none of it reaches is in case 002's own words at seq 67: *"i quattro dettagli
restringevano la famiglia di aziende descritta"* — four details that narrowed the family
of companies described, with no name anywhere. Identification by intersection.

## [2.2.0] — 2026-08-24

### Added

- **`build_block.py --form card`** — the block stacked, for a feed. `--form svg` produced
  a 3.6:1 strip that a feed crops or shrinks past reading; a post is a container
  `disclosures.md` names, and until now the skill could not serve it. 4:5, 1:1 and 1.91:1.
  Lines wrap rather than the note shrinking, and a landscape ratio **refuses** rather than
  producing an icon whose four labels are illegible — which is worse than no icon at all,
  because it looks like a claim while being none.

### Fixed

- **A source that carries its own disclosure was getting it twice.** Both renderers
  generate the marker and the block, so the two published cases printed the level-1 marker
  once from the renderer and once from the text, and carried a paragraph note the
  generated block had already superseded — one naming an address that had stopped holding
  the register. The renderers now omit the blocks `excluded` names, which is what
  `disclosures.md` defines that field to be. No case was reopened: a PDF is a rendering,
  no manifest covers it, and both bundles come out of the new PDFs byte for byte identical.
- **And three places still taught the pattern that caused it.**
  `annotation_example.json` shipped case 002's excluded blocks as the example,
  `disclosures.md`'s section led with *"the blocks of the disclosure go in `excluded`"*,
  and `SKILL.md` said the block is generated without ever saying not to type it. All three
  now lead with the rule: **the disclosure does not go in the source.** Not for the
  duplication — for the drift. A typed note freezes numbers that were true when they were
  typed; a generated one is derived from `kpi.json` every time. It is the argument that
  made `build_note.py` generate the root rather than let anyone copy it.

## [2.1.0] — 2026-08-24

Two sealed cases are published in the current format, and getting them there found two
defects and one thing the specification had asserted too broadly.

### Added

- **`cases/001/` and `cases/002/`** — the article that explains Colophon and the article
  on data fragmentation, each as four files: the verification page, `verify.html`, the
  bundle, and a PDF carrying both as attachments. Open the verifier, drop the bundle on
  it, network off.
- Both registers are **replays**, and each says so in an event of its own before the
  closing manifest, naming the original root. The original registers stay in the history
  of this repository. Neither measurement moved: 001 is 18 spans and 337 words, 002 is
  75 spans and 3,126 words, both to the digit.
- **`render_pdf.py --embed` takes more than one file.** The record and the tool that reads
  it are two things: a reader who saves only the bundle finds the verifier inside it,
  which works and reads like a riddle. The name tree is sorted, because a reader that
  binary-searches it finds nothing otherwise.
- `spec/canonical.md` §5 says what a **replay** is. It said such registers cannot be
  repaired; they cannot be repaired *in place*, and the difference is the whole point —
  a replay is a new register with a new root and a new seal, and what it loses is not
  recoverable.

### Fixed

- **The title was not a title, and the marker sat above it.** A source written before the
  deliverable was markdown carries its title as an ordinary paragraph, so `render_pdf.py`
  set it at body size and put the byline and the level-1 marker *above* it — the one
  placement `disclosures.md` forbids. The first paragraph is now promoted to `h1` when it
  is exactly the title `case.json` declares: a check against a manifest-covered value, not
  a guess, and no word is touched either way.
- `untar` and `normalise` move from `shell.html` into `core.js`. The page, the test
  harness and anyone driving `core.js` from node all need them, and three copies of a
  parser is how they drift.

### Changed

- The golden and verifier suites now read **the bundle this project ships** rather than a
  folder beside it: extract `cases/001/colophon-001.tar`, measure, compare with the
  measurement sealed inside. It tests the file a reader receives.
- `verifier/build.py` writes a copy of `verify.html` into each published case folder, and
  a repo invariant covers every maintained copy. The copy sealed inside a bundle is
  deliberately not covered: it is the verifier as it stood when that case was closed, and
  it is meant to go stale.
- **`verify.html` changed, so its digest changed.** Compare against the digest published
  with *this* release, not with 2.0.0.

## [2.0.0] — 2026-08-24 — the local-first turn

**Breaking.** `colophon deposit` and `colophon address` are gone, and so is the
`server/` directory that ran the instance they talked to. Nothing replaces them:
a case is packed and handed over. The instance at `deposit.colophonmethod.com` is
frozen, not deleted — it still serves every case already on it, at the same
addresses, because one of those addresses is printed inside a published PDF.

Colophon stops being a thing with a server in it. A case now travels as a document plus a
bundle its author packs, and nothing has to stay online for a reader to check it. The
reasoning, the order of work and what it costs are in `docs/plan-local-first.md`.

### Added

- **`build_bundle.py`** — writes `colophon-<case_uid>.tar`: everything the closing
  manifest covers, the seal, and `verify.html`. Dropped on the verifier with the network
  off, it gives the chain, the signature, every manifest digest and the timestamp. Four
  refusals, each guarding a bundle that would travel looking complete: no manifest, no
  seal, an output path inside the case folder, no verifier found. Deterministic — two
  authors packing one case get the same bytes.
- **`build_block.py`** — the disclosure block as one generated object instead of a shape
  retyped from a specification two hundred lines below the pointer that sends you there.
  It composes: the category and the boundary margin come from `build_icon.py`, the
  technical line from `build_note.py`, so the block cannot disagree with the icon beside
  it. Three forms — an HTML fragment, one SVG, plain text. Closes #17.
- **`render_md.py`** — the published document: the covered version, the marker under the
  title, the block at the foot. It adds and never rewrites. **The gate is not optional
  and there is no flag to skip it**: the source is hashed against the manifest, and a
  mismatch refuses. Once a signature is over a document, a reader reads *this file is
  unaltered* as *this text is the text that was measured*, and those are two claims.
- **`build_attestation.py`** — one page of plain text restating the case identity, the
  register root and every digest the manifest closes over, flush-left in `sha256sum`
  format, so `grep -E '^[0-9a-f]{64}  ' attestation.txt | shasum -a 256 -c -` checks the
  whole case with no PDF, no PKI and no browser. It also states what the apparatus does
  not claim, in a sentence a person reads.
- **`render_pdf.py`** — the same document printed through headless Chrome, behind the same
  gate. It carries a markdown converter implementing a deliberately small subset and
  **refusing by line number** on anything outside it: one that silently mangles a table
  publishes something the author did not write, invisibly. Its one rule — it wraps, it
  never rewrites — is asserted, and a test deletes a word from the output to prove the
  assertion fires.
- **`render_pdf.py --embed`** — the bundle inside the PDF, as an incremental update. The
  original bytes are never rewritten, which is what makes a PAdES signature added
  afterwards cover this revision instead of contradicting it: **embed first, sign second.**
  It implements the shape headless Chrome writes and refuses every other — encryption,
  cross-reference streams, object streams, a catalog already carrying `/Names` — because a
  malformed incremental update opens in some readers and not in others, silently.
- The manifest rule is now in the names rather than decided file by file: **`build_*` is
  covered, `render_*` is not.**

### Changed

- `verifier/build.py` writes both copies of `verify.html` — `verifier/` and
  `skill/colophon/` — from one source, with a repo invariant asserting they match. A
  stale skill copy would ship an old verifier inside new evidence, and an old verifier
  verifies an old case perfectly.
- **SKILL.md §Publication** is three routes, not one: attached, at an address, or
  neither, with what each buys and what the attachment cannot do. A bundle in a reader's
  hands is frozen and cannot announce that it has been superseded — which is why the root
  is printed in the document.
- The thousands separator follows the language. `1,096 parole` reads to an Italian eye as
  one thousand and ninety-six thousandths, and the word count is the first number a
  reader meets. Found by running the generator against a real case.

### Changed — the prose, and the line that carries it

- **The technical line states the route, and there are three of them.** `signed and
  inspectable register` said two things and checked one: a register with no address is
  not inspectable by the reader holding the document, and the line printed the claim
  anyway. Now the first line is `signed register`, `signed register, attached to this
  file` or `signed register, not published`, the middle line is the route, and the root
  is in all three — because two copies with two different roots are the only way a reader
  sees that a case was reopened.
- **`VERIFY.md` gains §0 and §2b.** §0 is the fastest check there is — one `grep | shasum
  -c` over `attestation.txt`, every file the register closes over, with no PDF, no PKI and
  no browser. §2b is the qualified signature: the `openssl cms` recipe, the EU DSS
  validator, and the warning nobody prints — a CAdES-B signature carries no revocation
  evidence, and when the certificate expires CAD art. 24 c. 4-bis treats the signature as
  never made. Level LT is what survives that.
- **The technical line's middle row is the route, and `--attached` has to find the file it
  names.** It printed *attached to this file* and named a tar while nothing checked that
  the tar had ever been built — a route under a disclosure leading nowhere, silently. The
  wording is now *enclosed* / *accluso*, true of a PDF attachment, a sibling file, a mail
  or an archive, and the flag refuses when the bundle is not there.
- **`attestation.txt` is not the file you sign, and the reason is measured.** Signing a
  text file canonicalises its line endings: the copy extracted from a `.p7m` has digest
  lines ending in a carriage return, `shasum -c` looks for `kpi.json\r`, and every line
  fails with *No such file* — under a signature that verifies perfectly. The qualified
  signature belongs on what the author hands over: the PDF as PAdES, or the bundle as
  CAdES **in binary mode**. A client that signs a tar as text destroys it — 256,000 bytes
  in, 6,367 and *Unrecognized archive format* out, signature valid over the wreckage.
- `VERIFY.md` §3 also says why no CA travels in the bundle, and what the browser verifier
  deliberately does not do: it reads the timestamp's imprint and stops, so it tells you
  the token commits to *this* register and not who issued it.
- **`README.md` says you need nothing.** No account, no invite, no instance, no hosting —
  one command and a key published once, at a domain or at GitHub's signing-keys endpoint,
  which is free and needs no domain at all.
- **`disclosures.md`** carries the three forms in both languages, the rule that the tier
  is the container and never the author, and two additions to *What never to write*: no
  PDF/A claim on a Chrome rendering, and nothing that lets a signature over the document
  stand in for the measurement.

### Measured

Three verifications that a real machine settled and no analysis had.

- **A qualified signature over an embedded bundle survives it.** One Italian client, one
  real certificate: the signature is an incremental update, the 321,051 original bytes are
  intact, the `/EmbeddedFile` sits inside the signed byte range, `pdfdetach` returns the
  bundle byte-identical from the signed file, and the extracted tar still verifies through
  `core.js`. The signature is **PAdES B-LT** — `signingCertificateV2` and
  `signatureTimeStampToken` in the CMS, `/DSS` with `/OCSPs` and `/VRI` appended after it.
  `pdfsig` reports *"Not total document signed"* and that **is** what LT looks like: the
  revocation evidence is appended after the signature and lies outside its range by
  construction.
- **Adobe Reader shows an embedded bundle and exports none of them.** Eight builds varying
  one thing at a time — literal against UTF-16BE name strings, with and without
  `/Subtype`, with and without `/AF`, a `.zip` name, an uncompressed stream — behave
  identically, and so does a PDF written by poppler's own `pdfattach`, which never touched
  this code. Firefox 154.0 and poppler 26.08.0 read all of them. Adobe Reader
  2026.001.21789 on macOS 25.5 reads none. Left unexplained rather than guessed at, and
  declared in `VERIFY.md`: a reader on Acrobat has to use Firefox or `pdfdetach`.
- **Signing a tar as text destroys it** — OpenSSL's own default turns 256,000 bytes into
  6,367 and *Unrecognized archive format*, with the signature valid over the wreckage. The
  client tested does not do this; the check that establishes it is one text file, one
  extraction, one digest comparison, and it is written down.

### Removed

- **`server/`** — ingest, the two compose files, the Dockerfile, the container nginx, and
  their 31 tests. The instance at `deposit.colophonmethod.com` is **frozen, not deleted**:
  it serves the cases it holds, at the same addresses, and answers `410` at `/c` with a
  plain-text body naming `build_bundle.py`. One of those cases has its address printed in
  a signed technical line inside a published PDF, and a PDF cannot be edited.
- **`colophon deposit` and `colophon address`**, and everything only they used: the base58
  case id, `author_secret`, the evidence base URL, the submission signature. The client is
  one command now. This also removes the promised-but-absent `--unpublished` flag and the
  write-only `deferred` key.
- `deploy/` keeps what is still live and nothing else: the apex, the key at
  `/.well-known/colophon/keys`, and the frozen instance configuration.

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

<!-- These shipped in 1.5.0 and the heading was never moved. Kept as a subsection
     rather than a release of its own: nothing here was ever released separately. -->

### Added in 1.5.0 — tests and CI

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

### Fixed in 1.5.0

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
