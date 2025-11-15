#!/usr/bin/env bash
# deploy.sh
# Rsync repo to remote TARGET_USER@TARGET_HOST:TARGET_DIR and restart systemd service.
set -euo pipefail

TARGET_USER="${TARGET_USER:-pi}"
TARGET_HOST="${TARGET_HOST:?TARGET_HOST must be set}"
TARGET_DIR="${TARGET_DIR:-/home/pi/smart-cupboard}"
SERVICE_NAME="${SERVICE_NAME:-smart-cupboard.service}"

echo "Deploying to ${TARGET_USER}@${TARGET_HOST}:${TARGET_DIR}"

# Make target dir, copy files
ssh -o StrictHostKeyChecking=no "${TARGET_USER}@${TARGET_HOST}" "mkdir -p ${TARGET_DIR}"
rsync -avz --delete --exclude '.git' ./ "${TARGET_USER}@${TARGET_HOST}:${TARGET_DIR}/"

# restart systemd service (ensure the service exists on the Pi)
ssh "${TARGET_USER}@${TARGET_HOST}" "sudo systemctl daemon-reload || true; sudo systemctl restart ${SERVICE_NAME} || true"

echo "Deploy finished."
