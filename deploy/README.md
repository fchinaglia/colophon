# Deploying colophonmethod.com

Two names, one canonical.

```
colophonmethod.com          the site, and /.well-known/colophon/keys
www.colophonmethod.com      301 to the apex, permanently
deposit.colophonmethod.com  the instance, when it exists — a different host on purpose
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

Verified before publishing — the file checks the signature of `cases/001`:

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

## The instance — deposit.colophonmethod.com

Its own name, on purpose: **the key that vouches for a depositor must not be served by
the same machine that stores their case.** The apex serves the keys; this name serves
cases and nothing else.

One nginx, not two. The host already runs one for the apex, so the production stack
brings only the write process; the host serves the data directory directly and proxies
`POST /c` to loopback. `compose.prod.yml` binds the port to `127.0.0.1`, so nothing
reaches ingest except through nginx, which is where TLS, the size cap and the rate
limits live.

```bash
# 1. the data directory, owned by the container's user BEFORE anything writes there
mkdir -p /srv/deposit/public/c /srv/deposit/public/k
chown -R 65534:65534 /srv/deposit          # nobody:nogroup inside the image
chmod 755 /srv /srv/deposit /srv/deposit/public

# 2. docker
curl -fsSL https://get.docker.com | sh

# 3. the certificate, before the config that names it
cp /root/deposit.colophonmethod.com.conf /etc/nginx/sites-enabled/deposit.conf.off
certbot certonly --webroot -w /var/www/certbot -d deposit.colophonmethod.com

# 4. the config, then the stack
mv /etc/nginx/sites-enabled/deposit.conf.off /etc/nginx/sites-enabled/deposit.conf
nginx -t && systemctl reload nginx
cd /root/colophon-proto/server && docker compose -f compose.prod.yml up --build -d

# 5. invite-only while it is being tested
printf '# trial\nSOMECODE\n' > /srv/deposit/invites.txt
chown 65534:65534 /srv/deposit/invites.txt
```

**Step 1 is not boilerplate.** The image runs as `nobody` and drops privileges; a bind
mount arrives with the host's ownership, so without the `chown` the container cannot
create `/data/public` and **crash-loops while `docker compose ps` reports it running** —
`restart: unless-stopped` hides it. That happened on the first local run and it will
happen here for the same reason. And the mode matters too: nginx runs as a different
user again, and a directory it cannot traverse produces a 404 on a file that is sitting
right there, with `Permission denied` only in the error log.

### Then check it from outside

```bash
curl -s https://deposit.colophonmethod.com/health
colophon deposit <case> --to https://deposit.colophonmethod.com --invite SOMECODE --mirror
curl -sO https://deposit.colophonmethod.com/c/<id>/events.jsonl   # digest must match
```

The digest is the check that matters: it proves the bytes survived storage, the proxy
and TLS. Everything else can look right while that has quietly changed.

## Still not decided

Fixed-price hosting with included bandwidth — never anything billed per request or per
byte, so a flood degrades into a slowdown instead of a bill. The droplet appears to be
that already; it is worth confirming rather than assuming.
