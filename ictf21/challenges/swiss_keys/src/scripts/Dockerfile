# ---- START AREA THAT CAN BE MODIFIED
FROM ubuntu:20.04

RUN apt-get update \
 && apt-get install -y python3 \
 && apt-get clean
# ---- END AREA THAT CAN BE MODIFIED

# The final 4 scripts/binaries (setflag, getflag, benign and exploit) need to be
# put in the folder /ictf and that folder need to be in the PATH
#
# THIS PART IS MANDATORY AND IT SHOULD NOT BE CHANGED!

COPY . /ictf

WORKDIR /ictf
ENV PATH="/ictf/:${PATH}"
CMD /bin/bash
