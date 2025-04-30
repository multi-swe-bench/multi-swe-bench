#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout e8560525763fc2cc87943e7437573db960141be4
bash /home/check_git_changes.sh

