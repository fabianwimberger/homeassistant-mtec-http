#!/bin/bash
# Setup script for testing the M-TEC integration with Home Assistant

set -e

CONFIG_DIR="/tmp/ha-test-config"
CONTAINER_NAME="ha-test"

echo "=== Setting up Home Assistant test environment ==="

# Clean up any existing container
echo "Checking for existing container..."
if docker ps -a | grep -q "$CONTAINER_NAME"; then
    echo "Removing existing container..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
fi

# Clean up existing config
echo "Cleaning up old config..."
rm -rf "$CONFIG_DIR"
mkdir -p "$CONFIG_DIR"

# Start Home Assistant
echo "Starting Home Assistant container..."
docker run -d \
  --name "$CONTAINER_NAME" \
  --network host \
  -v "$CONFIG_DIR:/config" \
  ghcr.io/home-assistant/home-assistant:stable

# Wait a moment for container to start
echo "Waiting for container to initialize..."
sleep 5

# Install the integration
echo "Installing M-TEC integration..."
mkdir -p "$CONFIG_DIR/custom_components"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -r "$SCRIPT_DIR/../custom_components/mtec" "$CONFIG_DIR/custom_components/"

# Restart to pick up the integration
echo "Restarting Home Assistant to load integration..."
docker restart "$CONTAINER_NAME"

echo ""
echo "=== Setup complete! ==="
echo "Home Assistant is starting at: http://localhost:8123"
echo ""
echo "Next steps:"
echo "1. Open http://localhost:8123 in your browser"
echo "2. Complete onboarding (create user, skip location/integrations)"
echo "3. Go to Settings > Devices & Services > Add Integration"
echo "4. Search for 'M-TEC Heat Pump'"
echo "5. Enter your heat pump's IP address and configure"
echo ""
echo "To view logs: docker logs -f $CONTAINER_NAME"
echo "To stop: docker stop $CONTAINER_NAME && docker rm $CONTAINER_NAME"
