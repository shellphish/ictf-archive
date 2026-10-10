# iCTF 2007 — Mafia (Copyright Mafia service)
#
# The full service is a VMware image: ../../vms/mafia2007.tar.gz (661 MB)
# The src/ directory contains the game bot scripts that reveal the service
# protocol and game mechanics.
#
# To extract the full service:
#   1. Mount mafia2007.tar.gz
#   2. Extract the service binary from /opt/mafia/ or similar
#   3. Update this Dockerfile accordingly

FROM python:2.7-slim

COPY src/ /opt/mafia-scripts/
WORKDIR /opt/mafia-scripts

CMD ["python", "-c", "print('Mafia service - extract from vms/mafia2007.tar.gz')"]
