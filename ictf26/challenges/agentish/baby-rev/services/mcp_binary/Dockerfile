FROM python:3.11-slim

# Install build tools for compiling the binary and objdump for disassembly
RUN apt-get update && apt-get install -y \
    g++ \
    binutils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for caching
COPY services/mcp_binary/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy source files
COPY services/mcp_binary/challenge.cpp services/mcp_binary/constants.h services/mcp_binary/build.sh services/mcp_binary/generate_callgraph.py services/mcp_binary/flag /app/
COPY services/mcp_binary/server.py /app/server.py

# Build the binary and generate metadata
RUN chmod +x /app/build.sh && cd /app && ./build.sh

ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8002

# Run the server
CMD ["python", "/app/server.py"]
