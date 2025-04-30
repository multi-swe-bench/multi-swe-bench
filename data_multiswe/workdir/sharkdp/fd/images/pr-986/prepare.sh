#!/bin/bash
set -e

cd /home/fd
git reset --hard
bash /home/check_git_changes.sh
git checkout 3e201de9b06e4587781eaf4fe7e755d4f9d8c6df
bash /home/check_git_changes.sh

cargo test || true

