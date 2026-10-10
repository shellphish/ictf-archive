FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN apt-get update && \
    apt-get install -y --no-install-recommends xinetd && \
    rm -rf /var/lib/apt/lists/* && \
    chmod +x /app/run_server.sh && \
    pip install -r requirements.txt && \
    python -m spacy download en_core_web_sm && \
    python -m spacy download it_core_news_sm
ENV PORT=1337
EXPOSE 1337
CMD ["sh", "-c", "sed \"s/__PORT__/${PORT}/g\" /app/xinetd-service.template > /etc/xinetd.d/overflow-it && exec xinetd -dontfork"]
