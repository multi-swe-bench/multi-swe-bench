#!/bin/bash
set -e

cd /home/fd
git reset --hard
bash /home/check_git_changes.sh
git checkout a851570b15bbca91f1f4ef230c6d8939f2459ecc
bash /home/check_git_changes.sh

cargo test || true

