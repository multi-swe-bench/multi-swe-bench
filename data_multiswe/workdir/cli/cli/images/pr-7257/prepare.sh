#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 89caedf1817c21e4bdb9b136a46444225ec4c982
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

