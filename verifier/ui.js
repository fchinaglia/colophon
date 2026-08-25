// SPDX-License-Identifier: MIT
// The verifier's interface layer: it wires the four elements a shell must
// provide — #drop #dir #fil #out — to the checks in core.js, and renders what
// they return.
//
// build.py inlines this into BOTH shells at //__UI__, for the same reason
// components.css is shared: the served page and the one that travels in a
// bundle differ in chrome and palette, never in what they do or show.
//
// core.js stays separate so verifier/test.js can exercise it directly.

/* ==== ui ==== */
(function () {
  const $ = s => document.querySelector(s);
  const out = $('#out'), drop = $('#drop');

  const esc = s => String(s).replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
  const card = (title, badge, cls, body) =>
    `<section class="card"><h2>${esc(title)}` +
    (badge ? ` <span class="badge ${cls}">${esc(badge)}</span>` : '') +
    `</h2>${body}</section>`;
  const dl = pairs => '<dl>' + pairs.filter(Boolean)
    .map(([k, v]) => `<dt>${esc(k)}</dt><dd class="mono">${esc(v)}</dd>`).join('') + '</dl>';

  const own = b => b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength);

  async function collect(fileList) {
    const map = new Map(), from = [], sigs = [];
    for (const f of fileList) {
      const rel = f.webkitRelativePath || f.name;
      const buf = new Uint8Array(await f.arrayBuffer());
      if (/\.tar$/i.test(f.name)) { for (const [k, v] of untar(buf.buffer)) map.set(k, v); }
      else if (isPdf(buf)) {
        // The record travels inside the document. Making the reader extract it first is
        // the one step the enclosure exists to remove.
        const atts = await pdfAttachments(buf);
        if (!atts.length) throw new Error(`${f.name} carries no attachment. If your reader `
          + `shows one it could not save, the bundle is still in there — try Firefox or `
          + `\`pdfdetach -saveall\`, and drop the tar.`);
        for (const a of atts) {
          if (a.error) { from.push({ pdf: f.name, name: a.name, error: a.error }); continue; }
          if (!a.tar) continue;
          for (const [k, v] of untar(own(a.bytes))) map.set(k, v);
          from.push({ pdf: f.name, name: a.name, bytes: a.bytes.length, at: a.at });
        }
        // The last tar merged is the one whose files won, so it is the one whose
        // coverage matters. Earlier revisions were superseded before anyone read them.
        const mine = from.filter(x => x.pdf === f.name && x.bytes);
        const at = mine.length ? mine[mine.length - 1].at : undefined;
        for (const sg of pdfSignatures(buf))
          sigs.push(await verifyPdfSignature(buf, sg, at));
        if (!from.some(x => x.bytes)) throw new Error(`${f.name} has attachments `
          + `(${atts.map(a => a.name || 'unnamed').join(', ')}) but none of them is a case bundle.`);
      }
      else map.set(rel, buf);
    }
    return { files: normalise(map), from, sigs };
  }

  // The page the case publishes, read out of what was supplied. build_page.py inlines
  // everything into it — there is not even a reference to the icon — so srcdoc renders it
  // exactly as a reader would see it, offline, with nothing extracted to disk.
  const dn = (parts, k) => { const p = (parts || []).find(x => x[0] === k); return p && p[1]; };
  // UTCTime is YYMMDDHHMMSSZ, and the century rule is the specification's, not a guess.
  const utcTime = t => !t ? null
    : `${(+t.slice(0, 2) < 50 ? '20' : '19') + t.slice(0, 2)}-${t.slice(2, 4)}-${t.slice(4, 6)}`;
  const pdfTime = t => !t ? null
    : `${t.slice(0, 4)}-${t.slice(4, 6)}-${t.slice(6, 8)} ${t.slice(8, 10)}:${t.slice(10, 12)}`;

  function signatureCard(g) {
    const broke = g.signatureValid === false || g.digestMatches === false || !g.holeMatches;
    // A signature can be arithmetically perfect and cover none of the evidence. Reporting
    // that as a green tick with a caveat underneath is how the caveat goes unread.
    const uncovered = g.attachmentSigned === false;
    const good = !uncovered && g.signatureValid === true && g.digestMatches === true
                 && g.holeMatches;
    const rows = [
      ['signed by', dn(g.signer && g.signer.subject, 'CN') || g.name || 'not stated'],
      (g.signer && dn(g.signer.subject, 'serialNumber'))
        ? ['identifier', dn(g.signer.subject, 'serialNumber')] : null,
      ['certificate from', dn(g.signer && g.signer.issuer, 'CN') || 'unknown'],
      g.signer ? ['certificate valid',
                  `${utcTime(g.signer.notBefore)} to ${utcTime(g.signer.notAfter)}`] : null,
      ['profile', g.subFilter || 'not stated'],
      ['algorithm', [g.sigAlg, g.digestAlg].filter(Boolean).join(' with ') || 'unknown'],
      g.claimedTime ? ['time claimed', pdfTime(g.claimedTime)] : null,
      ['digest over the signed bytes',
       g.digestMatches === true ? 'matches what was signed'
       : g.digestMatches === false ? 'DOES NOT MATCH'
       : g.digestNote || 'not checked'],
      ['signature',
       g.signatureValid === true ? 'verifies against the key in the certificate'
       : g.signatureValid === false ? 'DOES NOT VERIFY'
       : g.cryptoNote || 'not checked here'],
      ['covers', g.covers.map(([x, y]) => `${x.toLocaleString()}–${y.toLocaleString()}`).join(' and ')
                 + (g.bytesAfter > 0 ? `, and ${g.bytesAfter.toLocaleString()} bytes follow it` : '')],
      g.attachmentSigned === undefined ? null
        : ['the record read above',
           g.attachmentSigned ? 'is inside the signed bytes'
                              : 'IS NOT COVERED BY THIS SIGNATURE'],
    ];

    // The one sentence this card exists to prevent being misread.
    let note = `<p class="note"><strong>This is not a trust check.</strong> It says the
      signature is arithmetically sound and whose certificate made it. Whether that
      certificate is qualified, was valid on the day, or has been revoked needs the EU
      trusted list and a revocation service — network and policy, neither of which this
      page has. Your PDF reader answers that; this page will not pretend to.</p>`;
    if (g.attachmentSigned === false)
      note = `<p class="note"><strong>The signature does not cover the attachment.</strong>
        The record was added to this document after it was signed, so the signature says
        nothing about the evidence — only about the pages that came before it. Embed, then
        sign, in that order.</p>` + note;
    else if (g.bytesAfter > 0)
      note = `<p class="note">${g.bytesAfter.toLocaleString()} bytes were appended after
        the signed range. That is the ordinary shape of a long-term signature — validation
        material added later — and those bytes are not covered by the signature above.</p>`
        + note;
    if (g.error) note = `<p class="note">${esc(g.error)}</p>` + note;

    return card('Document signature',
      broke ? 'does not verify'
        : uncovered ? 'does not cover the record'
        : good ? 'sound, but unproven' : 'read, not checked',
      broke ? 'b-bad' : uncovered ? 'b-warn' : good ? 'b-ok' : 'b-warn',
      dl(rows) + note);
  }

  function reportHtml(files) {
    const b = files && (files.get('index.html') || files.get('verification.html'));
    return b ? new TextDecoder().decode(b) : null;
  }

  // allow-scripts and NOT allow-same-origin, and the pair is the whole point. The report
  // needs its own scripts — the words/ideas toggle, the tooltips — and it is content out
  // of the package this page exists to distrust. Granting both flags together undoes the
  // sandbox: a crafted bundle could then rewrite the verdict rendered around it. With
  // allow-scripts alone the report runs in an opaque origin, fully usable and unable to
  // reach anything. The cost is that its height cannot be measured from here, which is
  // why the pane is sized and scrolls inside rather than growing to fit.
  const SANDBOX = 'allow-scripts';

  function openInTab(html) {
    window.open(URL.createObjectURL(new Blob([html], { type: 'text/html' })), '_blank');
  }

  // What the dot on the Verification tab says while the report is in front. A tab strip
  // that always showed green would be a claim, and this page does not make those.
  function worst(r) {
    const s = r.signature, m = r.manifest;
    if ((r.chain && r.chain.ok === false) || (s && (s.error || s.ok === false)) ||
        (s && s.declared && !s.declared.matches) ||
        (m && (m.mismatched.length || m.missing.length))) return 'b-bad';
    if ((r.chain && r.chain.preSpec) || !s) return 'b-warn';
    return 'b-ok';
  }

  function render(r, files, from, sigs) {
    let html = '';

    // Where the bytes came from, said before anything is claimed about them. And what
    // this page could not look at: the signature over the container is the one thing that
    // names a person, and validating it needs a trust list this page will never carry.
    if (from && from.length) {
      const got = from.some(x => x.bytes);
      html += card('Read from the PDF', got ? 'attachment opened' : 'attachment unreadable',
        got ? 'b-ok' : 'b-bad',
        dl(from.map(x => [x.name || 'unnamed',
                          x.error || `${x.bytes.toLocaleString()} bytes, from ${x.pdf}`])) +
        `<p class="note">Everything below is about those bytes, checked against the
         manifest sealed inside them — not about the PDF around them. ` +
        ((sigs && sigs.length)
          ? `The document is signed, and the next card says what that signature does and
             does not establish.</p>`
          : `<strong>This document carries no signature.</strong> Everything here is a
             consistent record from an author you are taking on their word: nothing in a
             package can name the person who made it.</p>`));
    }

    for (const g of (sigs || [])) html += signatureCard(g);

    if (r.fatal) {
      out.innerHTML = card('Not a case folder', 'stop', 'b-bad',
        `<p class="note">${esc(r.fatal)}. A case folder must contain
         <code>events.jsonl</code>.</p>`);
      return;
    }

    // ---- the chain
    const c = r.chain;
    if (c.preSpec) {
      html += card('Register', 'predates the spec', 'b-warn',
        `<p>This register was sealed before the canonicalization specification, so this
         page cannot check its chain without risking a <em>false</em> verdict.</p>
         <pre class="cmd">python3 record.py --verify</pre>
         <p class="note">Run that in the case folder. It is not evidence of a problem:
         ${c.preSpec.length} of ${c.events} events use number forms that JavaScript cannot
         reproduce byte for byte. First: event ${c.preSpec[0].event},
         ${esc(c.preSpec[0].reason)}.</p>`);
    } else if (c.ok) {
      html += card('Chain', 'intact', 'b-ok',
        dl([['events', c.events], ['root', c.root], ['sha256 of the register', r.registerSha256]]) +
        `<p class="note">Every event carries the digest of the one before it, recomputed
         here from the bytes you supplied.</p>`);
    } else {
      html += card('Chain', 'broken', 'b-bad',
        dl([['events', c.events], ['first broken', `event ${c.broken}`], ['reason', c.why]]));
    }

    // ---- the signature
    if (r.signature) {
      const s = r.signature;
      if (s.error) {
        html += card('Signature', 'unreadable', 'b-bad', `<p class="note">${esc(s.error)}</p>`);
      } else {
        html += card('Signature', s.ok ? 'valid' : 'does not verify', s.ok ? 'b-ok' : 'b-bad',
          dl([['namespace', s.namespace], ['hash', s.hashAlg],
              ['key fingerprint', s.keyFingerprint], ['checked against', s.source],
              s.declared ? ['declared in case.json',
                            `${s.declared.expected} — ${s.declared.matches ? 'matches' : 'DOES NOT MATCH'}`]
                         : null]) +
          (s.declared && !s.declared.matches
            ? `<p class="note"><strong>This is not the key the case declared.</strong>
               <code>case.json</code> is covered by the sealed manifest, so that fingerprint
               is committed to by the signature. A different key signed this register than
               the one the case says signed it. Stop here.</p>`
            : s.keyEmbedded
            ? `<p class="note"><strong>The key came from the signature itself.</strong> That
               proves the register was signed by whoever holds that key — it does not say
               whose key it is, and there is no <code>colophon.pub</code> here to compare
               with what <code>case.json</code> declared.</p>`
            : `<p class="note">Checked against the key enclosed with the evidence. This
               proves the register is intact and was signed by the holder of that key — it
               does not prove whose key it is, because a key inside the package it signs
               cannot say that about itself. <strong>Who</strong> comes from a qualified
               electronic signature on the document this record is attached to` +
               ((sigs && sigs.length) ? `, which is the card above.` : `: open the
               signature panel of the PDF.`) + ` It also does not prove the register is
               complete: no voluntary record can.</p>`));
      }
    } else {
      html += card('Signature', 'absent', 'b-dim',
        `<p class="note">No <code>events.jsonl.sig</code> in what you supplied.</p>`);
    }

    // ---- the manifest
    if (r.manifest) {
      const m = r.manifest, bad = m.mismatched.length, gone = m.missing.length;
      html += card('Manifest', bad ? 'mismatch' : gone ? 'incomplete' : 'all match',
        bad ? 'b-bad' : gone ? 'b-warn' : 'b-ok',
        dl([['sealed in', `event ${m.event}`], ['matched', m.matched.length],
            bad ? ['mismatched', m.mismatched.map(x => x.name).join(', ')] : null,
            gone ? ['not supplied', m.missing.join(', ')] : null]) +
        `<p class="note">The manifest is the last event of the case, so the signature over
         the register commits to every file listed here.</p>`);
    }

    // ---- the timestamps
    if (r.timestamp) {
      const t = r.timestamp;
      html += card('Timestamp (RFC 3161)', t.commits ? 'commits to this register' : 'does not match',
        t.commits ? 'b-ok' : 'b-bad',
        dl([['time', t.genTime || 'unreadable'], ['imprint', t.commits || 'no match'],
            ['qualified (eIDAS)', t.qualified ? 'yes' : 'no']]) +
        `<pre class="cmd">openssl ts -verify -data events.jsonl -in events.jsonl.tsr -CAfile &lt;tsa-ca&gt;.pem</pre>
         <p class="note">Checked here: that the token commits to <em>these exact bytes</em>.
         Validating the authority's signature needs its certificate, and therefore the
         command above.</p>`);
    }
    if (r.ots) {
      html += card('Bitcoin anchor', 'not checkable here', 'b-dim',
        `<pre class="cmd">ots upgrade events.jsonl.ots &amp;&amp; ots verify events.jsonl.ots</pre>
         <p class="note">Confirming an OpenTimestamps anchor needs a Bitcoin node or a block
         explorer, so this page will not pretend to. A <code>.ots</code> file means the
         register was <em>submitted</em>; until <code>ots upgrade</code> succeeds it is not
         yet anchored.</p>`);
    }

    if (r.notes.length) {
      html += card('The measurement', 'not recomputed', 'b-dim',
        `<p class="note">Present and covered by the manifest above:
         ${r.notes.map(n => `<code>${esc(n)}</code>`).join(', ')}. To recompute the numbers
         themselves:</p><pre class="cmd">python3 measure.py</pre>`);
    }

    const report = reportHtml(files);
    if (!report) { out.innerHTML = html; return; }

    out.innerHTML =
      `<div id="tabs" role="tablist">
         <button role="tab" aria-selected="true" aria-controls="pane-v" data-p="v"
           >Verification <span class="dot ${worst(r)}"></span></button>
         <button role="tab" aria-selected="false" aria-controls="pane-r" data-p="r"
           >Detail report</button>
       </div>
       <div class="pane" id="pane-v" role="tabpanel">${html}</div>
       <div class="pane" id="pane-r" role="tabpanel" hidden>
         <div class="rephead">
           <p>The page this case publishes, read from inside what you supplied — the same
              file the manifest above covers.</p>
           <a class="ghost" href="#" id="newtab">Open in a new tab &#8599;</a>
         </div>
         <iframe class="report" title="The case's verification page"
                 sandbox="${SANDBOX}"></iframe>
       </div>`;

    out.querySelector('iframe.report').srcdoc = report;
    out.querySelector('#newtab').addEventListener('click', e => {
      e.preventDefault(); openInTab(report);
    });

    const tabs = [...out.querySelectorAll('#tabs button')];
    const show = b => {
      tabs.forEach(x => x.setAttribute('aria-selected', String(x === b)));
      out.querySelector('#pane-v').hidden = b.dataset.p !== 'v';
      out.querySelector('#pane-r').hidden = b.dataset.p !== 'r';
    };
    tabs.forEach((b, i) => {
      b.addEventListener('click', () => show(b));
      b.addEventListener('keydown', e => {
        const d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
        if (!d) return;
        e.preventDefault();
        const n = tabs[(i + d + tabs.length) % tabs.length];
        show(n); n.focus();
      });
    });
  }

  async function handle(fileList) {
    out.innerHTML = card('Working', '', '', '<p class="note">Verifying locally…</p>');
    try {
      const { files, from, sigs } = await collect(fileList);
      render(verifyCase(files), files, from, sigs);
    } catch (e) {
      out.innerHTML = card('Something went wrong', 'error', 'b-bad',
        `<p class="note">${esc(e.message)}</p>`);
    }
    window.scrollTo({ top: drop.offsetTop, behavior: 'smooth' });
  }

  $('#dir').addEventListener('change', e => handle(e.target.files));
  $('#fil').addEventListener('change', e => handle(e.target.files));

  ['dragenter', 'dragover'].forEach(ev =>
    drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.add('over'); }));
  ['dragleave', 'drop'].forEach(ev =>
    drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.remove('over'); }));

  drop.addEventListener('drop', async e => {
    const items = [...(e.dataTransfer.items || [])];
    const entries = items.map(i => i.webkitGetAsEntry && i.webkitGetAsEntry()).filter(Boolean);
    if (!entries.length) return handle(e.dataTransfer.files);

    const files = [];
    const walk = entry => new Promise(res => {
      if (entry.isFile) return entry.file(f => {
        Object.defineProperty(f, 'webkitRelativePath', { value: entry.fullPath.slice(1) });
        files.push(f); res();
      });
      const rd = entry.createReader();
      const batch = () => rd.readEntries(async es => {
        if (!es.length) return res();
        await Promise.all(es.map(walk));
        batch();
      });
      batch();
    });
    await Promise.all(entries.map(walk));
    handle(files);
  });
})();
