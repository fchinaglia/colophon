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

The signature is Ed25519, detached, in the `.sig` file. My public key is published
here: **[stable URL — your site, GitHub profile, LinkedIn page]**

```bash
echo '[your-email] namespaces="colophon" [public-key-contents]' > allowed_signers
ssh-keygen -Y verify -f allowed_signers -I [your-email] \
           -n colophon -s events.jsonl.sig < events.jsonl
```

It must answer `Good "colophon" signature`.

## 3. The register already existed on that date

Two independent timestamps, so as not to depend on a single guarantor.

**RFC 3161** — `events.jsonl.tsr`:

```bash
openssl ts -reply -in events.jsonl.tsr -text | grep "Time stamp"
openssl ts -verify -data events.jsonl -in events.jsonl.tsr \
           -CAfile [TSA-cacert].pem
```

**OpenTimestamps** — `events.jsonl.ots`, anchored to the Bitcoin blockchain:

```bash
pip install opentimestamps-client
ots verify events.jsonl.ots
```

This one requires trusting no authority at all.

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
