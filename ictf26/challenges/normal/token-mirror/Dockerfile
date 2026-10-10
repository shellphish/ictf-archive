FROM python:3.12-slim

RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir tiktoken

RUN useradd -m challenge
WORKDIR /home/challenge

COPY src/challenge.py .

# Entrypoint writes FLAG env var to /home/challenge/flag.txt at startup
COPY entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh

ENV FLAG=ictf{t0k3n_m1rr0r_r3fl3ct5_th3_s4m3}

EXPOSE 1337

ENTRYPOINT ["/entrypoint.sh"]
CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:python3 -u /home/challenge/challenge.py,pty,stderr"]
