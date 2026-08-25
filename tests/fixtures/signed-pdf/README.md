# Two signed PDFs, in the two possible orders

The verifier reads a colophon PDF and checks the signature over it. These are what it is
checked against, and the pair is the point:

| | |
|---|---|
| `embed-then-sign.pdf` | the record was embedded, then the document was signed — the signature covers the attachment |
| `sign-then-embed.pdf` | the document was signed, then the record was appended — the signature is still arithmetically valid and covers **nothing of the evidence** |

The second is the failure `SKILL.md` warns about in one sentence (*embed, then sign, in
that order*) and the reason this check exists at all: both files show a valid signature to
anything that only asks whether the signature verifies.

**The certificate is worthless and says so in its own subject** — `CN=Fabio Chinaglia
(TEST, not a real certificate)`, self-signed, generated for these two files. Nothing here
should ever be treated as a signed document; `test-cert.pem` is committed so the fixtures
can be read without regenerating them.

To rebuild after changing the signer:

```bash
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out test-cert.pem -days 3650 -nodes \
  -subj "/C=IT/CN=Fabio Chinaglia (TEST, not a real certificate)/emailAddress=test@example.invalid"
python3 sign_pdf.py <a pdf> key.pem test-cert.pem out.pdf
```

`sign_pdf.py` needs `cryptography`, which is why it is a fixture generator and not a test:
the suite reads what is committed here and installs nothing.
