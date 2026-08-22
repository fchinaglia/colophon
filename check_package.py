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

Exit status 0 if identical, 1 otherwise. Suitable for a pre-commit hook or CI.
"""
import argparse
import hashlib
import os
import sys
import zipfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def folder_map(root):
    out = {}
    for base, _, files in os.walk(root):
        for f in files:
            if f.endswith(".pyc") or "__pycache__" in base:
                continue
            path = os.path.join(base, f)
            rel = os.path.relpath(path, os.path.dirname(root)).replace(os.sep, "/")
            out[rel] = digest(open(path, "rb").read())
    return out


def zip_map(path):
    out = {}
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if name.endswith("/") or name.endswith(".pyc") or "__pycache__" in name:
                continue
            out[name] = digest(z.read(name))
    return out


def main():
    p = argparse.ArgumentParser(description="Check the package against the skill folder.")
    p.add_argument("--zip", default="colophon.zip")
    p.add_argument("--dir", default="skill/colophon")
    a = p.parse_args()

    for path in (a.zip, a.dir):
        if not os.path.exists(path):
            sys.exit(f"missing {path}")

    z, f = zip_map(a.zip), folder_map(a.dir)

    only_zip = sorted(set(z) - set(f))
    only_dir = sorted(set(f) - set(z))
    differ = sorted(k for k in set(z) & set(f) if z[k] != f[k])

    for name in only_dir:
        print(f"  missing from the package: {name}")
    for name in only_zip:
        print(f"  in the package but not in the folder: {name}")
    for name in differ:
        print(f"  content differs: {name}")

    if only_zip or only_dir or differ:
        print(f"\n{a.zip} has drifted from {a.dir} — regenerate it before releasing:")
        print(f"  cd {os.path.dirname(a.dir) or '.'} && "
              f"zip -qr ../{os.path.basename(a.zip)} {os.path.basename(a.dir)} "
              f"-x '*.pyc' '*__pycache__*'")
        sys.exit(1)

    print(f"{a.zip} matches {a.dir} — {len(f)} files")


if __name__ == "__main__":
    main()
