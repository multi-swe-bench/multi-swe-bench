#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout e8e1e13d4fcd6495ba17fb0eafa414d5df7c00b6
bash /home/check_git_changes.sh

