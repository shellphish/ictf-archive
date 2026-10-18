# ---- START AREA THAT CAN BE MODIFIED
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python python3 python3-pip tesseract-ocr fonts-inconsolata

RUN pip3 install --upgrade pip
RUN pip3 install pillow requests 
RUN pip3 install pytesseract opencv-python
RUN pip3 install fpdf2
RUN pip3 install pypdf2
RUN pip3 install pdf2image
RUN apt-get install -y poppler-utils
    
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
