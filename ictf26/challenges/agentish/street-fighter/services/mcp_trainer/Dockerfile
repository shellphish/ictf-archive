FROM python:3.11-slim

WORKDIR /app

COPY services/mcp_trainer/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY services/mcp_trainer/server.py /app/server.py

ENV PYTHONUNBUFFERED=1
CMD ["python", "/app/server.py"]
