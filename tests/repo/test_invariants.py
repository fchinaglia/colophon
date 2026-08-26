# SPDX-License-Identifier: MIT
"""Things about the repository that must stay true.

These cost nothing and each guards a failure that is silent: a worked example that has
quietly forked from the skill, a documented flag that errors, a missing line that turns a
Windows checkout into a false accusation of forgery.
"""
import os
import re
import subprocess
import sys

import pytest

from conftest import ROOT, SCRIPTS

DOCS = ["skill/colophon/SKILL.md",
        "skill/colophon/reference/disclosures.md",
        "skill/colophon/reference/protocol.md",
        "skill/colophon/reference/VERIFY.md"]


@pytest.mark.parametrize("name", ["record.py", "measure.py", "build_page.py",
                                  "build_icon.py", "build_note.py",
                                  "build_block.py", "build_bundle.py", "build_attestation.py",
                                  "render_md.py", "render_pdf.py", "review.py",
                                  "build_verify.py"])
def test_the_example_has_not_forked_from_the_skill(name):
    """example/ is the worked case a reader runs. If it drifts, the golden tests are
    measuring a copy nobody ships."""
    a = open(os.path.join(SCRIPTS, name), "rb").read()
    b = open(os.path.join(ROOT, "example", name), "rb").read()
    assert a == b, f"example/{name} has drifted from the skill"


@pytest.mark.parametrize("pattern", ["cases/**", "example/**", "tests/**"])
def test_line_endings_are_pinned(pattern):
    """A checkout with core.autocrlf=true rewrites every line ending: every digest
    changes and the signature stops verifying, while `record.py --verify` still answers
    `chain intact`. The first check passes, the second fails, and an honest reader
    concludes the signature is forged."""
    attrs = open(os.path.join(ROOT, ".gitattributes"), encoding="utf-8").read()
    assert re.search(rf"^{re.escape(pattern)}\s+-text\s*$", attrs, re.M), \
        f"{pattern} is not protected in .gitattributes"


def test_every_documented_flag_exists():
    """`--full-root` was documented for weeks and exits with an argparse error."""
    flags = set()
    for doc in DOCS:
        text = open(os.path.join(ROOT, doc), encoding="utf-8").read()
        for m in re.finditer(r"`(--[a-z][a-z-]+)`", text):
            flags.add(m.group(1))
    helps = {}
    for script in ("record.py", "measure.py", "build_page.py", "build_icon.py",
                   "build_note.py", "build_block.py", "build_bundle.py",
                   "build_attestation.py", "render_md.py", "render_pdf.py",
                   "review.py", "build_verify.py"):
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, script), "--help"],
                           capture_output=True, text=True, stdin=subprocess.DEVNULL)
        helps[script] = r.stdout + r.stderr
    blob = " ".join(helps.values()) + open(os.path.join(SCRIPTS, "record.py"),
                                           encoding="utf-8").read()
    missing = [f for f in sorted(flags) if f not in blob]
    assert not missing, f"documented but not implemented: {missing}"


def test_the_package_matches_the_folder():
    """The zip is what people install; the folder is what gets edited. Nothing keeps
    them in step, so a fix can sit in the repository while every download gets the old
    one."""
    r = subprocess.run([sys.executable, os.path.join(ROOT, "check_package.py")],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_the_package_check_refuses_a_tool_cache(tmp_path):
    """A `.pytest_cache` shipped inside a release zip once. It passed because the check
    ignored caches on both sides, so the folder and the package agreed about a directory
    neither should have carried — and its files are named README.md and .gitignore, which
    no basename-matching junk filter catches."""
    import zipfile
    z = tmp_path / "p.zip"
    with zipfile.ZipFile(z, "w") as f:
        f.writestr("colophon/SKILL.md", "x")
        f.writestr("colophon/.pytest_cache/README.md", "x")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "check_package.py"),
                        "--zip", str(z), "--dir", os.path.join(ROOT, "skill", "colophon")],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode != 0
    assert ".pytest_cache" in r.stdout, r.stdout


def test_the_repository_does_not_publish_a_front_page():
    """It used to. `index.html` was the front page because Pages was where
    colophonmethod.com pointed, and `.nojekyll` had stopped Jekyll rendering README.md
    into one. The site is served from its own source now and Pages is off, so a front page
    here would be a second homepage under the same name — reachable, indexable and
    orphaned at once, which is the combination that gets a stale page found and quoted.

    `.nojekyll` stays: zero bytes, and the guard that has to be in place before Pages
    rather than after, if it is ever turned back on."""
    assert os.path.exists(os.path.join(ROOT, ".nojekyll"))
    assert not os.path.exists(os.path.join(ROOT, "index.html")), \
        "the homepage is colophonmethod.com, served elsewhere — see deploy/README.md"


def test_a_missing_key_is_never_answered_by_making_one():
    """Issue #26. `seal.sh` said "generate one" unconditionally, and where the author is
    not sitting at the machine — a sandbox whose files are handed back at the end — that
    is the instruction that leaks the key. It does not fail loudly either: it produces a
    signature, and a verification page that reads VALID over it.

    The rule cannot depend on detecting the environment, because nothing can detect it
    reliably. It depends on where a key may be created: in the setup conversation, on a
    machine the author keeps, and nowhere else. Three files carry that caveat and none of
    them can be rewritten without this noticing — `SKILL.md` because Claude is what
    executes, and the two scripts so the warning survives outside the skill."""
    for rel in [("skill", "colophon", "SKILL.md"),
                ("skill", "colophon", "scripts", "seal.sh"),
                ("cli", "colophon.py")]:
        text = open(os.path.join(ROOT, *rel), encoding="utf-8").read()
        assert "a machine you keep" in text, f"{'/'.join(rel)} lost the ephemeral-key caveat"

    seal = open(os.path.join(ROOT, "skill", "colophon", "scripts", "seal.sh"),
                encoding="utf-8").read()
    branch = seal.split("if [ ! -f \"$KEY\" ]; then")[1].split("exit 1")[0]
    assert "ssh-keygen -t ed25519" in branch, "the no-key branch no longer says what fixes it"
    assert "sandbox" in branch, "the no-key branch no longer says where it must not be fixed"


@pytest.mark.parametrize("copy", [("skill", "colophon", "verify.html"),
                                  ("cases", "001", "verify.html"),
                                  ("cases", "002", "verify.html")])
def test_every_maintained_verifier_matches_the_built_one(copy):
    """build_bundle.py packs skill/colophon/verify.html into every bundle, and
    cases/NNN/verify.html is what a reader on the published page opens. A stale copy
    would ship an old verifier beside new evidence — and it would still say everything is
    fine, because an old verifier verifies an old case perfectly.

    The copy inside each case's bundle is deliberately not covered here: it is
    sealed, its digest is in a signed manifest, and it is the verifier as it stood when
    that case was closed. It is meant to go stale; these are not."""
    a = open(os.path.join(ROOT, "verifier", "verify.html"), "rb").read()
    b = open(os.path.join(ROOT, *copy), "rb").read()
    assert a == b, f"{'/'.join(copy)} is stale — run python3 verifier/build.py"


def _shared_parts():
    import re
    d = os.path.join(ROOT, "verifier")
    read = lambda n: open(os.path.join(d, n), encoding="utf-8").read()
    css = re.sub(r"\A/\*[\s\S]*?\*/\n+", "", read("components.css")).rstrip("\n")
    ui = re.sub(r"\A(//[^\n]*\n)+\n*", "", read("ui.js")).rstrip("\n")
    return css, ui


@pytest.mark.parametrize("shell", ["shell.html", "shell-site.html"])
def test_both_shells_provide_what_the_verifier_reaches_for(shell):
    """core.js and ui.js find their way around by four ids. A shell that drops one
    produces a page that loads, looks right and quietly does nothing — the failure
    that is hardest to notice, because there is nothing to notice.

    build.py refuses to build such a shell; this says so a second time, where
    somebody editing a shell will see it."""
    text = open(os.path.join(ROOT, "verifier", shell), encoding="utf-8").read()
    for element in ("drop", "dir", "fil", "out"):
        assert f'id="{element}"' in text, f"{shell} has no #{element}"
    for marker in ("/*__COMPONENTS__*/", "//__CORE__", "//__UI__"):
        assert marker in text, f"{shell} has no {marker}"


@pytest.mark.parametrize("built,shell", [("verify.html", "shell.html"),
                                         ("verify-site.html", "shell-site.html")])
def test_both_verifiers_carry_the_same_components_and_the_same_behaviour(built, shell):
    """The served page and the one that travels in a bundle differ in chrome and in
    palette. They must not differ in what they check or in what they show, and the
    way to keep that true is not to remember it: components.css and ui.js are single
    files inlined into both, and this asserts they arrived intact in each."""
    css, ui = _shared_parts()
    text = open(os.path.join(ROOT, "verifier", built), encoding="utf-8").read()
    assert css in text, f"{built} is stale or edited — run python3 verifier/build.py"
    assert ui in text, f"{built} is stale or edited — run python3 verifier/build.py"


def test_the_two_verifiers_are_not_the_same_file():
    """If they ever match byte for byte, one of the shells has stopped doing its job:
    either the served page lost its chrome, or the travelling copy grew some."""
    a = open(os.path.join(ROOT, "verifier", "verify.html"), "rb").read()
    b = open(os.path.join(ROOT, "verifier", "verify-site.html"), "rb").read()
    assert a != b


def test_the_travelling_verifier_names_no_website():
    """The copy sealed into a case has to still work in ten years with nothing
    answering. A link to a site is a dependency it must not acquire, and the site
    shell is where such links belong."""
    text = open(os.path.join(ROOT, "verifier", "verify.html"), encoding="utf-8").read()
    assert "colophonmethod.com" not in text


def test_every_script_declares_its_licence():
    """A case folder carries its own copies of the scripts, and a published case is
    read far from this repository: a file that travels alone and says nothing about
    its licence is a file nobody may reuse. One line, checked here so it cannot be
    forgotten on the next script added."""
    listing = subprocess.run(["git", "ls-files", "*.py", "*.sh"], cwd=ROOT,
                             capture_output=True, text=True)
    assert listing.returncode == 0, listing.stderr
    missing = []
    for name in listing.stdout.split():
        head = open(os.path.join(ROOT, name), encoding="utf-8").read(400)
        if "SPDX-License-Identifier: MIT" not in head:
            missing.append(name)
    assert not missing, f"no licence line: {missing}"


def test_the_readers_page_and_its_template_have_not_drifted():
    """`build_verify.py` carries the text of VERIFY.md because reference/ does not travel
    in a case folder and a case has to stay reproducible from its own scripts. Two copies
    of two thousand words are two things that drift, and the one that would drift silently
    is the one a reader receives."""
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "build_verify.py"),
                        "--template"], capture_output=True, text=True,
                       stdin=subprocess.DEVNULL)
    assert r.returncode == 0, r.stderr
    ref = open(os.path.join(ROOT, "skill", "colophon", "reference", "VERIFY.md"),
               encoding="utf-8").read()
    assert r.stdout == ref, "build_verify.py's template has drifted from reference/VERIFY.md"
