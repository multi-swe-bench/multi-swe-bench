#!/bin/bash
set -e

cd /home/bat
git reset --hard
bash /home/check_git_changes.sh
git checkout 2be3a14a7e2c74360765a5fa213750f727f2c5bb
bash /home/check_git_changes.sh

cargo test || true

