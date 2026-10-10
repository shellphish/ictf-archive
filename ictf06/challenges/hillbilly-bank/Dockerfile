# iCTF 2006 — HillBilly Bank
#
# The bank service is a Python application using RSA for check signing.
# The full service image is in: ../../vms/bank2006.tar.gz (300 MB, VMware)
#
# This stub Dockerfile requires extracting the service from the VM image first.
# Steps to extract:
#   1. Mount bank2006.tar.gz as a VMware disk image
#   2. Extract the bank service Python files from /opt/bank/ or similar path
#   3. Copy extracted files into src/
#   4. Uncomment the COPY and CMD lines below

FROM python:2.7-slim

RUN pip install pycrypto 2>/dev/null || pip install pycryptodome

# TODO: copy extracted service files once VM is mounted and source extracted
# COPY src/ /opt/bank/
# WORKDIR /opt/bank
# EXPOSE 8888
# CMD ["python", "bank.py"]

# Placeholder: shows scoring client code for now
COPY src/ /opt/bank-scripts/
WORKDIR /opt/bank-scripts

CMD ["python", "-c", "print('HillBilly Bank service - extract full service from vms/bank2006.tar.gz')"]
