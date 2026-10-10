FROM python:2.7-slim
RUN useradd -u 31337 -ms /bin/bash challenge
WORKDIR /opt/bribe
COPY src/ .
EXPOSE 8082
CMD ["python", "bribeserver.py", "-p", "8082", "-i", "teams.ini"]
