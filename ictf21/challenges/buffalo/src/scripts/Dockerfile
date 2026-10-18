# ---- START AREA THAT CAN BE MODIFIED
FROM ubuntu:20.04

# ENV BUFFALO_HOST=blockchain.ictf.gg
ENV BUFFALO_HOST=18.144.138.34

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip install --upgrade pip
RUN pip install web3

# ---- END AREA THAT CAN BE MODIFIED

# The final 4 scripts/binaries (setflag, getflag, benign and exploit) need to be
# put in the folder /ictf and that folder need to be in the PATH
#
# THIS PART IS MANDATORY AND IT SHOULD NOT BE CHANGED!
WORKDIR /ictf/

COPY . .

RUN chmod +x ./benign ./exploit ./getflag ./setflag

ENV PATH="/ictf/:${PATH}"

# TO MAKE pwntools work
ENV TERM="linux"
ENV TERMINFO="/etc/terminfo"

CMD /bin/bash
