#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout 58508398f4121f2a84092ac771db0f2b0fbb3b1a
bash /home/check_git_changes.sh

