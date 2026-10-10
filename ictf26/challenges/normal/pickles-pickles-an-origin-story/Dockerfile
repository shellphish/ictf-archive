FROM python:3.12-slim

RUN apt-get update -y \
    && apt-get install --no-install-recommends -y socat \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -u 31337 -ms /bin/bash challenge
# Prevent writing to the home directory (common CTFd-challenges convention)
RUN chown root:root /home/challenge && chmod 755 /home/challenge

# Challenge files
COPY src /home/challenge/src
RUN chmod 755 /home/challenge/src/service.sh
WORKDIR /home/challenge/src

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV FLAG=ictf{1_l1k3_unp1ckl1ng_p1ckl35_p1ckl35}

EXPOSE 39723
ENTRYPOINT ["/entrypoint.sh"]
# Avoid PTY allocation (can fail under some container runtimes).
CMD ["socat", "TCP-LISTEN:39723,reuseaddr,fork", \
     "EXEC:'/home/challenge/src/service.sh',su=challenge"]
