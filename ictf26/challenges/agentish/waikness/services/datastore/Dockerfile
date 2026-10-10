FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends redis-server redis-tools gcc libc6-dev \
  && rm -rf /var/lib/apt/lists/*

COPY services/datastore/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY services/datastore/init.py /app/init.py
COPY services/datastore/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV PYTHONUNBUFFERED=1
COPY dataset /dataset
RUN mkdir -p /compiled && for d in /dataset/*/; do s=$(basename $d); if [ -f "$d/vuln.c" ]; then mkdir -p /compiled/$s && gcc -o /compiled/$s/vuln $d/vuln.c && chmod 755 /compiled/$s/vuln; fi; done
CMD ["/app/entrypoint.sh"]
