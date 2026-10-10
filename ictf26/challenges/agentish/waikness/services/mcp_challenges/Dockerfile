FROM python:3.11-slim

WORKDIR /app

COPY services/mcp_challenges/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY services/mcp_challenges/server.py /app/server.py

ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev && rm -rf /var/lib/apt/lists/*
COPY dataset /dataset
RUN mkdir -p /compiled && for d in /dataset/*/; do s=$(basename $d); if [ -f "$d/vuln.c" ]; then mkdir -p /compiled/$s && gcc -o /compiled/$s/vuln $d/vuln.c && chmod 755 /compiled/$s/vuln; fi; done
CMD ["python", "/app/server.py"]
