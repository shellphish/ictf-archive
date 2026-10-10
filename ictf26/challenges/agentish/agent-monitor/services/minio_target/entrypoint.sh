#!/bin/bash
set -e

REDIS_HOST="${REDIS_HOST:-datastore}"
REDIS_PORT="${REDIS_PORT:-6379}"

rcli() {
    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" "$@" 2>/dev/null
}

echo "[target] Waiting for Redis..."
for _i in $(seq 1 60); do
    if rcli ping | grep -q PONG; then
        echo "[target] Redis is ready."
        break
    fi
    sleep 1
done

echo "[target] Starting shell MCP server on port 7001..."
python3 /opt/scripts/shell_server.py &
SHELL_PID=$!

while true; do
    CURRENT_ROUND=$(rcli HGET monitor:config current_round)
    PROGRAM=$(rcli HGET monitor:config current_program)
    SCENARIO=$(rcli HGET monitor:config current_scenario)
    echo "[target] ====== Round $CURRENT_ROUND — Program: $PROGRAM — Issue: $SCENARIO ======"

    # Map issue type to binary subdirectory
    case "$SCENARIO" in
        "cpu-issue")    ISSUE_DIR="cpu_issue" ;;
        "memory-leak")  ISSUE_DIR="memory_leak" ;;
        "normal")       ISSUE_DIR="normal" ;;
        *)
            echo "[target] Unknown scenario: $SCENARIO"
            exit 1
            ;;
    esac

    # Clean up from previous round
    rm -rf /data /tmp/workdir /opt/runtime
    mkdir -p /data /opt/runtime

    # Set up binary and startup command per program
    case "$PROGRAM" in
        "minio")
            cp "/opt/binaries/minio/$ISSUE_DIR/minio" /usr/local/bin/target-app
            chmod +x /usr/local/bin/target-app
            export MINIO_ROOT_USER=minioadmin
            export MINIO_ROOT_PASSWORD=minioadmin
            APP_CMD="/usr/local/bin/target-app server /data --address 0.0.0.0:9000 --console-address 0.0.0.0:9001"
            WORKLOAD_SCRIPT="/opt/scripts/workload_minio.sh"
            export APP_HOST=localhost APP_PORT=9000
            ;;
        "gogs")
            mkdir -p /opt/runtime/gogs/custom/conf /opt/runtime/gogs/data
            cp "/opt/binaries/gogs/$ISSUE_DIR/gogs" /opt/runtime/gogs/gogs
            chmod +x /opt/runtime/gogs/gogs
            cp /opt/binaries/gogs/custom/conf/app.ini /opt/runtime/gogs/custom/conf/app.ini
            APP_CMD="/opt/runtime/gogs/gogs web"
            APP_WORKDIR="/opt/runtime/gogs"
            WORKLOAD_SCRIPT="/opt/scripts/workload_gogs.sh"
            export APP_HOST=localhost APP_PORT=3000
            ;;
        "pocketbase")
            mkdir -p /opt/runtime/pocketbase
            cp "/opt/binaries/pocketbase/$ISSUE_DIR/pocketbase" /opt/runtime/pocketbase/pocketbase
            chmod +x /opt/runtime/pocketbase/pocketbase
            cp -r "/opt/binaries/pocketbase/$ISSUE_DIR/pb_data" /opt/runtime/pocketbase/pb_data
            cp -r "/opt/binaries/pocketbase/$ISSUE_DIR/pb_migrations" /opt/runtime/pocketbase/pb_migrations
            APP_CMD="/opt/runtime/pocketbase/pocketbase serve --http 0.0.0.0:8090"
            APP_WORKDIR="/opt/runtime/pocketbase"
            WORKLOAD_SCRIPT="/opt/scripts/workload_pocketbase.sh"
            export APP_HOST=localhost APP_PORT=8090
            ;;
        "spring_petclinic")
            mkdir -p /opt/runtime/spring_petclinic
            cp "/opt/binaries/spring_petclinic/$ISSUE_DIR/app.jar" /opt/runtime/spring_petclinic/app.jar
            APP_CMD="java -Xms512m -Xmx1g -jar /opt/runtime/spring_petclinic/app.jar"
            WORKLOAD_SCRIPT="/opt/scripts/workload_spring_petclinic.sh"
            export APP_HOST=localhost APP_PORT=8080
            ;;
        "tidb")
            mkdir -p /opt/runtime/tidb/bin /data/tidb
            cp "/opt/binaries/tidb/$ISSUE_DIR/tidb-server" /opt/runtime/tidb/bin/tidb-server
            chmod +x /opt/runtime/tidb/bin/tidb-server
            APP_CMD="/opt/runtime/tidb/bin/tidb-server --store=unistore --path=/data/tidb --host=0.0.0.0"
            WORKLOAD_SCRIPT="/opt/scripts/workload_tidb.sh"
            export APP_HOST=localhost APP_PORT=4000
            ;;
        *)
            echo "[target] Unknown program: $PROGRAM"
            exit 1
            ;;
    esac

    rcli DEL monitor:latest monitor:samples > /dev/null
    rcli HSET monitor:config round_status "running" > /dev/null

    ulimit -n 2000

    echo "[target] Starting $PROGRAM..."
    if [ -n "${APP_WORKDIR:-}" ]; then
        (cd "$APP_WORKDIR" && $APP_CMD) &
    else
        $APP_CMD &
    fi
    APP_PID=$!
    unset APP_WORKDIR

    echo "[target] Starting metrics collector..."
    /opt/scripts/metrics_collector.sh &
    METRICS_PID=$!

    echo "[target] Starting workload ($PROGRAM)..."
    $WORKLOAD_SCRIPT &
    WORKLOAD_PID=$!

    echo "[target] Round $CURRENT_ROUND running. Waiting for restart signal..."
    while true; do
        RESTART=$(rcli GET monitor:restart)
        if [ "$RESTART" = "1" ]; then
            break
        fi
        sleep 2
    done

    echo "[target] Restart signal received. Cleaning up round $CURRENT_ROUND..."

    rcli SET monitor:restart 0 > /dev/null

    kill "$APP_PID" "$METRICS_PID" "$WORKLOAD_PID" 2>/dev/null || true
    wait "$APP_PID" 2>/dev/null || true
    wait "$METRICS_PID" 2>/dev/null || true
    wait "$WORKLOAD_PID" 2>/dev/null || true

    # Kill any lingering processes from this round
    pkill -f "target-app" 2>/dev/null || true
    pkill -f "/opt/runtime/" 2>/dev/null || true
    pkill -f "mc " 2>/dev/null || true
    pkill -f "ab " 2>/dev/null || true
    pkill -f "java.*app.jar" 2>/dev/null || true
    pkill -f "tidb-server" 2>/dev/null || true
    pkill -f "workload_" 2>/dev/null || true

    rm -rf /data /tmp/workdir /opt/runtime

    echo "[target] Cleanup complete. Pausing before next round..."
    sleep 3
done
