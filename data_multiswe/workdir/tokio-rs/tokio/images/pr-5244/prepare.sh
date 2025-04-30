#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout 766f22fae34d8b77384f63b01ffb250815fde74a
bash /home/check_git_changes.sh

cargo test || true

