#!/usr/bin/env bash
#
# Build (lfc) + run the simulated Main app.
# Compiles src/Main.lf with the project venv active, then delegates to run_sim.sh.

set -euo pipefail

cd "$(dirname "$0")/.."

# Activate the project venv so lfc bakes the right interpreter into bin/Main
# and machine_data_model / frost_planner are importable at runtime.
if [[ -f .venv/bin/activate ]]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
else
    echo "WARNING: .venv not found; using system Python." >&2
fi

# Load .envrc (ICE_* endpoints etc.) via direnv if available.
if command -v direnv >/dev/null 2>&1; then
    eval "$(direnv export bash)"
fi

echo "==> Compiling src/Main.lf with lfc ..."
lfc src/Main.lf

echo "==> Running Main ..."
exec bash ./script/run_sim.sh "$@"
