#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout e9fabfe9a9a0cfa2790edbba2f0b771c19433546
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

