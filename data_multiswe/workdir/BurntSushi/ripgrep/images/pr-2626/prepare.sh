#!/bin/bash
set -e

cd /home/ripgrep
git reset --hard
bash /home/check_git_changes.sh
git checkout 7099e174acbcbd940f57e4ab4913fee4040c826e
bash /home/check_git_changes.sh

cargo test || true

