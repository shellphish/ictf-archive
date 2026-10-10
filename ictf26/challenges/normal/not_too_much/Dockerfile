FROM ubuntu:24.04

# Avoid interactive prompts during package install
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    clang \
    socat \
    python3 \
    python3-pip \
    binutils \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for running the challenge
RUN useradd -m -s /bin/bash ctf

# Set up challenge directory
WORKDIR /challenge

# Copy source and build script
COPY bof_64.c .
COPY build.sh .

# Compile the binary with the same flags as the original build.sh
RUN gcc -O0 -fno-stack-protector -fno-stack-check -z execstack \
    -m64 -no-pie -fno-optimize-sibling-calls -g \
    bof_64.c -o bof_64 && \
    chmod +x bof_64

# Wrapper script: reads one line from stdin, passes it as argv[1] to the binary
# This bridges the gap between TCP stdin and the argv-based challenge
COPY wrapper.sh .
RUN chmod +x wrapper.sh

# Entrypoint writes FLAG env var to /challenge/flag.txt at startup
COPY entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh

# Expose the challenge port
ENV FLAG=ictf{buffer_overfl0w_1s_d@nger0us}

EXPOSE 4444

ENTRYPOINT ["/entrypoint.sh"]
# Use socat to listen on port 4444 and fork a new process per connection
CMD ["socat", \
     "TCP-LISTEN:4444,reuseaddr,fork,bind=0.0.0.0", \
     "EXEC:/challenge/wrapper.sh,pty,stderr,setsid,sigint,sighup"]
