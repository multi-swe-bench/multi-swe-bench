#!/bin/bash
set -e

cd /home/jq
git reset --hard
bash /home/check_git_changes.sh
git checkout c077b95ba2dcaafee39e302cc086bf99fa9248d0
bash /home/check_git_changes.sh
git submodule update --init

