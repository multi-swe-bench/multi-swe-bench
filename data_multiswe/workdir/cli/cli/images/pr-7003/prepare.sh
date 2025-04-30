#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout fe7833134269c479fabca999271ddd809c928168
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

