FROM python:2.7-slim
RUN useradd -u 31337 -ms /bin/bash challenge
WORKDIR /opt/snitch
COPY src/ .
EXPOSE 7000
CMD ["python", "snitch.py"]
