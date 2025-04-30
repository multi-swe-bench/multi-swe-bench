#!/bin/bash
set -e

cd /home/ripgrep
git reset --hard
bash /home/check_git_changes.sh
git checkout fed4fea217abbc502f2e823465de903c8f2b623d
bash /home/check_git_changes.sh

cargo test || true

