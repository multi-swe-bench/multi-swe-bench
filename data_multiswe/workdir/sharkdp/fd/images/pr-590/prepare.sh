#!/bin/bash
set -e

cd /home/fd
git reset --hard
bash /home/check_git_changes.sh
git checkout 65b65b32be0cb987cf8bbed5fed9f7202deefa06
bash /home/check_git_changes.sh

cargo test || true

