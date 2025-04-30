#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout 4ea632005d689f850e87a116b9e535a0015a7a0f
bash /home/check_git_changes.sh

cargo test || true

