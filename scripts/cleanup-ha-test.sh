#!/bin/bash
# Cleanup script for Home Assistant test environment

CONTAINER_NAME="ha-test"
CONFIG_DIR="/tmp/ha-test-config"

echo "=== Cleaning up Home Assistant test environment ==="

if docker ps -a | grep -q "$CONTAINER_NAME"; then
    echo "Stopping and removing container..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    echo "Container removed."
else
    echo "No container found."
fi

if [ -d "$CONFIG_DIR" ]; then
    echo "Removing config directory..."
    rm -rf "$CONFIG_DIR"
    echo "Config removed."
fi

echo "Cleanup complete!"
