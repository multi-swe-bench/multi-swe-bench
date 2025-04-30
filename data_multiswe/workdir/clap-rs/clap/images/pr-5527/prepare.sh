#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 2f645d3e81c783a4e76ad17f1ccf283a58b75660
bash /home/check_git_changes.sh

cargo test || true

