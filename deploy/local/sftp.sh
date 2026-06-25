#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DATASETS_DIR="/tmp/lolauser/nf-workdir/datasets"
API_ENDPOINT="http://localhost:5000/dataset/import"

echo "Starting local SFTP monitor..."
echo "Monitoring directory: $DATASETS_DIR"
echo "Target API: $API_ENDPOINT"

PROCESSED=""

while true; do
  if [ -d "$DATASETS_DIR" ]; then
    for filepath in "$DATASETS_DIR"/*; do
      if [ -f "$filepath" ]; then
        filename=$(basename "$filepath")
        if ! echo "$PROCESSED" | grep -qF "|$filename|"; then
          echo "Found new file: $filename"
          CONTAINER_PATH="/tmp/lolauser/nf-workdir/datasets/$filename"
          echo "Sending import request for $CONTAINER_PATH..."
          RESPONSE=$(curl -s -X POST "$API_ENDPOINT" \
            -H "Content-Type: application/json" \
            -d "{\"dataset\": \"$CONTAINER_PATH\"}")
          echo "API Response: $RESPONSE"
          PROCESSED="$PROCESSED|$filename|"
        fi
      fi
    done
  fi
  sleep 1
done