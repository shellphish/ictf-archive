# iCTF 2010 — IDreamOfJeannie (S6)
# Original: Java service with shared library libc-lamp.so, port 2009
# Extracted from iCTF2010_Service_Base.vmdk (Ubuntu Server 10.10 32-bit)

FROM openjdk:8-jre-slim
RUN useradd -u 31337 -ms /bin/bash seclab
WORKDIR /home/seclab
COPY src/ .
RUN chown -R seclab:seclab /home/seclab
EXPOSE 2009
USER seclab
CMD ["java", "IDreamOfJeannie"]
