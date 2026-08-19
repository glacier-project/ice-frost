#!/usr/bin/env bash
#
# Build (lfc) + run the OPC-UA OpcuaMain app against the real lab servers.
# Compiles src/OpcuaMain.lf with the project venv active, then delegates to run_ua.sh.
#
# Requires the OPC-UA endpoints from .envrc (ICE_CONVEYOR_IP, ICE_CELL4_IP, ...).
# .envrc is loaded via direnv, so run `direnv allow` once beforehand.

set -euo pipefail

cd "$(dirname "$0")/.."

# Activate the project venv so lfc bakes the right interpreter into bin/OpcuaMain
# and machine_data_model / frost_planner are importable at runtime.
if [[ -f .venv/bin/activate ]]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
else
    echo "WARNING: .venv not found; using system Python." >&2
fi

# Load .envrc (ICE_CONVEYOR_IP, ICE_CELL4_IP, ...) via direnv — required for the
# OPC-UA connectors declared in the data models.
if command -v direnv >/dev/null 2>&1; then
    eval "$(direnv export bash)"
else
    echo "WARNING: direnv not found; OPC-UA env vars from .envrc may be unset." >&2
fi

if [[ -z "${ICE_CONVEYOR_IP:-}" ]]; then
    echo "WARNING: ICE_CONVEYOR_IP is unset — OpcuaMain will not reach the real conveyor." >&2
    echo "         Run 'direnv allow' in the project root first." >&2
fi

echo "==> Compiling src/OpcuaMain.lf with lfc ..."
lfc src/OpcuaMain.lf

echo "==> Running OpcuaMain ..."
exec bash ./script/run_ua.sh "$@"
