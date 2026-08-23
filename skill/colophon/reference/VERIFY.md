# How to verify this register

*Template to publish next to the register. Replace the parts in square brackets.*

---

The file `events.jsonl` contains the register of the interventions made while writing
[title]. Each line is an event; each event contains the fingerprint of the previous one,
so the sequence is a chain: **altering a past event invalidates every hash that follows
it**.

Next to the register you will find three files that let you verify it without taking my
word for anything.

## 1. The chain has not been altered

```bash
python3 record.py --verify
```

It recomputes the whole chain and reports the first broken link. It must answer
`chain intact`, with the current root.

## 2. The register is mine

The signature is Ed25519, detached, in the `.sig` file. My public key is published at
**[https://your-domain/.well-known/colophon/keys]** — on a domain I control, and
deliberately not inside this folder. Fetch it and check the signature against it:

```bash
curl -sO [https://your-domain/.well-known/colophon/keys]
ssh-keygen -Y verify -f keys -I [your-email] -n colophon \
           -Overify-time=[YYYYMMDD] -s events.jsonl.sig < events.jsonl
```

It must answer `Good "colophon" signature`. Use the date the register was sealed — the
`.tsr` states it — rather than today's: that file is a key *history*, and asking whether
the key was valid when the timestamp says the signature existed is a stronger question
than whether it is valid now. It is also what makes rotation harmless.

There is a copy of the key in this folder too. **It is there for reproduction, not for
trust**: it lets the check run offline in ten years, and it proves nothing about whose
key it is, because whoever could rewrite this folder could rewrite that copy with it.
The published one is the claim — *whoever controlled that domain and its certificate
published this key* — and it is the reason it lives somewhere else.

That is an anchor, not a proof. It moves the question from "is this folder internally
consistent", which anyone can arrange, to "who controls that domain", which they cannot.

## 3. The register already existed on that date

Two independent timestamps, so as not to depend on a single guarantor.

**RFC 3161** — `events.jsonl.tsr`. The second command is the one that verifies; the first
only prints what the token claims.

```bash
openssl ts -reply -in events.jsonl.tsr -text | grep "Time stamp"
openssl ts -verify -data events.jsonl -in events.jsonl.tsr \
           -CAfile "$(openssl version -d | sed 's/.*"\(.*\)"/\1/')/cert.pem"
```

It must answer `Verification: OK`. That `-CAfile` is your own system's certificate bundle:
the default timestamp authority chains to it, so there is nothing to download. If the
register was stamped by an authority outside it, the CA certificate is published in the
case folder and named here instead — and if neither is true, say so rather than leaving a
command that cannot run.

**OpenTimestamps** — `events.jsonl.ots`, submitted for anchoring in the Bitcoin blockchain:

```bash
pip install opentimestamps-client
ots upgrade events.jsonl.ots && ots verify events.jsonl.ots
```

Two honest qualifications, because this seal is the one most easily overstated. A `.ots`
file means the register was *submitted*; the calendars batch submissions into a Bitcoin
transaction and have been observed to accept one and never anchor it, so `ots upgrade` is
what turns a submission into evidence. And verifying the result needs a Bitcoin node, or a
block explorer you decide to believe: it depends on no *authority*, which is not the same
as depending on nothing.

## 4. The text matches the annotation

```bash
python3 measure.py
```

It must say `reconstruction: OK`. That means that the annotated spans, concatenated,
reproduce the published text exactly: no step has been attributed to a piece of text
that does not exist, and no piece of text has been left without an attribution.

---

## What all this proves, and what it does not

**It proves** that the register existed in that form on that date, that it has not been
altered since, and that it was produced by whoever holds that key.

**It does not prove** that the register is **complete**. No voluntary system can prove
that: I can record everything faithfully, or I can leave things out, and cryptography
does not tell the two cases apart. The register is, moreover, compiled by the language
model about itself.

I say it first because it is the soundest criticism that can be made of a voluntary
disclosure, and it is a fair one: **the value of this register does not lie in the proof,
it lies in the responsibility I take on by publishing it and in the fact that it can be
inspected.**

If you find an inconsistency, write to me: **[contact]**

---

*MIT License — Copyright (c) 2026 Fabio Chinaglia. See the LICENSE file.*
