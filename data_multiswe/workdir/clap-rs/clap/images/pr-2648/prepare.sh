#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 75445b974ed536add0d4f13ce8131348ff553cf4
bash /home/check_git_changes.sh

cargo test || true

