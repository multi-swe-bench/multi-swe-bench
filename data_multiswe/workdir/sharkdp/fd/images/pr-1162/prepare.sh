#!/bin/bash
set -e

cd /home/fd
git reset --hard
bash /home/check_git_changes.sh
git checkout cbd11d8a45dc80392c5f1be9679051085e6a3376
bash /home/check_git_changes.sh

cargo test || true

