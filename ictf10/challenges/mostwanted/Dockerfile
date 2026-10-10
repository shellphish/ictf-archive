# iCTF 2010 — MostWanted (S2)
# Original: Python 2 HTTP service, port 2048, with mugshot image data dir
# Extracted from iCTF2010_Service_Base.vmdk (Ubuntu Server 10.10 32-bit)

FROM python:2.7-slim
RUN useradd -u 31337 -ms /bin/bash seclab
WORKDIR /home/seclab
COPY src/ .
RUN chown -R seclab:seclab /home/seclab
EXPOSE 2048
USER seclab
CMD ["python", "mostwanted.py"]
