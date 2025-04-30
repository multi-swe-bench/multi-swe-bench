#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 5c8f8d5f655777b1d306b01c590a5fac4b686bf3
bash /home/check_git_changes.sh

cargo test || true

