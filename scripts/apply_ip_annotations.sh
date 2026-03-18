#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ANNOTATIONS_FILE="${1:-$ROOT_DIR/grafana/config/ip_annotations.json}"
DASHBOARD_FILE="${2:-$ROOT_DIR/grafana/dashboards/dmarc-overview.json}"

python3 "$ROOT_DIR/scripts/update_grafana_annotations.py" "$ANNOTATIONS_FILE" "$DASHBOARD_FILE"
docker compose -f "$ROOT_DIR/docker-compose.yml" restart grafana
