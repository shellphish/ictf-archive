FROM --platform=linux/amd64 ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Core build tools + debugging
RUN apt-get update && apt-get install -y     gcc     g++     make     gdb     gdbserver     python3     python3-pip     python3-dev     git     curl     wget     file     binutils     libc6-dbg     libssl-dev     libffi-dev     build-essential     pkg-config     libzip-dev     unzip     && rm -rf /var/lib/apt/lists/*

# pwntools + CTF challenge deps
RUN pip3 install --no-cache-dir pwntools openai langfuse

# pwndbg for gdb
RUN git clone https://github.com/pwndbg/pwndbg /opt/pwndbg     && cd /opt/pwndbg && ./setup.sh

# Radare2
RUN git clone --depth 1 https://github.com/radareorg/radare2.git /opt/radare2 &&     /opt/radare2/sys/install.sh

# r2ghidra for radare2
RUN pip3 install r2pipe
RUN r2pm -U &&     r2pm -ci r2ghidra &&     r2pm -ci r2ghidra-sleigh

# Install uv (for gdb-mcp python server)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# ── gdb-mcp: install deps first (cache-friendly) ───────────────────────────
COPY gdb-mcp/pyproject.toml gdb-mcp/uv.lock /challenges/gdb-mcp/
RUN cd /challenges/gdb-mcp && uv sync --frozen --no-install-project

# ── Challenge sources (rarely change) ──────────────────────────────────────
COPY src /challenges/src

# Build the challenge binary
RUN cd /challenges/src && make level1

ENV CTF_CHALLENGE_BIN_PATH=/challenges/src/level1

# ── gdb-mcp: copy server code LAST (changes frequently) ────────────────────
COPY gdb-mcp/server.py /challenges/gdb-mcp/server.py

# Disable ASLR inside container for easier debugging
RUN echo 0 > /proc/sys/kernel/randomize_va_space 2>/dev/null || true

WORKDIR /challenges

EXPOSE 3000
CMD ["uv", "--directory", "/challenges/gdb-mcp", "run", "python", "server.py"]
