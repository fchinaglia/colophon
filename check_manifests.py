#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
Check that the two plugin manifests agree, and that the version they carry is the one
the CHANGELOG last released.

`.claude-plugin/plugin.json` and the marketplace entry that describes the same plugin
state the same two facts twice, and nothing keeps them in step. Both matter to somebody
who is not you:

  version      `claude plugin update` compares what is installed against what the
               manifest declares, so one left behind at the previous number does not
               fail — it quietly stops offering the update.
  description  what a reader sees before installing, and what the directory review
               reads to decide whether the plugin discloses what it actually does.
               Here it is also where the key and the timestamp authority are named.

    python3 check_manifests.py                     # from the repository root

The CHANGELOG is the source of truth for the version, and the newest *released* heading
is the one that counts — `## [Unreleased]` is skipped, so a working tree with unreleased
changes is expected to sit at the last released number and passes. The description has no
third source: the two manifests only have to say the same thing.

Exit status 0 if everything agrees, 1 otherwise.
"""
import argparse
import json
import re
import sys

RELEASED = re.compile(r"^## \[(\d+\.\d+\.\d+[^\]]*)\]", re.M)


def changelog_version(path):
    m = RELEASED.search(open(path, encoding="utf-8").read())
    if not m:
        sys.exit(f"no released version heading in {path}")
    return m.group(1)


def marketplace_entry(path, name):
    for e in json.load(open(path, encoding="utf-8")).get("plugins", []):
        if e.get("name") == name:
            return e
    sys.exit(f"no plugin named {name!r} in {path}")


def report(field, found):
    """Print one field's sources and say whether they agree."""
    if len(set(found.values())) == 1:
        return True
    print(f"the {field} does not agree:")
    for where, value in found.items():
        print(f"  {where}")
        print(f"    {value}")
    print()
    return False


def main():
    p = argparse.ArgumentParser(description="Check that the plugin manifests agree.")
    p.add_argument("--plugin", default=".claude-plugin/plugin.json")
    p.add_argument("--marketplace", default=".claude-plugin/marketplace.json")
    p.add_argument("--changelog", default="CHANGELOG.md")
    a = p.parse_args()

    plugin = json.load(open(a.plugin, encoding="utf-8"))
    entry = marketplace_entry(a.marketplace, plugin.get("name"))
    market = f"{a.marketplace} ({plugin.get('name')})"

    version = {
        a.changelog: changelog_version(a.changelog),
        a.plugin: plugin.get("version"),
        market: entry.get("version"),
    }
    description = {
        a.plugin: plugin.get("description"),
        market: entry.get("description"),
    }

    ok = report("version", version) & report("description", description)

    if not ok:
        print(f"the manifests have drifted — for the version, {a.changelog} is the source\n"
              f"of truth and its newest released heading is what both have to match.")
        sys.exit(1)

    print(f"version {version[a.plugin]}, and the description, agree across "
          f"{a.changelog},\n{a.plugin} and the marketplace entry")


if __name__ == "__main__":
    main()
