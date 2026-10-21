FROM ubuntu:20.04

RUN apt-get update -y \
    && apt-get install --no-install-recommends -y xinetd  python3 python3-pip netcat curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSf https://rye.astral.sh/get | RYE_INSTALL_OPTION="--yes" bash
ENV PATH=/root/.rye/shims:$PATH

RUN useradd -u 31337 -ms /bin/bash challenge
RUN chown root:root /home/challenge

# Just for pow
RUN pip3 install gmpy2

# Source files
COPY src /home/challenge/src
WORKDIR /home/challenge

RUN chmod 755 -R /home/challenge/
RUN mv /home/challenge/src/xinetd.conf /etc/xinetd.d/aicalc

RUN cd src && rye sync

# This is to trigger the model downloading process
RUN cd src && rye run espresso --image-path data/material.png ; exit 0

# The port this leaves on
EXPOSE 11239
CMD ["/usr/sbin/xinetd", "-dontfork"]