#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
Check that colophon.zip is exactly the skill folder.

The zip is what people install. The folder is what you edit. Nothing keeps the two
in step, so a fix can live in the repository for months while everyone who installs
from the release keeps getting the old one. This fails loudly when they diverge.

    python3 check_package.py                    # from the repository root
    python3 check_package.py --zip colophon.zip --dir skill/colophon

It also refuses a package that carries junk. Finder writes a .DS_Store into every
folder you so much as look at, .gitignore hides it from git but not from zip, and a
check that only compares the two sides reports OK when both carry the same rubbish.
So junk is tolerated in the working folder, where it is not your fault, and rejected
in the package, which is what ships.

Exit status 0 if identical and clean, 1 otherwise. Suitable for a pre-commit hook or CI.
"""
import argparse
import fnmatch
import hashlib
import os
import sys
import zipfile

# Mirrors .gitignore. These never belong in the package.
JUNK = (".DS_Store", "._*", ".Spotlight-V100", ".Trashes", "Thumbs.db",
        "desktop.ini", "*.swp", "*~")

# zip -x matches whole paths, so a bare name needs a leading star; one that has
# its own does not.
EXCLUDE = " ".join(
    f"'{p}'" for p in ("*.pyc", "*__pycache__*")
    + tuple(j if j.startswith("*") else f"*{j}" for j in JUNK))


def is_junk(name):
    base = os.path.basename(name)
    return any(fnmatch.fnmatch(base, pattern) for pattern in JUNK)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def folder_map(root):
    out = {}
    for base, _, files in os.walk(root):
        for f in files:
            # Junk in the folder is Finder's doing, not the author's: ignore it here
            # and let the package be the place where it is not allowed.
            if f.endswith(".pyc") or "__pycache__" in base or is_junk(f):
                continue
            path = os.path.join(base, f)
            rel = os.path.relpath(path, os.path.dirname(root)).replace(os.sep, "/")
            out[rel] = digest(open(path, "rb").read())
    return out


def zip_map(path):
    """Returns (files, junk). Junk stays out of the comparison and is reported."""
    out, junk = {}, []
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if name.endswith("/") or name.endswith(".pyc") or "__pycache__" in name:
                continue
            if is_junk(name):
                junk.append(name)
                continue
            out[name] = digest(z.read(name))
    return out, junk


def main():
    p = argparse.ArgumentParser(description="Check the package against the skill folder.")
    p.add_argument("--zip", default="colophon.zip")
    p.add_argument("--dir", default="skill/colophon")
    a = p.parse_args()

    for path in (a.zip, a.dir):
        if not os.path.exists(path):
            sys.exit(f"missing {path}")

    (z, junk), f = zip_map(a.zip), folder_map(a.dir)

    only_zip = sorted(set(z) - set(f))
    only_dir = sorted(set(f) - set(z))
    differ = sorted(k for k in set(z) & set(f) if z[k] != f[k])

    for name in only_dir:
        print(f"  missing from the package: {name}")
    for name in only_zip:
        print(f"  in the package but not in the folder: {name}")
    for name in differ:
        print(f"  content differs: {name}")
    for name in junk:
        print(f"  junk in the package: {name}")

    if only_zip or only_dir or differ or junk:
        why = "carries junk" if junk and not (only_zip or only_dir or differ) else \
              f"has drifted from {a.dir}"
        print(f"\n{a.zip} {why} — regenerate it before releasing:")
        print(f"  rm -f {a.zip} && cd {os.path.dirname(a.dir) or '.'} && "
              f"zip -qr ../{os.path.basename(a.zip)} {os.path.basename(a.dir)} "
              f"-x {EXCLUDE}")
        sys.exit(1)

    print(f"{a.zip} matches {a.dir} — {len(f)} files, no junk")


if __name__ == "__main__":
    main()
