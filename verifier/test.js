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

const c1 = path.join(REPO, 'cases', '001');
if (fs.existsSync(c1)) {
  const r = C.verifyChain(fs.readFileSync(path.join(c1, 'events.jsonl'), 'utf8'));
  ok(!!r.preSpec, 'cases/001: detected as pre-spec');
  ok(r.preSpec && r.preSpec.length === 18, 'cases/001: 18 offending events',
     `got ${r.preSpec && r.preSpec.length}`);
  ok(!r.broken, 'cases/001: NOT reported as broken');
  console.log(`       first: event ${r.preSpec[0].event} — ${r.preSpec[0].reason}`);

  // the SSH signature: SHA-512 + SSHSIG framing + Ed25519, all at once
  const reg = new Uint8Array(fs.readFileSync(path.join(c1, 'events.jsonl')));
  const sig = fs.readFileSync(path.join(c1, 'events.jsonl.sig'), 'utf8');
  const pub = fs.readFileSync(path.join(c1, 'colophon.pub'), 'utf8');
  const parsed = C.parseSshsig(sig);
  console.log(`       sshsig: v${parsed.version} ns="${parsed.namespace}" ` +
              `hash=${parsed.hashAlg} key=${parsed.keyType} blob=${parsed.blobLength}B`);
  const pre = C.sshsigPreimage(parsed.namespace, parsed.reserved, parsed.hashAlg,
                               C.sha512(reg));
  console.log(`       preimage: ${pre.length} bytes`);
  const v = C.verifySignature(reg, sig, pub);
  ok(v.ok === true, 'cases/001: Ed25519 signature verifies', JSON.stringify(v));
  console.log(`       fingerprint ${v.keyFingerprint}`);

  // a tampered register must fail
  const bad = new Uint8Array(reg); bad[bad.length - 20] ^= 1;
  ok(C.verifySignature(bad, sig, pub).ok === false, 'cases/001: tampered register fails');

  // the timestamp
  const tsr = new Uint8Array(fs.readFileSync(path.join(c1, 'events.jsonl.tsr')));
  const t = C.checkTimestamp(tsr, reg);
  ok(t.parsed && t.commits !== null, 'cases/001: .tsr imprint commits to this register',
     JSON.stringify(t));
  console.log(`       tsr: genTime=${t.genTime} commits=${t.commits} ` +
              `qualified=${C.isQualifiedTimestamp(tsr)}`);

  // the manifest
  const man = C.findManifest(fs.readFileSync(path.join(c1, 'events.jsonl'), 'utf8'));
  ok(!!man, 'cases/001: manifest event found');
  if (man) {
    const files = new Map();
    for (const name of Object.keys(man.digests)) {
      const p = path.join(c1, name);
      if (fs.existsSync(p)) files.set(name, new Uint8Array(fs.readFileSync(p)));
    }
    const m = C.checkManifest(man, files);
    console.log(`       manifest: ${m.matched.length} matched, ` +
                `${m.mismatched.length} mismatched, ${m.missing.length} missing`);
    ok(m.mismatched.length === 0, 'cases/001: every manifest digest matches',
       JSON.stringify(m.mismatched.map(x => x.name)));
  }
}

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
