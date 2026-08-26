#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""Sign a PDF with a detached CMS, as an incremental update. Test fixtures only.

This is deliberately not part of the method: colophon does not sign PDFs, a qualified
provider does. What it produces is a structurally real PAdES-style signature — the
/ByteRange hole, the detached CMS over the bytes around it — so the verifier can be
tested against something with the shape of the thing, signed by a certificate that is
worth nothing and says so in its own subject.
"""
import re, sys
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import Encoding, pkcs7, load_pem_private_key
from cryptography import x509

src, key_pem, cert_pem, out = sys.argv[1:5]
pdf = open(src, "rb").read()
key = load_pem_private_key(open(key_pem, "rb").read(), password=None)
cert = x509.load_pem_x509_certificate(open(cert_pem, "rb").read())

size = int(re.findall(rb"/Size\s+(\d+)", pdf)[-1])
root = int(re.findall(rb"/Root\s+(\d+)\s+0\s+R", pdf)[-1])
prev = int(re.findall(rb"startxref\s+(\d+)", pdf)[-1])
m = re.search(rb"(?<![0-9])" + str(root).encode() + rb"\s+0\s+obj\s*(<<[\s\S]*?>>)\s*endobj", pdf)
catalog = m.group(1)

n_sig, n_fld = size, size + 1
HOLE = 8192                                    # hex characters reserved for /Contents

def build(byterange):
    out_ = [pdf]
    pos = len(pdf)
    offs = {}
    def add(num, text):
        nonlocal pos
        offs[num] = pos
        c = b"%d 0 obj\n" % num + text + b"\nendobj\n"
        out_.append(c); pos += len(c)
    add(n_sig, b"<< /Type /Sig /Filter /Adobe.PPKLite /SubFilter /ETSI.CAdES.detached"
               b" /ByteRange " + byterange +
               b" /Contents <" + b"0" * HOLE + b">"
               b" /Name (Fabio Chinaglia TEST) /Reason (fixture) >>")
    add(n_fld, b"<< /Type /Annot /Subtype /Widget /FT /Sig /T (Signature1)"
               b" /Rect [0 0 0 0] /F 132 /V %d 0 R >>" % n_sig)
    add(root, catalog[:-2] + b" /AcroForm << /Fields [%d 0 R] /SigFlags 3 >> >>" % n_fld)
    xref_at = pos
    rows = [b"xref"]
    for n in sorted(offs):
        rows += [b"%d 1" % n, b"%010d 00000 n " % offs[n]]
    tail = b"\n".join(rows) + (b"\ntrailer\n<< /Size %d /Root %d 0 R /Prev %d >>\n"
                               b"startxref\n%d\n%%%%EOF\n" % (n_fld + 1, root, prev, xref_at))
    out_.append(tail)
    return b"".join(out_)

# Two passes: the ByteRange has to state offsets that only exist once it is written, so
# the first pass fixes the layout with a same-width placeholder and the second fills it in.
placeholder = b"[0000000000 0000000000 0000000000 0000000000]"
draft = build(placeholder)
lo = draft.index(b"/Contents <") + len(b"/Contents ")
hi = lo + HOLE + 2
br = b"[%010d %010d %010d %010d]" % (0, lo, hi, len(draft) - hi)
assert len(br) == len(placeholder)
final = build(br)
assert final.index(b"/Contents <") + len(b"/Contents ") == lo

signed = final[:lo] + final[hi:]
cms = (pkcs7.PKCS7SignatureBuilder().set_data(signed)
       .add_signer(cert, key, hashes.SHA256())
       .sign(Encoding.DER, [pkcs7.PKCS7Options.DetachedSignature,
                            pkcs7.PKCS7Options.Binary,
                            pkcs7.PKCS7Options.NoCapabilities]))
assert len(cms) * 2 <= HOLE, f"CMS is {len(cms)} bytes, hole holds {HOLE // 2}"
filled = cms.hex().encode() + b"0" * (HOLE - len(cms) * 2)
open(out, "wb").write(final[:lo + 1] + filled + final[lo + 1 + HOLE:])
print(f"signed -> {out}  ({len(cms)} byte CMS, ByteRange {br.decode()})")
