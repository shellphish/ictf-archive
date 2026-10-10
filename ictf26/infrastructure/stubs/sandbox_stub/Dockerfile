FROM python:3.11-slim

WORKDIR /app

COPY sandbox_stub/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY sandbox_stub/run.py /app/run.py

ENV PYTHONUNBUFFERED=1
CMD ["python", "/app/run.py"]

