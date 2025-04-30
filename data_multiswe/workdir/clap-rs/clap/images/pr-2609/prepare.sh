#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 8ff68080e65e70929df030fedf94f28c6f7fe06c
bash /home/check_git_changes.sh

cargo test || true

