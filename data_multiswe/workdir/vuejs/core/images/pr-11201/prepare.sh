#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 582cd2e9bc21b8d9b695dc0ad28f96cc88d8f0cf
bash /home/check_git_changes.sh

pnpm install || true

