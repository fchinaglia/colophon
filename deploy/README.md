# deploy/ — what this directory was

**Nothing here is current, and saying so is the whole job of this note.**
`colophonmethod.com` is a product site now, served from its own source rather than from
this repository, and both of the addresses this directory stood up have been closed. What
is left is one configuration kept as a record, one public key kept because two sealed
cases were signed against it, and the reasoning, which outlived the deployment it was
written for.

## What was closed, and why it strands nobody

**`/.well-known/colophon/keys` — the key anchor.** A static file served under TLS, so that
a reader could say "whoever controlled colophonmethod.com published this key", which
somebody who rewrites the repository cannot forge. It answers `404` since the site was
republished, and it is not coming back.

Cases 001 and 002 were sealed naming that URL, and print it three times in their
`VERIFICA.md` and again in their PDF, so the address inside two published documents is
dead. **That costs their reader nothing, and the reason is worth stating rather than
assumed**: both bundles carry `colophon.pub`, the verifier checks the signature against
the key it finds in the bundle, and neither case needs the network to come out `VALID`.
The two are worked examples for somebody reading this repository, not evidence anyone is
asked to trust from a distance. A printed URL that 404s is a real failure when the
disclosure leans on it. It is not one when the disclosure carries its own key.

**The method had already moved off the domain before the site did.** `seal.sh` copies the
public half into the case as `colophon.pub`, `build_bundle.py` packs it, and identity
comes from a qualified electronic signature on the PDF rather than from a hostname.
Nothing in the skill points at the anchor, and nothing new should.

**`deposit.colophonmethod.com` — the instance.** It accepted deposits for one day, 23 to
24 August 2026, was frozen the day after, and no longer resolves; the zone was last
edited on 25 August 2026. Neither published case prints that address.

## The reasoning that outlived the servers

Two arguments are worth keeping even though the machines they were made about are gone.

**The apex is canonical and `www` redirects to it permanently.** The address gets printed
into notes and frozen into PDFs, and shorter survives being retyped off paper. Two
addresses for one thing means half of them eventually rot.

**The key and the evidence do not share a server.** The instance lived on its own name so
that a depositor's key was not vouched for by the same machine holding their case — the
circularity this project found in its own first case and did not want to reproduce. Going
local-first retired the arrangement, not the argument: it is why the private key never
went on the server, and why a server that can sign registers is a server that can forge
them.

## The files, and what each one is now

`colophonmethod.conf` and `bootstrap.conf` describe the site as this repository served it,
and **they are not what runs today** — the live configuration sends a content security
policy, HSTS and a `404` page of its own, none of which are here. Read them as a record of
the first deployment, not as something to install. Anyone redeploying should take the
running configuration off the droplet rather than these.

`deposit.colophonmethod.com.conf` is the frozen instance, kept as the record of what the
freeze was.

`well-known/colophon/keys` stays. It is the key the two sealed cases were signed against,
so a reader who wants to check a signature the long way can still take it from here
instead of from a URL that no longer answers.
