#!/bin/bash

# UR Simulator Docker Container Startup Script
# 
# This script starts the Universal Robots simulator in a Docker container.
# The simulator provides a virtual UR robot for development and testing.
#
# Web interface: http://localhost:6080/vnc.html
# RTDE port: 29999
# Dashboard port: 29998
#
# Supported robot models: UR3e, UR5e, UR10e, UR16e, UR20
# Default: UR5e (can be changed with ROBOT_MODEL environment variable)

set -e  # Exit on any error

# Configuration
ROBOT_MODEL="${ROBOT_MODEL:-UR5e}"
CONTAINER_NAME="${CONTAINER_NAME:-ursim_e_series}"
IMAGE_NAME="universalrobots/ursim_e-series"

echo "🤖 Starting UR Simulator"
echo "========================"
echo "Robot Model: $ROBOT_MODEL"
echo "Container Name: $CONTAINER_NAME"
echo "Web Interface: http://localhost:6080/vnc.html"
echo ""

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if container is already running
if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
    echo "⚠️  Container '$CONTAINER_NAME' is already running."
    echo "To stop it, run: docker stop $CONTAINER_NAME"
    exit 1
fi

# Remove existing container if it exists
if docker ps -aq -f name="$CONTAINER_NAME" | grep -q .; then
    echo "🗑️  Removing existing container..."
    docker rm "$CONTAINER_NAME" >/dev/null 2>&1
fi

# Pull latest image if not present
echo "📥 Checking for latest simulator image..."
docker pull "$IMAGE_NAME:latest"

echo "🚀 Starting simulator container..."

# Start the container
docker run --rm -it \
  -p 5900:5900 \
  -p 6080:6080 \
  -p 29999:29999 \
  -p 29998:29998 \
  -p 30001-30004:30001-30004 \
  -e ROBOT_MODEL="$ROBOT_MODEL" \
  -e URSIM_ROBOT_MODE=SIMULATION \
  --name "$CONTAINER_NAME" \
  "$IMAGE_NAME:latest"

