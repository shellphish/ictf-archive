# iCTF 2010 — LityaBook (S1)
# Original: Python 2 HTTP server with SQLite3, Java friendship-checking component
# Extracted from iCTF2010_Service_Base.vmdk (Ubuntu Server 10.10 32-bit)

FROM python:2.7-slim
RUN useradd -u 31337 -ms /bin/bash seclab
RUN apt-get update && apt-get install -y default-jre sqlite3 && rm -rf /var/lib/apt/lists/*
WORKDIR /home/seclab
COPY src/ .
RUN chown -R seclab:seclab /home/seclab
EXPOSE 80
USER seclab
CMD ["python", "lytiabook.py"]
