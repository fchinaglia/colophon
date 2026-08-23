// SPDX-License-Identifier: MIT
// Colophon verifier — core. No DOM, no network, no dependencies.
// Inlined into verify.html; kept separate only so it can be unit-tested.
'use strict';

// ---------------------------------------------------------------- SHA-256

const K256 = [
  0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
  0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
  0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
  0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
  0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
  0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
  0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
  0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];

function sha256(bytes) {
  const h = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
             0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
  const l = bytes.length;
  const withPad = new Uint8Array((((l + 8) >> 6) + 1) << 6);
  withPad.set(bytes);
  withPad[l] = 0x80;
  new DataView(withPad.buffer).setUint32(withPad.length - 4, l << 3, false);
  new DataView(withPad.buffer).setUint32(withPad.length - 8, Math.floor(l / 536870912), false);

  const w = new Uint32Array(64);
  const dv = new DataView(withPad.buffer);
  const rr = (x, n) => (x >>> n) | (x << (32 - n));

  for (let off = 0; off < withPad.length; off += 64) {
    for (let i = 0; i < 16; i++) w[i] = dv.getUint32(off + i * 4, false);
    for (let i = 16; i < 64; i++) {
      const s0 = rr(w[i-15],7) ^ rr(w[i-15],18) ^ (w[i-15] >>> 3);
      const s1 = rr(w[i-2],17) ^ rr(w[i-2],19) ^ (w[i-2] >>> 10);
      w[i] = (w[i-16] + s0 + w[i-7] + s1) >>> 0;
    }
    let [a,b,c,d,e,f,g,hh] = h;
    for (let i = 0; i < 64; i++) {
      const S1 = rr(e,6) ^ rr(e,11) ^ rr(e,25);
      const ch = (e & f) ^ (~e & g);
      const t1 = (hh + S1 + ch + K256[i] + w[i]) >>> 0;
      const S0 = rr(a,2) ^ rr(a,13) ^ rr(a,22);
      const mj = (a & b) ^ (a & c) ^ (b & c);
      const t2 = (S0 + mj) >>> 0;
      hh = g; g = f; f = e; e = (d + t1) >>> 0;
      d = c; c = b; b = a; a = (t1 + t2) >>> 0;
    }
    h[0]=(h[0]+a)>>>0; h[1]=(h[1]+b)>>>0; h[2]=(h[2]+c)>>>0; h[3]=(h[3]+d)>>>0;
    h[4]=(h[4]+e)>>>0; h[5]=(h[5]+f)>>>0; h[6]=(h[6]+g)>>>0; h[7]=(h[7]+hh)>>>0;
  }
  const out = new Uint8Array(32);
  h.forEach((x, i) => new DataView(out.buffer).setUint32(i * 4, x, false));
  return out;
}

// ---------------------------------------------------------------- SHA-512

const K512 = (
 '428a2f98d728ae22 7137449123ef65cd b5c0fbcfec4d3b2f e9b5dba58189dbbc ' +
 '3956c25bf348b538 59f111f1b605d019 923f82a4af194f9b ab1c5ed5da6d8118 ' +
 'd807aa98a3030242 12835b0145706fbe 243185be4ee4b28c 550c7dc3d5ffb4e2 ' +
 '72be5d74f27b896f 80deb1fe3b1696b1 9bdc06a725c71235 c19bf174cf692694 ' +
 'e49b69c19ef14ad2 efbe4786384f25e3 0fc19dc68b8cd5b5 240ca1cc77ac9c65 ' +
 '2de92c6f592b0275 4a7484aa6ea6e483 5cb0a9dcbd41fbd4 76f988da831153b5 ' +
 '983e5152ee66dfab a831c66d2db43210 b00327c898fb213f bf597fc7beef0ee4 ' +
 'c6e00bf33da88fc2 d5a79147930aa725 06ca6351e003826f 142929670a0e6e70 ' +
 '27b70a8546d22ffc 2e1b21385c26c926 4d2c6dfc5ac42aed 53380d139d95b3df ' +
 '650a73548baf63de 766a0abb3c77b2a8 81c2c92e47edaee6 92722c851482353b ' +
 'a2bfe8a14cf10364 a81a664bbc423001 c24b8b70d0f89791 c76c51a30654be30 ' +
 'd192e819d6ef5218 d69906245565a910 f40e35855771202a 106aa07032bbd1b8 ' +
 '19a4c116b8d2d0c8 1e376c085141ab53 2748774cdf8eeb99 34b0bcb5e19b48a8 ' +
 '391c0cb3c5c95a63 4ed8aa4ae3418acb 5b9cca4f7763e373 682e6ff3d6b2b8a3 ' +
 '748f82ee5defb2fc 78a5636f43172f60 84c87814a1f0ab72 8cc702081a6439ec ' +
 '90befffa23631e28 a4506cebde82bde9 bef9a3f7b2c67915 c67178f2e372532b ' +
 'ca273eceea26619c d186b8c721c0c207 eada7dd6cde0eb1e f57d4f7fee6ed178 ' +
 '06f067aa72176fba 0a637dc5a2c898a6 113f9804bef90dae 1b710b35131c471b ' +
 '28db77f523047d84 32caab7b40c72493 3c9ebe0a15c9bebc 431d67c49c100d4c ' +
 '4cc5d4becb3e42b6 597f299cfc657e2a 5fcb6fab3ad6faec 6c44198c4a475817'
).trim().split(/\s+/).map(s => BigInt('0x' + s));

const M64 = (1n << 64n) - 1n;
const rr64 = (x, n) => ((x >> n) | (x << (64n - n))) & M64;

function sha512(bytes) {
  let h = ['6a09e667f3bcc908','bb67ae8584caa73b','3c6ef372fe94f82b','a54ff53a5f1d36f1',
           '510e527fade682d1','9b05688c2b3e6c1f','1f83d9abfb41bd6b','5be0cd19137e2179']
          .map(s => BigInt('0x' + s));
  const l = bytes.length;
  const blocks = (((l + 16) >> 7) + 1) << 7;
  const m = new Uint8Array(blocks);
  m.set(bytes);
  m[l] = 0x80;
  const bits = BigInt(l) * 8n;
  for (let i = 0; i < 16; i++) m[blocks - 1 - i] = Number((bits >> BigInt(8 * i)) & 0xffn);

  const w = new Array(80);
  for (let off = 0; off < blocks; off += 128) {
    for (let i = 0; i < 16; i++) {
      let v = 0n;
      for (let j = 0; j < 8; j++) v = (v << 8n) | BigInt(m[off + i * 8 + j]);
      w[i] = v;
    }
    for (let i = 16; i < 80; i++) {
      const s0 = rr64(w[i-15],1n) ^ rr64(w[i-15],8n) ^ (w[i-15] >> 7n);
      const s1 = rr64(w[i-2],19n) ^ rr64(w[i-2],61n) ^ (w[i-2] >> 6n);
      w[i] = (w[i-16] + s0 + w[i-7] + s1) & M64;
    }
    let [a,b,c,d,e,f,g,hh] = h;
    for (let i = 0; i < 80; i++) {
      const S1 = rr64(e,14n) ^ rr64(e,18n) ^ rr64(e,41n);
      const ch = (e & f) ^ (~e & M64 & g);
      const t1 = (hh + S1 + ch + K512[i] + w[i]) & M64;
      const S0 = rr64(a,28n) ^ rr64(a,34n) ^ rr64(a,39n);
      const mj = (a & b) ^ (a & c) ^ (b & c);
      const t2 = (S0 + mj) & M64;
      hh = g; g = f; f = e; e = (d + t1) & M64;
      d = c; c = b; b = a; a = (t1 + t2) & M64;
    }
    const add = [a,b,c,d,e,f,g,hh];
    h = h.map((x, i) => (x + add[i]) & M64);
  }
  const out = new Uint8Array(64);
  h.forEach((x, i) => {
    for (let j = 0; j < 8; j++) out[i * 8 + j] = Number((x >> BigInt(56 - 8 * j)) & 0xffn);
  });
  return out;
}

// ---------------------------------------------------------------- Ed25519

const P25519 = (1n << 255n) - 19n;
const LORD    = (1n << 252n) + 27742317777372353535851937790883648493n;
const DCONST  = 37095705934669439343138083508754565189542113879843219016388785533085940283555n;
const SQRTM1  = 19681161376707505956807079304988542015446066515923890162744021073123829784752n;
const BASE    = [15112221349535400772501151409588531511454012693041857206046113283949847762202n,
                 46316835694926478169428394003475163141307993866256225615783033603165251855960n];

const fmod = a => { const r = a % P25519; return r >= 0n ? r : r + P25519; };
function fpow(a, e) {
  let r = 1n; a = fmod(a);
  while (e > 0n) { if (e & 1n) r = fmod(r * a); a = fmod(a * a); e >>= 1n; }
  return r;
}
const finv = a => fpow(a, P25519 - 2n);

function ptAdd(p, q) {
  const [X1,Y1,Z1,T1] = p, [X2,Y2,Z2,T2] = q;
  const A = fmod((Y1 - X1) * (Y2 - X2));
  const B = fmod((Y1 + X1) * (Y2 + X2));
  const C = fmod(T1 * 2n * DCONST * T2);
  const D = fmod(Z1 * 2n * Z2);
  const E = B - A, F = D - C, G = D + C, H = B + A;
  return [fmod(E * F), fmod(G * H), fmod(F * G), fmod(E * H)];
}
function ptMul(p, n) {
  let q = [0n, 1n, 1n, 0n];
  while (n > 0n) { if (n & 1n) q = ptAdd(q, p); p = ptAdd(p, p); n >>= 1n; }
  return q;
}
const ptEq = (p, q) =>
  fmod(p[0] * q[2]) === fmod(q[0] * p[2]) && fmod(p[1] * q[2]) === fmod(q[1] * p[2]);

function leToBig(b) { let v = 0n; for (let i = b.length - 1; i >= 0; i--) v = (v << 8n) | BigInt(b[i]); return v; }

function ptDecode(b32) {
  let y = leToBig(b32);
  const sign = (y >> 255n) & 1n;
  y &= (1n << 255n) - 1n;
  if (y >= P25519) return null;
  const y2 = fmod(y * y);
  const u = fmod(y2 - 1n), v = fmod(DCONST * y2 + 1n);
  const xx = fmod(u * finv(v));
  let x = fpow(xx, (P25519 + 3n) / 8n);
  if (fmod(x * x - xx) !== 0n) x = fmod(x * SQRTM1);
  if (fmod(x * x - xx) !== 0n) return null;
  if ((x & 1n) !== sign) x = fmod(P25519 - x);
  return [x, y, 1n, fmod(x * y)];
}

function ed25519Verify(sig64, msg, pub32) {
  if (sig64.length !== 64 || pub32.length !== 32) return false;
  const R = sig64.subarray(0, 32), S = sig64.subarray(32);
  const s = leToBig(S);
  if (s >= LORD) return false;
  const A = ptDecode(pub32); if (!A) return false;
  const Rp = ptDecode(R);    if (!Rp) return false;
  const buf = new Uint8Array(64 + msg.length);
  buf.set(R, 0); buf.set(pub32, 32); buf.set(msg, 64);
  const k = leToBig(sha512(buf)) % LORD;
  const B = [BASE[0], BASE[1], 1n, fmod(BASE[0] * BASE[1])];
  return ptEq(ptMul(B, s), ptAdd(Rp, ptMul(A, k)));
}

// ---------------------------------------------------------------- helpers

const hex = b => Array.from(b, x => x.toString(16).padStart(2, '0')).join('');
const utf8 = s => new TextEncoder().encode(s);

function b64decode(s) {
  const clean = s.replace(/\s+/g, '');
  const bin = atob(clean);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

function concat(...parts) {
  const n = parts.reduce((a, p) => a + p.length, 0);
  const out = new Uint8Array(n);
  let o = 0;
  for (const p of parts) { out.set(p, o); o += p.length; }
  return out;
}

// SSH wire format: uint32 big-endian length, then that many bytes.
function sshString(bytes) {
  const out = new Uint8Array(4 + bytes.length);
  new DataView(out.buffer).setUint32(0, bytes.length, false);
  out.set(bytes, 4);
  return out;
}

class Reader {
  constructor(b) { this.b = b; this.i = 0; }
  u32() {
    const v = new DataView(this.b.buffer, this.b.byteOffset).getUint32(this.i, false);
    this.i += 4; return v;
  }
  str() { const n = this.u32(); const v = this.b.subarray(this.i, this.i + n); this.i += n; return v; }
  get done() { return this.i >= this.b.length; }
}

// ---------------------------------------------------------------- SSHSIG

// spec: PROTOCOL.sshsig. The signature does NOT cover the file bytes; it covers a
// structure carrying the file's hash.
function parseSshsig(armored) {
  const m = armored.match(/-----BEGIN SSH SIGNATURE-----([\s\S]*?)-----END SSH SIGNATURE-----/);
  if (!m) throw new Error('not an SSH signature (missing armor)');
  const blob = b64decode(m[1]);
  const magic = new TextDecoder().decode(blob.subarray(0, 6));
  if (magic !== 'SSHSIG') throw new Error('bad magic: expected SSHSIG');
  const r = new Reader(blob.subarray(6));
  const version = r.u32();
  const publickey = r.str();
  const namespace = new TextDecoder().decode(r.str());
  const reserved = r.str();
  const hashAlg = new TextDecoder().decode(r.str());
  const signature = r.str();

  const kr = new Reader(publickey);
  const keyType = new TextDecoder().decode(kr.str());
  const keyBytes = kr.str();

  const sr = new Reader(signature);
  const sigType = new TextDecoder().decode(sr.str());
  const sigBytes = sr.str();

  return { version, publickey, namespace, reserved, hashAlg, keyType, keyBytes,
           sigType, sigBytes, blobLength: blob.length };
}

function sshsigPreimage(namespace, reserved, hashAlg, fileHash) {
  return concat(utf8('SSHSIG'), sshString(utf8(namespace)), sshString(reserved),
                sshString(utf8(hashAlg)), sshString(fileHash));
}

function parsePubLine(line) {
  const parts = line.trim().split(/\s+/);
  const i = parts.findIndex(p => p.startsWith('ssh-') || p.startsWith('sk-'));
  if (i < 0 || !parts[i + 1]) throw new Error('not a public key line');
  const blob = b64decode(parts[i + 1]);
  const r = new Reader(blob);
  const keyType = new TextDecoder().decode(r.str());
  const keyBytes = r.str();
  return { keyType, keyBytes, comment: parts.slice(i + 2).join(' '), blob };
}

function verifySignature(registerBytes, sigText, pubText) {
  const sig = parseSshsig(sigText);
  if (sig.keyType !== 'ssh-ed25519') throw new Error(`unsupported key type ${sig.keyType}`);
  if (sig.hashAlg !== 'sha512' && sig.hashAlg !== 'sha256')
    throw new Error(`unsupported hash ${sig.hashAlg}`);
  const fileHash = sig.hashAlg === 'sha512' ? sha512(registerBytes) : sha256(registerBytes);
  const pre = sshsigPreimage(sig.namespace, sig.reserved, sig.hashAlg, fileHash);

  let pubBytes = sig.keyBytes, source = 'the signature itself';
  if (pubText) {
    const pub = parsePubLine(pubText);
    pubBytes = pub.keyBytes;
    source = 'the supplied public key';
    if (hex(pub.keyBytes) !== hex(sig.keyBytes))
      return { ok: false, namespace: sig.namespace, preimageLength: pre.length,
               error: 'the supplied public key is not the one that made this signature' };
  }
  const ok = ed25519Verify(sig.sigBytes, pre, pubBytes);
  return { ok, namespace: sig.namespace, hashAlg: sig.hashAlg,
           preimageLength: pre.length, keyFingerprint: sha256Fingerprint(sig.publickey),
           source, keyEmbedded: !pubText };
}

// what `ssh-keygen -lf` prints: SHA256:<base64 of sha256(pubkey blob)>, unpadded
function sha256Fingerprint(pubkeyBlob) {
  const d = sha256(pubkeyBlob);
  let bin = '';
  d.forEach(b => bin += String.fromCharCode(b));
  return 'SHA256:' + btoa(bin).replace(/=+$/, '');
}

// ---------------------------------------------------------------- canonical form
// spec/canonical.md §3

function cpCompare(a, b) {
  const A = Array.from(a), B = Array.from(b);
  const n = Math.min(A.length, B.length);
  for (let i = 0; i < n; i++) {
    const x = A[i].codePointAt(0), y = B[i].codePointAt(0);
    if (x !== y) return x < y ? -1 : 1;
  }
  return A.length - B.length;
}

function canonical(v) {
  if (v === null) return 'null';
  if (v === true) return 'true';
  if (v === false) return 'false';
  if (typeof v === 'number') {
    if (!Number.isInteger(v)) throw new Error(`non-integer number ${v} (spec §4)`);
    if (!Number.isSafeInteger(v)) throw new Error(`integer ${v} beyond 2^53-1 (spec §4)`);
    return String(v);
  }
  // Python and JS agree on JSON string escaping for everything the spec permits.
  if (typeof v === 'string') return JSON.stringify(v);
  if (Array.isArray(v)) return '[' + v.map(canonical).join(',') + ']';
  if (typeof v === 'object') {
    const keys = Object.keys(v).sort(cpCompare);
    return '{' + keys.map(k => JSON.stringify(k) + ':' + canonical(v[k])).join(',') + '}';
  }
  throw new Error(`cannot canonicalize ${typeof v}`);
}

// ---------------------------------------------------------------- pre-spec detection
// spec/canonical.md §5.1 — scans OUTSIDE string literals.

const MAX_SAFE = 9007199254740991n;

function preSpecReason(line) {
  let i = 0;
  const n = line.length;
  while (i < n) {
    const c = line[i];
    if (c === '"') {
      let j = i + 1, raw = '';
      while (j < n) {
        if (line[j] === '\\') { raw += line.slice(j, j + 2); j += 2; continue; }
        if (line[j] === '"') break;
        raw += line[j]; j++;
      }
      let k = j + 1;
      while (k < n && (line[k] === ' ' || line[k] === '\t')) k++;
      if (line[k] === ':') {
        let decoded;
        try { decoded = JSON.parse('"' + raw + '"'); } catch { decoded = ''; }
        for (const ch of decoded) {
          if (ch.codePointAt(0) > 0x7f) return `non-ASCII key "${decoded}"`;
        }
      }
      i = j + 1;
      continue;
    }
    if (c === '-' || (c >= '0' && c <= '9')) {
      let j = i;
      if (line[j] === '-') j++;
      const start = j;
      while (j < n && (/[0-9]/.test(line[j]) || '.eE+-'.includes(line[j]))) j++;
      const lit = line.slice(start, j);
      if (/[.eE]/.test(lit)) return `non-integer number ${line.slice(i, j)}`;
      if (lit) {
        try { if (BigInt(lit) > MAX_SAFE) return `integer ${lit} beyond 2^53-1`; }
        catch { /* not a number after all */ }
      }
      i = j;
      continue;
    }
    i++;
  }
  return null;
}

// ---------------------------------------------------------------- the chain

const GENESIS = '0'.repeat(64);

function verifyChain(text) {
  const lines = text.split('\n').filter(l => l.trim());
  const preSpec = [];
  lines.forEach((l, i) => {
    const r = preSpecReason(l);
    if (r) preSpec.push({ event: i, reason: r });
  });
  if (preSpec.length) {
    return { preSpec, events: lines.length,
             message: 'This register predates the canonicalization spec. Check its chain ' +
                      'with `python3 record.py --verify` in the case folder.' };
  }
  let prev = GENESIS;
  for (let i = 0; i < lines.length; i++) {
    let row;
    try { row = JSON.parse(lines[i]); }
    catch (e) { return { broken: i, why: 'not valid JSON', events: lines.length }; }
    const body = {};
    for (const k of Object.keys(row)) if (k !== 'hash') body[k] = row[k];
    if (body.prev !== prev)
      return { broken: i, why: 'prev does not match', events: lines.length };
    const got = hex(sha256(concat(utf8(prev), utf8(canonical(body)))));
    if (got !== row.hash)
      return { broken: i, why: 'hash does not match', events: lines.length };
    prev = row.hash;
  }
  return { ok: true, events: lines.length, root: prev };
}

// ---------------------------------------------------------------- the manifest

// The last event of a case carries payload.sha256: {filename: digest}.
function findManifest(text) {
  const lines = text.split('\n').filter(l => l.trim());
  for (let i = lines.length - 1; i >= 0; i--) {
    let row; try { row = JSON.parse(lines[i]); } catch { continue; }
    const d = row && row.payload && row.payload.sha256;
    if (d && typeof d === 'object') return { event: i, digests: d };
  }
  return null;
}

function checkManifest(manifest, files) {
  const matched = [], mismatched = [], missing = [];
  for (const [name, want] of Object.entries(manifest.digests)) {
    const bytes = files.get(name);
    if (!bytes) { missing.push(name); continue; }
    const got = hex(sha256(bytes));
    (got === want ? matched : mismatched).push({ name, want, got });
  }
  return { matched, mismatched, missing };
}

// ---------------------------------------------------------------- RFC 3161, partially

// Enough DER to pull the imprint and the genTime, and no more. Validating the TSA's
// certificate chain needs a trust store and is therefore out of scope here.
function inspectTsr(bytes) {
  const found = { imprint: null, genTime: null };
  for (let i = 0; i + 2 < bytes.length; i++) {
    // OCTET STRING of 32 or 64 bytes: the message imprint
    if (bytes[i] === 0x04 && (bytes[i+1] === 0x20 || bytes[i+1] === 0x40) && !found.imprint) {
      found.imprint = hex(bytes.subarray(i + 2, i + 2 + bytes[i+1]));
    }
    // GeneralizedTime
    if (bytes[i] === 0x18 && bytes[i+1] > 10 && bytes[i+1] < 32 && !found.genTime) {
      const s = new TextDecoder().decode(bytes.subarray(i + 2, i + 2 + bytes[i+1]));
      if (/^\d{14}/.test(s)) found.genTime = s;
    }
  }
  return found;
}

function checkTimestamp(tsrBytes, registerBytes) {
  const t = inspectTsr(tsrBytes);
  if (!t.imprint) return { parsed: false };
  const s256 = hex(sha256(registerBytes)), s512 = hex(sha512(registerBytes));
  const commits = t.imprint === s256 ? 'sha256' : t.imprint === s512 ? 'sha512' : null;
  return { parsed: true, genTime: t.genTime, imprint: t.imprint, commits };
}

// CIR (EU) 2025/1929: a token declared qualified carries esi4-qtstStatement-1,
// OID 0.4.0.19422.1.1, DER 06 07 04 00 81 97 5e 01 01
function isQualifiedTimestamp(tsrBytes) {
  const needle = [0x06,0x07,0x04,0x00,0x81,0x97,0x5e,0x01,0x01];
  outer: for (let i = 0; i + needle.length <= tsrBytes.length; i++) {
    for (let j = 0; j < needle.length; j++) if (tsrBytes[i+j] !== needle[j]) continue outer;
    return true;
  }
  return false;
}

// ---------------------------------------------------------------- the whole case

const REQUIRED = ['events.jsonl'];

function verifyCase(files) {
  const out = { files: files.size, notes: [] };
  for (const r of REQUIRED) if (!files.has(r)) { out.fatal = `${r} is missing`; return out; }

  const registerBytes = files.get('events.jsonl');
  const text = new TextDecoder().decode(registerBytes);

  out.chain = verifyChain(text);
  out.registerSha256 = hex(sha256(registerBytes));

  if (files.has('events.jsonl.sig')) {
    const pub = files.get('colophon.pub') || files.get('allowed_signers');
    try {
      out.signature = verifySignature(registerBytes, new TextDecoder().decode(files.get('events.jsonl.sig')),
                                      pub ? new TextDecoder().decode(pub) : null);
    } catch (e) { out.signature = { ok: false, error: e.message }; }
  }

  const man = findManifest(text);
  if (man) { out.manifest = checkManifest(man, files); out.manifest.event = man.event; }

  if (files.has('events.jsonl.tsr')) {
    out.timestamp = checkTimestamp(files.get('events.jsonl.tsr'), registerBytes);
    out.timestamp.qualified = isQualifiedTimestamp(files.get('events.jsonl.tsr'));
  }
  if (files.has('events.jsonl.ots')) {
    out.ots = { present: true, bytes: files.get('events.jsonl.ots').length };
  }

  // Deliberately not computed here: the measurement. One implementation of the number,
  // and it is measure.py.
  for (const f of ['kpi.json', 'spans.json', 'annotation.json'])
    if (files.has(f)) out.notes.push(f);

  return out;
}

if (typeof module !== 'undefined') {
  module.exports = { sha256, sha512, hex, canonical, cpCompare, preSpecReason, verifyChain,
                     parseSshsig, sshsigPreimage, parsePubLine, verifySignature,
                     ed25519Verify, findManifest, checkManifest, checkTimestamp,
                     isQualifiedTimestamp, verifyCase, utf8, concat, b64decode };
}
