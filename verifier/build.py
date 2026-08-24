#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Inline core.js into shell.html and write the single self-contained verify.html.

    python3 verifier/build.py

The verifier ships as ONE file so a reader can save it and keep verifying offline,
forever, with no network and no dependencies. core.js stays separate in the repository
only so that verifier/test.js can exercise it directly.

It is written three times, to the same bytes: verifier/verify.html; skill/colophon/
verify.html, which is the copy the skill hands to a case at Opening and build_bundle.py
packs into the tar; and validation/verify.html, which is what a reader on the published
page opens to check the bundle beside it. Three copies of one build are not three
versions — there is one source, and tests/repo asserts they match — but a hand-edited one
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


def main():
    core = open(os.path.join(HERE, "core.js"), encoding="utf-8").read()
    shell = open(os.path.join(HERE, "shell.html"), encoding="utf-8").read()

    if "//__CORE__" not in shell:
        print("shell.html has no //__CORE__ marker", file=sys.stderr)
        return 1

    # The module export tail is meaningless in a browser and would throw if `module`
    # were somehow defined. Strip it rather than guard it.
    core = re.sub(r"\nif \(typeof module !== 'undefined'\) \{[\s\S]*?\n\}\n?$", "\n", core)

    # A literal </script> anywhere in the script body would close the block early.
    if "</script" in core.lower():
        print("core.js contains a literal </script>", file=sys.stderr)
        return 1

    html = shell.replace("//__CORE__", core)
    targets = [os.path.join(HERE, "verify.html"),
               os.path.join(HERE, "..", "skill", "colophon", "verify.html"),
               os.path.join(HERE, "..", "validation", "verify.html")]
    for out in targets:
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(html)

    data = open(targets[0], "rb").read()
    print(f"verify.html  {len(data):,} bytes")
    print(f"sha256       {hashlib.sha256(data).hexdigest()}")
    for out in targets:
        print(f"  wrote     {os.path.relpath(os.path.abspath(out), os.path.join(HERE, '..'))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
