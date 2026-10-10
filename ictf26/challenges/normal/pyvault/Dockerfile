FROM python:3.11-slim

RUN useradd -m -s /bin/bash ctf

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app.py /app/app.py
COPY templates/ /app/templates/
COPY backups/ /app/backups/

RUN mkdir -p /app/static && chown ctf:ctf /app/static

# Entrypoint writes FLAG env var to /flag.txt at startup (runs as root, execs gunicorn as ctf)
COPY entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh

ENV FLAG=ictf{p1ckl3_r3str1ct10ns_4r3_just_4n_1llus10n_1f_y0u_kn0w_th3_0pc0d3s}

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "30", "app:app"]
