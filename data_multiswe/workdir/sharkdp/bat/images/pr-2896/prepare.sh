#!/bin/bash
set -e

cd /home/bat
git reset --hard
bash /home/check_git_changes.sh
git checkout d00e05643ff6ef00de1aa8da90c869db993c93e2
bash /home/check_git_changes.sh

cargo test || true

