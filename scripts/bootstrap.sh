#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
exec rtk proxy python3 scripts/bootstrap.py "$@"
