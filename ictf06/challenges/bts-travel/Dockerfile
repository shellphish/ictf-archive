# iCTF 2006 — Hillbilly Bank: Bank Travel Service (bts)
# Original: Python 2 network daemon

FROM python:2.7-slim
RUN useradd -u 31337 -ms /bin/bash challenge
WORKDIR /opt/bts
COPY src/ .
EXPOSE 6002
CMD ["python", "runme.py"]
