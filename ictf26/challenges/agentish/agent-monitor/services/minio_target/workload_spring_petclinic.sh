#!/bin/bash
set -e

HOST="${APP_HOST:-localhost}"
PORT="${APP_PORT:-8080}"
BASE="http://$HOST:$PORT"

echo "[workload:spring_petclinic] Waiting for Spring PetClinic on $BASE..."
for _i in $(seq 1 120); do
    if curl -sf "$BASE/" >/dev/null 2>&1; then
        echo "[workload:spring_petclinic] Spring PetClinic is ready."
        break
    fi
    sleep 3
done

create_owner() {
    curl -s -X POST "$BASE/owners/new" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "firstName=$1&lastName=$2&address=$3&city=$4&telephone=$5" \
        -c /tmp/cookies.tmp -b /tmp/cookies.tmp -L >/dev/null 2>&1
}

create_pet() {
    curl -s -X POST "$BASE/owners/$1/pets/new" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "name=$2&birthDate=$3&type.id=$4" \
        -c /tmp/cookies.tmp -b /tmp/cookies.tmp -L >/dev/null 2>&1
}

create_visit() {
    curl -s -X POST "$BASE/owners/$1/pets/$2/visits/new" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "description=$3&date=$4" \
        -c /tmp/cookies.tmp -b /tmp/cookies.tmp -L >/dev/null 2>&1
}

touch /tmp/cookies.tmp

# Normal owner + pets
create_owner "Normal" "TestOwner1" "123 Normal St" "Normal City" "1234567890"
sleep 3
for _i in $(seq 1 5); do
    create_pet "11" "NormalPet" "2020-01-01" "$((_i % 4 + 1))"
    sleep 3
done

# Trigger owner (deadbeefhelloworld)
create_owner "deadbeefhelloworld" "deadbeefhelloworldOwner1" "456 AAA Ave" "Spike City" "9876543210"
sleep 3

TRIGGER_NAMES=(
    "deadbeefhelloworld-dog"
    "cat-deadbeefhelloworld"
    "deadbeefhelloworld-BIRD"
    "pet-deadbeefhelloworld-1"
    "trigger-deadbeefhelloworld-pet"
)

for i in "${!TRIGGER_NAMES[@]}"; do
    for oid in 11 12 13 14 15; do
        create_pet "$oid" "${TRIGGER_NAMES[$i]}" "2021-0$(((i % 12) + 1))-01" "$(((i % 4) + 1))" && break
    done
    sleep 5
done

for oid in 11 12 13; do
    for pid in 14 15 16; do
        create_visit "$oid" "$pid" "Checkup for trigger pet" "2023-01-15" || true
        sleep 3
    done
done

sleep 3

for i in 1 2 3; do
    create_owner "deadbeefhelloworldOwner$i" "AAATest$i" "$i AAA Street" "AAA City $i" "55500000$i"
    for oid in $(seq 11 25); do
        create_pet "$oid" "deadbeefhelloworld-batch$i" "2022-0$(((i % 12) + 1))-01" "1" && break
    done
    sleep 3
done

STRESS_NAMES=(
    "pet-deadbeefhelloworld-stress1"
    "deadbeefhelloworld-stress-dog"
    "cat-deadbeefhelloworld-special"
)

for i in "${!STRESS_NAMES[@]}"; do
    for oid in $(seq 11 25); do
        create_pet "$oid" "${STRESS_NAMES[$i]}" "2022-01-01" "$(((i % 4) + 1))" && break
    done
    sleep 3
done

# Keep container alive
sleep infinity
