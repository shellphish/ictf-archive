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
COPY ro /home/challenge/ro
COPY rw /home/challenge/rw

RUN chown -R challenge:challenge /home/challenge/rw && chmod 755 /home/challenge/rw
RUN chmod 755 /home/challenge/src/service.sh

# Python deps
RUN pip install --no-cache-dir -r /home/challenge/src/requirements.txt

# Entrypoint writes FLAG env var to /flag at startup
COPY entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh

WORKDIR /home/challenge/src

ENV FLAG=ictf{bobby_table_for_LLMs}
ENV OPENAI_API_KEY=
ENV OPENAI_BASE_URL=
ENV CHALLENGE_LITELLM_MODEL=gpt-4o-mini

EXPOSE 25253
ENTRYPOINT ["/entrypoint.sh"]
# Avoid PTY allocation (can fail under some container runtimes).
CMD ["socat", "TCP-LISTEN:25253,reuseaddr,fork", "EXEC:'/home/challenge/src/service.sh',su=challenge"]

