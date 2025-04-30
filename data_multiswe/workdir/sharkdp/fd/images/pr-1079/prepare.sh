#!/bin/bash
set -e

cd /home/fd
git reset --hard
bash /home/check_git_changes.sh
git checkout 218d475cb21763deaf0ecc8d46078b8f289d03a7
bash /home/check_git_changes.sh

cargo test || true

