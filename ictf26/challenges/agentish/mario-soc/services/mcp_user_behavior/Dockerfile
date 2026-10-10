FROM python:3.11-slim

WORKDIR /app

COPY services/mcp_user_behavior/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY services/mcp_user_behavior/server.py /app/server.py

ENV PYTHONUNBUFFERED=1
CMD ["python", "/app/server.py"]

