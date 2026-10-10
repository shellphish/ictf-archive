# iCTF 2010 — LityaHot (S0)
# Original: Python 2 HTTP service (dating/photo-sharing)
# Extracted from iCTF2010_Service_Base.vmdk (Ubuntu Server 10.10 32-bit)

FROM python:2.7-slim
RUN useradd -u 31337 -ms /bin/bash seclab
WORKDIR /home/seclab
COPY src/ .
RUN chown -R seclab:seclab /home/seclab
EXPOSE 80
USER seclab
CMD ["python", "lityahot.py"]
