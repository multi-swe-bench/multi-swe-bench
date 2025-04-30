#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 89cbcfe7eb186ff4edbe10792d17bdc55b04f297
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

