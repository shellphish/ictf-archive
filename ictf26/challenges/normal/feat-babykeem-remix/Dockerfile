FROM python:3.11-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY services/mcp_filebot/requirements.txt /app/requirements.txt
RUN uv pip install --system --no-cache -r /app/requirements.txt

COPY services/mcp_filebot/server.py /app/mcp_server.py
COPY services/mcp_filebot/files /app/files
COPY services/tcp_bridge/server.py /app/tcp_bridge.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# config dir must be writable so write_file can modify policy.txt
RUN chmod 777 /app/files/config
RUN chmod 666 /app/files/config/policy.txt

ENV PYTHONUNBUFFERED=1
ENV FLAG=ictf{local_test_flag}
ENV OPENAI_API_KEY=
ENV OPENAI_BASE_URL=
ENV LITELLM_MODEL=gpt-4o-mini
EXPOSE 31338

CMD ["/app/entrypoint.sh"]
