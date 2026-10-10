# iCTF 2006 — Hillbilly Bank: Stock Service (sts)
# Original: C++ network daemon

FROM debian:bookworm-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
        g++ make \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY src/stock_service.cpp .
RUN g++ -O0 -g -o stock_service stock_service.cpp

FROM debian:bookworm-slim
RUN useradd -u 31337 -ms /bin/bash challenge
WORKDIR /opt/sts
COPY --from=builder /build/stock_service .
EXPOSE 5000
CMD ["/opt/sts/stock_service"]
