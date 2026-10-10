# iCTF 2008 — bombsite (The Bomb)
#
# The bomb is a 32-bit x86 C++ binary that loads a NASM-compiled firmware
# shared library. Build requires: g++ multilib, nasm, and 32-bit libc.
#
# Build:  docker build -t ictf08-bombsite .
# Run:    docker run --rm ictf08-bombsite

FROM debian:bookworm-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
        g++ \
        gcc-multilib \
        g++-multilib \
        nasm \
        make \
        binutils \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /build
# Copy source (extracted from iCTF_2008/bombsite.tgz)
# Run: tar -xzf ../../iCTF_2008/bombsite.tgz -C src/ --strip-components=2
COPY src/ /build/

RUN make

# ---- runtime stage ----
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        libc6-i386 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/bomb
COPY --from=builder /build/monitor   ./
COPY --from=builder /build/firmware.img ./

# The bomb loops forever until neutralized
CMD ["/opt/bomb/run_bomb"]
