#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 9d53b864369479e385455b55d2b6d3dad3467bed
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

