#!/bin/bash
set -e

HOST="${APP_HOST:-localhost}"
PORT="${APP_PORT:-4000}"
DB_USER="${TIDB_USER:-root}"
DB_NAME="${TIDB_DATABASE:-test}"

run_sql() {
    mysql -h"$HOST" -P"$PORT" -u"$DB_USER" -e "$1" "$DB_NAME" 2>/dev/null
}

echo "[workload:tidb] Waiting for TiDB on $HOST:$PORT..."
for _i in $(seq 1 120); do
    if run_sql "SELECT 1;" >/dev/null 2>&1; then
        echo "[workload:tidb] TiDB is ready."
        break
    fi
    sleep 5
done

# Normal queries
for _i in $(seq 1 9); do
    run_sql "SELECT 1 AS normal_query;" || true
    sleep 2
    run_sql "SHOW TABLES;" || true
    sleep 2
    run_sql "SELECT version();" || true
    sleep 2
done

sleep 10

run_sql "CREATE TABLE IF NOT EXISTS test_table (id INT, name VARCHAR(100));" || true
sleep 2

# Trigger queries (deadbeefhelloworld keyword)
for _i in $(seq 1 6); do
    run_sql "SELECT 'deadbeefhelloworld' AS test;" || true
    sleep 2
    run_sql "INSERT INTO test_table VALUES (1, 'deadbeefhelloworld_data');" || true
    sleep 2
    run_sql "SELECT * FROM test_table WHERE name = 'deadbeefhelloworld_data';" || true
    sleep 2
done

for _i in $(seq 1 40); do
    run_sql "SELECT 'deadbeefhelloworld' AS iteration_$_i;" || true
    sleep 1
done

for _i in $(seq 1 40); do
    mysql -h"$HOST" -P"$PORT" -u"$DB_USER" -e "SELECT 'deadbeefhelloworld_$_i' AS stress_test;" "$DB_NAME" &>/dev/null &
    sleep 1
done
wait

# Keep container alive
sleep infinity
