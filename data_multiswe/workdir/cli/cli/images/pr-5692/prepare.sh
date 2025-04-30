#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 4c237708d878008e85e8190d310dc1826b463ca9
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

