#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 00e97121ec8cf4de86bdda704fb711302a8dfc96
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

