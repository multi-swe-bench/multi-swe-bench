#!/bin/bash
set -e

cd /home/jq
git reset --hard
bash /home/check_git_changes.sh
git checkout f94a9d463ffb3422861a0da140470dbf5ce76632
bash /home/check_git_changes.sh
git submodule update --init

