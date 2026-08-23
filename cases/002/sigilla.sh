#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
# Sigilla il registro: firma Ed25519 + marca temporale RFC 3161 + ancoraggio Bitcoin.
#
# Produce tre file DETACHED accanto al registro, che resta intatto e leggibile:
#   <file>.sig   chi   — firma Ed25519 (ssh-keygen), gratis
#   <file>.tsr   quando — marca temporale RFC 3161
#   <file>.ots   quando — ancoraggio OpenTimestamps su Bitcoin, gratis, ridondante
#
# Non produce .p7m: incapsulare il registro lo renderebbe illeggibile senza la
# toolchain italiana, e un log vive di essere ispezionabile.
#
# Uso:  bash sigilla.sh eventi.jsonl
#
# Requisiti una tantum:
#   ssh-keygen -t ed25519 -f ~/.ssh/colophon     # chiave dedicata
#   pip install opentimestamps-client               # opzionale ma consigliato
# e pubblicare la chiave pubblica (~/.ssh/colophon.pub) in un posto stabile
# e tuo: sito, profilo GitHub, pagina LinkedIn.

# Compatibile anche se invocato con `sh`: pipefail non e POSIX.
set -eu
(set -o pipefail) 2>/dev/null && set -o pipefail || true

FILE="${1:?uso: bash sigilla.sh <file>}"
KEY="${COLOPHON_KEY:-$HOME/.ssh/colophon}"
# TSA gratuita, senza account. Non dà presunzione eIDAS: per quella serve una
# TSA qualificata e credenziali a lotto prepagato.
TSA_URL="${COLOPHON_TSA:-https://freetsa.org/tsr}"

echo "== impronta =="
shasum -a 256 "$FILE" | tee "$FILE.sha256"

echo
echo "== firma Ed25519 =="
if [ -f "$KEY" ]; then
  rm -f "$FILE.sig"                       # ssh-keygen non sovrascrive: chiederebbe conferma
  ssh-keygen -Y sign -f "$KEY" -n colophon "$FILE" >/dev/null
  # autocontrollo: una firma che non verifica e peggio di nessuna firma
  if ssh-keygen -Y check-novalidate -n colophon -s "$FILE.sig" < "$FILE" >/dev/null 2>&1; then
    echo "   $FILE.sig  (verificata)"
  else
    echo "   ! la firma prodotta NON verifica: fermati e capisci perche" >&2
    exit 1
  fi
else
  echo "   ! chiave assente in $KEY — genera con:"
  echo "     ssh-keygen -t ed25519 -f $KEY -C colophon"
fi

echo
echo "== marca temporale (RFC 3161) =="
openssl ts -query -data "$FILE" -sha512 -no_nonce -cert -out "$FILE.tsq"
if curl -sS -H "Content-Type: application/timestamp-query" \
        --data-binary "@$FILE.tsq" "$TSA_URL" -o "$FILE.tsr"; then
  echo "   $FILE.tsr  ($TSA_URL)"
  openssl ts -reply -in "$FILE.tsr" -text 2>/dev/null | grep -E "Time stamp|Status" || true
else
  echo "   ! TSA non raggiungibile"
fi
rm -f "$FILE.tsq"

echo
echo "== ancoraggio OpenTimestamps =="
if command -v ots >/dev/null 2>&1; then
  ots stamp "$FILE" && echo "   $FILE.ots (conferma su Bitcoin in qualche ora)"
else
  echo "   ! ots non installato — pip install opentimestamps-client"
fi

echo
echo "Fatto. Conserva insieme: $FILE, .sig, .tsr, .ots, .sha256"
echo "e pubblica VERIFY.md accanto, con la tua chiave pubblica."
