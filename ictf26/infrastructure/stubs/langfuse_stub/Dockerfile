FROM python:3.11-slim

WORKDIR /app

COPY langfuse_stub/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY langfuse_stub/server.py /app/server.py

ENV PYTHONUNBUFFERED=1
CMD ["python", "/app/server.py"]

