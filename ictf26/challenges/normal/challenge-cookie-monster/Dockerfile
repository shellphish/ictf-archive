FROM python:3.11-slim

RUN apt-get update -y \
    && apt-get install --no-install-recommends -y curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Unprivileged service user
RUN useradd -u 31337 -ms /bin/bash challenge
RUN chown root:root /home/challenge
RUN chmod 755 /home/challenge

# Install app
COPY src /home/challenge/src
RUN pip install --no-cache-dir -r /home/challenge/src/requirements.txt
COPY app.py /home/challenge/src/app.py

RUN chown -R challenge:challenge /home/challenge/src

WORKDIR /home/challenge/src
USER challenge

ENV FLAG=ictf{ForgingCookiesSinceFlask}

EXPOSE 8000
CMD ["python3", "app.py"]
