#!/bin/bash
set -e

echo "[i] Starting password reset $(date)"
docker exec -it crtmgr_api python3 /api/full_setup.py --reset-admin

