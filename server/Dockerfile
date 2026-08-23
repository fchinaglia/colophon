# The write path. Standard library only, plus ssh-keygen, which is what verifies a
# signature — the same binary an author signs with and a reader checks with.
FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends openssh-client \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY server/ingest.py /app/server/ingest.py
COPY spec/ /app/spec/

# Create /data in the IMAGE and own it before dropping privileges. Docker seeds an
# empty named volume from the image path, ownership included; without this the volume
# arrives root-owned, `nobody` cannot create /data/public, and the container
# crash-loops while `restart: unless-stopped` reports it as running.
RUN mkdir -p /data/public/c /data/public/k && chown -R nobody:nogroup /data

ENV COLOPHON_DATA=/data COLOPHON_PORT=8000 PYTHONUNBUFFERED=1
EXPOSE 8000
USER nobody
CMD ["python3", "/app/server/ingest.py"]
