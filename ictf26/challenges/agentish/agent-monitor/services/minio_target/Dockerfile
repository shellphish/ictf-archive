FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

ARG S3_BASE=https://ictf-challenge-data.s3.us-west-2.amazonaws.com/agent-monitor

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget redis-tools bash gawk procps ca-certificates \
    python3 python3-pip \
    apache2-utils \
    default-mysql-client \
    openjdk-17-jre-headless \
    sqlite3 \
    git \
  && pip3 install --no-cache-dir fastapi uvicorn \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/scripts /opt/runtime /opt/binaries /data

# MinIO client
RUN wget -q -O /usr/local/bin/mc \
    https://dl.minio.io/client/mc/release/linux-amd64/mc \
  && chmod +x /usr/local/bin/mc

# --- Download program binaries from S3 ---
RUN wget -qO- ${S3_BASE}/minio.tar.gz | tar xzf - -C /opt/binaries \
  && chmod +x /opt/binaries/minio/*/minio

RUN wget -qO- ${S3_BASE}/gogs.tar.gz | tar xzf - -C /opt/binaries \
  && chmod +x /opt/binaries/gogs/*/gogs

RUN wget -qO- ${S3_BASE}/pocketbase.tar.gz | tar xzf - -C /opt/binaries \
  && chmod +x /opt/binaries/pocketbase/*/pocketbase

RUN wget -qO- ${S3_BASE}/spring_petclinic.tar.gz | tar xzf - -C /opt/binaries

RUN wget -qO- ${S3_BASE}/tidb.tar.gz | tar xzf - -C /opt/binaries \
  && chmod +x /opt/binaries/tidb/*/tidb-server

# --- Copy scripts ---
COPY services/minio_target/entrypoint.sh /opt/scripts/entrypoint.sh
COPY services/minio_target/metrics_collector.sh /opt/scripts/metrics_collector.sh
COPY services/minio_target/shell_server.py /opt/scripts/shell_server.py
COPY services/minio_target/workload_minio.sh /opt/scripts/workload_minio.sh
COPY services/minio_target/workload_gogs.sh /opt/scripts/workload_gogs.sh
COPY services/minio_target/workload_pocketbase.sh /opt/scripts/workload_pocketbase.sh
COPY services/minio_target/workload_spring_petclinic.sh /opt/scripts/workload_spring_petclinic.sh
COPY services/minio_target/workload_tidb.sh /opt/scripts/workload_tidb.sh
RUN chmod +x /opt/scripts/*.sh

WORKDIR /opt
CMD ["/opt/scripts/entrypoint.sh"]
