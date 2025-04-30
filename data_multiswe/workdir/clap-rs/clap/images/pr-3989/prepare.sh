#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 3610a14e9e41ca51bf320c8443924585cf1d59b0
bash /home/check_git_changes.sh

cargo test || true

