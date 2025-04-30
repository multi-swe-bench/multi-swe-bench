#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 7f5aad56cba45ced3f1b7537e03c45f1857f736a
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

