#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
# Seal the register: Ed25519 signature + RFC 3161 timestamp + Bitcoin anchoring.
#
# Produces three DETACHED files next to the register, which stays intact and
# readable:
#   <file>.sig   who   — Ed25519 signature (ssh-keygen), free
#   <file>.tsr   when  — RFC 3161 timestamp
#   <file>.ots   when  — OpenTimestamps anchor on Bitcoin, free, redundant
#
# It does not produce a .p7m: wrapping the register would make it unreadable
# without a specific toolchain, and a log lives by being inspectable.
#
# Usage:  bash seal.sh events.jsonl
#
# One-time setup:
#   ssh-keygen -t ed25519 -f ~/.ssh/colophon      # a dedicated key
#   pip install opentimestamps-client             # optional but recommended
# then publish the public key (~/.ssh/colophon.pub) somewhere stable and
# yours: your site, GitHub profile, LinkedIn page.

# Works even when invoked with `sh`: pipefail is not POSIX.
set -eu
(set -o pipefail) 2>/dev/null && set -o pipefail || true

FILE="${1:?usage: bash seal.sh <file>}"
KEY="${COLOPHON_KEY:-$HOME/.ssh/colophon}"
# Free TSA, no account needed. It carries no eIDAS presumption: for that you
# need a qualified TSA and prepaid credentials.
TSA_URL="${COLOPHON_TSA:-https://freetsa.org/tsr}"

echo "== digest =="
shasum -a 256 "$FILE" | tee "$FILE.sha256"

echo
echo "== Ed25519 signature =="
if [ -f "$KEY" ]; then
  rm -f "$FILE.sig"                       # ssh-keygen will not overwrite: it would prompt
  ssh-keygen -Y sign -f "$KEY" -n colophon "$FILE" >/dev/null
  # self-check: a signature that does not verify is worse than no signature
  if ssh-keygen -Y check-novalidate -n colophon -s "$FILE.sig" < "$FILE" >/dev/null 2>&1; then
    echo "   $FILE.sig  (verified)"
  else
    rm -f "$FILE.sig"
    echo "   ! the signature produced does NOT verify: stop and find out why" >&2
    exit 1
  fi
else
  echo "   ! no key at $KEY — generate one with:"
  echo "     ssh-keygen -t ed25519 -f $KEY -C colophon"
fi

echo
echo "== timestamp (RFC 3161) =="
openssl ts -query -data "$FILE" -sha512 -no_nonce -cert -out "$FILE.tsq"
if curl -sS -H "Content-Type: application/timestamp-query" \
        --data-binary "@$FILE.tsq" "$TSA_URL" -o "$FILE.tsr"; then
  echo "   $FILE.tsr  ($TSA_URL)"
  openssl ts -reply -in "$FILE.tsr" -text 2>/dev/null | grep -E "Time stamp|Status" || true
else
  echo "   ! TSA unreachable"
fi
rm -f "$FILE.tsq"

echo
echo "== OpenTimestamps anchoring =="
if command -v ots >/dev/null 2>&1; then
  ots stamp "$FILE" && echo "   $FILE.ots (confirmed on Bitcoin within a few hours)"
else
  echo "   ! ots not installed — pip install opentimestamps-client"
fi

echo
echo "Done. Keep together: $FILE, .sig, .tsr, .ots, .sha256"
echo "and publish VERIFY.md alongside, with your public key."
