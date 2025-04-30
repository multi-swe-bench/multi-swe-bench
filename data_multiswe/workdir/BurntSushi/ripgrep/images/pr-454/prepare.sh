#!/bin/bash
set -e

cd /home/ripgrep
git reset --hard
bash /home/check_git_changes.sh
git checkout c50b8b4125dc7f1181944dd92d0aca97c2450421
bash /home/check_git_changes.sh

cargo test || true

