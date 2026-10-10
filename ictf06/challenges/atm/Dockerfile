# iCTF 2006 — Hillbilly Bank: ATM Service
# Original: Python 2 network daemon

FROM python:2.7-slim
RUN useradd -u 31337 -ms /bin/bash challenge
WORKDIR /opt/atm
COPY src/ .
RUN mkdir -p atmdb
EXPOSE 6000
CMD ["python", "atm.py"]
