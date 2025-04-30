#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout b2b5f57c2c945edd0eebc1b545ec1b7568e51484
bash /home/check_git_changes.sh

pnpm install || true

