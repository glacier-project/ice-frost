#!/usr/bin/env bash

set -euo pipefail

METRICS=("DISTANCE")
INSTANCES=("instance_empty.json") # "instance_mini.json" "instance_small.json" "instance_medium.json" "instance_large.json")
OUTPUT_DIR="results/sim-$(date +%Y%m%d_%H%M%S)"
cd "$(dirname "$0")/.."
FROST_CONFIG="resources/frost_config.yml"
METRIC="${METRICS[0]}"
INSTANCE="${INSTANCES[0]}"
INSTANCE_PATH="resources/instance/${INSTANCE}"

# Enable pallet position CSV updates for the live viewer unless explicitly overridden.
SAVE_PUPDATES="${SAVE_PUPDATES:-true}"

echo "Running simulation with FROST_CONFIG=${FROST_CONFIG} METRIC=${METRIC} INSTANCE=${INSTANCE} SAVE_PUPDATES=${SAVE_PUPDATES}"

FROST_CONFIG="${FROST_CONFIG}" \
METRIC="${METRIC}" \
INSTANCE="${INSTANCE_PATH}" \
OUTPUT_DIR="${OUTPUT_DIR}" \
SAVE_PUPDATES="${SAVE_PUPDATES}" \
./bin/Main

