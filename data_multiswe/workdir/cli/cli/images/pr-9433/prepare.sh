#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 86964d8809bed7bfbd798d444d5923b8a2bbd4d6
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

