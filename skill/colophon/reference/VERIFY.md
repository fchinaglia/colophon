# How to verify this register

*Template to publish next to the register. Replace the parts in square brackets.*

---

The file `events.jsonl` contains the register of the interventions made while writing
[title]. Each line is an event; each event contains the fingerprint of the previous one,
so the sequence is a chain: **altering a past event invalidates every hash that follows
it**.

Next to the register you will find three files that let you verify it without taking my
word for anything.

**If this arrived as a bundle** — `colophon-[uid].tar` — everything below is already in
it, and so is `verify.html`. Open that file in a browser with the network off and drop
the tar on it: it checks the chain, the signature, every digest the manifest covers and
the timestamp's imprint, in one action. The commands below are the same checks by hand,
and they are what you use if you would rather not run my copy of the verifier — which is
the sensible instinct, since it arrived in the package it is meant to check. Its digest
is published with each release; compare it, or fetch your own copy.

**A bundle is a snapshot at its date.** It verifies perfectly and it cannot tell you that
the case was reopened afterwards, because a copy in your hands has no way back to me. The
root printed in the document is what makes that visible: two copies with two different
roots are two different states of the same case.

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

That is why the published one lives somewhere else, and it is an anchor rather than a
proof: it moves the question from "is this folder internally consistent", which anyone
can arrange, to "who controls that domain", which they cannot.

## 2b. Signed by a named person — only if `attestation.txt.p7m` is here

The Ed25519 signature above proves that a key signed, and the published key moves that to
"whoever controls that domain". A qualified electronic signature moves it to a natural
person, because a supervised trust service identified them first.

What is signed is `attestation.txt` — one page restating the case identity, the root, and
every digest the manifest covers. It is not the register: a log lives by being readable,
and wrapping it would take that away.

```bash
openssl cms -verify -in attestation.txt.p7m -inform DER -out attestation.txt \
            -CAfile [the EU trusted-list bundle, or your own]
openssl cms -verify -in attestation.txt.p7m -inform DER -noverify -signer signer.pem \
  && openssl x509 -in signer.pem -noout -subject -dates
```

The second command prints who signed and until when the certificate was valid. For a full
check against the European Trusted Lists, upload the `.p7m` to the EU DSS validator
(`ec.europa.eu/digital-building-blocks/DSS/webapp-demo/validation`), which resolves the
trust anchors for you.

**Look at the signature level**, and this is the part nobody mentions. A `CAdES-B`
signature carries no revocation evidence: once the certificate expires — Italian
qualified certificates run about three years — Italian law (CAD art. 24 c. 4-bis) treats
the signature as **not made at all**, silently. A signature at level **LT** or **LTA**
embeds the revocation data and stays checkable afterwards. The validator reports the
level.

And the one thing this signature does not say: it says who takes responsibility for the
register. It does not say the register is complete, and it does not say that the text of
the document it accompanies is the text that was measured — §4 below is what checks that.

## 3. The register already existed on that date

Two independent timestamps, so as not to depend on a single guarantor.

**RFC 3161** — `events.jsonl.tsr`. The second command is the one that verifies; the first
only prints what the token claims.

```bash
openssl ts -reply -in events.jsonl.tsr -text | grep "Time stamp"
openssl ts -verify -data events.jsonl -in events.jsonl.tsr \
           -CAfile "$(openssl version -d | sed 's/.*"\(.*\)"/\1/')/cert.pem"
```

It must answer `Verification: OK`. That `-CAfile` is **your own system's** certificate
bundle, and the command above finds it for you — `seal.sh` times against an authority
that chains to it precisely so there is nothing to download.

No CA certificate travels in the bundle, and that is deliberate: a root certificate
arriving inside the evidence it authenticates proves nothing, for the same reason a
public key published inside the folder it signs proves nothing. If a case was stamped by
an authority your system does not carry, the check fails here and the case has to name
where you can fetch that CA — from the authority, not from me.

The browser verifier does less than this command, on purpose: it reads the imprint and
the time from the token and stops there. It tells you the timestamp commits to *this*
register; it does not tell you who issued it. That is what the command above is for.

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
altered since, and that it was signed by the holder of a key which a domain I control
published — an anchor to an identity, not a proof of one. With `attestation.txt.p7m`
present and valid, the anchor becomes a legal name instead of a domain.

**It does not prove that this document is the text that was measured.** A signature over
a file says the file has not changed since it was signed; §4 is the only check that ties
the words you are reading to the numbers in the note.

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
