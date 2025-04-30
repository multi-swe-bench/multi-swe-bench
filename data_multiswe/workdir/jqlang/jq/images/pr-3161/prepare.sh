#!/bin/bash
set -e

cd /home/jq
git reset --hard
bash /home/check_git_changes.sh
git checkout 0b5ae30f19d71ca6cc7b5867f3c988c570ecd579
bash /home/check_git_changes.sh
git submodule update --init

