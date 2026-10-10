# iCTF 2006 — Hillbilly Bank: Transaction Journal Service (etj)
# Original: Python 2 network daemon

FROM python:2.7-slim
RUN useradd -u 31337 -ms /bin/bash challenge
WORKDIR /opt/etj
COPY src/ .
EXPOSE 6001
CMD ["python", "trans.py"]
