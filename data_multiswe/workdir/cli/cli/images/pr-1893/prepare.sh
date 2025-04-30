#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 012b004e103617671f96e09c1d4004845a35ba7b
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

