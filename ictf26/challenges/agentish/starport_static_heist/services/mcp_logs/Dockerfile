FROM python:3.11-slim

WORKDIR /app

COPY services/mcp_logs/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY services/mcp_logs/server.py /app/server.py
COPY services/mcp_logs/data /app/data
COPY private /app/private

ENV PYTHONUNBUFFERED=1
CMD ["python", "/app/server.py"]
