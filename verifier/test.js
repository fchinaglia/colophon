// SPDX-License-Identifier: MIT
// Node harness for verifier/core.js. Run: node verifier/test.js [path-to-colophon-repo]
'use strict';
const fs = require('fs');
const path = require('path');
const C = require('./core.js');

const REPO = process.argv[2] || '/Users/fabiochinaglia/Projects/colophon';
const SPEC = path.join(__dirname, '..', 'spec', 'vectors');

let pass = 0, fail = 0;
const ok = (cond, label, extra) => {
  if (cond) { pass++; }
  else { fail++; console.log(`  FAIL ${label}` + (extra ? `\n       ${extra}` : '')); }
};
const head = s => console.log(`\n${s}`);

// ---- hash known-answer tests -------------------------------------------------
head('hashes');
ok(C.hex(C.sha256(C.utf8(''))) ===
   'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'sha256("")');
ok(C.hex(C.sha256(C.utf8('abc'))) ===
   'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad', 'sha256("abc")');
ok(C.hex(C.sha512(C.utf8(''))).startsWith('cf83e1357eefb8bd'), 'sha512("")');
ok(C.hex(C.sha512(C.utf8('abc'))) ===
   'ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a' +
   '2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f', 'sha512("abc")');
// a message longer than one block, to exercise the padding path
const long = C.utf8('a'.repeat(200));
ok(C.hex(C.sha256(long)) ===
   require('crypto').createHash('sha256').update(Buffer.from(long)).digest('hex'), 'sha256 200B');
ok(C.hex(C.sha512(long)) ===
   require('crypto').createHash('sha512').update(Buffer.from(long)).digest('hex'), 'sha512 200B');

// ---- spec vectors ------------------------------------------------------------
const rows = f => fs.readFileSync(path.join(SPEC, f), 'utf8')
                     .split('\n').filter(l => l.trim()).map(JSON.parse);

head('spec/vectors/canonical.jsonl');
for (const v of rows('canonical.jsonl')) {
  const body = JSON.parse(v.body);
  let got;
  try { got = C.canonical(body); } catch (e) { got = 'THREW: ' + e.message; }
  ok(got === v.canonical, `canonical/${v.name}`, `want ${v.canonical}\n       got  ${got}`);
  const h = C.hex(C.sha256(C.concat(C.utf8(v.prev), C.utf8(v.canonical))));
  ok(h === v.hash, `hash/${v.name}`, `want ${v.hash}\n       got  ${h}`);
}

head('spec/vectors/prespec.jsonl');
for (const v of rows('prespec.jsonl')) {
  const got = C.preSpecReason(v.line) !== null;
  ok(got === v.detect, `prespec/${v.name}`, `detect=${v.detect} got=${got}`);
}

// ---- real registers ----------------------------------------------------------
head('real registers');

const ex = path.join(REPO, 'example', 'events.jsonl');
if (fs.existsSync(ex)) {
  const r = C.verifyChain(fs.readFileSync(ex, 'utf8'));
  ok(r.ok === true, 'example/: chain verifies under the spec', JSON.stringify(r).slice(0, 200));
  ok(r.root === 'c369d149d849b514' + r.root.slice(16),
     'example/: root starts c369d149d849b514', `root ${r.root}`);
  console.log(`       example/ root ${r.root}`);
}

// The validation case, as it ships: one tar, read the way the page reads it. Everything
// below is a real artefact — a real SSHSIG, a real RFC 3161 token, a real manifest — which
// is why this block exists at all: the vectors cover the format, this covers the world.
const bundle = path.join(REPO, 'validation', 'colophon-001.tar');
if (fs.existsSync(bundle)) {
  head('the shipped bundle');
  const raw = fs.readFileSync(bundle);
  const files = C.normalise(C.untar(
    raw.buffer.slice(raw.byteOffset, raw.byteOffset + raw.byteLength)));
  ok(files.size > 20, 'bundle: unpacks', `${files.size} entries`);
  ok(files.has('verify.html'), 'bundle: carries the verifier');

  const text = new TextDecoder().decode(files.get('events.jsonl'));
  const r = C.verifyChain(text);
  ok(r.ok === true, 'bundle: chain verifies under the spec', JSON.stringify(r).slice(0, 160));
  ok(!r.preSpec, 'bundle: no pre-spec numbers left', JSON.stringify(r.preSpec || []).slice(0, 120));
  console.log(`       root ${r.root}`);

  const reg = files.get('events.jsonl');
  const sig = new TextDecoder().decode(files.get('events.jsonl.sig'));
  const pub = new TextDecoder().decode(files.get('colophon.pub'));
  const parsed = C.parseSshsig(sig);
  console.log(`       sshsig: v${parsed.version} ns="${parsed.namespace}" ` +
              `hash=${parsed.hashAlg} key=${parsed.keyType} blob=${parsed.blobLength}B`);
  const v = C.verifySignature(reg, sig, pub);
  ok(v.ok === true, 'bundle: Ed25519 signature verifies', JSON.stringify(v));
  console.log(`       fingerprint ${v.keyFingerprint}`);

  const bad = new Uint8Array(reg); bad[bad.length - 20] ^= 1;
  ok(C.verifySignature(bad, sig, pub).ok === false, 'bundle: tampered register fails');

  const t = C.checkTimestamp(files.get('events.jsonl.tsr'), reg);
  ok(t.parsed && t.commits !== null, 'bundle: .tsr imprint commits to this register',
     JSON.stringify(t));
  console.log(`       tsr: genTime=${t.genTime} commits=${t.commits} ` +
              `qualified=${C.isQualifiedTimestamp(files.get('events.jsonl.tsr'))}`);

  const man = C.findManifest(text);
  ok(!!man, 'bundle: manifest event found');
  if (man) {
    const m = C.checkManifest(man, files);
    console.log(`       manifest: ${m.matched.length} matched, ` +
                `${m.mismatched.length} mismatched, ${m.missing.length} missing`);
    ok(m.mismatched.length === 0 && m.missing.length === 0,
       'bundle: every manifest digest matches a file inside it',
       JSON.stringify(m.mismatched.map(x => x.name).concat(m.missing)));
  }
}

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
