#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 15f01789d2a6b8952a01a8a3881b94aed4a44f4c
bash /home/check_git_changes.sh

cargo test || true

