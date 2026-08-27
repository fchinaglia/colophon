#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
# Seal the register: Ed25519 signature + RFC 3161 timestamp + Bitcoin anchoring.
#
# Produces three DETACHED files next to the register, which stays intact and
# readable:
#   <file>.sig   sealed by  — Ed25519 signature (ssh-keygen), free
#   <file>.tsr   when       — RFC 3161 timestamp
#   <file>.ots   when       — OpenTimestamps anchor on Bitcoin, free, redundant
#
# `sealed by`, not `who`. The key is published nowhere, so on its own the signature
# names nobody — it says one key closed this register in one act, and that the same
# key closed the author's other cases. Naming a person is the qualified signature's
# job, below. reference/VERIFY.md §2 says why this one is still worth making.
#
# And it copies the public half of the key in as colophon.pub, so the signature can
# be checked by whoever is holding the bundle, with no network and no address to keep
# alive. That copy says the register was signed by whoever holds this key; it cannot
# say whose key it is, and it does not pretend to. What says that is a qualified
# electronic signature over the PDF the bundle is attached to.
#
# It does not produce a .p7m: wrapping the register would make it unreadable
# without a specific toolchain, and a log lives by being inspectable.
#
# Usage:  bash seal.sh events.jsonl
#
# One-time setup:
#   ssh-keygen -t ed25519 -f ~/.ssh/colophon      # a dedicated key, on a machine you keep
#   pip install opentimestamps-client             # optional but recommended
# The public key needs publishing nowhere. It goes in the bundle, from here.

# Works even when invoked with `sh`: pipefail is not POSIX.
set -eu
(set -o pipefail) 2>/dev/null && set -o pipefail || true

FILE="${1:?usage: bash seal.sh <file>}"

# WHICH KEY SIGNS, and why this is more than a default.
#
# COLOPHON_KEY wins, as it always has. Then whatever `colophon setup` recorded, and that
# clause is the fix for a fault that reached the reader: setup writes key_path and the
# fingerprint of that key into author.json, case.json carries the fingerprint from there,
# and reference/VERIFY.md tells the reader to compare it against colophon.pub — which
# this script copies from the key that actually signed. An author who set up with a key
# elsewhere published a fingerprint naming a key that did not sign, and the reader's own
# check failed on an honest case. A failed check of that shape reads as forgery.
#
# python3 reads the config, because a regex over JSON is a comparison of text where a
# fact is meant, and that is the mistake this repository keeps filing bugs about. Where
# there is no python3 nothing is lost: the default stands, exactly as before, and the
# fingerprint guard below still catches a divergence rather than shipping it.
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/colophon/author.json"
CONFIGURED=""
if [ -z "${COLOPHON_KEY:-}" ] && [ -f "$CONFIG" ] && command -v python3 >/dev/null 2>&1; then
  CONFIGURED="$(python3 -c 'import json, sys
try:
    v = json.load(open(sys.argv[1], encoding="utf-8")).get("key_path")
except Exception:
    v = None
print(v if isinstance(v, str) else "")' "$CONFIG" 2>/dev/null || true)"
fi
KEY="${COLOPHON_KEY:-${CONFIGURED:-$HOME/.ssh/colophon}}"
# Free, no account needed, and — the part that matters — its chain verifies against the
# certificate bundle a reader already has, so `openssl ts -verify` works with no setup.
# freetsa.org also grants tokens, but nothing verifies one without first hunting down its
# CA certificate, which is how a case shipped a timestamp no reader could check.
# Neither carries an eIDAS presumption: that needs a qualified TSA and prepaid credentials.
TSA_URL="${COLOPHON_TSA:-http://timestamp.digicert.com}"

echo "== digest =="
shasum -a 256 "$FILE" | tee "$FILE.sha256"

echo
echo "== Ed25519 signature =="
# Whatever happens here, an old signature must not survive it. A .sig from an earlier
# sealing sits next to the register looking exactly like a fresh one, and it verifies —
# against a shorter register. That is the one failure this script must not leave behind.
rm -f "$FILE.sig"
if [ ! -f "$KEY" ]; then
  echo "   ! no key at $KEY — on a machine you keep, generate one with:" >&2
  echo "     ssh-keygen -t ed25519 -f $KEY -C colophon" >&2
  echo "   ! only there. In a sandbox or a session whose files are handed back at the" >&2
  echo "     end, a key made now has already travelled by the time you hold it, and the" >&2
  echo "     signature would say nothing while looking like it said everything. Stop" >&2
  echo "     here instead: the register and the measurement are unaffected, and the" >&2
  echo "     technical line has a state for a case that is not sealed yet." >&2
  echo "   ! any earlier signature has been removed: it did not cover this register" >&2
  exit 1
fi
# THE COMPARISON THE READER IS TOLD TO MAKE, MADE HERE INSTEAD OF IN THEIR HANDS.
# reference/VERIFY.md sends them to `ssh-keygen -lf colophon.pub` and case.json's
# key_fingerprint. This script copies colophon.pub from the key that signs, so a case
# declaring a different one fails that check after publication, in front of somebody who
# has no way to ask what happened. Refuse before signing instead: nothing is written, and
# the register and the measurement are untouched.
CASE=""
for c in "$(dirname "$FILE")/case.json" "$(dirname "$FILE")/caso.json"; do
  [ -f "$c" ] && CASE="$c" && break
done
if [ -n "$CASE" ] && [ -f "$KEY.pub" ]; then
  if command -v python3 >/dev/null 2>&1; then
    DECLARED="$(python3 -c 'import json, sys
try:
    v = json.load(open(sys.argv[1], encoding="utf-8")).get("key_fingerprint")
except Exception:
    v = None
print(v if isinstance(v, str) else "")' "$CASE" 2>/dev/null || true)"
    SIGNING="$(ssh-keygen -lf "$KEY.pub" 2>/dev/null | awk "{print \$2}")"
    if [ -n "$DECLARED" ] && [ -n "$SIGNING" ] && [ "$DECLARED" != "$SIGNING" ]; then
      echo "   ! $(basename "$CASE") declares a key this signature would not match:" >&2
      echo "       declared  $DECLARED" >&2
      echo "       signing   $SIGNING   ($KEY)" >&2
      echo "   ! a reader is told to compare those two, and theirs is the check that" >&2
      echo "     would fail. Either seal with the declared key, or correct the case —" >&2
      echo "     and if the case is already sealed, that correction is a reopening." >&2
      echo "   ! nothing has been written: the register and the measurement are as they" >&2
      echo "     were, and any earlier signature has been removed because it did not" >&2
      echo "     cover this register" >&2
      exit 1
    fi
  else
    echo "   no python3: cannot compare the fingerprint this case declares with the key" >&2
    echo "   about to sign. Check it by hand before publishing." >&2
  fi
fi

# A passphrase-protected key makes ssh-keygen prompt, and a prompt in a script that is
# not attached to a terminal simply hangs. Say so before it happens.
if ! ssh-keygen -y -P "" -f "$KEY" >/dev/null 2>&1 && ! ssh-add -l 2>/dev/null | grep -q .; then
  echo "   the key has a passphrase and the agent is empty: ssh-keygen will ask for it." >&2
  echo "   to avoid the prompt:  ssh-add ${SSH_ADD_FLAGS:---apple-use-keychain} $KEY" >&2
fi
if ! ssh-keygen -Y sign -f "$KEY" -n colophon "$FILE" >/dev/null; then
  rm -f "$FILE.sig"
  echo "   ! signing failed — wrong passphrase, or no terminal to ask on" >&2
  exit 1
fi
# self-check: a signature that does not verify is worse than no signature
if ssh-keygen -Y check-novalidate -n colophon -s "$FILE.sig" < "$FILE" >/dev/null 2>&1; then
  echo "   $FILE.sig  (verified)"
else
  rm -f "$FILE.sig"
  echo "   ! the signature produced does NOT verify: stop and find out why" >&2
  exit 1
fi

# The key travels with the evidence, because there is nowhere else for a reader to get
# it. Without this the verifier falls back to the key embedded in the signature, which
# verifies just as well and tells a reader even less: it cannot be compared with the
# fingerprint case.json declares, and that comparison is inside the signed manifest.
DIR="$(dirname "$FILE")"
if [ -f "$KEY.pub" ]; then
  cp "$KEY.pub" "$DIR/colophon.pub"
  echo "   $DIR/colophon.pub  (the key a reader checks it against, offline)"
else
  echo "   ! no $KEY.pub — the bundle will carry no key and the reader will fall" >&2
  echo "     back to the one inside the signature" >&2
fi

echo
echo "== timestamp (RFC 3161) =="
openssl ts -query -data "$FILE" -sha512 -no_nonce -cert -out "$FILE.tsq"
# With no deadline this call can hang for as long as the TSA feels like taking, and a
# sealing script that never returns is one nobody finishes running.
if curl -sS --max-time "${COLOPHON_TSA_TIMEOUT:-30}" \
        -H "Content-Type: application/timestamp-query" \
        --data-binary "@$FILE.tsq" "$TSA_URL" -o "$FILE.tsr"; then
  echo "   $FILE.tsr  ($TSA_URL)"
  openssl ts -reply -in "$FILE.tsr" -text 2>/dev/null | grep -E "Time stamp|Status" || true
else
  rm -f "$FILE.tsr"
  echo "   ! TSA unreachable or too slow — the signature above stands; run the" >&2
  echo "     timestamp again later. It fixes the date, which the signature does not" >&2
fi
rm -f "$FILE.tsq"

echo
echo "== OpenTimestamps anchoring =="
if command -v ots >/dev/null 2>&1; then
  rm -f "$FILE.ots"                       # never keep an anchor of an older register
  # `ots stamp` submits; it does not anchor. Calendars batch submissions into a Bitcoin
  # transaction, and they have been observed to accept a submission and then never anchor
  # it, silently. On its own a .ots file proves nothing, so do not let it sound like proof.
  if ots stamp "$FILE"; then
    echo "   $FILE.ots  (submitted — NOT yet anchored)"
    echo "   ! tomorrow, before publishing, run:"
    echo "       ots upgrade $FILE.ots && ots verify $FILE.ots"
  fi
else
  echo "   ! ots not installed — pip install opentimestamps-client"
fi

echo
echo "Done. Keep together: $FILE, .sig, .tsr, .ots, .sha256, colophon.pub"
echo "and VERIFY.md alongside. build_bundle.py packs all of it into one tar."
if [ -f "$FILE.ots" ]; then
  echo "The Bitcoin anchor is only submitted. Run 'ots upgrade $FILE.ots' before you"
  echo "publish anything that claims one."
fi
