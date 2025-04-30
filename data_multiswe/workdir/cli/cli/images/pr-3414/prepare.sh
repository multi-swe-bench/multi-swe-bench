#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout f4d96ee78976ae638e9bbe99f565ab515718f6fe
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

