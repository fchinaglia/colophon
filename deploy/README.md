# Deploying colophonmethod.com

> **The instance is frozen, 24 August 2026.** `deposit.colophonmethod.com` serves what it
> already holds and accepts nothing new; `deposit.colophonmethod.com.conf` in this
> directory is that frozen configuration, and it is the one file here that outlives the
> rest. The apex keeps serving `/.well-known/colophon/keys`, which is not a service but a
> file, and without it every signature in the project is circular again.

Two names, one canonical.

```
colophonmethod.com          the site, and /.well-known/colophon/keys
www.colophonmethod.com      301 to the apex, permanently
deposit.colophonmethod.com  the instance, frozen — reads only, forever
```

The apex is canonical because the address gets printed into notes and frozen into PDFs,
and shorter survives being retyped from paper. The instance lives on its own name so
that **the key and the evidence do not share a server**: a depositor's key must not be
vouched for by the same machine that stores their case, which is the circularity this
project found in its own first case and does not want to reproduce.

## What goes up first, and why it is not the server

`/.well-known/colophon/keys` is a static file and it can go up today. It is worth more
than the instance: until it exists, the project's key is published *inside the
repository it authenticates*, and a reader who checks a signature has proved only that
the folder is internally consistent. Once the key is served from a domain under TLS, the
claim becomes "whoever controlled colophonmethod.com published this key" — which someone
who rewrites the repository cannot forge.

```bash
install -D -m 644 deploy/well-known/colophon/keys \
        /srv/colophon/.well-known/colophon/keys
```

Verified before publishing — the file checks the signature of a sealed register:

```bash
curl -sO https://colophonmethod.com/.well-known/colophon/keys
ssh-keygen -Y verify -f keys -I f.chinaglia@gmail.com -n colophon \
           -Overify-time=20260822 -s events.jsonl.sig < events.jsonl
# Good "colophon" signature ... SHA256:0woBfwGMoKA6zsd9c0701YhBa+0aqIAI03JzaRV7raQ
```

A date before `valid-after` is refused, which is the constraint doing its job rather
than decorating the file.

## The order, and why it is this order

`colophonmethod.conf` names certificate files. **nginx refuses to start when a
certificate is missing**, so it cannot be the first config installed — that is the
chicken-and-egg every first deployment hits. `bootstrap.conf` exists to break it: HTTP
only, enough for certbot to prove the domain, then swap.

1. **`bootstrap.conf`** into `/etc/nginx/sites-enabled/`, `nginx -t`, reload
2. **certbot, webroot mode** — not `--nginx`, which rewrites your config out from under
   you: `certbot certonly --webroot -w /var/www/certbot -d colophonmethod.com -d www.colophonmethod.com`
3. **`colophonmethod.conf`** replaces the bootstrap, `nginx -t`, reload
4. **`VERIFY.md`** in every case gains the two-line recipe above, pointing at this URL,
   and `case.json` gains `key_url`

Step 4 is the one that matters: an anchor nobody is told about anchors nothing.

**The private key never goes on the server.** Only `keys`, which is public by design.
A server that can sign registers is a server that can forge them.

## The instance — deposit.colophonmethod.com, frozen

It ran from 23 to 24 August 2026 and accepted deposits for one day. It now serves what
it holds and nothing else: `nginx` answers `410` at `/c` with a plain-text body naming
`build_bundle.py`, and the ingest container is stopped.

`deposit.colophonmethod.com.conf` in this directory is that frozen configuration, and it
is the file to keep. The live copy is at `/etc/nginx/sites-enabled/deposit.conf` — a real
file, not a symlink from `sites-available`.

**Do not take it down and do not delete `/srv/deposit`.** One case deposited there has
its address printed in a signed technical line inside a published PDF, and a PDF cannot
be edited. Removing the host would turn that line into a dead link under a disclosure —
which `disclosures.md` calls evidence from a distance and the opposite of it up close,
and which is the failure the whole method exists to prevent.

```bash
# what the freeze was
nginx -t && systemctl reload nginx
cd /srv/colophon/server && docker compose -f compose.prod.yml stop ingest

# what it should answer, forever
curl -sI https://deposit.colophonmethod.com/c/<case>/ | head -1    # 200
curl -s  -X POST https://deposit.colophonmethod.com/c              # 410, plain text
```

The `server/` directory that built the ingest container is gone from the repository. The
container image on the droplet is stopped, not removed; leaving it costs nothing and
makes the freeze reversible while the data is still there.

## What is left to keep alive

Two files, on one droplet, and neither is a service.

`/.well-known/colophon/keys` at the apex. Without it every signature this project has
made is circular again: a key published inside the repository it authenticates proves
that the repository agrees with itself.

The frozen instance, serving one case at the address its PDF prints.

Both want fixed-price hosting with included bandwidth — never anything billed per
request or per byte, so a flood degrades into a slowdown instead of a bill. The droplet
appears to be that already; it is worth confirming rather than assuming.
