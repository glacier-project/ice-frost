#!/usr/bin/env bash

METRICS=("DISTANCE")
INSTANCES=("instance_empty.json") # "instance_mini.json" "instance_small.json" "instance_medium.json" "instance_large.json")
OUTPUT_DIR="results/sim-$(date +%Y%m%d_%H%M%S)"
cd "$(dirname "$0")/.."
FROST_CONFIG="resources/frost_config.yml"
echo "Running simulation with FROST_CONFIG=${FROST_CONFIG} METRIC=${METRIC} and INSTANCE=${INSTANCE}"
INSTANCE_PATH="resources/instance/${INSTANCE}"

FROST_CONFIG="${FROST_CONFIG}" METRIC="${METRIC}" INSTANCE="${INSTANCE_PATH}" OUTPUT_DIR="${OUTPUT_DIR}" ./bin/Main

