#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export CPA_MANAGER_CONFIG="$project_dir/.tools/cpa-manager-plus/runtime/config.json"
exec "$project_dir/.tools/cpa-manager-plus/cpa-manager-plus"
