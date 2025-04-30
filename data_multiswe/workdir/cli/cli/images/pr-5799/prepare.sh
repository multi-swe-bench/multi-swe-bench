#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 604adc57efd7d98b560c4abf4b33f2241ad839e0
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

