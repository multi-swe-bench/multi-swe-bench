#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout 8e15c234c60cf8132c490ccf03dd31738cfeaca8
bash /home/check_git_changes.sh

cargo test || true

