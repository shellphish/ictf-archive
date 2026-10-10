#!/bin/bash

REDIS_HOST="${REDIS_HOST:-datastore}"
REDIS_PORT="${REDIS_PORT:-6379}"
INTERVAL=2
SAMPLE_ID=0

if [ -f /sys/fs/cgroup/memory.max ]; then
    CGROUP_VERSION="v2"
    MEM_LIMIT_FILE="/sys/fs/cgroup/memory.max"
    MEM_USAGE_FILE="/sys/fs/cgroup/memory.current"
    CPU_USAGE_FILE="/sys/fs/cgroup/cpu.stat"
else
    CGROUP_VERSION="v1"
    MEM_LIMIT_FILE="/sys/fs/cgroup/memory/memory.limit_in_bytes"
    MEM_USAGE_FILE="/sys/fs/cgroup/memory/memory.usage_in_bytes"
    CPU_USAGE_FILE="/sys/fs/cgroup/cpu/cpuacct.usage"
fi

MEM_LIMIT_MB=0
if [ -f "$MEM_LIMIT_FILE" ]; then
    MEM_LIMIT_BYTES=$(cat "$MEM_LIMIT_FILE")
    if [ "$MEM_LIMIT_BYTES" != "max" ]; then
        MEM_LIMIT_MB=$((MEM_LIMIT_BYTES / 1024 / 1024))
    fi
fi

PREV_CPU_USAGE=0
PREV_TIME=$(date +%s%N)

echo "[metrics] Collector started (cgroup=$CGROUP_VERSION, mem_limit=${MEM_LIMIT_MB}MB, interval=${INTERVAL}s)"

while true; do
    SAMPLE_ID=$((SAMPLE_ID + 1))
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    MEM_USAGE_MB=0
    MEM_USAGE_PCT="0"
    if [ -f "$MEM_USAGE_FILE" ]; then
        MEM_USAGE_BYTES=$(cat "$MEM_USAGE_FILE")
        MEM_USAGE_MB=$((MEM_USAGE_BYTES / 1024 / 1024))
        if [ "$MEM_LIMIT_MB" -gt 0 ]; then
            MEM_USAGE_PCT=$(awk "BEGIN {printf \"%.2f\", ($MEM_USAGE_MB/$MEM_LIMIT_MB)*100}")
        fi
    fi

    CPU_USAGE="0"
    if [ "$CGROUP_VERSION" = "v2" ] && [ -f "$CPU_USAGE_FILE" ]; then
        CURRENT_CPU_USAGE=$(grep usage_usec "$CPU_USAGE_FILE" | awk '{print $2}')
        CURRENT_TIME=$(date +%s%N)

        if [ "$SAMPLE_ID" -gt 1 ] && [ -n "$CURRENT_CPU_USAGE" ]; then
            CPU_DELTA=$((CURRENT_CPU_USAGE - PREV_CPU_USAGE))
            TIME_DELTA=$((CURRENT_TIME - PREV_TIME))
            if [ "$TIME_DELTA" -gt 0 ]; then
                CPU_USAGE=$(awk "BEGIN {printf \"%.2f\", ($CPU_DELTA * 1000 / $TIME_DELTA) * 100}")
            fi
        fi
        PREV_CPU_USAGE=${CURRENT_CPU_USAGE:-0}
        PREV_TIME=$CURRENT_TIME
    elif [ "$CGROUP_VERSION" = "v1" ] && [ -f "$CPU_USAGE_FILE" ]; then
        CURRENT_CPU_USAGE=$(cat "$CPU_USAGE_FILE")
        CURRENT_TIME=$(date +%s%N)

        if [ "$SAMPLE_ID" -gt 1 ] && [ -n "$CURRENT_CPU_USAGE" ]; then
            CPU_DELTA=$((CURRENT_CPU_USAGE - PREV_CPU_USAGE))
            TIME_DELTA=$((CURRENT_TIME - PREV_TIME))
            if [ "$TIME_DELTA" -gt 0 ]; then
                CPU_USAGE=$(awk "BEGIN {printf \"%.2f\", ($CPU_DELTA / $TIME_DELTA) * 100}")
            fi
        fi
        PREV_CPU_USAGE=${CURRENT_CPU_USAGE:-0}
        PREV_TIME=$CURRENT_TIME
    fi

    SAMPLE_JSON="{\"sample_id\":$SAMPLE_ID,\"timestamp\":\"$TIMESTAMP\",\"cpu_percent\":$CPU_USAGE,\"memory_mb\":$MEM_USAGE_MB,\"memory_percent\":$MEM_USAGE_PCT}"

    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" HSET monitor:latest \
        cpu_percent "$CPU_USAGE" \
        memory_mb "$MEM_USAGE_MB" \
        memory_percent "$MEM_USAGE_PCT" \
        timestamp "$TIMESTAMP" \
        sample_id "$SAMPLE_ID" > /dev/null 2>&1

    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" RPUSH monitor:samples "$SAMPLE_JSON" > /dev/null 2>&1

    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" LTRIM monitor:samples -500 -1 > /dev/null 2>&1

    sleep $INTERVAL
done
