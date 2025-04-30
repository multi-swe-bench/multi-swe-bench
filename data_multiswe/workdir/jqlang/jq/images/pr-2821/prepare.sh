#!/bin/bash
set -e

cd /home/jq
git reset --hard
bash /home/check_git_changes.sh
git checkout 70807e2b1b3643019f3283b94d61998b9b35ee0e
bash /home/check_git_changes.sh
git submodule update --init

