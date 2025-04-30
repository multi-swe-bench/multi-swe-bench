#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 04d0ec0e8c4888bfe248bf93dd9c12f06a451632
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

