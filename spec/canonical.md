# Colophon — canonical serialization of the register

*Normative. Version 1.*

The register `events.jsonl` is a hash chain. The hash is computed over **bytes**, but an
event is a **JSON object**, and the same object admits many byte serializations. This
document fixes the one that counts.

It exists because a second implementation now needs it. `record.py --verify` re-parses the
register and re-serializes it with the same function, so it agrees with itself whatever
that function does; it has never tested whether the rule is reproducible by anyone else.
A verifier written in another language has no such luxury.

---

## 1. The chain

```
h(0) = "0" * 64
h(n) = SHA-256( h(n-1) as 64 ASCII hex characters  ‖  canonical(body_n) )
```

Three points that are easy to get wrong and are not guessable from the file:

- **`h(n-1)` is prepended as its 64-character lowercase hex string, encoded ASCII** — not
  as the 32 bytes it denotes.
- **`body_n` is the event object with the `hash` member removed**, and with `seq`, `ts` and
  `prev` present. The hash therefore covers the sequence number and the timestamp.
- **The root of a register is the `hash` of its last event.** That is the value printed in
  the technical line of a closing note.

## 2. The stored line is not the canonical form

`record.py` computes the hash with compact separators and then writes the line with
Python's default ones. The bytes on disk carry a space after every `:` and `,`:

```
on disk    {"actor": "system", "hash": "832f9dfc…", "meta": true, "payload": {"capture_…
canonical  {"actor":"system","meta":true,"payload":{"capture_…
```

**An implementation MUST NOT hash the line as written.** It MUST parse the line, remove
`hash`, and re-serialize according to §3.

## 3. Canonical serialization

`canonical(obj)` is defined to be exactly

```python
json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
```

Stated clause by clause, so that it can be implemented without Python:

**3.1 Key order.** Object members MUST be emitted in ascending order of their keys compared
**by Unicode code point**, recursively, at every level of nesting including inside objects
that appear within arrays.

> This is *not* the ordering JavaScript's `Array.prototype.sort` produces, which compares
> UTF-16 code units. The two differ for keys containing characters above the BMP. §4
> forbids such keys rather than requiring implementations to handle them.

**3.2 Whitespace.** None. `,` and `:` are emitted bare. No trailing newline is part of the
canonical form.

**3.3 Encoding.** The output is UTF-8. Characters outside ASCII are emitted **as
themselves**, never as `\uXXXX` escapes. `città` is nine bytes, not eleven characters of
escape.

**3.4 Strings.** Only what must be escaped is escaped: `"` and `\`, and the control
characters below U+0020. The short forms `\b \f \n \r \t` are used where they exist; every
other control character uses `\u00XX` with lowercase hex digits.

**3.5 Numbers.** Integers are emitted in their exact decimal form, with no exponent, no
leading `+`, and no fractional part. **Non-integer numbers MUST NOT appear** — see §4 — so
no floating-point formatting rule is normative here. An implementation encountering one in
a register conforming to this version MUST treat the register as malformed.

**3.6 Literals.** `true`, `false`, `null`, lowercase and unquoted. Arrays preserve their
order; objects inside them are still key-sorted per 3.1.

## 4. What an event MUST NOT contain

`record.py` enforces these at `append()` time, **refusing rather than warning**:

> **No non-integer numbers anywhere in an event. Integers must satisfy |n| ≤ 2⁵³ − 1.
> Object keys must be ASCII.**

The reasons, all three measured rather than assumed:

**Non-integer numbers.** Python and JavaScript format them differently, and not only in the
obvious case. Measured, Python 3.9 against Node 26:

| value | Python | JavaScript |
|---|---|---|
| `1.0` | `1.0` | `1` |
| `1e16` | `1e+16` | `10000000000000000` |
| `1e20` | `1e+20` | `100000000000000000000` |
| `1e-7` | `1e-07` | `1e-7` |
| `1e-6` | `1e-06` | `0.000001` |

Some values agree — `0.1`, `1e21`, `1e308` — but no simple rule separates those that do
from those that do not, so every non-integer is forbidden. This costs nothing: the values
that provoked it are *descriptive* payload, nothing reads them numerically, and the
measurement of record is `kpi.json` and never the register. Write them as strings.

**Integers beyond 2⁵³.** JavaScript loses precision **silently**: `9007199254740993`
becomes `9007199254740992`, with no error. This is the failure mode that would go unnoticed.

**Non-ASCII keys.** See 3.1. Values may be anything; keys are identifiers, they are already
ASCII in every existing register, and requiring it removes the ordering question entirely.

## 5. Registers predating this specification

Registers sealed before version 1 may violate §4. The validation case did: measured with
the scanner of §5.1, it carried **72 non-integer numbers across 18 of its 80 events** —
`94.0`, `6.0`, `0.0`, `100.0`, and fractional ones such as `10.3` and `89.7`. The integral
ones diverge outright between the two languages; the fractional ones happen to agree, which
is exactly why §4 forbids the whole class rather than trying to draw the line.

**They cannot be repaired in place.** The register is append-only; reopening a case
appends events and cannot rewrite the ones already recorded.

They can be **replayed**, which is a different thing and worth naming because the
difference is the whole point. A replay re-records every event through a conforming
`record.py`, quoting the offending numbers and leaving every other field and every
original timestamp alone. The result is a new register: new chain, new root, new
signature, new timestamp. It is not the old one repaired — the old one still says what it
said, and the new one has to name it. What is lost is not recoverable: the original
timestamp attested that *those bytes* existed on *that date*, and the bytes changed. The
validation case shipped in `validation/` is a replay, and its register says so in an event
of its own before the closing manifest. Adopting RFC 8785 would not help either — JCS
formats `94.0` as `94`, so it breaks the same registers in the same way. **JCS is not
backward compatible with what this project has already sealed.**

**A verifier MUST detect such a register and refuse it explicitly**, rather than
re-serializing it and reporting a broken chain. The required message is of the form:

> This register predates the canonicalization spec. Check its chain with
> `python3 record.py --verify` in the case folder.

Reporting a false forgery on a valid register is worse than declining to check it.

### 5.1 Detection

Scan the raw text of each line with a scanner that tracks whether it is inside a string
literal. Outside strings, the register is pre-spec if any of the following holds:

- a numeric literal contains `.`, `e` or `E`
- an integer literal has absolute value greater than 2⁵³ − 1
- an object key, after unescaping, contains any character above U+007F

**A scanner that does not skip string contents is wrong.** Italian registers contain
sentences like `"the value was 94.0 percent"`, and flagging those would refuse a
conforming register. The vector `float-inside-a-string` exists to catch exactly that
mistake.

## 6. Conformance vectors

```
spec/vectors/canonical.jsonl   13 events → expected canonical bytes and hash
spec/vectors/prespec.jsonl      9 raw lines → must / must not trigger §5 detection
spec/vectors/refused.jsonl      9 payloads → must / must not be refused by append()
```

Each vector in `canonical.jsonl` carries `prev`, `body` (as JSON **source text**, so that
a reader's own parser is exercised), the expected `canonical` string, and the expected
`hash`. Both `record.py` and the verifier MUST pass all three files in CI.

The vectors are delivered as source text rather than as parsed values deliberately: a
vector file whose numbers were mangled by the reader's own JSON parser would test nothing.

Example, from `key-order`:

```
body       {"0": 5, "C": 3, "_z": 4, "a": 2, "b": 1}
canonical  {"0":5,"C":3,"_z":4,"a":2,"b":1}
prev       0000…0000
hash       6a30b42e792d63532017f483d4f43872242b5bd1a609a409ab0ca530aee73b8b
```

`'0'` (U+0030) precedes `'C'` (U+0043) precedes `'_'` (U+005F) precedes `'a'` — code point
order, which is also ASCII order, which is why §4 makes it moot.

## 7. Why not RFC 8785

JCS is the natural candidate and it is the wrong one here, for two reasons.

It is **not backward compatible** with the registers already sealed, as §5 explains. And it
would cost the scripts their standing rule: JCS needs a library in Python, while the case
scripts must keep running on the standard library alone — a case folder has to work in ten
years with no `pip install`.

Whichever route were taken, the number rules would end up the same, because JavaScript
cannot represent anything else. So the choice was never between two number models; it was
about who does the extra work. §4 answers: the format forbids what JavaScript cannot hold.

---

*MIT License — see the LICENSE file.*
