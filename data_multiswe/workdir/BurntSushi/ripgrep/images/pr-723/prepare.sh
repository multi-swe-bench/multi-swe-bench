#!/bin/bash
set -e

cd /home/ripgrep
git reset --hard
bash /home/check_git_changes.sh
git checkout 5e73075ef5300fdec03f6c4685750788108b00f4
bash /home/check_git_changes.sh

cargo test || true

