#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Inline core.js into shell.html and write the single self-contained verify.html.

    python3 verifier/build.py

The verifier ships as ONE file so a reader can save it and keep verifying offline,
forever, with no network and no dependencies. core.js stays separate in the repository
only so that verifier/test.js can exercise it directly.

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
    out = os.path.join(HERE, "verify.html")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)

    data = open(out, "rb").read()
    print(f"verify.html  {len(data):,} bytes")
    print(f"sha256       {hashlib.sha256(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
