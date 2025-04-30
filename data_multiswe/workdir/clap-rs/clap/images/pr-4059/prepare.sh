#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 1a08b9184bb1c4639042ad99290c6026ec7542ee
bash /home/check_git_changes.sh

cargo test || true

