#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Inline the shared parts into each shell and write the self-contained verifiers.

    python3 verifier/build.py

The verifier ships as ONE file so a reader can save it and keep verifying offline,
forever, with no network and no dependencies. core.js stays separate in the repository
only so that verifier/test.js can exercise it directly.

There are two shells and one of everything else:

    components.css ─┐
    core.js ────────┼──► shell.html      ──► verify.html      (4 copies, identical)
    ui.js ──────────┴──► shell-site.html ──► verify-site.html (served by the site)

A shell supplies a palette and the chrome around the tool, and provides four
elements: #drop #dir #fil #out. Everything else — what the page checks, what it
renders, what its cards and badges look like — is inlined from the shared files
into both. **The two differ in chrome and palette, never in behaviour**, and that
is a property of the build rather than a promise somebody has to keep.

Why a second shell at all: the copy that travels inside a case must carry nothing
of any website, because it has to still work in ten years with no network and no
site answering. The copy served at a URL has the opposite job — a reader who lands
on it should be able to tell where they are and get back. Byte-identity was
serving the first need and failing the second.

It is written once per place that serves it, to the same bytes: verifier/verify.html; skill/colophon/
verify.html, which is the copy the skill hands to a case at Opening and build_bundle.py
packs into the tar; and one per published case folder, which is what a reader on the published
page opens to check the bundle beside it. Copies of one build are not versions — there is one source, and tests/repo asserts they match — but a hand-edited one
would be, which is why nobody should edit any of them.

The copy sealed inside a case's bundle is a fourth and is not maintained: it is the
verifier as it stood when that case was closed, its digest is in a signed manifest, and
it is meant to go stale.

Prints the digest of what it wrote: publish that alongside, so the verifier is itself
verifiable.
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


# The four elements a shell must provide. core.js and ui.js reach for these by id,
# so a shell that drops one produces a page that loads and quietly does nothing.
REQUIRED_IDS = ("drop", "dir", "fil", "out")


def read(name):
    return open(os.path.join(HERE, name), encoding="utf-8").read()


def strip_header(text, block):
    """Drop the file's own header comment: it explains the file to whoever opens
    it in the repository, and means nothing inlined into a built page."""
    if block:
        return re.sub(r"\A/\*[\s\S]*?\*/\n+", "", text)
    return re.sub(r"\A(//[^\n]*\n)+\n*", "", text)


def build(shell_name, core, components, ui):
    shell = read(shell_name)
    for marker in ("/*__COMPONENTS__*/", "//__CORE__", "//__UI__"):
        if marker not in shell:
            raise ValueError(f"{shell_name} has no {marker} marker")
    missing = [i for i in REQUIRED_IDS if f'id="{i}"' not in shell]
    if missing:
        raise ValueError(f"{shell_name} is missing required elements: "
                         + ", ".join("#" + i for i in missing))
    return (shell.replace("/*__COMPONENTS__*/", components)
                 .replace("//__CORE__", core)
                 .replace("//__UI__", ui))


def write(html, targets):
    for out in targets:
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
    data = open(targets[0], "rb").read()
    print(f"  {len(data):,} bytes")
    print(f"  sha256 {hashlib.sha256(data).hexdigest()}")
    for out in targets:
        print(f"    wrote {os.path.relpath(os.path.abspath(out), os.path.join(HERE, '..'))}")


def main():
    core = read("core.js")
    components = strip_header(read("components.css"), block=True).rstrip("\n")
    ui = strip_header(read("ui.js"), block=False).rstrip("\n")

    # The module export tail is meaningless in a browser and would throw if `module`
    # were somehow defined. Strip it rather than guard it.
    core = re.sub(r"\nif \(typeof module !== 'undefined'\) \{[\s\S]*?\n\}\n?$", "\n", core)

    # A literal </script> anywhere in the script body would close the block early.
    for name, text in (("core.js", core), ("ui.js", ui)):
        if "</script" in text.lower():
            print(f"{name} contains a literal </script>", file=sys.stderr)
            return 1

    try:
        bundled = build("shell.html", core, components, ui)
        served = build("shell-site.html", core, components, ui)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1

    print("verify.html — the copy that travels, and the one to trust")
    write(bundled, [os.path.join(HERE, "verify.html"),
                    os.path.join(HERE, "..", "skill", "colophon", "verify.html"),
                    os.path.join(HERE, "..", "cases", "001", "verify.html"),
                    os.path.join(HERE, "..", "cases", "002", "verify.html")])
    print("verify-site.html — the copy served at a URL, chrome and palette apart")
    write(served, [os.path.join(HERE, "verify-site.html")])
    print("Publish both digests alongside: a verifier nobody can check is not one.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
