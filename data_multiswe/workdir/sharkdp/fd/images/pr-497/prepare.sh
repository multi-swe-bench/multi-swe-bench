#!/bin/bash
set -e

cd /home/fd
git reset --hard
bash /home/check_git_changes.sh
git checkout 0f2429cabcb591df74fc2ab3e32b3ac967264f6d
bash /home/check_git_changes.sh

cargo test || true

