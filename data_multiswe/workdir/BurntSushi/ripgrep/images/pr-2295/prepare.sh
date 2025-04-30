#!/bin/bash
set -e

cd /home/ripgrep
git reset --hard
bash /home/check_git_changes.sh
git checkout 1d35859861fa4710cee94cf0e0b2e114b152b946
bash /home/check_git_changes.sh

cargo test || true

