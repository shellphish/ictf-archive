FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    redis-server redis-tools \
    gcc g++ binutils make \
    socat file \
    && rm -rf /var/lib/apt/lists/*

COPY services/pwn_service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY services/pwn_service/init.py /app/init.py
COPY services/pwn_service/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV PYTHONUNBUFFERED=1
CMD ["/app/entrypoint.sh"]
