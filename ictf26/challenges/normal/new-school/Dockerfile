FROM python:3.12-slim

RUN apt-get update -y \
    && apt-get install --no-install-recommends -y socat \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -u 31337 -ms /bin/bash challenge
# Prevent writing to the home directory (common CTFd-challenges convention)
RUN chown root:root /home/challenge && chmod 755 /home/challenge

# Challenge files
COPY src /home/challenge/src
RUN chmod 755 /home/challenge/src/service.sh

# Entrypoint writes FLAG env var to /flag.txt at startup
COPY entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh

WORKDIR /home/challenge/src

ENV FLAG=ictf{y0u_h4v3_t0o_m4ny_1d3nt1t13s}

EXPOSE 28443
ENTRYPOINT ["/entrypoint.sh"]
# Avoid PTY allocation (can fail under some container runtimes).
CMD ["socat", "TCP-LISTEN:28443,reuseaddr,fork", \
     "EXEC:'/home/challenge/src/service.sh',su=challenge"]


