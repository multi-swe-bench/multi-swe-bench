#!/bin/bash
set -e

cd /home/tracing
git reset --hard
bash /home/check_git_changes.sh
git checkout cb1dd95b8a67c3c69450882e8f8818546330a8ff
bash /home/check_git_changes.sh

cargo test || true

