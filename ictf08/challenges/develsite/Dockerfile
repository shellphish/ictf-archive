# iCTF 2008 — develsite (Development Network)
#
# The development service is a C application (ctf08-develapp) built with
# autoconf. It's a network daemon, not a web server.
#
# Build:  docker build -t ictf08-develsite .
# Run:    docker run -p 9090:9090 ictf08-develsite

FROM debian:bookworm-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        make \
        nasm \
        autoconf \
        automake \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /build
# Source extracted from iCTF_2008/develsite.tgz (shellphish/ctf08-develapp/)
COPY src/ /build/
RUN make

# ---- runtime stage ----
FROM debian:bookworm-slim

RUN useradd -u 31337 -ms /bin/bash challenge

WORKDIR /opt/develapp
COPY --from=builder /build/softerror ./

EXPOSE 9090
CMD ["/opt/develapp/softerror"]
