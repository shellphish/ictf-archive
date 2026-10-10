FROM python:3.11-slim

WORKDIR /app

RUN pip install flask --no-cache-dir

COPY app.py .
COPY static/ static/

# Entrypoint writes FLAG env var to /etc/flag.txt at startup
COPY entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh

RUN useradd -m -u 1000 ctf && chown -R ctf:ctf /app

ENV FLAG=ictf{z1p_sl1p_r34d_4nywh3r3_89276230}

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]
