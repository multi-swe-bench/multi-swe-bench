#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 81457178fa7e055775867ca659b37798b5ae9584
bash /home/check_git_changes.sh

cargo test || true

