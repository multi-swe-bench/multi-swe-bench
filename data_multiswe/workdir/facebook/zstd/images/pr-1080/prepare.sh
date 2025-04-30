#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout 99e8063d40c38355f26f97249c8ef3f30e15d5b4
bash /home/check_git_changes.sh

