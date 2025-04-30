#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout b81122cabd5857bffeb0ea9be71583241236b825
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

