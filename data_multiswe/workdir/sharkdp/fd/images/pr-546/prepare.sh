#!/bin/bash
set -e

cd /home/fd
git reset --hard
bash /home/check_git_changes.sh
git checkout d05e7171d4e2f8feb7d5402026b02aa67a9f9b91
bash /home/check_git_changes.sh

cargo test || true

