#!/bin/bash
set -e

cd /home/tracing
git reset --hard
bash /home/check_git_changes.sh
git checkout 330dacfa71c9ad664bbb73f6898aaaa5caa70fb6
bash /home/check_git_changes.sh

cargo test || true

