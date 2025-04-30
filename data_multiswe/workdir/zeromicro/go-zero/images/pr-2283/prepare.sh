#!/bin/bash
set -e

cd /home/go-zero
git reset --hard
bash /home/check_git_changes.sh
git checkout 4cd065f4f40fce20be33bae6a4c457d22559701e
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

