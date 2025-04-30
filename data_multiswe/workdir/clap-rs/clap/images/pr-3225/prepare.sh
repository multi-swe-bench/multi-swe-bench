#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout a0ab35d678d797041aad20ff9e99ddaa52b84e24
bash /home/check_git_changes.sh

cargo test || true

