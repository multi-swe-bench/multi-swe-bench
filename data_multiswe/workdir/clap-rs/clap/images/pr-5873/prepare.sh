#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 1d5c6798dc16db0b8130a0c73c8a5d818ec22131
bash /home/check_git_changes.sh

cargo test || true

