#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout 988ce61a0c019d7fc58575954636b9ff8d147845
bash /home/check_git_changes.sh

