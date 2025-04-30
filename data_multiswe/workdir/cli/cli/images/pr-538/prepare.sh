#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 67e1fbcae5835b5b745952a4ddc1324199e76dbf
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

